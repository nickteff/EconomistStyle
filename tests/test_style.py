"""Tests for style registration and the portability guarantees."""

from __future__ import annotations

import os
import subprocess
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest

import economiststyle


def test_styles_are_registered():
    assert economiststyle.available_styles() == [
        "theeconomist",
        "theeconomist-gray",
    ]
    assert "theeconomist" in plt.style.available


def test_style_resolves_by_bare_name():
    """The whole point of packaging: no relative path, no cwd dependency."""
    plt.style.use("theeconomist")


def test_style_resolves_from_an_unrelated_working_directory(tmp_path):
    """Guards the original bug: the style used to need cwd == repo root."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import economiststyle, matplotlib.pyplot as plt;"
            "plt.style.use('theeconomist');"
            "print('ok')",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env={**os.environ, "MPLBACKEND": "Agg"},
    )
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_import_emits_no_deprecation_warnings():
    """Registration must not lean on deprecated Matplotlib internals.

    ``matplotlib.style.core`` is deprecated in 3.11 and removed in 3.13;
    importing it to reach ``USER_LIBRARY_PATHS`` would put this package on a
    countdown to breaking.
    """
    result = subprocess.run(
        [sys.executable, "-W", "error::DeprecationWarning", "-c",
         "import economiststyle; print('ok')"],
        capture_output=True,
        text=True,
        env={**os.environ, "MPLBACKEND": "Agg"},
    )
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_font_family_stays_sans_serif():
    """The portability guard.

    Setting ``font.family`` to a face name (as the original style did with
    ``Gill Sans MT``) makes Matplotlib skip the ``font.sans-serif`` fallback
    list entirely, so any machine without that proprietary font silently
    renders in DejaVu Sans instead of degrading to a near match.
    """
    plt.style.use("theeconomist")
    assert mpl.rcParams["font.family"] == ["sans-serif"]

    stack = mpl.rcParams["font.sans-serif"]
    assert stack[0] == "Gill Sans MT", "preferred face should lead the stack"
    assert "DejaVu Sans" in stack, "must fall back to a font that always exists"


def test_style_cycle_matches_palette_module():
    """Keeps the .mplstyle sheet and palette.py from drifting apart."""
    plt.style.use("theeconomist")
    cycle = mpl.rcParams["axes.prop_cycle"].by_key()["color"]
    assert [c.lower() for c in cycle] == [
        c.lower() for c in economiststyle.CYCLE
    ]


def test_gray_variant_overrides_only_the_cycle():
    economiststyle.use("gray")
    gray_cycle = mpl.rcParams["axes.prop_cycle"].by_key()["color"]
    assert gray_cycle[0].lower() == "#1a1719"
    # The overlay must not disturb what the base style established.
    assert mpl.rcParams["font.family"] == ["sans-serif"]
    assert mpl.rcParams["axes.spines.left"] is False

    economiststyle.use()
    assert mpl.rcParams["axes.prop_cycle"].by_key()["color"][0].lower() == "#009fd7"


def test_grey_spelling_is_accepted():
    economiststyle.use("grey")
    assert mpl.rcParams["axes.prop_cycle"].by_key()["color"][0].lower() == "#1a1719"
    economiststyle.use()


def test_unknown_variant_raises():
    with pytest.raises(ValueError, match="unknown variant"):
        economiststyle.use("neon")
