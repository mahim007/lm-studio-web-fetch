import requests
from bs4 import BeautifulSoup
import json
import re

def web_search_tool(url: str) -> dict:
    """
    Fetched content from a URL, parses the main article body, 
    and returns a structured json data suitable for LLM
    """

    print(f"Attempting to fetch and parse: {url}")

    try:
        # 1. Fetcher Layer
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'} # Updated User Agent
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {url}: {e}")
        return {"error" : f"could not access the web page due to a connection error: {e}"}

    # 2. Parser Layer
    soup = BeautifulSoup(response.content, 'html.parser')

    article_body = None

    # try multiple common tags to find the main content according to their importance
    selectors = {
        'div.article-body',
        'div[role="main"]',
        'div#main-content',
        'div.content',
        'article',
        'body'
    }

    for selector in selectors:
        container = soup.select_one(selector)
        if container:
            article_body = container
            break

    extracted_text = ""
    structured_content = []

    # Extraction and filtering logic
    if article_body:
        # extract paragraph and clean them up
        potential_elements = article_body.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
        
        for element in potential_elements:
            text = element.get_text(strip=True)

            # Only keep text that is reasonably long to avoid noise, but not too long to be overwhelming
            if text and len(text) > 70:
                structured_content.append(text)
        
        extracted_text = reduce_noise(structured_content)
    else:
        print(f"Could not find a suitable content container for URL: {url}")
        fallback_text = soup.body.get_text(separator='\n', strip=True)
        extracted_text = reduce_noise([line for line in fallback_text.split('\n') if len(line) > 50])

    
    output = {
        "url": url,
        "title": soup.find('title').get_text(strip=True) if soup.find('title') else "No Title Found",
        "extracted_summary": f"Successfully scrapped content from {url}",
        "extracted_content": extracted_text
    }

    return output

def reduce_noise(content: list) -> str:
    cleaned_paragraphs = []
    for text in content:
        if re.search(r"^\^.*?\.\n", text):
            continue

        if "Bibcode:" in text or "DOI:" in text or "References" in text:
            continue

        cleaned_paragraphs.append(text)

    raw_text = "\n\n---\n\n".join(cleaned_paragraphs)
    # Step 1: Remove all known structural markers and headers
    clean_text = re.sub(r'subsection[a-z]+\d+|Toggle Approaches|History|Major processing tasks in an NLP system include:|Though natural language processing tasks are closely intertwined', '', raw_text, flags=re.IGNORECASE)

    # Step 2: Collapse separators and redundant whitespace
    clean_text = re.sub(r'\n\s*[-—]*\s*\n', '\n\n', clean_text) # Replaces all '---' with simple paragraph breaks
    clean_text = re.sub(r'\n\s*\n\s*\n', '\n\n', clean_text) # Collapses multiple newlines

    # Step 3: Clean up residual structural text and bad spacing (e.g., "word n-gram model, at the time...")
    clean_text = re.sub(r'\s{2,}', ' ', clean_text).strip() # Reduce all double spaces to single space
    clean_text = clean_text.replace('(e.g.,', ' (e.g.,').replace('and natural language processing.', 'natural language processing.')

    # Step 4: Final citation cleanup (just in case any slipped through)
    clean_text = re.sub(r'\[.*?\]', '', clean_text)
    return clean_text.strip()

if __name__ == "__main__":
    test_url = "https://en.wikipedia.org/wiki/Natural_language_processing"
    result = web_search_tool(test_url)
    print("=========================")
    print("✅ SUCCESSFUL JSON OUTPUT FOR LLM:")
    print(json.dumps(result, indent=4))