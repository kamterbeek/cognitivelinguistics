pip install requests beautifulsoup4 pandas newspaper3k

import requests
from bs4 import BeautifulSoup
import pandas as pd
from newspaper import Article
from urllib.parse import urljoin
import time

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
    print(f"Fetching list page: {page_url}")
    response = requests.get(page_url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if href.startswith("/"):
            href = urljoin(page_url, href)

        if href.startswith("http"):
            if "statement" in href.lower() or "release" in href.lower():
                links.add(href)

    return list(links)

def fetch_and_filter_article(url):
    print(f"Parsing article: {url}")
    try:
        article = Article(url)
        article.download()
        article.parse()
    except Exception as e:
        print("Failed:", e)
        return None

    text = article.text or ""

    if any(k.lower() in text.lower() for k in KEYWORDS):
        return {
            "url": url,
            "title": article.title,
            "date": article.publish_date,
            "text": text
        }

    return None

def main():
    records = []

    for start_url in START_URLS:
        links = get_article_links(start_url)

        for link in links:
            record = fetch_and_filter_article(link)
            if record:
                records.append(record)

            time.sleep(1.0)  # ethical rate limiting

    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} records to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
