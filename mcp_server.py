import logging
import os
import sys

from mcp.server.fastmcp import FastMCP
from web_search.tools import web_search
from web_fetch.tools import web_fetch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("web_tools")

# Server configuration
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "5000"))

mcp = FastMCP("web_tools")


@mcp.tool()
def web_fetch_call(url: str) -> dict:
    """Fetch and extract the full content from a web page URL. Returns the page title and extracted text content. Use this after web_search_call to get detailed information from search results."""
    logger.info(f"Tool called: web_fetch(url='{url}')")
    return web_fetch(url=url)

@mcp.tool()
def web_search_call(query: str, limit: int = 10) -> list[dict]:
    """Search the web using DuckDuckGo. Returns title, URL, and snippet for up to 10 results. IMPORTANT: After searching, ALWAYS fetch at least 2-3 of the most relevant URLs using web_fetch_call to get the full detailed content. Don't rely on snippets alone. For FACTUAL questions (versions, dates, numbers), you MUST fetch the official/source URL to get exact verified information."""
    logger.info(f"Tool called: web_search(query='{query}', limit={limit})")
    return web_search(query=query, limit=limit)



# Create ASGI app for uvicorn
app = mcp.streamable_http_app()


if __name__ == "__main__":
    import uvicorn

    logger.info("=" * 50)
    logger.info("Starting MCP Server")
    logger.info(f"Server name: {mcp.name}")
    logger.info(f"Host: {SERVER_HOST}")
    logger.info(f"Port: {SERVER_PORT}")
    logger.info(f"MCP endpoint: http://{SERVER_HOST}:{SERVER_PORT}/mcp")
    logger.info("=" * 50)

    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT, log_level="info")