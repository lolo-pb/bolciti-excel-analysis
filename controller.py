from datetime import date
from scraper import scrape_exports
import processor as p


def main():
    # Hardcoded period
    # YY/MM/DD
    start = date(2025, 1, 1)
    end = date(2025, 12, 31)

    if start > end:
        raise ValueError("Start date must be before or equal to end date")

    # 1) Download + rename into res/
    scrape_exports(start, end)

    # 2) Process files from res/ and write outputs
    p.run_processor()

if __name__ == "__main__":
    main()
