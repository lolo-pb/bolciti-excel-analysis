import pandas as pd
from modules.helpers import standardize_columns



def build() -> pd.DataFrame:
    ## Processing raw input

    # Extract data frames from excel files
    gastos_blancos = pd.read_excel("res/gastos-sg.xlsx", header=6)
    gastos_negros  = pd.read_excel("res/gastos-s2.xlsx", header=6)

    # Standardizes colum names
    gastos_blancos = standardize_columns(gastos_blancos)
    gastos_negros  = standardize_columns(gastos_negros )

    # Only keep the columns i want to work with
    gastos_blancos = gastos_blancos[[ "tipo_gasto", "proveedor", "fecha", "total"]]
    gastos_negros  = gastos_negros [[ "tipo_gasto", "proveedor", "fecha", "total"]]



    ## Join both black and white gastos
    gastos = pd.concat([gastos_blancos, gastos_negros],ignore_index=True)



    return gastos