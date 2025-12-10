import threading
import re
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Config: tweak keywords here
# -----------------------------
CATEGORY_KEYWORDS = {
    "Groceries": ["walmart", "kroger", "aldi", "whole foods", "trader joe", "costco", "safeway"],
    "Dining": ["restaurant", "cafe", "coffee", "starbucks", "mcdonald", "kfc", "domino", "ubereats", "doordash"],
    "Transport": ["uber", "lyft", "shell", "bp", "exxon", "chevron", "metro", "bus", "train", "parking"],
    "Utilities": ["electric", "water", "gas", "internet", "utility", "comcast", "verizon", "att"],
    "Rent/Mortgage": ["rent", "mortgage", "landlord"],
    "Entertainment": ["netflix", "spotify", "hulu", "disney", "cinema", "theatre", "steam"],
    "Shopping": ["amazon", "walmart.com", "target", "best buy", "ikea", "etsy"],
    "Health": ["pharmacy", "walgreens", "cvs", "clinic", "hospital", "dentist"],
    "Income": ["payroll", "salary", "paycheck", "deposit", "stripe", "paypal payout"],
    "Other": []
}
AUTO_INCOME_IF_POSITIVE = True

# ---------- Core logic (same engine as CLI) ----------
def _guess_column(df, candidates):
    norm = {re.sub(r"[\W_]+", "", c).lower(): c for c in df.columns}
    for cand in candidates:
        key = re.sub(r"[\W_]+", "", cand).lower()
        if key in norm:
            return norm[key]
    for k, orig in norm.items():
        if any(re.sub(r"[\W_]+", "", c).lower() in k for c in candidates):
            return orig
    return None

def _load_and_normalize(path: Path) -> pd.DataFrame:
    ext = path.suffix.lower()
    if ext == ".csv":
        df = pd.read_csv(path)
    elif ext in {".xlsx", ".xls"}:
        df = pd.read_excel(path)  # first sheet by default
    else:
        raise ValueError(f"Unsupported file type: {path.name}")

    date_col = _guess_column(df, ["Date", "Transaction Date", "Posted Date", "dt", "Txn Date"])
    desc_col = _guess_column(df, ["Description", "Details", "Merchant", "Narration", "Memo"])
    amt_col  = _guess_column(df, ["Amount", "Transaction Amount", "Amt", "Value"])

    if not all([date_col, desc_col, amt_col]):
        raise ValueError(f"Could not find date/description/amount in {path.name}")

    out = df[[date_col, desc_col, amt_col]].copy()
    out.columns = ["Date", "Description", "Amount"]

    out["Date"] = pd.to_datetime(out["Date"], errors="coerce", infer_datetime_format=True)
    out["Amount"] = (
        out["Amount"].astype(str)
        .str.replace(r"[^\d\-\.\,]", "", regex=True)
        .str.replace(",", "", regex=False)
        .astype(float)
    )
    out = out.dropna(subset=["Date", "Amount"])
    out["SourceFile"] = path.name
    return out

def _categorize(description, amount):
    text = str(description).lower()
    if AUTO_INCOME_IF_POSITIVE and amount > 0:
        for kw in CATEGORY_KEYWORDS.get("Income", []):
            if kw in text:
                return "Income"
        return "Income"
    for cat, kws in CATEGORY_KEYWORDS.items():
        if cat == "Income":
            continue
        for kw in kws:
            if kw in text:
                return cat
    return "Uncategorized"

def build_report(input_files, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    for f in input_files:
        try:
            frames.append(_load_and_normalize(Path(f)))
        except Exception as e:
            # skip but keep going
            print(f"Skipping {f}: {e}")
    if not frames:
        raise RuntimeError("No usable files after parsing.")

    df = pd.concat(frames, ignore_index=True).sort_values("Date")
    df["Month"] = df["Date"].dt.to_period("M").dt.to_timestamp()
    df["Category"] = [ _categorize(d, a) for d, a in zip(df["Description"], df["Amount"]) ]

    clean_csv = output_dir / "transactions_clean.csv"
    df.to_csv(clean_csv, index=False)

    spend = df[df["Amount"] < 0].copy()
    income = df[df["Amount"] > 0].copy()

    summary_spend = (
        spend.groupby(["Month", "Category"], as_index=False)["Amount"]
        .sum()
        .assign(Amount=lambda x: x["Amount"].abs())
    )
    monthly_totals = summary_spend.groupby("Month", as_index=False)["Amount"].sum().rename(columns={"Amount":"TotalSpend"})
    monthly_income = income.groupby("Month", as_index=False)["Amount"].sum().rename(columns={"Amount":"TotalIncome"})
    monthly_net = pd.merge(monthly_income, monthly_totals, on="Month", how="outer").fillna(0.0)
    monthly_net["Net"] = monthly_net["TotalIncome"] - monthly_net["TotalSpend"]

    excel_path = output_dir / "expense_report.xlsx"
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Transactions")
        summary_spend.pivot(index="Month", columns="Category", values="Amount").fillna(0.0)\
            .to_excel(writer, sheet_name="CategoryByMonth")
        monthly_net.to_excel(writer, index=False, sheet_name="Income_vs_Spend")

    latest_month = summary_spend["Month"].max() if not summary_spend.empty else None
    chart_path = None
    if latest_month is not None and pd.notna(latest_month):
        latest = summary_spend[summary_spend["Month"] == latest_month].sort_values("Amount", ascending=False)
        if not latest.empty:
            plt.figure(figsize=(8,5))
            plt.bar(latest["Category"], latest["Amount"])
            plt.title(f"Category Spend – {latest_month.strftime('%Y-%m')}")
            plt.ylabel("Amount")
            plt.xticks(rotation=30, ha="right")
            plt.tight_layout()
            chart_path = output_dir / "category_spend.png"
            plt.savefig(chart_path, dpi=160)
            plt.close()

    return {"clean_csv": clean_csv, "excel": excel_path, "chart": chart_path}

# ----------------------------- GUI -----------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Report Builder")
        self.geometry("760x480")
        self.files = []
        self.output_dir = None
        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 10, "pady": 8}

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True)

        # File controls
        top = ttk.LabelFrame(frm, text="Input files (.csv, .xlsx, .xls)")
        top.pack(fill="x", **pad)

        btns = ttk.Frame(top)
        btns.pack(fill="x", padx=8, pady=8)

        ttk.Button(btns, text="Add Files…", command=self.add_files).pack(side="left")
        ttk.Button(btns, text="Remove Selected", command=self.remove_selected).pack(side="left", padx=6)
        ttk.Button(btns, text="Clear", command=self.clear_files).pack(side="left")

        self.listbox = tk.Listbox(top, height=8, selectmode=tk.EXTENDED)
        self.listbox.pack(fill="both", expand=True, padx=8, pady=(0,8))

        # Output folder
        outfrm = ttk.LabelFrame(frm, text="Output folder")
        outfrm.pack(fill="x", **pad)

        outrow = ttk.Frame(outfrm)
        outrow.pack(fill="x", padx=8, pady=8)
        self.outvar = tk.StringVar()
        ttk.Entry(outrow, textvariable=self.outvar).pack(side="left", fill="x", expand=True)
        ttk.Button(outrow, text="Choose…", command=self.choose_output).pack(side="left", padx=6)

        # Actions
        act = ttk.Frame(frm)
        act.pack(fill="x", **pad)
        self.run_btn = ttk.Button(act, text="Generate Report", command=self.run_report)
        self.run_btn.pack(side="left")
        ttk.Button(act, text="Edit Categories…", command=self.show_categories).pack(side="left", padx=8)

        # Status
        self.progress = ttk.Progressbar(frm, mode="indeterminate")
        self.progress.pack(fill="x", padx=10, pady=(0,6))
        self.status = tk.StringVar(value="Ready.")
        ttk.Label(frm, textvariable=self.status, anchor="w").pack(fill="x", padx=12, pady=(0,10))

    # --- callbacks ---
    def add_files(self):
        paths = filedialog.askopenfilenames(
            title="Select CSV/Excel files",
            filetypes=[("CSV/Excel", "*.csv;*.xlsx;*.xls"), ("CSV", "*.csv"), ("Excel", "*.xlsx;*.xls"), ("All files","*.*")]
        )
        for p in paths:
            if p not in self.files:
                self.files.append(p)
                self.listbox.insert("end", p)

    def remove_selected(self):
        sel = list(self.listbox.curselection())
        for idx in reversed(sel):
            self.listbox.delete(idx)
            del self.files[idx]

    def clear_files(self):
        self.listbox.delete(0, "end")
        self.files = []

    def choose_output(self):
        d = filedialog.askdirectory(title="Select output folder")
        if d:
            self.output_dir = Path(d)
            self.outvar.set(str(self.output_dir))

    def show_categories(self):
        # simple viewer/editor window (in-memory for this run)
        win = tk.Toplevel(self)
        win.title("Edit Categories (comma-separated keywords)")
        win.geometry("600x420")

        text = tk.Text(win, wrap="word")
        text.pack(fill="both", expand=True)

        # preload
        def dump():
            lines = []
            for cat, kws in CATEGORY_KEYWORDS.items():
                lines.append(f"{cat}: {', '.join(kws)}")
            return "\n".join(lines)
        text.insert("1.0", dump())

        def save():
            try:
                newmap = {}
                for line in text.get("1.0", "end").splitlines():
                    if not line.strip():
                        continue
                    if ":" not in line:
                        raise ValueError(f"Missing ':' in line: {line}")
                    cat, rest = line.split(":", 1)
                    kws = [k.strip().lower() for k in rest.split(",") if k.strip()]
                    newmap[cat.strip()] = kws
                CATEGORY_KEYWORDS.clear()
                CATEGORY_KEYWORDS.update(newmap)
                messagebox.showinfo("Saved", "Categories updated for this session.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(win, text="Save", command=save).pack(pady=8)

    def run_report(self):
        if not self.files:
            messagebox.showwarning("No files", "Please add at least one CSV or Excel file.")
            return
        if not self.output_dir:
            # default next to first file
            self.output_dir = Path(self.files[0]).parent / "report_out"
            self.outvar.set(str(self.output_dir))

        self.status.set("Working…")
        self.progress.start(10)
        self.run_btn.config(state="disabled")

        def worker():
            try:
                paths = build_report(self.files, self.output_dir)
                msg = "Done!\n\n"
                msg += f"• Cleaned CSV: {paths['clean_csv']}\n"
                msg += f"• Excel report: {paths['excel']}\n"
                if paths.get("chart"):
                    msg += f"• Chart: {paths['chart']}\n"
                self.after(0, lambda: messagebox.showinfo("Success", msg))
                self.after(0, lambda: self.status.set("Finished."))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.after(0, lambda: self.status.set("Failed."))
            finally:
                self.after(0, self.progress.stop)
                self.after(0, lambda: self.run_btn.config(state="normal"))

        threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    App().mainloop()
