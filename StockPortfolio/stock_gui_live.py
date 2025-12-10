# stock_gui_dropdown.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv, time, threading
import urllib.request
import yfinance as yf

# ---------- CONFIG ----------
CURRENCY = "₹"
TTL_SECONDS = 60
NSE_LIST_URL = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"

_price_cache = {}

# ---------------------------------------
# Fetch ALL NSE symbols (one time at startup)
# ---------------------------------------
def fetch_all_nse_symbols():
    req = urllib.request.Request(
        NSE_LIST_URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        lines = r.read().decode("utf-8").splitlines()
        reader = csv.DictReader(lines)
        symbols = [row["SYMBOL"].strip().upper() for row in reader if row.get("SYMBOL")]
    return sorted(symbols)

# ---------------------------------------
# Live price (with cache)
# ---------------------------------------
def get_live_price(symbol):
    yf_symbol = f"{symbol}.NS"
    now = time.time()
    if yf_symbol in _price_cache:
        price, ts = _price_cache[yf_symbol]
        if now - ts < TTL_SECONDS:
            return price

    t = yf.Ticker(yf_symbol)
    price = None
    # Try fast_info
    try:
        fi = getattr(t, "fast_info", None)
        if fi and getattr(fi, "last_price", None):
            price = float(fi.last_price)
    except Exception:
        pass
    # Fallback: last close
    if price is None:
        hist = t.history(period="1d", interval="1d")
        if hist is not None and not hist.empty:
            price = float(hist["Close"].iloc[-1])

    if price is None:
        raise ValueError(f"Cannot fetch live price for {symbol}")

    _price_cache[yf_symbol] = (price, now)
    return price

# ---------------------------------------
# Model
# ---------------------------------------
class Portfolio:
    def __init__(self):
        self.rows = []  # (symbol, qty, price, value)

    def add(self, symbol, qty):
        if qty <= 0:
            raise ValueError("Quantity must be > 0")
        price = get_live_price(symbol)
        self.rows.append((symbol, qty, price, price * qty))

    def remove(self, index):
        if 0 <= index < len(self.rows):
            self.rows.pop(index)

    def clear(self):
        self.rows.clear()

    @property
    def total(self):
        return sum(v for *_ , v in self.rows)

# ---------------------------------------
# GUI
# ---------------------------------------
class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=16)
        master.title("Stock Portfolio Tracker — NSE (Dropdown w/ Quick-Jump)")
        master.minsize(900, 600)
        master.configure(bg="#0f172a")
        self._style()

        self.model = Portfolio()

        # symbols will be loaded in background
        self.symbols = []
        self._load_symbols_thread()

        # Layout (same palette/structure)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        ttk.Label(self, text="Portfolio Tracker (NSE Live)", style="Title.TLabel")\
            .grid(row=0, column=0, sticky="w", pady=(0, 12))

        # --- Form ---
        form = ttk.Frame(self)
        form.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        for i in range(6): form.columnconfigure(i, weight=1)

        ttk.Label(form, text="Select Stock", style="Muted.TLabel")\
            .grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Quantity", style="Muted.TLabel")\
            .grid(row=0, column=1, sticky="w")

        self.symbol_var = tk.StringVar()
        self.qty_var = tk.StringVar(value="1")

        # Readonly dropdown (prefilled at startup)
        self.combo = ttk.Combobox(
            form,
            textvariable=self.symbol_var,
            state="readonly",
            style="Input.TCombobox",
            values=[],
            height=20,  # taller drop list
        )
        self.combo.grid(row=1, column=0, sticky="ew", padx=(0, 8))
        self.combo.bind("<Button-1>", lambda e: self._open_dropdown())

        # --- Quick-Jump bar (digits 0–9 then A–Z) ---
        jump = ttk.Frame(form)
        jump.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        # digits
        for i, d in enumerate("0123456789"):
            ttk.Button(jump, text=d, width=3, command=lambda p=d: self.jump_to_prefix(p)).grid(row=0, column=i, padx=1, pady=1)
        # letters
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for j, ch in enumerate(letters):
            ttk.Button(jump, text=ch, width=3, command=lambda p=ch: self.jump_to_prefix(p)).grid(row=1, column=j%13, padx=1, pady=1)
            if j == 12:
                # new row after M to keep compact grid
                pass

        self.qty_entry = ttk.Entry(form, textvariable=self.qty_var, style="Input.TEntry")
        self.qty_entry.grid(row=1, column=1, sticky="ew", padx=(0, 8))

        ttk.Button(form, text="Add (Live)", style="Accent.TButton",
                   command=self.on_add).grid(row=1, column=2, sticky="ew")
        ttk.Button(form, text="Remove Selected",
                   command=self.on_remove).grid(row=1, column=3, sticky="ew", padx=(8, 0))
        ttk.Button(form, text="Clear",
                   command=self.on_clear).grid(row=1, column=4, sticky="ew")
        ttk.Button(form, text="Refresh Prices",
                   command=self.on_refresh).grid(row=1, column=5, sticky="ew", padx=(8, 0))

        # --- Table ---
        cols = ("symbol", "qty", "price", "value")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=14)
        self.tree.grid(row=3, column=0, sticky="nsew")
        self.tree.heading("symbol", text="Symbol")
        self.tree.heading("qty", text="Quantity")
        self.tree.heading("price", text=f"Live Price ({CURRENCY})")
        self.tree.heading("value", text=f"Value ({CURRENCY})")
        self.tree.column("symbol", width=140, anchor="center")
        self.tree.column("qty", width=120, anchor="e")
        self.tree.column("price", width=180, anchor="e")
        self.tree.column("value", width=180, anchor="e")

        # --- Footer ---
        footer = ttk.Frame(self)
        footer.grid(row=4, column=0, sticky="ew", pady=(12, 0))
        footer.columnconfigure(0, weight=1)

        self.total_var = tk.StringVar(value=f"Total: {CURRENCY}0.00")
        ttk.Label(footer, textvariable=self.total_var, style="Total.TLabel")\
            .grid(row=0, column=0, sticky="w")
        ttk.Button(footer, text="Save .csv", command=lambda: self.save("csv"))\
            .grid(row=0, column=1, sticky="e", padx=6)
        ttk.Button(footer, text="Save .txt", command=lambda: self.save("txt"))\
            .grid(row=0, column=2, sticky="e")

        self.grid(sticky="nsew")
        self.qty_entry.bind("<Return>", lambda e: self.on_add())

    # ---------------- STYLE (same palette as before) ----------------
    def _style(self):
        s = ttk.Style()
        try: s.theme_use("clam")
        except Exception: pass

        s.configure(".", background="#0f172a", foreground="#e2e8f0")
        s.configure("TFrame", background="#0f172a")
        s.configure("TLabel", background="#0f172a", foreground="#e2e8f0")
        s.configure("Title.TLabel", font=("Inter", 18, "bold"))
        s.configure("Muted.TLabel", foreground="#cbd5e1")
        s.configure("Total.TLabel", font=("Inter", 14, "bold"))

        # Buttons with hover text fixed
        s.configure("TButton", background="#0b1220", foreground="#e2e8f0", padding=8)
        s.map("TButton",
              background=[("active", "#1e293b")],
              foreground=[("active", "#e2e8f0")])

        s.configure("Accent.TButton", background="#a7f3d0", foreground="#0f172a", padding=8)
        s.map("Accent.TButton",
              background=[("active", "#6ee7b7")],
              foreground=[("active", "#0f172a")])

        # Table
        s.configure("Treeview", background="#0b1220", fieldbackground="#0b1220",
                   foreground="#e2e8f0", rowheight=28, borderwidth=0)
        s.configure("Treeview.Heading", background="#111827", foreground="#e2e8f0")

        # Inputs: white fields, black text
        s.configure("Input.TEntry", foreground="#000000", fieldbackground="#ffffff")
        s.configure("Input.TCombobox", foreground="#000000", fieldbackground="#ffffff", background="#ffffff")

    # ---------------- LOAD SYMBOLS ONCE ----------------
    def _load_symbols_thread(self):
        def task():
            try:
                syms = fetch_all_nse_symbols()
                self.symbols = syms
                self.after(0, lambda: self.combo.configure(values=syms))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("NSE list error", str(e)))
        threading.Thread(target=task, daemon=True).start()

    # ---------- Combobox popdown internals ----------
    def _open_dropdown(self):
        self.combo.event_generate("<Down>")

    def _popdown_listbox(self):
        """Return the internal listbox of ttk.Combobox (for scrolling/selection)."""
        try:
            pop = self.combo.tk.call("ttk::combobox::PopdownWindow", str(self.combo))
            lb = self.combo.nametowidget(pop + ".f.l")
            return lb
        except Exception:
            return None

    def _ensure_visible(self, index: int):
        lb = self._popdown_listbox()
        if lb is not None:
            try:
                lb.see(index)
                lb.selection_clear(0, "end")
                lb.selection_set(index)
                lb.activate(index)
            except Exception:
                pass

    # ---------- Quick-Jump logic ----------
    def jump_to_prefix(self, prefix: str):
        """Open the dropdown and jump to the first symbol starting with the prefix."""
        prefix = prefix.upper()
        vals = self.combo.cget("values")
        if not vals:
            return
        # find first starting with prefix
        idx = next((i for i, v in enumerate(vals) if v.startswith(prefix)), None)
        if idx is None:
            # if prefix is a digit, try exact (some tickers start with digits)
            idx = next((i for i, v in enumerate(vals) if v[0:1] == prefix), None)
        if idx is not None:
            self.combo.current(idx)
            self.symbol_var.set(vals[idx])
            self._open_dropdown()
            self._ensure_visible(idx)

    # ---------------- ACTIONS ----------------
    def on_add(self):
        sym = self.symbol_var.get().strip().upper()
        if not sym:
            messagebox.showwarning("Missing", "Select a stock from the dropdown.")
            return
        try:
            qty = float(self.qty_var.get())
        except ValueError:
            messagebox.showerror("Invalid quantity", "Enter a numeric quantity.")
            return
        try:
            self.model.add(sym, qty)
        except Exception as e:
            messagebox.showerror("Add failed", str(e))
            return
        self.refresh_table()

    def on_remove(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = self.tree.index(sel[0])
        self.model.remove(idx)
        self.refresh_table()

    def on_clear(self):
        if not self.model.rows:
            return
        if messagebox.askyesno("Clear", "Remove all items?"):
            self.model.clear()
            self.refresh_table()

    def on_refresh(self):
        _price_cache.clear()
        try:
            new_rows = []
            for sym, qty, _, _ in self.model.rows:
                price = get_live_price(sym)
                new_rows.append((sym, qty, price, price * qty))
            self.model.rows = new_rows
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Refresh failed", str(e))

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for sym, qty, price, value in self.model.rows:
            self.tree.insert("", "end",
                             values=(sym, f"{qty:g}", f"{price:,.2f}", f"{value:,.2f}"))
        self.total_var.set(f"Total: {CURRENCY}{self.model.total:,.2f}")

    def save(self, kind="csv"):
        if not self.model.rows:
            messagebox.showinfo("Nothing to save", "Add some stocks first.")
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        if kind == "csv":
            fp = filedialog.asksaveasfilename(defaultextension=".csv",
                                              filetypes=[("CSV","*.csv")],
                                              initialfile=f"portfolio_{ts}.csv")
            if not fp: return
            with open(fp, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Symbol","Quantity","Live Price (INR)","Value (INR)"])
                for sym, qty, price, value in self.model.rows:
                    w.writerow([sym, qty, f"{price:.2f}", f"{value:.2f}"])
                w.writerow([]); w.writerow(["Total","","", f"{self.model.total:.2f}"])
        else:
            fp = filedialog.asksaveasfilename(defaultextension=".txt",
                                              filetypes=[("Text","*.txt")],
                                              initialfile=f"portfolio_{ts}.txt")
            if not fp: return
            with open(fp, "w", encoding="utf-8") as f:
                f.write("Stock Portfolio (NSE Live)\n")
                f.write("===========================\n")
                for sym, qty, price, value in self.model.rows:
                    f.write(f"{sym:12} qty={qty:g}  price={CURRENCY}{price:,.2f}  value={CURRENCY}{value:,.2f}\n")
                f.write("---------------------------\n")
                f.write(f"TOTAL: {CURRENCY}{self.model.total:,.2f}\n")
        messagebox.showinfo("Saved", "File saved successfully.")

# -------------------
def main():
    root = tk.Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
