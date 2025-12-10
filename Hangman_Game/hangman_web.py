from flask import Flask, render_template, jsonify, request
import urllib.request, json

app = Flask(__name__)

WORD_API_URL = "https://random-word-api.herokuapp.com/word?number=1"

def fetch_online_word() -> str:
    with urllib.request.urlopen(WORD_API_URL, timeout=8) as r:
        data = json.loads(r.read().decode("utf-8"))
        if isinstance(data, list) and data:
            w = str(data[0]).strip()
            if w.isalpha() and 3 <= len(w) <= 14:
                return w.lower()
    raise RuntimeError("Upstream word API returned no valid word")

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api/random_word")
def random_word():
    try:
        return jsonify({"word": fetch_online_word()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/shutdown")
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        return jsonify({"error": "Cannot shut down server"}), 500
    func()
    return jsonify({"status": "Server shutting down..."})

if __name__ == "__main__":
    app.run(debug=True)
