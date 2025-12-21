import pandas as pd
from modules.helpers import sanitize, standardize_columns, normalize_names, pivot_by_period

SECTION_ORDER = ["confeccion", "impresion", "extrusion", "echado", "oficina", "gral"]
SECTION_MAP = {
    # Confección
    "CABRERA ALEX EDUARDO": "confeccion",
    "CRISTIAN DARIO BAEZ": "confeccion",
    "JAVIER EDUARDO PAZ": "confeccion",
    "JORGE LUIS LEITES": "confeccion",
    "MARCELO CESAR UBOLDI": "confeccion",

    # Impresión
    "ENRIQUE CORDOBA": "impresion",
    "PATRICIO OMAR DIAZ": "impresion",
    "REMIGIO DANIEL RUIZ": "impresion",

    # Extrusión
    "MARIO AGUSTIN ALGAÑARAZ": "extrusion",
    "MARIO ALGAÑARAZ": "extrusion",
    "MARTINEZ ANGEL EDUARDO": "extrusion",

    # Echado
    "MATIAS LEONARDO MORENO": "echado",
    "BRIZUELA HERNAN":"echado",

    # Oficina
    "CARLOS GUSTAVO CAPPONI": "oficina",
    "NORMA MABEL PASCUAL": "oficina",
    "GUILLERMO PIZZUTO": "oficina",

    # General
    "COLINA POLANCO ALAIN ANTONIO": "gral",
    "BRIAN NAHUEL SOTO":"gral",


    ## Desconocidos caen en gral
    #"LEONARDO LEDESMA":"",
    #"ROSA BEATRIZ DI PAOLO":"",
    #"SERGIO DAMIAN ARRIETA ":"",
}

def build_sueldos_by_employee() -> pd.DataFrame:
    ## Processing raw input

    # Extract data frames from excel files
    sueldos_negros = pd.read_excel("res/sueldos-s2.xlsx", header=5, dtype={"Total": float})
    sueldos_blancos = pd.read_excel("res/sueldos-sg.xlsx", header=5, dtype={"Total": float})

    # Standardizes colum names
    sueldos_blancos = standardize_columns(sueldos_blancos)
    sueldos_negros = standardize_columns(sueldos_negros)

    # Only keep the columns i want to work with
    sueldos_blancos = sueldos_blancos[[ "fecha_cierre", "empleado", "total"]]
    sueldos_negros = sueldos_negros[[ "fecha_cierre", "empleado", "total"]]



    ## Join both black and white sueldos
    sueldos = pd.concat([sueldos_blancos, sueldos_negros],ignore_index=True)



    # Normalizes 
    sueldos["fecha_cierre"] = pd.to_datetime(sueldos["fecha_cierre"], errors="coerce")
    sueldos = sanitize(sueldos,[ "fecha_cierre", "empleado"])
    sueldos["empleado"] = normalize_names(sueldos["empleado"])

    # Adds seccion
    sueldos["seccion"] = sueldos["empleado"].map(SECTION_MAP).fillna("gral")

    ## Ordering and styling of output table

    # pivot: one column per month, totals summed
    sueldos = pivot_by_period(sueldos,"fecha_cierre",["seccion", "empleado"],"total")

    # order rows by section (custom order) and then employee
    sueldos["seccion"] = pd.Categorical(
        sueldos["seccion"], categories=SECTION_ORDER, ordered=True
    )

    #### done
    sueldos = sueldos.sort_values(["seccion", "empleado"]).reset_index(drop=True)

    return sueldos

def build_sueldos_by_section() -> pd.DataFrame:

    sueldos = build_sueldos_by_employee()

    month_cols = sueldos.columns.difference(["seccion", "empleado"])

    sueldos_seccion = (
        sueldos
          .groupby("seccion", as_index=False, observed=False)[month_cols] 
          .sum()
    )#observed incluye categorias que no aparecen

    #print(sueldos_seccion.to_string(index=False))

    return sueldos_seccion
