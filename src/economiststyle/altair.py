"""An Economist-inspired Vega-Lite theme for Altair.

Not part of :mod:`economiststyle`'s import-time registration: Altair is an
optional dependency (this module does ``import altair`` at module scope), so
pulling it in from ``economiststyle/__init__.py`` would make Altair a hard
requirement of the base, Matplotlib-only package. Import this module
explicitly instead::

    import economiststyle.altair as economist_altair
    economist_altair.enable()

    import altair as alt
    alt.Chart(df).mark_line().encode(x="year:T", y="value:Q", color="series:N")

Vega-Lite has no analogue to the red corner tag
:func:`economiststyle.annotate.econ_title` draws on a Matplotlib figure: a
Vega-Lite spec has no drawing surface outside a view's own scales, so a mark
can't be placed in the figure margin the way ``fig.add_artist`` places one on
a Matplotlib canvas. This module therefore covers only what a Vega-Lite theme
*can* express — the colour cycle, axis/grid/tick styling, fonts, mark
defaults, and title/subtitle placement, which Vega-Lite (unlike Matplotlib)
supports natively rather than needing hand-drawn figure text.
"""

from __future__ import annotations

import altair as alt

from .annotate import LABEL_GREY
from .palette import CYCLE, RAMPS

__all__ = ["THEME", "GRAY_THEME", "available_themes", "enable"]

#: Same reasoning as the .mplstyle font stack: a comma-separated CSS-style
#: fallback list, since Vega/Vega-Lite text marks resolve ``font`` the way a
#: browser resolves ``font-family``. DejaVu Sans is dropped from the tail of
#: the stack because it is a Matplotlib-bundled fallback with no equivalent
#: in a browser; plain ``sans-serif`` is the browser's own fallback.
_FONT_STACK = (
    "Gill Sans MT, Gill Sans, Lato, Fira Sans, Source Sans Pro, "
    "Open Sans, sans-serif"
)

#: The grayscale cycle, darkest-first, matching
#: ``theeconomist-gray.mplstyle``'s ``axes.prop_cycle``.
_GRAY_CYCLE = RAMPS["grey"][:6]

_VARIANTS = {
    "default": "theeconomist",
    "gray": "theeconomist-gray",
    "grey": "theeconomist-gray",
}


def _config(category: list[str]) -> dict:
    """Build a Vega-Lite theme config for the given colour cycle."""
    return {
        "background": "white",
        "config": {
            "font": _FONT_STACK,
            "title": {
                "anchor": "start",
                "font": _FONT_STACK,
                "fontSize": 14,
                "fontWeight": "bold",
                "subtitleFont": _FONT_STACK,
                "subtitleFontSize": 11,
                "subtitleColor": LABEL_GREY,
            },
            "axis": {
                "labelColor": LABEL_GREY,
                "labelFont": _FONT_STACK,
                "titleColor": LABEL_GREY,
                "titleFont": _FONT_STACK,
                "domainColor": LABEL_GREY,
                "tickColor": LABEL_GREY,
                "gridOpacity": 0.5,
            },
            # Grid only on the y axis, spine only on the x axis: matches
            # axes.grid.axis: y and the axes.spines.* block in
            # theeconomist.mplstyle.
            "axisY": {"domain": False, "ticks": False, "grid": True},
            "axisX": {"domain": True, "ticks": True, "grid": False},
            # No border around the plot area, matching the spineless look.
            "view": {"stroke": None},
            "line": {"strokeWidth": 1.75},
            "point": {"size": 90, "filled": True},
            "range": {"category": category},
            "legend": {
                "orient": "top",
                "title": None,
                "labelFont": _FONT_STACK,
                "symbolType": "circle",
            },
        },
    }


#: The full-colour theme, matching ``theeconomist.mplstyle``.
THEME: dict = _config(CYCLE)

#: The grayscale variant, matching ``theeconomist-gray.mplstyle``.
GRAY_THEME: dict = _config(_GRAY_CYCLE)


def available_themes() -> list[str]:
    """Return the theme names this module registers, as ``enable`` accepts them."""
    return ["theeconomist", "theeconomist-gray"]


def _register() -> None:
    """Register the themes with Altair, without enabling either.

    Uses ``alt.theme.register`` (Altair >= 5.5), the current public theme
    API, rather than the older ``alt.themes.register``/``enable`` pair it
    superseded — the same "prefer the API that isn't on its way out"
    reasoning as the Matplotlib side's ``_user_library_paths()``.
    """
    alt.theme.register("theeconomist", enable=False)(lambda: THEME)
    alt.theme.register("theeconomist-gray", enable=False)(lambda: GRAY_THEME)


def enable(variant: str = "default") -> None:
    """Activate the theme.

    Parameters
    ----------
    variant
        ``"default"`` for the full-colour theme, or ``"gray"`` (``"grey"``
        also works) for the grayscale variant.

    Raises
    ------
    ValueError
        If ``variant`` is not one of the known variants.
    """
    try:
        name = _VARIANTS[variant]
    except KeyError:
        known = ", ".join(sorted(set(_VARIANTS) - {"grey"}))
        raise ValueError(
            f"unknown variant {variant!r}; expected one of: {known}"
        ) from None
    alt.theme.enable(name)


_register()
