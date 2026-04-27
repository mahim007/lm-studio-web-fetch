from .fetcher import web_fetch_tool

def create_fetch_tool():
    """Define fetch_web_"""
    return {
        "name": "web_fetch",
        "description": "Fetch and extract content from a web page URL. Returns the page title and extracted text content suitable for reading.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The complete URL of the web page to fetch"
                }
            },
            "required": ["url"]
        }
    }

def web_fetch(url: str) -> dict:
    """Fetch content from an URL."""

    if not url.startswith(("http://", "https://")):
        return {
            "error": "Invalid URL. Must start with http:// or https://"
        }

    return web_fetch_tool(url=url)