"""The demo dataset that ships with the package.

The corruption-vs-human-development scatter is the chart the whole style was
built to reproduce, so its data travels with the package rather than sitting
beside the notebook. That means examples work from any working directory
instead of only from a checkout's root.
"""

from __future__ import annotations

from importlib.resources import files
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    import pandas as pd

__all__ = ["load_cpi_hdi", "data_path"]

#: Region codes as they appear in the CSV, mapped to display labels.
#: Deliberately single-line: line breaking is a presentation decision that
#: belongs to whatever is drawing the legend, not to the data loader.
REGIONS: dict[str, str] = {
    "EU W. Europe": "OECD",
    "Americas": "Americas",
    "Asia Pacific": "Asia & Oceania",
    "East EU Cemt Asia": "Central & Eastern Europe",
    "MENA": "Middle East & North Africa",
    "SSA": "Sub-Saharan Africa",
}


def data_path() -> str:
    """Return the filesystem path to the bundled CSV."""
    return str(files("economiststyle.data") / "EconomistData.csv")


def load_cpi_hdi(*, tidy: bool = True) -> "pd.DataFrame":
    """Load the 2011 Corruption Perceptions / Human Development dataset.

    Parameters
    ----------
    tidy
        When True (the default) the frame is cleaned up for plotting: the
        unnamed index column is dropped, ``HDI.Rank`` is renamed to a valid
        identifier so it survives a statsmodels formula, a ``Log_CPI`` column
        is added, region codes are expanded to display labels, and rows are
        sorted by CPI. Pass False for the raw CSV exactly as stored.

    Returns
    -------
    pandas.DataFrame
    """
    import numpy as np
    import pandas as pd

    df = pd.read_csv(data_path())
    if not tidy:
        return df

    df = df.iloc[:, 1:]
    df = df.rename(columns={"HDI.Rank": "HDI_Rank"})
    df["Log_CPI"] = np.log(df["CPI"])
    df["Region"] = df["Region"].replace(REGIONS)
    return df.sort_values(by="CPI").reset_index(drop=True)
