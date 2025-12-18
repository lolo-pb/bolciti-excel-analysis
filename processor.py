import pandas as pd

### Backend

## Processing raw input

# Extract data frames from excel files
sueldos_negros = pd.read_excel("res/sueldos-s2.xlsx", header=5, dtype={"Total": float})
sueldos_blancos = pd.read_excel("res/sueldos-sg.xlsx", header=5, dtype={"Total": float})


# Standardizes colum names
sueldos_blancos.columns = (
    sueldos_blancos.columns
      .str.strip()              # remove leading/trailing spaces
      .str.lower()              # lowercase
      .str.replace(' ', '_')    # snake case >:P
)
sueldos_negros.columns = (
    sueldos_negros.columns
      .str.strip()              # remove leading/trailing spaces
      .str.lower()              # lowercase
      .str.replace(' ', '_')    # snake case >:P
)

# Only keep the columns i want to work with
sueldos_blancos = sueldos_blancos[[ "fecha_cierre", "empleado", "total"]]
sueldos_negros = sueldos_negros[[ "fecha_cierre", "empleado", "total"]]

# Join both black and white sueldos
sueldos = pd.concat(
    [sueldos_blancos, sueldos_negros],
    ignore_index=True
)



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

    ## Desconocidos caen en gral
    #"BRIAN NAHUEL SOTO":"",
    #"BRIZUELA HERNAN":"",
    #"COLINA POLANCO ALAIN ANTONIO":"",
    #"LEONARDO LEDESMA":"",
    #"ROSA BEATRIZ DI PAOLO":"",
    #"SERGIO DAMIAN ARRIETA ":"",
}
# Normalizes names
sueldos["empleado"] = (
    sueldos["empleado"]
      .str.strip()
      .str.replace(r"\s+", " ", regex=True)
)
sueldos["seccion"] = sueldos["empleado"].map(section_map).fillna("gral")



## Ordering and styling of output table
# Asign a month by entry
sueldos["mes"] = sueldos["fecha_cierre"].dt.to_period("M")

# pivot: one column per month, totals summed
sueldos = sueldos.pivot_table(
    index=["seccion","empleado"],
    columns="mes",
    values="total",
    aggfunc="sum",
    fill_value=0
).reset_index()

# order rows by section (custom order) and then employee
section_order = ["confeccion", "impresion", "extrusion", "echado", "oficina", "gral"]
sueldos["seccion"] = pd.Categorical(
    sueldos["seccion"], categories=section_order, ordered=True
)

#### done
sueldos = sueldos.sort_values(["seccion", "empleado"]).reset_index(drop=True)
#print(sueldos.to_string(index=False))


month_cols = sueldos.columns.difference(["seccion", "empleado"])

sueldos_seccion = (
    sueldos
      .groupby("seccion", as_index=False, observed=False)[month_cols] 
      .sum()
)#observed incluye categorias que no aparecen

print(sueldos_seccion.to_string(index=False))

