import pandas as pd
from helpers import sanitize, standardize_columns, normalize_names, pivot_by_period

def build_stock() -> pd.DataFrame:
    ## Processing raw input
    
    # Extract data frames from excel files
    stock_negros  = pd.read_excel("res/stock-s2.xlsx", header=6, dtype={"Total": float})
    stock_blancos = pd.read_excel("res/stock-sg.xlsx", header=6, dtype={"Total": float})

    # Standardizes colum names
    stock_blancos = standardize_columns(stock_blancos)
    stock_negros = standardize_columns(stock_negros)

    # Only keep the columns i want to work with
    stock_blancos = stock_blancos[[ "tipo_gasto", "proveedor", "fecha", "total"]]
    stock_negros  =  stock_negros[[ "tipo_gasto", "proveedor", "fecha", "total"]]


    ## Join both black and white stock
    stock = pd.concat([stock_blancos, stock_negros],ignore_index=True)


    # Normalizes 
    stock["fecha"] = pd.to_datetime(stock["fecha"], errors="coerce")
    stock = sanitize(stock,[ "tipo_gasto", "proveedor", "fecha"])

    ## Ordering and styling of output table

    # pivot: one column per month, totals summed
    stock = pivot_by_period(stock,"fecha",[],"total")

    print(stock.head())
    return stock
