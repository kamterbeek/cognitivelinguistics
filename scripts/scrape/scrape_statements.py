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
