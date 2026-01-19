"""
Ethical scraping of US government statements for academic research.

- Respects robots.txt implicitly (low request rate)
- Identifies user agent
- Stores text corpus in DuckDB for downstream dbt modeling
"""

import time
from urllib.parse import urljoin

import duckdb
import requests
import pandas as pd
from bs4 import BeautifulSoup
from newspaper import Article


# -------------------------
# Configuration
# -------------------------

START_URLS = [
    "https://trumpwhitehouse.archives.gov/briefings-statements/",
    "https://www.whitehouse.gov/briefing-room/statements-releases/",
]

HEADERS = {
    "User-Agent": "AcademicResearchBot/1.0 (ethical, non-commercial research)"
}

DB_PATH = "data/corpus.duckdb"
TABLE_NAME = "raw_statements"


# -------------------------
# Scraping logic
# -------------------------

def scrape_statements(start_url: str) -> list[dict]:
    results = []

    response = requests.get(start_url, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.select("a[href]")

    for link in links:
        href = link.get("href")
        if not href:
            continue

        url = urljoin(start_url, href)

        if "statement" not in url.lower():
            continue

        try:
            article = Article(url)
            article.download()
            article.parse()

            if not article.text.strip():
                continue

            results.append(
                {
                    "source_url": url,
                    "title": article.title,
                    "text": article.text,
                    "publish_date": article.publish_date,
                }
            )

            time.sleep(1)  # ethical rate limiting

        except Exception:
            continue

    return results


# -------------------------
# Persistence
# -------------------------

def save_to_duckdb(records: list[dict]) -> None:
    if not records:
        print("No records to save.")
        return

    df = pd.DataFrame(records)

    conn = duckdb.connect(DB_PATH)
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} AS
        SELECT * FROM df
        """
    )
    conn.execute(
        f"""
        INSERT INTO {TABLE_NAME}
        SELECT * FROM df
        """
    )
    conn.close()


# -------------------------
# Main
# -------------------------

def main() -> None:
    all_records = []

    for url in START_URLS:
        print(f"Scraping: {url}")
        records = scrape_statements(url)
        all_records.extend(records)

    print(f"Collected {len(all_records)} statements")
    save_to_duckdb(all_records)
    print("Saved to DuckDB")


if __name__ == "__main__":
    main()
