import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from queue_manager import process_request

load_dotenv()

app = Flask(__name__)

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
DEFAULT_AI = os.getenv("DEFAULT_AI", "claude")
DEFAULT_MODE = os.getenv("DEFAULT_MODE", "incognito")

# ── ROUTES ─────────────────────────────────────────────────

@app.route('/', methods=['GET'])
def frontend():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "default_ai": DEFAULT_AI,
        "default_mode": DEFAULT_MODE,
        "port": PORT
    })

@app.route('/ask', methods=['POST'])
def ask():
    """
    POST /ask
    {
        "query": "What is AI?",
        "ai": "claude",          # optional, uses DEFAULT_AI
        "mode": "incognito",     # optional, uses DEFAULT_MODE
        "chat_id": "my_session"  # optional, only for stateful mode (future)
    }
    """
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query'"}), 400

    query = data['query']
    ai = data.get('ai', DEFAULT_AI)
    mode = data.get('mode', DEFAULT_MODE)

    kwargs = {k: v for k, v in data.items()
              if k not in ('query', 'ai', 'mode')}

    try:
        reply = process_request(ai, mode, query, **kwargs)
        return jsonify({
            "status": "ok",
            "ai": ai,
            "mode": mode,
            "query": query,
            "reply": reply,
            "chars": len(reply)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

# ── START ───────────────────────────────────────────────────

if __name__ == "__main__":
    print("╔══════════════════════════════════════╗")
    print("║       AI Gateway Server v1.0         ║")
    print("╠══════════════════════════════════════╣")
    print(f"║  GET  http://localhost:{PORT}/health    ║")
    print(f"║  POST http://localhost:{PORT}/ask       ║")
    print(f"║  GET  http://localhost:{PORT}/          ║")
    print("╠══════════════════════════════════════╣")
    print(f"║  Default AI:   {DEFAULT_AI:<22}║")
    print(f"║  Default Mode: {DEFAULT_MODE:<22}║")
    print("╚══════════════════════════════════════╝")
    app.run(host=HOST, port=PORT, debug=False)