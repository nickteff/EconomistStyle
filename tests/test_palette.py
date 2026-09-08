"""Tests for the colour palette and its Matplotlib registration."""

from __future__ import annotations

import matplotlib.colors as mcolors
import pytest

import economiststyle
from economiststyle import palette


def test_every_colour_is_a_valid_hex():
    everything = [
        *palette.BRAND.values(),
        *(c for ramp in palette.RAMPS.values() for c in ramp),
        *palette.CYCLE,
    ]
    for color in everything:
        assert mcolors.is_color_like(color), color


def test_cycle_has_ten_colours():
    assert len(palette.CYCLE) == 10


@pytest.mark.parametrize("family", sorted(palette.RAMPS))
def test_ramps_have_no_duplicates(family):
    """The original grey ramp listed #909294 twice, shifting every index
    after it. Guard against that reappearing in any ramp."""
    ramp = [c.lower() for c in palette.RAMPS[family]]
    assert len(ramp) == len(set(ramp)), f"{family} ramp repeats a colour"


def test_named_colours_resolve_through_matplotlib():
    economiststyle.register_colors()
    assert mcolors.to_hex("blue:0") == "#004c64"
    assert mcolors.to_hex("red:0") == "#e30010"
    assert mcolors.to_hex("economist:red") == "#e3120b"
    assert mcolors.to_hex("economist:london") == "#b6b6b6"


def test_named_colours_cover_every_ramp_entry():
    names = economiststyle.named_colors()
    for family, ramp in palette.RAMPS.items():
        for i in range(len(ramp)):
            assert f"{family}:{i}" in names


def test_register_colors_uses_the_public_mapping():
    """Registration must go through the public accessor.

    The original notebook mutated the private
    ``matplotlib.colors._colors_full_map`` and monkeypatched
    ``matplotlib._color_data``; neither carries a compatibility guarantee.
    """
    registered = economiststyle.register_colors()
    live = mcolors.get_named_colors_mapping()
    for name, value in registered.items():
        assert live[name] == value
