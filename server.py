from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# In-memory storage of messages
# Each item: {"time": "ISO", "msg": "text"}
messages = []


@app.route("/upload", methods=["POST"])
def upload():
    """
    Reader agent sends:
    {
      "timestamp": "...",
      "messages": ["line1", "line2", ...]
    }
    """
    data = request.json or {}
    ts = data.get("timestamp")
    lines = data.get("messages", [])

    if not ts or not isinstance(lines, list):
        return {"status": "error", "detail": "bad payload"}, 400

    for line in lines:
        line = str(line).strip()
        if line:
            messages.append({
                "time": ts,
                "msg": line
            })

    print(f"[SERVER] Received {len(lines)} messages at {ts}")
    return {"status": "ok"}


@app.route("/fetch", methods=["GET"])
def fetch():
    """
    Receiver GUI calls this to get full message list.
    """
    return jsonify(messages)


if __name__ == "__main__":
    # Run on all interfaces so PC #2 can reach PC #1
    app.run(host="0.0.0.0", port=5000)
