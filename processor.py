import pandas as pd

### Backend

## Processing raw input

# Extract data frames from excel files
sueldos_negros = pd.read_excel("res/sueldos-s2.xlsx", header=5)
sueldos_blancos = pd.read_excel("res/sueldos-sg.xlsx", header=5)

# Standardizes colum names
sueldos_blancos.columns = (
    sueldos_blancos.columns
      .str.strip()              # remove leading/trailing spaces
      .str.lower()              # lowercase
      .str.replace(' ', '_')    # snake case >:P
)

# Only keep the columns i want to work with
sueldos_blancos = sueldos_blancos[[ "fecha_cierre", "empleado", "total"]]



## Adding sections, not in system 
section_map = {
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

    # Oficina
    "CARLOS GUSTAVO CAPPONI": "oficina",
    "NORMA MABEL PASCUAL": "oficina",
    "GUILLERMO PIZZUTO": "oficina",

    # General
    "COLINA POLANCO ALAIN ANTONIO": "gral",
}
# Normalizes names
sueldos_blancos["empleado"] = (
    sueldos_blancos["empleado"]
      .str.strip()
      .str.replace(r"\s+", " ", regex=True)
)
sueldos_blancos["seccion"] = sueldos_blancos["empleado"].map(section_map).fillna("gral")



## Ordering and styling of output table
# Asign a month by entry
sueldos_blancos["mes"] = sueldos_blancos["fecha_cierre"].dt.to_period("M")

# pivot: one column per month, totals summed
sueldos_mensuales = sueldos_blancos.pivot_table(
    index=["seccion","empleado"],
    columns="mes",
    values="total",
    aggfunc="sum",
    fill_value=0
).reset_index()

# order rows by section (custom order) and then employee
section_order = ["confeccion", "impresion", "extrusion", "echado", "oficina", "gral"]
sueldos_mensuales["seccion"] = pd.Categorical(
    sueldos_mensuales["seccion"], categories=section_order, ordered=True
)

sueldos_mensuales = sueldos_mensuales.sort_values(["seccion", "empleado"]).reset_index(drop=True)

print(sueldos_mensuales.to_string(index=False))
