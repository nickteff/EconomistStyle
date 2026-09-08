# economiststyle

An Economist-inspired Matplotlib style. Began in 2017 as a hobby notebook for
learning Matplotlib; revived in 2026 as an installable package with the
notebook kept as the derivation narrative.

## Layout

```text
src/economiststyle/
  __init__.py          registers styles + colours on import; use(), available_styles()
  palette.py           BRAND, RAMPS, CYCLE, named_colors(), register_colors()
  annotate.py          econ_title() — the red tag, headline, subtitle, source line
  datasets.py          load_cpi_hdi(), data_path(), REGIONS
  styles/              theeconomist.mplstyle, theeconomist-gray.mplstyle
  data/                EconomistData.csv
tests/                 pytest suite
examples/make_gallery.py   renders gallery/*.png; doubles as a smoke test
MatplotlibLearning.ipynb   the original derivation, still executed by CI
```

## Commands

```bash
uv sync
uv run pytest
uv run python examples/make_gallery.py
```

## Design decisions worth not undoing

**`font.family` must stay `sans-serif`.** Naming a face directly (the original
style said `font.family: Gill Sans MT`) makes Matplotlib skip the
`font.sans-serif` fallback list, so any machine without that proprietary font
silently renders in DejaVu Sans. The preferred face leads the *stack* instead.
`tests/test_style.py::test_font_family_stays_sans_serif` guards this.

**Colour registration goes through `mcolors.get_named_colors_mapping()`.** It
returns the live mapping, so an in-place `.update()` suffices. The original
notebook mutated the private `matplotlib.colors._colors_full_map` and
monkeypatched `matplotlib._color_data`; neither has any compatibility
guarantee.

**Style registration avoids `matplotlib.style.core`.** That module is
deprecated in Matplotlib 3.11 and removed in 3.13. `_user_library_paths()`
prefers the public `matplotlib.style.USER_LIBRARY_PATHS` and only falls back to
the old location when the new one is genuinely absent, so no deprecation
warning fires on current versions. The sheets are also loaded straight into
`matplotlib.style.library`, so registration does not hinge on any single entry
point. `test_import_emits_no_deprecation_warnings` guards this.

**The gray variant is a delta-only overlay,** applied as
`plt.style.use(["theeconomist", "theeconomist-gray"])`. Making it standalone
would duplicate ~50 lines that then drift.

**Chart furniture geometry is measured, not invented.** The red tag was taken
off a published chart: 9x27 px at (0, 0) in a 595x404 original — a portrait
block about three times taller than wide, flush into the top-left corner. There
is **no rule across the top**; an earlier attempt drew a wide flat bar plus a
full-width hairline and both were wrong. The plot area also runs much wider
than Matplotlib's defaults: 0.066 to 0.963 of figure width, versus 0.125/0.9.
`test_tag_is_portrait_and_flush_to_the_corner` and
`test_plot_area_is_widened_to_house_margins` guard these.

**R-squared is a proportion.** `"{:.2f}%".format(0.52)` prints `0.52%`; the
published chart shows `52%`. Scale by 100 before the `%`.

**Layout constants are derived, not hardcoded.** `econ_title` computes text
heights from the font sizes and the figure height (`line_height()`), so the
block closes up correctly whatever combination of title/subtitle/source is
present. Callers reserve space for a legend band with `headroom=` rather than
pinning `subplots_adjust(top=...)`. A hardcoded `top=0.76` in the gallery —
tuned when the chart still had a subtitle — went stale the moment the subtitle
was dropped and left a 0.09-of-figure-height hole between the title and the
legend. The published chart's title-to-legend gap is 0.0248 of figure height;
`headroom=0.094` reproduces it for a two-row legend on a 6.5in figure.

**Presentation choices stay out of `datasets.py`.** Region labels are
single-line; line breaking belongs to whatever draws the legend.

## Verifying visual changes

`examples/make_gallery.py` renders PNGs into `gallery/`. Read those images back
to check the result — "no exception raised" is not evidence a chart looks
right. Two layout bugs in this repo (legend overprinting the subtitle, then the
title block colliding with the legend band) rendered without error and were
only visible in the image.

## History worth knowing

The notebook was trimmed from 72 cells to 36, dropping general Matplotlib and
seaborn tutorial material, a Gaussian Process demo using a scikit-learn API
removed years ago, and Canada-immigration charts sourced from `cdn.rawgit.com`
(dead since 2019). Several cells had reused `color` as a loop variable,
clobbering the list the flagship chart needed; loop variables were renamed.
