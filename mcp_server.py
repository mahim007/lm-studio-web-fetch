from mcp.server.fastmcp import FastMCP
from web_search_tool import web_search_tool

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

    return web_search_tool(url=url)

if __name__ == "__main__":
    # Use stdio transport for LM Studio MCP integration
    mcp.run(transport="stdio")