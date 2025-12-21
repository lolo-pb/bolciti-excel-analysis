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
    '''Removes the rows that have nan in the selected columns'''

    mask_bad = (df.copy()[list(descriptor_cols)].isna().all(axis=1))
    
    return df[~mask_bad]


def join_pivots(df_a: pd.DataFrame, df_b: pd.DataFrame, fill_value=0) -> pd.DataFrame:
    # make sure seccion is index so concat aligns by month columns
    a = df_a.set_index("seccion")
    b = df_b.set_index("seccion")

    # union rows + union columns
    out = pd.concat([a, b], axis=0, sort=True)

    # consistent column order (chronological)
    out = out.reindex(sorted(out.columns), axis=1)

    # fill missing month cells
    out = out.fillna(fill_value)

    return out.reset_index()


def add_totals_and_result(
    spendings: pd.DataFrame,
    facturacion: pd.DataFrame,
    seccion_col: str = "seccion",
    fact_row_label: str = "facturacion",
    total_spend_label: str = "gastos_total",
    result_label: str = "ganancia",
    total_col_name: str = "TOTAL",
) -> pd.DataFrame:
    """
    spendings: pivot table with rows=seccion, cols=months (YYYY-MM), values=spendings
    facturacion: pivot table with one row OR a dataframe containing month columns
                (it can have 'concepto' or 'cliente' etc; we only take the month columns)
    """

    out = spendings.copy()

    # Identify month columns (everything except seccion)
    month_cols = [c for c in out.columns if c != seccion_col]

    # --- TOTAL column per row (sum across months)
    out[total_col_name] = out[month_cols].sum(axis=1)

    # --- Total spendings row (sum across all spendings rows, per month)
    total_spend_series = out[month_cols].sum(axis=0)
    total_spend_row = pd.DataFrame(
        [[total_spend_label] + total_spend_series.tolist() + [total_spend_series.sum()]],
        columns=[seccion_col] + month_cols + [total_col_name],
    )

    # --- Facturacion row (align columns; supports 1-row df)
    # Take only month columns that exist in spendings, fill missing with 0
    fact_months = [c for c in facturacion.columns if c in month_cols]

    # If facturacion has multiple rows, sum them (safe default)
    fact_series = facturacion[fact_months].sum(axis=0)

    # Ensure all months exist
    fact_series = fact_series.reindex(month_cols).fillna(0)

    fact_row = pd.DataFrame(
        [[fact_row_label] + fact_series.tolist() + [fact_series.sum()]],
        columns=[seccion_col] + month_cols + [total_col_name],
    )

    # --- Resultado row = facturacion - total spendings (per month)
    result_series = fact_series - total_spend_series.reindex(month_cols).fillna(0)
    result_row = pd.DataFrame(
        [[result_label] + result_series.tolist() + [result_series.sum()]],
        columns=[seccion_col] + month_cols + [total_col_name],
    )

    # Append rows
    final = pd.concat([out, total_spend_row, fact_row, result_row], ignore_index=True)

    return final