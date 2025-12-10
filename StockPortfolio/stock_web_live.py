from flask import Flask, render_template, request, jsonify, make_response
import csv, io, time, urllib.request
from datetime import datetime
import yfinance as yf

app = Flask(__name__)

CURRENCY = "₹"
TTL_SECONDS = 60
_price_cache = {}  # { "RELIANCE.NS": (price, ts) }

NSE_LIST_URL = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"

# ---------- Helpers ----------
def to_yf_symbol(sym: str) -> str:
    s = sym.strip().upper()
    return s if "." in s else f"{s}.NS"

def get_live_price(sym: str) -> float:
    yf_sym = to_yf_symbol(sym)
    now = time.time()
    if yf_sym in _price_cache:
        price, ts = _price_cache[yf_sym]
        if now - ts < TTL_SECONDS:
            return price

    t = yf.Ticker(yf_sym)
    price = None
    try:
        fi = getattr(t, "fast_info", None)
        if fi and getattr(fi, "last_price", None):
            price = float(fi.last_price)
    except Exception:
        pass

    if price is None:
        hist = t.history(period="1d")
        if hist is not None and not hist.empty:
            price = float(hist["Close"].iloc[-1])

    if price is None:
        raise ValueError(f"Could not fetch live price for {yf_sym}")

    _price_cache[yf_sym] = (price, now)
    return price

def fetch_all_nse_symbols():
    """Fetch full NSE symbols list from official CSV."""
    req = urllib.request.Request(NSE_LIST_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=12) as r:
        text = r.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    symbols = sorted({(row.get("SYMBOL") or "").strip().upper() for row in reader if row.get("SYMBOL")})
    return symbols

# ---------- Routes ----------
@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/symbols")
def symbols():
    try:
        syms = fetch_all_nse_symbols()
        return jsonify(syms)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/api/quote")
def quote():
    sym = (request.args.get("symbol") or "").strip()
    if not sym:
        return jsonify({"error": "symbol is required"}), 400
    try:
        price = get_live_price(sym)
        return jsonify({"symbol": sym.upper(), "price": price, "currency": CURRENCY})
    except Exception as e:
        return jsonify({"error": str(e)}), 502

@app.post("/api/export")
def export():
    data = request.get_json(force=True, silent=True) or {}
    rows = data.get("rows", [])
    fmt  = (data.get("fmt") or "csv").lower()
    total = float(data.get("total", 0))

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    if fmt == "txt":
        buf = io.StringIO()
        buf.write("Stock Portfolio (NSE Live)\n")
        buf.write("==========================\n")
        for r in rows:
            buf.write(
                f"{r['symbol']:12}  qty={r['qty']}  price={CURRENCY}{float(r['price']):,.2f}  "
                f"value={CURRENCY}{float(r['value']):,.2f}\n"
            )
        buf.write("--------------------------\n")
        buf.write(f"TOTAL: {CURRENCY}{total:,.2f}\n")
        resp = make_response(buf.getvalue())
        resp.headers["Content-Type"] = "text/plain; charset=utf-8"
        resp.headers["Content-Disposition"] = f"attachment; filename=portfolio_{ts}.txt"
        return resp

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Symbol","Quantity","Live Price (INR)","Value (INR)"])
    for r in rows:
        w.writerow([r["symbol"], r["qty"], f"{float(r['price']):.2f}", f"{float(r['value']):.2f}"])
    w.writerow([]); w.writerow(["Total","","", f"{total:.2f}"])
    resp = make_response(buf.getvalue())
    resp.headers["Content-Type"] = "text/csv; charset=utf-8"
    resp.headers["Content-Disposition"] = f"attachment; filename=portfolio_{ts}.csv"
    return resp

# exit support
@app.get("/shutdown")
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        return jsonify({"error":"Cannot shut down server"}), 500
    func(); return jsonify({"status":"Server shutting down..."})

if __name__ == "__main__":
    # pip install flask yfinance
    app.run(debug=True)
