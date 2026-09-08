"""An Economist-inspired Matplotlib style.

Importing this package registers its style sheets with Matplotlib and its
colour palette as named colours, so the styles resolve by bare name from any
working directory::

    import economiststyle          # registers on import
    import matplotlib.pyplot as plt

    plt.style.use("theeconomist")

or, equivalently and with the grayscale variant available::

    economiststyle.use()
    economiststyle.use("gray")

Matplotlib has no entry-point plugin system for style sheets, so registration
is done in two belt-and-braces steps: the package's ``styles/`` directory is
added to Matplotlib's user style search path (so the sheets survive anyone
calling ``reload_library()`` later), and the sheets are then loaded straight
into the live style library (so registration does not hinge on any single
Matplotlib entry point continuing to exist).

This project is an independent homage. It is not affiliated with, endorsed by,
or derived from any asset of The Economist.
"""

from __future__ import annotations

from importlib.resources import as_file, files
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.style as mpl_style

from .annotate import ECONOMIST_RED, LABEL_GREY, econ_title
from .datasets import data_path, load_cpi_hdi
from .palette import BRAND, CYCLE, RAMPS, named_colors, register_colors

__version__ = "0.2.0"

__all__ = [
    "BRAND",
    "CYCLE",
    "ECONOMIST_RED",
    "LABEL_GREY",
    "RAMPS",
    "__version__",
    "available_styles",
    "data_path",
    "econ_title",
    "load_cpi_hdi",
    "named_colors",
    "register_colors",
    "style_dir",
    "use",
]

#: Styles this package provides, mapped to the sheets ``use()`` layers for them.
_VARIANTS: dict[str, list[str]] = {
    "default": ["theeconomist"],
    "gray": ["theeconomist", "theeconomist-gray"],
    "grey": ["theeconomist", "theeconomist-gray"],
}


def style_dir() -> Path:
    """Return the directory holding the bundled ``.mplstyle`` files."""
    with as_file(files("economiststyle") / "styles") as path:
        return Path(path)


def _user_library_paths() -> list[str] | None:
    """Return Matplotlib's user style search path list, or None.

    The list moved: it is public as ``matplotlib.style.USER_LIBRARY_PATHS``
    on current Matplotlib, but older releases only exposed it on
    ``matplotlib.style.core``, a module that is deprecated in 3.11 and removed
    in 3.13. Prefer the public location and only reach for the old one when
    the new one is genuinely absent, so no deprecation warning is emitted on
    versions that have moved on.
    """
    paths = getattr(mpl_style, "USER_LIBRARY_PATHS", None)
    if paths is not None:
        return paths
    try:  # Matplotlib older than the move
        import matplotlib.style.core as _core
    except ImportError:  # pragma: no cover - only on future removals
        return None
    return getattr(_core, "USER_LIBRARY_PATHS", None)


def _register_styles() -> None:
    """Add the bundled styles to Matplotlib's style library."""
    directory = style_dir()

    # Join the search path so the sheets are rediscovered if anything calls
    # reload_library() after us.
    paths = _user_library_paths()
    if paths is not None and str(directory) not in paths:
        paths.append(str(directory))

    # Load them into the live library directly, which needs nothing beyond
    # long-stable public API and works even if the search path is unavailable.
    for sheet in sorted(directory.glob("*.mplstyle")):
        mpl_style.library[sheet.stem] = mpl.rc_params_from_file(
            sheet, use_default_template=False
        )
    mpl_style.available[:] = sorted(mpl_style.library)


def available_styles() -> list[str]:
    """Return the bundled style names, as accepted by ``plt.style.use``."""
    return sorted(p.stem for p in style_dir().glob("*.mplstyle"))


def use(variant: str = "default") -> None:
    """Activate the style.

    Parameters
    ----------
    variant
        ``"default"`` for the full-colour style, or ``"gray"`` (``"grey"``
        also works) for the print/grayscale overlay layered on top of it.

    Raises
    ------
    ValueError
        If ``variant`` is not one of the known variants.
    """
    try:
        sheets = _VARIANTS[variant]
    except KeyError:
        known = ", ".join(sorted(set(_VARIANTS) - {"grey"}))
        raise ValueError(
            f"unknown variant {variant!r}; expected one of: {known}"
        ) from None
    plt.style.use(sheets)


_register_styles()
register_colors()
