"""Render the gallery images used by the README.

Run with::

    uv run python examples/make_gallery.py

Everything here goes through the packaged public API, so this doubles as a
smoke test: if the style fails to register, the palette fails to resolve, or
the title block collides with the axes, it shows up in the output.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: works the same in CI as on a laptop

import matplotlib.pyplot as plt
import numpy as np

import economiststyle
from economiststyle import econ_title

OUT = Path(__file__).resolve().parent.parent / "gallery"

# The published chart hand-places a label on nearly every notable country.
# Matplotlib has no collision avoidance, so this list stops at the points that
# sit in open space; adding the dense top-right cluster (Germany, Japan,
# France) or the crowded bottom-left (Sudan, Afghanistan) overprints them.
POINTS_TO_LABEL = [
    "Russia", "Iraq", "Congo", "Argentina", "India", "Italy",
    "South Africa", "Spain", "Botswana", "Cape Verde", "Bhutan",
    "Rwanda", "United States", "Barbados", "Norway", "New Zealand",
    "Greece", "Brazil", "Venezuela", "China",
]

#: Region colours for the flagship chart, following the published original:
#: an ordered ramp running dark blue -> light blue -> teal -> coral -> brown,
#: rather than the categorical cycle. The ordering carries meaning here, so it
#: is set explicitly instead of leaning on ``axes.prop_cycle``.
REGION_COLORS = {
    "OECD": "blue:0",
    "Americas": "blue:1",
    "Asia & Oceania": "blue:2",
    "Central & Eastern Europe": "aquamarine:0",
    "Middle East & North Africa": "red:2",
    "Sub-Saharan Africa": "brown:0",
}


def corruption_chart(path: Path) -> None:
    """The flagship chart: corruption vs. human development, 2011."""
    import statsmodels.formula.api as smf

    df = economiststyle.load_cpi_hdi()

    fig, ax = plt.subplots(figsize=(10, 6.5))

    for region, color in REGION_COLORS.items():
        subset = df[df["Region"] == region]
        ax.scatter(
            subset["CPI"], subset["HDI"],
            facecolors="none", edgecolors=color,
            s=70, linewidth=1.6, label=region,
        )

    model = smf.ols("HDI ~ Log_CPI", data=df).fit()
    ax.plot(
        df["CPI"], model.predict(df["Log_CPI"]),
        "-", c="economist:red", linewidth=1.75,
        # R-squared is a proportion; the published chart shows it as a whole
        # percentage. Formatting it as "{:.2f}%" would print "0.52%".
        label=f"$R^2=${model.rsquared * 100:.0f}%",
    )

    for country in POINTS_TO_LABEL:
        row = df.loc[df["Country"] == country, ["CPI", "HDI"]]
        if row.empty:
            continue
        x, y = row.values.reshape(-1)
        ax.annotate(
            country, xy=(x, y), xytext=(-2, 6),
            textcoords="offset points", size=9,
        )

    ax.set(xlim=(0.9, 10.3), ylim=(0.2, 1.0))
    ax.xaxis.set_major_locator(plt.MaxNLocator(10))
    ax.set_xlabel(
        "Corruption Perceptions Index, 2011 (10=least corrupt)", style="italic"
    )
    ax.set_ylabel("Human Development Index, 2011 (1=best)", style="italic")

    # Legend banded horizontally above the plot, Economist-fashion, so it
    # never sits on top of the data.
    ax.legend(
        loc="lower left", bbox_to_anchor=(0, 1.02),
        ncol=4, columnspacing=1.1, fontsize=9,
        handletextpad=0.4, labelspacing=0.5,
    )

    # No subtitle: the published chart runs straight from the title to the
    # legend band. `headroom` reserves the two legend rows, so the spacing is
    # derived from the title block rather than pinned to a hardcoded top that
    # goes stale the moment the block changes.
    econ_title(
        fig,
        "Corruption and human development",
        source="Sources: Transparency International; UN Human Development Report",
        # Two legend rows plus the ~0.025 of figure height the published chart
        # leaves between the title and the legend band.
        headroom=0.094,
    )
    fig.savefig(path)
    plt.close(fig)


def palette_chart(path: Path) -> None:
    """The ten cycle colours, in order."""
    fig, ax = plt.subplots(figsize=(10, 4))

    for i, color in enumerate(economiststyle.CYCLE):
        ax.barh(i, 1, color=color, height=0.78)
        ax.text(1.02, i, f"C{i}  {color}", va="center", size=10)

    ax.set(xlim=(0, 1.6), ylim=(-0.7, len(economiststyle.CYCLE) - 0.3))
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    econ_title(fig, "The colour cycle", "axes.prop_cycle, in order")
    fig.savefig(path)
    plt.close(fig)


def timeseries_chart(path: Path, *, variant: str = "default") -> None:
    """A multi-series line chart, for comparing the colour and gray styles."""
    economiststyle.use(variant)

    rng = np.random.default_rng(0)
    dates = np.arange("2016-01", "2026-01", dtype="datetime64[M]")

    fig, ax = plt.subplots(figsize=(10, 5))
    for i, name in enumerate(["Britain", "United States", "Germany", "Japan"]):
        series = rng.normal(0.4, 1.6, dates.size).cumsum() + 100
        ax.plot(dates, series, label=name)

    ax.set_ylabel("Index, 2016=100", style="italic")
    ax.legend(ncol=4)

    label = "Grayscale variant" if variant in {"gray", "grey"} else "Default palette"
    econ_title(fig, "Output per person", label, "Source: Simulated data")
    fig.savefig(path)
    plt.close(fig)
    economiststyle.use()


def altair_timeseries_chart(path: Path, *, variant: str = "default") -> None:
    """The Altair counterpart to ``timeseries_chart``.

    Same simulated data and figure intent as the Matplotlib version, so the
    two gallery images are a direct side-by-side check that the Vega-Lite
    theme (``economiststyle.altair``) reproduces the Matplotlib style: same
    colour cycle, y-only grid, spineless axes, bold left-aligned title with a
    grey subtitle, legend banded above the plot. It does not attempt the red
    corner tag — Vega-Lite has no drawing surface outside a view's own
    scales, so that furniture stays Matplotlib-only for now.
    """
    import altair as alt
    import pandas as pd

    import economiststyle.altair as economist_altair

    economist_altair.enable(variant)

    rng = np.random.default_rng(0)
    dates = np.arange("2016-01", "2026-01", dtype="datetime64[M]")
    countries = ["Britain", "United States", "Germany", "Japan"]
    df = pd.concat(
        [
            pd.DataFrame(
                {
                    "date": dates,
                    "value": rng.normal(0.4, 1.6, dates.size).cumsum() + 100,
                    "country": name,
                }
            )
            for name in countries
        ],
        ignore_index=True,
    )

    label = "Grayscale variant" if variant in {"gray", "grey"} else "Default palette"
    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("date:T", title=None),
            y=alt.Y("value:Q", title="Index, 2016=100"),
            # Sorted to the call order above rather than Altair's default
            # alphabetical domain sort, matching how the Matplotlib version
            # colours series in plot order.
            color=alt.Color("country:N", title=None, sort=countries),
        )
        .properties(
            title=alt.Title("Output per person", subtitle=label),
            width=560,
            height=320,
        )
    )
    chart.save(path, scale_factor=2)
    economist_altair.enable()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out", type=Path, default=OUT, help="directory to write PNGs into"
    )
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    economiststyle.use()

    charts = {
        "corruption.png": corruption_chart,
        "palette.png": palette_chart,
        "timeseries.png": lambda p: timeseries_chart(p, variant="default"),
        "timeseries-gray.png": lambda p: timeseries_chart(p, variant="gray"),
        "timeseries-altair.png": lambda p: altair_timeseries_chart(p, variant="default"),
        "timeseries-altair-gray.png": lambda p: altair_timeseries_chart(p, variant="gray"),
    }
    for name, fn in charts.items():
        target = args.out / name
        fn(target)
        print(f"wrote {target}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
