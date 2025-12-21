import pandas as pd
from typing import List
from typing import Iterable


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns
          .str.strip()
          .str.lower()
          .str.replace(" ", "_")
    )
    return df

def normalize_names(s: pd.Series) -> pd.Series:
    return (
        s.astype(str)
         .str.strip()
         .str.replace(r"\s+", " ", regex=True)
    )



def pivot_by_period(
    df: pd.DataFrame,
    date_col: str,
    index_cols: List[str],
    value_col: str,
    fill_value=0,
) -> pd.DataFrame:

    df = df.copy()

    # ensure datetime
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    # create period column
    df["period"] = df[date_col].dt.to_period("M")

    # pivot
    pivot = df.pivot_table(
        index=index_cols,
        columns="period",
        values=value_col,
        aggfunc="sum",
        fill_value=fill_value,
        observed=False
    ).reset_index()

    return pivot


def sanitize( df: pd.DataFrame, descriptor_cols: Iterable[str]) -> pd.DataFrame:

    mask_bad = (df.copy()[list(descriptor_cols)].isna().all(axis=1))
    
    return df[~mask_bad]
