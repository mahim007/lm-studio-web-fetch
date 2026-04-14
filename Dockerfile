FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY web_search_tool.py .
COPY mcp_server.py .

EXPOSE 5000

# Use mcp CLI to run the server
CMD ["uvicorn", "mcp_server:app", "--host", "0.0.0.0", "--port", "5000"]
