from flask import Flask, request, jsonify
from web_search_tool import web_search_tool
import json

app = Flask(__name__)

@app.route('/fetch_web_page', methods=['POST'])

def fetch_web_page():
    """
    Tool endpoint called by LM Studio.
    Receives a URL in the request body, calls web_search_tool,
    and returns the structured JSON result.
    """

    data = request.get_json()

    if not data or 'url' not in data:
        return jsonify({"error": "Missing 'url' in request body"}), 400
    
    url = data['url']
    print(f"[Tool Server] Received request for URL: {url}")

    result = web_search_tool(url)

    return jsonify(result)

@app.route('/health')
def health():
    """ Health check endpoint to verify sever is running."""
    return jsonify({"sustus": "ok"})

if __name__ == '__main__':
    print("=" * 60)
    print("  LM Studio Tool Server")
    print("  Running on: http://127.0.0.1:5000")
    print("  Tool endpoint: http://127.0.0.1:5000/fetch_web_page")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)