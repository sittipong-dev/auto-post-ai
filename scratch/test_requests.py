import requests
from bs4 import BeautifulSoup
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

url = "https://shopee.co.th/product/1278126372/26962408187"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

try:
    print(f"Fetching {url}")
    res = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {res.status_code}")
    
    soup = BeautifulSoup(res.text, 'html.parser')
    og_img = soup.find('meta', property='og:image')
    if og_img:
        print(f"Found og:image: {og_img['content']}")
    else:
        print("No og:image found.")
        print(f"HTML snippet: {res.text[:500]}")
except Exception as e:
    print(e)
