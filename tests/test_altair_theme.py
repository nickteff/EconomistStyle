"""Tests for the optional Altair theme.

Altair is an optional dependency (see the ``altair`` extra in
pyproject.toml), so every test here skips outright if it is not installed —
mirroring how the base package must keep working without it.
"""

from __future__ import annotations

import pytest

alt = pytest.importorskip("altair")

import economiststyle.altair as economist_altair  # noqa: E402
from economiststyle.altair import GRAY_THEME, THEME  # noqa: E402
from economiststyle.palette import CYCLE  # noqa: E402


def test_theme_cycle_matches_palette_module():
    """Keeps the Altair theme and palette.py from drifting apart."""
    assert THEME["config"]["range"]["category"] == CYCLE


def test_gray_theme_uses_the_dark_first_grey_ramp():
    assert GRAY_THEME["config"]["range"]["category"][0].upper() == "#1A1719"


def test_available_themes():
    assert economist_altair.available_themes() == [
        "theeconomist",
        "theeconomist-gray",
    ]


def test_themes_are_registered():
    assert "theeconomist" in alt.theme.names()
    assert "theeconomist-gray" in alt.theme.names()


def test_enable_activates_the_named_theme():
    economist_altair.enable()
    assert alt.theme.active == "theeconomist"

    economist_altair.enable("gray")
    assert alt.theme.active == "theeconomist-gray"

    economist_altair.enable("grey")
    assert alt.theme.active == "theeconomist-gray"

    economist_altair.enable()
    assert alt.theme.active == "theeconomist"


def test_unknown_variant_raises():
    with pytest.raises(ValueError, match="unknown variant"):
        economist_altair.enable("neon")


def test_theme_produces_a_valid_spec():
    """A chart under the theme must still serialise to a valid Vega-Lite spec."""
    import pandas as pd

    economist_altair.enable()
    df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    chart = alt.Chart(df).mark_line().encode(x="x:Q", y="y:Q")
    spec = chart.to_dict()
    assert spec["config"]["range"]["category"] == CYCLE
