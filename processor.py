import pandas as pd
from modules.excel_style import style_financial_sheet
from pathlib import Path

from modules.sueldos import build_sueldos_by_section, build_sueldos_by_employee
from modules.gastos import build_gastos_by_section
from modules.facturacion import  build_facturas_total, build_facturas_por_cliente
from modules.helpers import join_pivots, add_totals_and_result

###  Esto deberia llamar a los modules y cada module deberia devolver las 
### tablas divididas por mes/ o dividirlas en el main?
def run_processor():
        print("Processor running...")

        sueldos = build_sueldos_by_section()
        #print(sueldos.to_string(index=False))

        gastos = build_gastos_by_section()
        #print(gastos.to_string(index=False))

        #facturas = build_facturas_por_cliente()
        facturas =build_facturas_total()
        #print(facturas.to_string(index=False))
        

        resumen_spendings = join_pivots(gastos, sueldos)
        final = add_totals_and_result(resumen_spendings, facturas)

        #print(final.to_string(index=False))


        output_path = Path("out/resumen_financiero.xlsx")
        output_path.parent.mkdir(parents=True, exist_ok=True)   

        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            final.to_excel(writer, sheet_name="Resumen", index=False)

        # apply formatting AFTER export
        style_financial_sheet(
            filepath=output_path,
            sheet_name="Resumen",
            freeze_panes_cell="B2",
            special_row_fills = {
                "gastos_total": "FFF2CC",
                "facturacion": "BDD7EE",
                "ganancia": "E2EFDA",
            }
        )

        print("Done:")
        print("Exported:", output_path)
        return
run_processor()
