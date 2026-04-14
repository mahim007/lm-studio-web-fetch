import logging
import os
import sys

from mcp.server.fastmcp import FastMCP
from web_search_tool import web_search_tool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("fetch_web_page")

# Server configuration
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "5000"))

mcp = FastMCP("fetch_web_page")


@mcp.tool()
def fetch_web_page(url: str) -> dict:
    """
    Fetches and extracts content from a web page URL.

    Args:
        url: The complete URL of the web page to fetch.

    Returns:
        A dictionary with url, title, extracted_summary and extracted_content.
    """
    logger.info(f"Tool called: fetch_web_page(url='{url}')")
    try:
        result = web_search_tool(url=url)
        logger.info(f"Tool completed successfully: {url}")
        return result
    except Exception as e:
        logger.error(f"Tool failed: {url} - {type(e).__name__}: {e}")
        raise


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