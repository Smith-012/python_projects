
# 📈 NSE Live Portfolio Tracker (Desktop GUI + Web)

A polished **stock portfolio tracker** for the **Indian stock market (NSE)** delivered in two flavors:

- **Desktop GUI** using **Python + Tkinter** (`stock_gui_dropdown.py`)
- **Web App** using **Flask + HTML/CSS/JS** (`stock_web_live.py` + `/templates` + `/static`)

Both apps:
- Fetch the **entire NSE symbol list dynamically** from the **official NSE CSV** (no hard-coded lists)
- Use **live prices** via **yfinance** with a short cache (TTL = 60s)
- Let you **add/remove/clear** items, **refresh prices**, and **export** to **CSV/TXT**
- Provide a clean **dark UI** with a **Quick‑Jump** feature to jump to symbols by **0–9 / A–Z**

---

## ✨ Features

### ✅ Dynamic NSE Symbols (No Static List)
- Symbols are fetched at runtime from the official NSE listing:
  - `https://archives.nseindia.com/content/equities/EQUITY_L.csv`
- The **GUI** preloads symbols into a **Combobox**, with a quick‑jump helper.
- The **Web App** preloads symbols into a **dropdown** and shows an **A–Z / 0–9 Quick‑Jump** bar beneath it.

### ✅ Live Price Fetch (INR)
- Powered by **yfinance**:
  - First tries `Ticker.fast_info.last_price`
  - Falls back to `Ticker.history(period="1d")` last close
- Local cache to reduce API calls: **TTL_SECONDS = 60**

### ✅ Portfolio Tools
- Add a symbol + quantity → live **price** and **value** are calculated
- **Refresh** prices button
- **Remove** one row or **Clear** all rows
- **Exports**: save `.csv` or `.txt` with totals

### ✅ UI Touches
- **Dark palette** (slate style), rounded inputs & cards
- **SweetAlert2** toasts/dialogs (web)
- **Exit** button on the web to confirm and shut down the Flask dev server

---

## 🗂 Project Structure

```
project/
│
├── stock_gui_dropdown.py         # Desktop GUI app (Tkinter)
├── stock_web_live.py             # Flask backend for web app
├── templates/
│   └── index.html                # Web UI
└── static/
    ├── style.css                 # Web styles
    └── script.js                 # Web client logic
```

---

## 🖥️ Desktop GUI (Tkinter)

**File:** `stock_gui_dropdown.py`

### Install
```bash
pip install yfinance
```

### Run
```bash
python stock_gui_dropdown.py
```

### Highlights
- Loads **all NSE symbols** once at startup (official CSV)
- **Combobox** with **Quick‑Jump buttons** (0–9 / A–Z)
- Live prices with caching
- Table shows **Symbol**, **Quantity**, **Live Price (₹)**, **Value (₹)**
- **Save CSV/TXT** with running **Total**

---

## 🌐 Web App (Flask)

**Backend:** `stock_web_live.py`  
**Frontend:** `templates/index.html`, `static/style.css`, `static/script.js`

### Install
```bash
pip install flask yfinance
```

### Run
```bash
python stock_web_live.py
```

### Open
```
http://127.0.0.1:5000/
```

### Endpoints
- `GET /` → serve UI
- `GET /api/symbols` → return full NSE symbol list (live, no static)
- `GET /api/quote?symbol=RELIANCE` → return live price (in INR)
- `POST /api/export` → returns CSV/TXT for download
- `GET /shutdown` → graceful dev server shutdown (used by “Exit”)

---

## ⚙️ How It Works

### Fetching NSE Symbols
- Backend requests **EQUITY_L.csv** from NSE archive
- Parses with `csv.DictReader` → builds a **sorted, unique** uppercase list of `SYMBOL`

### Price Strategy
1. Try `yf.Ticker("<SYMBOL>.NS").fast_info.last_price`
2. If missing, `history(period="1d")` and use last close
3. Cache price in `_price_cache` for **60 seconds**

> Note: Yahoo Finance data can occasionally lag or throttle. The 60s cache reduces API pressure and improves responsiveness.

---

## 🧪 Tips & Troubleshooting

- If prices fail: try again (temporary throttling), or check ticker accuracy
- If symbols don’t load: ensure internet access to NSE archives and no firewall blocking
- Windows may not allow the browser window to close programmatically; the **Exit** action still requests server shutdown.

---

## 🔐 Privacy & API Keys

- No keys required. Everything uses **public endpoints** + **yfinance**
- No data is stored server-side; exports are created on demand in the browser/download

---

## 🙌 Credits

- **NSE India** for the symbols CSV
- **Yahoo Finance** (via `yfinance`) for price data
- **SweetAlert2** for clean modals/toasts (web)

---
