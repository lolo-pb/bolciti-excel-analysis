from modules.sueldos import build_sueldos_by_section, build_sueldos_by_employee
from modules.gastos import build_gastos_by_section
from modules.facturacion import  build_facturas_total, build_facturas_por_cliente
from modules.helpers import join_pivots

###  Esto deberia llamar a los modules y cada module deberia devolver las 
### tablas divididas por mes/ o dividirlas en el main?
def main():
        #sueldos = build_sueldos_by_section()
        #print(sueldos.to_string(index=False))

        #print("=====================================================================")

        #gastos = build_gastos_by_section()
        #print(gastos.to_string(index=False))

        #print("=====================================================================")
        #facturas = build_facturas_por_cliente()
        facturas =build_facturas_total()
        print(facturas.to_string(index=False))
        #print(facturas.head())
        #print(facturas.dtypes)

        #print("=====================================================================")

        #resumen = join_pivots(gastos,sueldos)
        #print(resumen.to_string(index=False))

if __name__ == "__main__":
    main()
