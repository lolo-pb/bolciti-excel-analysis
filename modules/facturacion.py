import pandas as pd
from modules.helpers import sanitize, standardize_columns, pivot_by_period, normalize_names

SECTION_ORDER = []
SECTION_MAP = {}

def build_facturas_base() -> pd.DataFrame:
    '''Internal Use only'''
    ## Processing raw input

    # Extract data frames from excel files
    facturas_blancos = pd.read_excel("res/facturas-sg.xlsx", header=7)
    facturas_negros = pd.read_excel("res/facturas-s2.xlsx", header=7)

    # Standardizes colum names
    facturas_blancos = standardize_columns(facturas_blancos)
    facturas_negros = standardize_columns(facturas_negros)

    # Only keep the columns i want to work with
    facturas_blancos = facturas_blancos[[ "cliente", "fecha", "total"]]
    facturas_negros = facturas_negros[[ "cliente", "fecha", "total"]]

    ## Join both black and white facturas
    facturas = pd.concat([facturas_blancos, facturas_negros],ignore_index=True)

    # Normalize
    facturas["fecha"] = pd.to_datetime(facturas["fecha"], errors="coerce")
    facturas = sanitize(facturas,[ "cliente", "fecha"])
    facturas["cliente"] = normalize_names(facturas["cliente"])

    return facturas

def build_facturas_por_cliente() -> pd.DataFrame:

    facturas = build_facturas_base()
    facturas = pivot_by_period(facturas, "fecha",["cliente"],"total")

    return facturas

def build_facturas_total() -> pd.DataFrame:

    facturas = build_facturas_base()
    facturas = pivot_by_period(facturas, "fecha",[],"total")

    return facturas