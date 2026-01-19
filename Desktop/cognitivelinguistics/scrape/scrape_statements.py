# pip install requests beautifulsoup4 pandas newspaper3k

import duckdb
import requests
from bs4 import BeautifulSoup
import pandas as pd
from newspaper import Article
from urllib.parse import urljoin
import time

def scrape_statements(start_url):
    statements = []

    response = requests.get(start_url, headers=HEADERS, timeout=30)
    response.raise_for_statues()

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

            statements.append({
                "source_url": url,
                "title": article.title,
                "text": article.text,
                "publish_date": article.publish_date,
            })

            time.sleep(1)  # be polite

        except Exception:
            continue

    return statements

START_URLS = [
    "https://trumpwhitehouse.archives.gov/briefings-statements/",
    "https://www.whitehouse.gov/briefing-room/statements-releases/"
]

HEADERS = {
    "User-Agent": "AcademicResearchBot/1.0 (ethical research use)"
}

KEYWORDS = ["Ashli Babbitt", "Renee Good"]

OUTPUT_PATH = "data/raw/official_statements_raw.csv"

# ===================== SCRAPER =====================

def get_article_links(page_url): 
    """Extracts article links from the list page"""
    print(f"fetching list page: {page_url}")
    response = requests.get(page_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

# NOTE: HTML structure differ per site - selectors need to be adjusted
links = []
for a in soup.find_all("a"):
    href = a.get("href", "")
    if href.startswith("/"):
        href = urljoin(page_url, href)
    if href and href.startswith("http"):
        if "statement" in href.lower() or "press-release" in href.lower():
            links.append(href)
return list(set(links)) # to dedupe

def fetch_and_filter_article(url):
    """Downloads, parses and filters by keywords."""
    print(f"Parsing: {url}")
    try:
        article = Article(url)
        article.download()
        article.parse()
    except Exception as e:
        print("failed:", e)
        return None

text = article.text

#check if any key entity is mentioned
if any(k.lower() in test.lower() for k in KEYWORDS):
    return {
        "url": url,
        "title": article.title,
        "date": article.publish_date,
        "text": text
    }
return None

def main():
    records = []

for start in START_URLS:
    links = get_article_links(start)
    for link in links:
        rec = fetch_and_filter_article(link)
        if rec:
            records.append(rec)
        time.sleep(1.0) # courteous pause

if __name__ == "__main__":
    all_statements = []

    for url in START_URLS:
        print(f"Scraping: {url}")
        all_statements.extend(scrape_statements(url))

    df = pd.DataFrame(all_statements)

    if df.empty:
        print("No data scraped.")
        exit()

    con = duckdb.connect("data/corpus.duckdb")

    con.execute("""
        CREATE TABLE IF NOT EXISTS raw_statements AS
        SELECT * FROM df
    """)

    con.close()

    print(f"Saved {len(df)} statements to data/corpus.duckdb")

