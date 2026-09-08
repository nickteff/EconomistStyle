"""Tests for the title block and the bundled dataset."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest
from matplotlib.patches import Rectangle

import economiststyle
from economiststyle import econ_title


@pytest.fixture
def fig():
    figure = plt.figure(figsize=(8, 5))
    figure.add_subplot(111)
    yield figure
    plt.close(figure)


def _texts(figure):
    return [t.get_text() for t in figure.texts]


def test_draws_tag_title_subtitle_and_source(fig):
    econ_title(fig, "Headline", "Subtitle here", "Source: somewhere")

    rectangles = [a for a in fig.artists if isinstance(a, Rectangle)]
    assert len(rectangles) == 1, "one tag, and no rule across the top"
    assert matplotlib.colors.to_hex(
        rectangles[0].get_facecolor()
    ) == economiststyle.ECONOMIST_RED.lower()

    assert _texts(fig) == ["Headline", "Subtitle here", "Source: somewhere"]


def test_tag_is_portrait_and_flush_to_the_corner(fig):
    """Geometry measured from a published chart: a 9x27px tag at (0, 0).

    An earlier version drew a wide, flat bar plus a full-width rule across
    the top. Both were wrong: the tag stands taller than it is wide, and
    there is no rule.
    """
    econ_title(fig, "Headline")
    tag = next(a for a in fig.artists if isinstance(a, Rectangle))

    fig_w, fig_h = fig.get_size_inches()
    width_in = tag.get_width() * fig_w
    height_in = tag.get_height() * fig_h
    assert height_in > 2 * width_in, "tag is a portrait block, not a flat bar"

    x0, y0 = tag.get_xy()
    assert x0 == pytest.approx(0.0), "flush to the left edge"
    assert y0 + tag.get_height() == pytest.approx(1.0), "flush to the top"


def test_plot_area_is_widened_to_house_margins(fig):
    """The published plot area runs 0.066->0.963, not Matplotlib's 0.125/0.9."""
    econ_title(fig, "Headline")
    assert fig.subplotpars.left < 0.1
    assert fig.subplotpars.right > 0.95


def test_title_only(fig):
    econ_title(fig, "Just a headline")
    assert _texts(fig) == ["Just a headline"]


def test_returns_the_figure_for_chaining(fig):
    assert econ_title(fig, "Headline") is fig


def test_title_is_bold_and_left_aligned(fig):
    econ_title(fig, "Headline", x=0.03)
    title = fig.texts[0]
    assert title.get_fontweight() == "bold"
    assert title.get_ha() == "left"
    assert title.get_position()[0] == pytest.approx(0.03)


def test_adjust_makes_room_below_the_block(fig):
    econ_title(fig, "Headline", "Subtitle", "Source")
    assert fig.subplotpars.top < 0.9


def test_axes_top_accounts_for_the_title_height(fig):
    """The plot must start below the *bottom* of the title, not its top.

    An earlier version advanced past the subtitle but never past the title
    itself, so the axes top was a magic constant that only avoided a
    collision by luck — and left a visible gap once the subtitle was removed.
    """
    top, title_size = 0.962, 14.0
    econ_title(fig, "Headline", top=top, title_size=title_size, headroom=0.0)

    title_height = title_size / 72.0 / fig.get_figheight() * 1.45
    assert fig.subplotpars.top == pytest.approx(top - title_height, abs=0.005)


def test_a_subtitle_pushes_the_plot_further_down(fig):
    econ_title(fig, "Headline")
    without = fig.subplotpars.top

    fig2 = plt.figure(figsize=(8, 5))
    fig2.add_subplot(111)
    econ_title(fig2, "Headline", "Subtitle")
    assert fig2.subplotpars.top < without
    plt.close(fig2)


def test_headroom_reserves_extra_space(fig):
    econ_title(fig, "Headline", headroom=0.0)
    tight = fig.subplotpars.top

    fig2 = plt.figure(figsize=(8, 5))
    fig2.add_subplot(111)
    econ_title(fig2, "Headline", headroom=0.09)
    assert fig2.subplotpars.top == pytest.approx(tight - 0.09, abs=1e-6)
    plt.close(fig2)


def test_adjust_skipped_when_a_layout_engine_is_active():
    """subplots_adjust fights constrained layout, so it must be skipped."""
    figure = plt.figure(figsize=(8, 5), layout="constrained")
    figure.add_subplot(111)
    before = figure.subplotpars.top
    econ_title(figure, "Headline", "Subtitle")
    assert figure.subplotpars.top == before
    plt.close(figure)


def test_dataset_loads_tidy():
    df = economiststyle.load_cpi_hdi()
    assert {"Country", "HDI", "CPI", "Region", "Log_CPI"} <= set(df.columns)
    assert "HDI.Rank" not in df.columns, "renamed for statsmodels formulas"
    assert df["CPI"].is_monotonic_increasing
    assert "OECD" in set(df["Region"])
    assert not any("\n" in r for r in df["Region"]), "labels stay single-line"


def test_dataset_loads_raw():
    raw = economiststyle.load_cpi_hdi(tidy=False)
    assert "HDI.Rank" in raw.columns
    assert "Log_CPI" not in raw.columns


def test_data_path_points_at_a_real_file():
    from pathlib import Path

    assert Path(economiststyle.data_path()).is_file()
