import os
from pathlib import Path
from datetime import date
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

BASE_URL_S2 = "https://nube2.sipe.com.ar/Bolciti2/Default.aspx?nwflowId=NavegacionWorkflow152402497&codigo=frmHome"
BASE_URL_SG = "https://nube2.sipe.com.ar/Bolciti/Default.aspx?nwflowId=NavegacionWorkflow1203130143&codigo=frmHome"
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

from datetime import date

def _set_date_by_string(page, input_selector: str, target: date):
    # 1) Make sure the element exists first
    page.wait_for_selector(input_selector, state="attached", timeout=30_000)

    value = target.strftime("%d/%m/%Y")  # adjust if the site expects another format

    # 2) Set the value + fire events
    page.evaluate(
        """({ selector, value }) => {
            const input = document.querySelector(selector);
            if (!input) {
              throw new Error("Input not found for selector: " + selector);
            }
            input.value = value;
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
        }""",
        {"selector": input_selector, "value": value},
    )

    # 3) (Optional but useful) verify it actually changed
    actual = page.locator(input_selector).input_value()
    if actual.strip() != value:
        raise RuntimeError(f"Date did not stick. Wanted '{value}', got '{actual}'")



def _export_report(page, from_input: str, to_input: str, start: date, end: date, out_path: Path):
    _set_date_by_string(page, from_input, start)
    _set_date_by_string(page, to_input, end)
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

def scrape_exports(start: date, end: date):
    _clear_res_folder()
    scrape_exports_url(start,end,BASE_URL_S2,"s2")
    scrape_exports_url(start,end,BASE_URL_SG,"sg")
    

def scrape_exports_url(start: date, end: date, url, name: str) -> dict[str, Path]:
    """
    Clears res/*.xls[x], logs in, exports the 3 Excel files into res/, returns their paths.
    """
    print("Retrieving files from")
    print(url)
    print("...")

    user = os.environ["APP_USER"]
    pw = os.environ["APP_PASS"]

    ym = f"{start.year}-{start.month:02d}"  # just for naming
    outputs = {
        "sueldos": RES_DIR / f"sueldos-{name}.xlsx",
        "ventas_facturas": RES_DIR / f"facturas-{name}.xlsx",
        "compras_gastos": RES_DIR / f"gastos-{name}.xlsx",
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        try:
            # Login
            page.goto(url)
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

    print("Done")
    return outputs
