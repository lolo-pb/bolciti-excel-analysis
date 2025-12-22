import os
from pathlib import Path
from datetime import date
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

BASE_URL = "https://nube2.sipe.com.ar/Bolciti2/Default.aspx?codigo=frmSueldosPagosLista"
RES_DIR = Path("res")


def _clear_res_folder():
    RES_DIR.mkdir(parents=True, exist_ok=True)
    for p in RES_DIR.iterdir():
        if p.is_file() and p.suffix.lower() in {".xlsx", ".xls"}:
            p.unlink()


def _set_date_jquery_ui(page, input_selector: str, target: date):
    page.locator(input_selector).click()
    dp = page.locator("#ui-datepicker-div")

    # Prefer dropdowns if the widget has them
    month_select = dp.locator("select.ui-datepicker-month")
    year_select = dp.locator("select.ui-datepicker-year")

    if month_select.count() > 0 and year_select.count() > 0:
        month_select.select_option(str(target.month - 1))  # 0-11
        year_select.select_option(str(target.year))
    else:
        # Fallback: keep it simple; if needed we can implement smart prev/next logic later
        # This fallback does NOT guarantee correct month if the widget starts far away.
        pass

    dp.get_by_role("link", name=str(target.day), exact=True).click()


def _export_report(page, from_input: str, to_input: str, start: date, end: date, out_path: Path):
    _set_date_jquery_ui(page, from_input, start)
    _set_date_jquery_ui(page, to_input, end)
    page.get_by_role("button", name="Filtrar").click()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with page.expect_download() as d:
        page.get_by_role("button", name="Exportar").click()
    d.value.save_as(out_path)

    # helps avoid “menu click timeout” due to busy UI
    page.wait_for_load_state("networkidle")


def _open_menu_section(page, text: str):
    # robust menu open: scroll + retry
    loc = page.get_by_role("listitem").filter(has_text=text).locator("span").first
    loc.scroll_into_view_if_needed()
    loc.click(timeout=60_000)


def scrape_exports(start: date, end: date) -> dict[str, Path]:
    """
    Clears res/*.xls[x], logs in, exports the 3 Excel files into res/, returns their paths.
    """
    user = os.environ["APP_USER"]
    pw = os.environ["APP_PASS"]

    _clear_res_folder()

    ym = f"{start.year}-{start.month:02d}"  # just for naming
    outputs = {
        "sueldos": RES_DIR / "sueldos-s2.xlsx",
        "ventas_facturas": RES_DIR / "facturas-s2.xlsx",
        "compras_gastos": RES_DIR / "gastos-s2.xlsx",
    }
    

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        try:
            # Login
            page.goto(BASE_URL)
            page.locator("#ctl00_ContentPlaceHolder1_UsuarioTX").fill(user)
            page.locator("#ctl00_ContentPlaceHolder1_ClaveTX").fill(pw)
            page.get_by_role("button", name="Ingresar").click()
            page.wait_for_load_state("networkidle")

            # 1) Sueldos
            _open_menu_section(page, "Sueldos y Otros Empleados")
            page.get_by_role("link", name="Sueldos", exact=True).click(timeout=60_000)
            _export_report(
                page,
                from_input="#ctl00_ContentPlaceHolder1_Filtro_2",
                to_input="#ctl00_ContentPlaceHolder1_Filtro_3",
                start=start,
                end=end,
                out_path=outputs["sueldos"],
            )

            # 2) Ventas - Facturas
            _open_menu_section(page, "Ventas Grupos Clientes Notas")
            page.get_by_role("link", name="Facturas", exact=True).click(timeout=60_000)
            _export_report(
                page,
                from_input="#ctl00_ContentPlaceHolder1_Filtro_4",
                to_input="#ctl00_ContentPlaceHolder1_Filtro_5",
                start=start,
                end=end,
                out_path=outputs["ventas_facturas"],
            )

            # 3) Compras - Facturas Gastos
            _open_menu_section(page, "Compras Proveedores Facturas")
            page.get_by_role("link", name="Facturas Gastos").click(timeout=60_000)
            _export_report(
                page,
                from_input="#ctl00_ContentPlaceHolder1_Filtro_2",
                to_input="#ctl00_ContentPlaceHolder1_Filtro_3",
                start=start,
                end=end,
                out_path=outputs["compras_gastos"],
            )

        except Exception:
            Path("out").mkdir(exist_ok=True)
            page.screenshot(path="out/scrape_fail.png", full_page=True)
            raise
        finally:
            context.close()
            browser.close()

    return outputs
