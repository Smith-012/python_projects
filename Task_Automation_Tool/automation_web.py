from flask import Flask, render_template, request, jsonify, make_response
import io, re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

@app.get("/")
def home():
    return render_template("index.html")

# ---- Email extraction (server optional; we keep it for parity) ----
@app.post("/api/extract_emails")
def extract_emails():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text","")
    emails = sorted(set(EMAIL_RE.findall(text)))
    return jsonify({"count": len(emails), "emails": emails})

# ---- Scrape title via server to avoid browser CORS ----
@app.get("/api/scrape_title")
def scrape_title():
    url = (request.args.get("url") or "").strip()
    if not url:
        return jsonify({"error":"url required"}), 400
    try:
        headers={"User-Agent":"Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10); r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        title = (soup.title.string or "").strip() if soup.title else ""
        if not title: return jsonify({"error":"No <title> found"}), 404
        return jsonify({"title": title})
    except Exception as e:
        return jsonify({"error": str(e)}), 502

@app.post("/api/export_title")
def export_title():
    data = request.get_json(force=True, silent=True) or {}
    url = (data.get("url") or "").strip()
    title = (data.get("title") or "").strip()
    if not url or not title:
        return jsonify({"error":"url and title required"}), 400
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    buf = io.StringIO()
    buf.write(f"URL: {url}\nTitle: {title}\n")
    resp = make_response(buf.getvalue())
    resp.headers["Content-Type"] = "text/plain; charset=utf-8"
    resp.headers["Content-Disposition"] = f"attachment; filename=page_title_{ts}.txt"
    return resp

# ---- Exit server (optional convenience) ----
@app.get("/shutdown")
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if not func:
        return jsonify({"error":"Cannot shut down server"}), 500
    func(); return jsonify({"status":"Server shutting down..."})

if __name__ == "__main__":
    # pip install flask requests beautifulsoup4
    app.run(debug=True)
