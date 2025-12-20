import pandas as pd
from modules.helpers import sanitize, standardize_columns, pivot_by_period, normalize_names

SECTION_ORDER = ["alquiler", "electricidad", "fletes", "material", "maquinas", "vehiculos", "servicios", "otros"]
SECTION_MAP = {
    # LOGÍSTICA
    "FLETES": "fletes",

    # SERVICIOS 
    "SERVICIOS": "servicios",
    "HONORARIOS": "servicios",
    "TAREAS CONTABLES": "servicios",
    "ASESORAMIENTO JURIDICO": "servicios",
    "LABORATORIO DE MEDICINA": "servicios",
    "ELECTRICISTA": "servicios",
    
    #MAQUINAS
    "SERVICIO TECNICO DE LA EXTRUSORA": "maquinas",
    "REPARACION TROQUELADOR MAQ CONFECCION": "maquinas",
    "REPUESTOS DE MAQUINARIAS": "maquinas",

    # AGUA / GAS / LUZ
    "GASTOS DE ELECTRICIDAD": "electricidad",

    # COMBUSTIBLE / VEHÍCULOS
    "COMBUSTIBLE": "vehiculos",
    "LAVADO DE CAMIONETA": "vehiculos",
    "REPUESTOS CAMIONETA": "vehiculos",

    #MATERIALES
    "CONOS PARA BOBINAS DE CARTON": "material",
    "RECUPERADO BLANCO DE JOSE": "material",
    "LAMINA BICARBONATO S/IMPRESION": "material",
    "POLIMEROS": "material",
    "POLIETILENO BOBINAS": "material",
    "CILINDROS": "material",


    #ALQUILER
    "ALQUILER": "alquiler",

    #OTROS
    "GASTOS PLOMERIA": "otros",
    "ART. DE ELECTRICIDAD E INSTALACION SISTEMA": "otros",
    "MATERIALES DE CONSTRUCCION": "otros",
    "LIBRERIA": "otros",
    "SISTEMA DE SEGURIDAD": "otros",
    "MATERALES ELECTRICOS": "otros",
    "SISTEMAS DE ALARMA": "otros",
    "JORNADAS DE CAPACITACION": "otros",
    "VARIOS": "otros",
    "GASTOS VARIOS": "otros",
    
}


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


    # Normalizes/sanitizes
    gastos = sanitize(gastos,["tipo_gasto","proveedor","fecha"])
    gastos["tipo_gasto"] = normalize_names(gastos["tipo_gasto"])

    # Map secciones
    gastos["seccion"] = gastos["tipo_gasto"].map(SECTION_MAP).fillna("otros")

    gastos["seccion"] = pd.Categorical(
            gastos["seccion"], categories=SECTION_ORDER, ordered=True
        )
    gastos = gastos.sort_values("seccion")

    return gastos

    gastos = pivot_by_period(gastos,"fecha","seccion","total")

    return gastos