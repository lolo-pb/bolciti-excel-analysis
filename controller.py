from datetime import date
from pathlib import Path
from scraper import scrape_exports
import processor as p


def run_controller(start: date, end: date, output_path: Path) -> None:
    if start > end:
        raise ValueError("Start date must be before or equal to end date")

    # 1) Download + rename into res/
    scrape_exports(start, end)

    # 2) Process files from res/ and write output
    p.run_processor(output_path)


# Optional: keep a dev/CLI default run
def main() -> None:
    start = date(2025, 1, 1)
    end = date(2025, 12, 31)
    output_path = Path("out/resumen_financiero.xlsx")
    run_controller(start, end, output_path)


if __name__ == "__main__":
    main()
