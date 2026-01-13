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

#
