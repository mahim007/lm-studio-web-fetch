import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse
from typing import List, Dict

logger = logging.getLogger("web_search")

def parse_duckduckgo_url(href: str) -> str:
    """Parse DuckDuckGo redirect URL to extract actual URL."""

    if not href:
        return ""
    
    # Handle protocol-relative URLs
    if href.startswith("//"):
        return "https:" + href
    
    # Parse redirect URL (contains uddg= parameter)
    if "/l/?uddg=" in href:
        parsed = urlparse(href)
        params = parse_qs(parsed.query)
        return params.get('uddg', [href])[0]
    
    return href

def search_duckduckgo(query: str, limit: int = 10) -> List[Dict]:
    """Search DuckDuckGo and return results"""
    logger.info(f"Searching DuckDuckGo for: '{query}' (limit={limit})")
    url = "https://html.duckduckgo.com/html/"
    params = {"q": query}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html"
    }

    response = requests.get(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    logger.info(f"Parsing {limit} results from response")
    for result in soup.select("#links .result")[:limit]:
        title_element = result.select_one(".result__a")
        snippet_element = result.select_one(".result__snippet")

        if title_element:
            raw_url = title_element.get("href", "")
            actual_url = parse_duckduckgo_url(raw_url)
            results.append({
                "title": title_element.get_text(strip=True),
                "url": actual_url,
                "snippet": snippet_element.get_text(strip=True) if snippet_element else ""
            })
    
    logger.info(f"Search completed: {len(results)} results returned")
    return results

