"""Chart furniture: the title block a style sheet cannot express.

An ``.mplstyle`` file can set colours, spines, grids and fonts, but the thing
that most makes a chart *read* as The Economist is layout the rcParams system
has no vocabulary for: the small red tag flush into the top-left corner, a bold
left-aligned title beside it, an optional lighter subtitle, and a source line
along the bottom. :func:`econ_title` draws that block.

The tag geometry is taken from a published chart rather than invented: in a
595x404 original the tag measures 9x27 pixels at (0, 0) — a portrait block
roughly three times taller than it is wide, flush to the corner, standing to
the left of the title. There is no rule across the top of the graphic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from matplotlib.patches import Rectangle

if TYPE_CHECKING:  # pragma: no cover
    from matplotlib.figure import Figure

__all__ = ["econ_title", "ECONOMIST_RED", "LABEL_GREY"]

#: The signature red of the masthead and the corner tag.
ECONOMIST_RED = "#E3120B"

#: The grey used for subtitles, axis labels and source lines.
LABEL_GREY = "#525254"


def econ_title(
    fig: "Figure",
    title: str,
    subtitle: str | None = None,
    source: str | None = None,
    *,
    x: float = 0.035,
    top: float = 0.962,
    tag_color: str = ECONOMIST_RED,
    tag_x: float = 0.0,
    tag_top: float = 1.0,
    tag_width: float = 0.015,
    tag_height: float = 0.067,
    title_size: float = 14.0,
    subtitle_size: float = 11.0,
    source_size: float = 8.5,
    adjust: bool = True,
    left: float = 0.075,
    right: float = 0.965,
    headroom: float = 0.02,
) -> "Figure":
    """Draw the Economist title block on ``fig``.

    Everything is positioned in figure coordinates, so this works with any
    axes layout, including subplot grids.

    Parameters
    ----------
    fig
        The figure to annotate.
    title
        Bold headline, left-aligned and set to the right of the tag.
    subtitle
        Optional lighter line beneath the title — conventionally the units or
        the qualifier ("% of GDP", "2011"). The house style often omits it and
        goes straight from the title to the legend.
    source
        Optional source credit, set small and grey along the bottom.
    x
        Left edge of the text block, in figure coordinates. The title,
        subtitle and source all align to it.
    top
        Figure-coordinate height of the top of the title text.
    tag_x, tag_top, tag_width, tag_height
        Geometry of the red tag, in figure coordinates. The defaults put a
        portrait block flush into the top-left corner, proportioned about
        1:4.5 in figure fractions, which lands near 1:3 once the usual
        landscape figure aspect is applied.
    adjust
        When True, pull the axes down (and up from the bottom, if a source
        line was drawn) so the furniture does not collide with the plot, and
        widen the plot area to ``left``/``right``. Ignored when the figure
        manages its own layout engine, since ``subplots_adjust`` would fight
        with it.
    left, right
        Horizontal extent of the plot area, in figure coordinates. The
        defaults are measured from a published chart, whose plot runs from
        0.066 to 0.963 — considerably wider than Matplotlib's 0.125/0.9, and
        a large part of why the house style reads as it does. Any axis label
        that overhangs is still captured, because the style sheet saves with
        ``savefig.bbox: tight``.
    headroom
        Extra vertical space to leave between the bottom of the title block
        and the top of the plot, in figure coordinates. The default is a hair
        of breathing room; raise it to reserve a band for a legend placed
        above the axes (roughly 0.035 per legend row on a 6-7in figure).

    Returns
    -------
    matplotlib.figure.Figure
        The same figure, so calls can be chained.
    """
    # Text heights are derived from the font sizes and the figure height
    # rather than hardcoded, so the block closes up correctly whichever of
    # the title/subtitle/source are present and whatever size the figure is.
    fig_height_in = fig.get_figheight()

    def line_height(points: float, leading: float = 1.45) -> float:
        """Height of one line of text, as a fraction of figure height."""
        return points / 72.0 / fig_height_in * leading

    y = top

    # The signature tag: a portrait block flush into the top-left corner,
    # standing to the left of the title. No rule runs across the top.
    fig.add_artist(
        Rectangle(
            (tag_x, tag_top - tag_height),
            tag_width,
            tag_height,
            transform=fig.transFigure,
            facecolor=tag_color,
            edgecolor="none",
            zorder=6,
        )
    )
    fig.text(
        x,
        y,
        title,
        transform=fig.transFigure,
        fontsize=title_size,
        fontweight="bold",
        va="top",
        ha="left",
        zorder=5,
    )

    # Advance past the title's own height. Omitting this was why the axes top
    # had to be guessed at with a magic constant.
    y -= line_height(title_size)

    if subtitle:
        y -= line_height(subtitle_size) * 0.35   # gap between the two lines
        fig.text(
            x,
            y,
            subtitle,
            transform=fig.transFigure,
            fontsize=subtitle_size,
            color=LABEL_GREY,
            va="top",
            ha="left",
            zorder=5,
        )
        y -= line_height(subtitle_size)

    if source:
        fig.text(
            x,
            0.015,
            source,
            transform=fig.transFigure,
            fontsize=source_size,
            color=LABEL_GREY,
            va="bottom",
            ha="left",
            zorder=5,
        )

    # A figure driven by constrained/tight layout positions its own axes;
    # calling subplots_adjust there is ignored with a warning, so skip it.
    if adjust and fig.get_layout_engine() is None:
        fig.subplots_adjust(
            left=left,
            right=right,
            # y is now the bottom of the text block, so the plot starts just
            # below it plus whatever headroom the caller reserved.
            top=max(0.05, y - headroom),
            bottom=0.135 if source else 0.11,
        )

    return fig
