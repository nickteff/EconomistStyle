"""The Economist colour palette.

Three things live here:

* ``BRAND`` — the named brand colours, keyed by the city names the original
  notebook used ("economist", "beijing", "london", ...).
* ``RAMPS`` — the tonal ramps, keyed by hue, each ordered light-to-dark
  within its family.
* ``CYCLE`` — the ten curated colours, in the order they appear in the style
  sheet's ``axes.prop_cycle``. ``CYCLE[0]`` is what a single-series chart
  gets, so it leads with the signature blue.

Importing :mod:`economiststyle` registers every ramp colour with Matplotlib
under a ``family:index`` name (``"blue:0"``, ``"red:2"``) plus the brand
colours under ``economist:name`` (``"economist:red"``), so they can be passed
anywhere Matplotlib accepts a colour string.
"""

from __future__ import annotations

import matplotlib.colors as mcolors

__all__ = [
    "BRAND",
    "RAMPS",
    "CYCLE",
    "named_colors",
    "register_colors",
]


#: Brand colours, keyed by the city names used in the original notebook.
BRAND: dict[str, str] = {
    "economist": "#e3120b",
    "beijing": "#121212",
    "kiev": "#383e42",
    "moscow": "#7a7a7a",
    "london": "#b6b6b6",
    "cardiff": "#d7d7d7",
    "berlin": "#f2f2f2",
    "prague": "#fbfbfb",
    "thimphu": "#ffffff",
    "honolulu": "#16c9b3",
    "dakar": "#0d6380",
    "boston": "#c5cbe9",
    "milan": "#4c60eb",
    "chicago": "#3e51b5",
    "kosice": "#8594e6",
    "athens": "#20328e",
    "copenhagen": "#38a8e0",
    "budapest": "#fc150d",
    "timbuktu": "#bc2621",
    "york": "#fff600",
    "amsterdam": "#fed630",
    "bristol": "#08c5b2",
    "rome": "#f39200",
    "genoa": "#4e64b5",
    "manchester": "#3ca8df",
}

#: Tonal ramps, keyed by hue family.
RAMPS: dict[str, list[str]] = {
    "red": ["#E30010", "#e11b17", "#E84932", "#E88B6F", "#EBA289"],
    "brown": ["#632514", "#762B1A", "#9D8278", "#DEC3AB", "#EAD6BF"],
    "green": ["#44674C", "#6E8F75", "#96B19B", "#B9CDBC", "#DBE8DC"],
    "aquamarine": ["#00857C", "#528EA5", "#6895A7", "#74BCBF"],
    "blue": ["#004C64", "#009FD7", "#75D0F4", "#C1D5DF", "#D5E3EA", "#F4FBFE"],
    "grey": [
        "#1A1719",
        "#525254",
        "#5E5E60",
        "#696A6C",
        "#808184",
        "#909294",
        "#ACADB0",
        "#CBCCCE",
        "#E6E7E8",
    ],
}

#: The ten curated cycle colours, matching the style sheet's prop_cycle.
CYCLE: list[str] = [
    RAMPS["blue"][1],        # #009FD7
    RAMPS["red"][0],         # #E30010
    RAMPS["aquamarine"][1],  # #528EA5
    BRAND["rome"],           # #f39200
    RAMPS["blue"][0],        # #004C64
    RAMPS["red"][2],         # #E84932
    RAMPS["aquamarine"][3],  # #74BCBF
    BRAND["amsterdam"],      # #fed630
    RAMPS["blue"][2],        # #75D0F4
    RAMPS["red"][4],         # #EBA289
]


def named_colors() -> dict[str, str]:
    """Return the ``name -> hex`` mapping this package registers.

    Ramp colours are named ``family:index`` (``"blue:0"``) and brand colours
    ``economist:name`` (``"economist:red"``). The brand key ``"economist"``
    itself is exposed as ``"economist:red"`` because it *is* the signature
    red, and a bare ``"economist"`` would read ambiguously at a call site.
    """
    colors = {
        f"{family}:{i}": hex_value
        for family, ramp in RAMPS.items()
        for i, hex_value in enumerate(ramp)
    }
    for name, hex_value in BRAND.items():
        key = "economist:red" if name == "economist" else f"economist:{name}"
        colors[key] = hex_value
    return colors


def register_colors() -> dict[str, str]:
    """Register the palette as Matplotlib named colours.

    Uses the public :func:`matplotlib.colors.get_named_colors_mapping`, which
    returns the live mapping Matplotlib resolves colour strings against, so
    updating it in place is enough. The original notebook reached into the
    private ``matplotlib.colors._colors_full_map`` and reassigned it, and
    also monkeypatched ``matplotlib._color_data`` — both are private and have
    no compatibility guarantee across Matplotlib releases.

    Returns the mapping that was registered.
    """
    colors = named_colors()
    mcolors.get_named_colors_mapping().update(colors)
    return colors
