import pandas as pd
from modules.helpers import sanitize, standardize_columns, pivot_by_period, normalize_names

SECTION_ORDER = [ "alquiler" , "honorarios", "contabilidad" , "inversiones", "fletes"   , "logistica",
                  "vehiculos", "maquinas"  , "mantenimiento", "material"   , "servicios", "otros"    ,]

SECTION_MAP = {
    # FLETES
    "FLETES": "fletes",

    # LOGISTICA
    "PEAJE": "logistica",
    "GASTOS DE VIAJES": "logistica",
    "PLAYA DE ESTACIONAMIENTO": "logistica",

    # SERVICIOS
    "SERVICIOS": "servicios",
    "GASTOS DE ELECTRICIDAD": "servicios",
    "SERVICIO DE COMEDOR EN PLANTA": "servicios",
    "SERVICIO EXTERNO EN SEGURIDAD , HIGIENE Y MEDIO AMBIENTE": "servicios",
    
    # MANTENIMIENTO
    "SERVICIOS DE COMPRESORES": "mantenimiento",
    "SERVICIO DEL TECHISTA": "mantenimiento",
    "HERRERIA": "mantenimiento",
    "CERRAJERIA VS": "mantenimiento",
    "ARTICULO DE FERRETERIA": "mantenimiento",
    "MATERALES ELECTRICOS": "mantenimiento",
    "GASTOS PLOMERIA": "mantenimiento",


    # MAQUINAS
    "SERVICIO TECNICO DE LA EXTRUSORA": "maquinas",
    "REPARACION TROQUELADOR MAQ CONFECCION": "maquinas",
    "REPUESTOS DE MAQUINARIAS": "maquinas",
    "COMPRA MAQUINARIA": "maquinas",
    "COMPRA DE MAQUINARIAS EXTRUXSORA": "maquinas",
    "MAQUINA HIDRO-ELEVADORA": "maquinas",
    "ELEVEDADOR HIDRAULICO": "maquinas",
    "SCHUSTER MAQUINARIAS": "maquinas",
    "TROQUELES PARA MAQ. CAMISETAS": "maquinas",
    "ACCESORIOS PARA MAQUINA": "maquinas",

    # CONTABILIDAD
    "TAREAS CONTABLES": "contabilidad",
    "ASESORAMIENTO JURIDICO": "contabilidad",
    "ACTAS MUNICIPALES": "contabilidad",
    "IMPUESTOS": "contabilidad",
    "INTERESES": "contabilidad",
    "CHEQUE RECHAZADO": "contabilidad",
    "CHEQUES RECHAZADOS": "contabilidad",
    "NOTA DE CREDITO": "contabilidad",
    "NOTAS DE DEBITOS AJUSTES CTA CTE": "contabilidad",

    # HONORARIOS
    "HONORARIOS": "honorarios",

    # VEHICULOS
    "COMBUSTIBLE": "vehiculos",
    "LAVADO DE CAMIONETA": "vehiculos",
    "REPUESTOS CAMIONETA": "vehiculos",
    "COMPRA DE CAMIONETA": "vehiculos",
    "PASTILLAS DE FRENO": "vehiculos",

    # MATERIALES
    "CONOS PARA BOBINAS DE CARTON": "material",
    "LAMINA BICARBONATO S/IMPRESION": "material",
    "POLIMEROS": "material",
    "POLIETILENO BOBINAS": "material",
    "POLIETILENO BOLSAS": "material",
    "POLIETILENO LINEAL": "material",
    "POLIETILENO ALTA DENSIDAD": "material",
    "POLIETILENO BICAPA": "material",
    "FILM POLIETILENO S/ IMPRESION": "material",
    "KG FILM PP": "material",
    "KG PE AD CRISTAL": "material",
    "KG PE ALTA VIRGEN": "material",
    "PE AD BLANCO RECUPERADO": "material",
    "BD RECUPERADO CRISTAL": "material",
    "BD GRUESO BG 6025": "material",
    "RECUPERADO GRUMO BLANCO BD": "material",
    "FASON DE RECUPERADO": "material",
    "SCRAP": "material",
    "GRUMO": "material",
    "ADICTIVOS": "material",
    "TINTAS Y DILUYENTES": "material",
    "PEGAMENTO": "material",
    "BOBINAS DE ARRANQUE": "material",
    "BOBINAS DE PP": "material",
    "BOBINAS OP IMPRESAS": "material",
    "BOBINAS RECUPERADO CECEPLAS": "material",
    "BOBINAS AMARILLA 87/ 75 CON FUELLE": "material",
    "BOBINAS CARAMELO C/ FUELLE": "material",
    "BOLSAS PP CRISTAL": "material",
    "BOLSAS ZIPLOC C/ BANDAS ADH.": "material",
    "PAPEL Y CARTON": "material",
    "ARTICULOS DE PAPEL Y CARTON": "material",
    "TUBOS DE CARTON": "material",
    "TELA DE TEFLON": "material",
    "TELA DE TEFLON DE 127 MICRONES": "material",
    "MASTER": "material",


    # ALQUILER
    "ALQUILER": "alquiler",
    "LEASING": "alquiler",

    # ALQUILER HUALFIN
    "ABONO MENSUAL ALQUILER": "hualfin",

    # INVERSIONES
    "INVERSIONES": "inversiones",
}



def build_gastos_by_section() -> pd.DataFrame:
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

    gastos = pivot_by_period(gastos,"fecha","seccion","total")

    return gastos