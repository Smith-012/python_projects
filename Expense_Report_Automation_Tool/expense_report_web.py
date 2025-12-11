# Web-based Expense Report Builder (Streamlit)
# Save this file at the root of your Task-1 folder as: expense_report_web.py
# Run with:  streamlit run expense_report_web.py
# Deps: pip install streamlit pandas matplotlib openpyxl

import io
import re
from pathlib import Path
from datetime import datetime

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Default Category Keywords (editable in UI)
# -----------------------------
DEFAULT_CATEGORY_KEYWORDS = {
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

# -----------------------------
# Helpers
# -----------------------------

def _guess_column(df: pd.DataFrame, candidates):
    norm = {re.sub(r"[\W_]+", "", c).lower(): c for c in df.columns}
    for cand in candidates:
        key = re.sub(r"[\W_]+", "", cand).lower()
        if key in norm:
            return norm[key]
    for k, orig in norm.items():
        if any(re.sub(r"[\W_]+", "", c).lower() in k for c in candidates):
            return orig
    return None


def _load_and_normalize_from_upload(upload) -> pd.DataFrame:
    """upload is a streamlit UploadedFile"""
    name = upload.name
    ext = Path(name).suffix.lower()

    if ext == ".csv":
        df = pd.read_csv(upload)
    elif ext in {".xlsx", ".xls"}:
        df = pd.read_excel(upload)  # first sheet by default
    else:
        raise ValueError(f"Unsupported file type: {name}")

    date_col = _guess_column(df, ["Date", "Transaction Date", "Posted Date", "dt", "Txn Date"])
    desc_col = _guess_column(df, ["Description", "Details", "Merchant", "Narration", "Memo"])
    amt_col  = _guess_column(df, ["Amount", "Transaction Amount", "Amt", "Value"])

    if not all([date_col, desc_col, amt_col]):
        raise ValueError(f"Could not find date/description/amount in {name}")

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
    out["SourceFile"] = name
    return out


def _categorize(description, amount, mapping):
    text = str(description).lower()
    if AUTO_INCOME_IF_POSITIVE and amount > 0:
        for kw in mapping.get("Income", []):
            if kw in text:
                return "Income"
        return "Income"
    for cat, kws in mapping.items():
        if cat == "Income":
            continue
        for kw in kws:
            if kw in text:
                return cat
    return "Uncategorized"


def build_report_from_uploads(uploads, output_dir: Path, mapping: dict):
    output_dir.mkdir(parents=True, exist_ok=True)

    frames = []
    for up in uploads:
        try:
            frames.append(_load_and_normalize_from_upload(up))
        except Exception as e:
            st.warning(f"Skipping {up.name}: {e}")
    if not frames:
        raise RuntimeError("No usable files after parsing.")

    df = pd.concat(frames, ignore_index=True).sort_values("Date")
    df["Month"] = df["Date"].dt.to_period("M").dt.to_timestamp()
    df["Category"] = [ _categorize(d, a, mapping) for d, a in zip(df["Description"], df["Amount"]) ]

    # Save cleaned CSV to disk and also as bytes for download
    clean_csv_path = output_dir / "transactions_clean.csv"
    df.to_csv(clean_csv_path, index=False)
    clean_csv_bytes = df.to_csv(index=False).encode()

    # Spend vs Income
    spend = df[df["Amount"] < 0].copy()
    income = df[df["Amount"] > 0].copy()

    summary_spend = (
        spend.groupby(["Month", "Category"], as_index=False)["Amount"].sum()
        .assign(Amount=lambda x: x["Amount"].abs())
    )
    monthly_totals = summary_spend.groupby("Month", as_index=False)["Amount"].sum().rename(columns={"Amount":"TotalSpend"})
    monthly_income = income.groupby("Month", as_index=False)["Amount"].sum().rename(columns={"Amount":"TotalIncome"})
    monthly_net = pd.merge(monthly_income, monthly_totals, on="Month", how="outer").fillna(0.0)
    monthly_net["Net"] = monthly_net["TotalIncome"] - monthly_net["TotalSpend"]

    # Excel report
    excel_path = output_dir / "expense_report.xlsx"
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Transactions")
        summary_spend.pivot(index="Month", columns="Category", values="Amount").fillna(0.0)\
            .to_excel(writer, sheet_name="CategoryByMonth")
        monthly_net.to_excel(writer, index=False, sheet_name="Income_vs_Spend")
    # Bytes for download
    excel_bytes = io.BytesIO()
    with pd.ExcelWriter(excel_bytes, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Transactions")
        summary_spend.pivot(index="Month", columns="Category", values="Amount").fillna(0.0)\
            .to_excel(writer, sheet_name="CategoryByMonth")
        monthly_net.to_excel(writer, index=False, sheet_name="Income_vs_Spend")
    excel_bytes.seek(0)

    # Chart for latest month
    latest_month = summary_spend["Month"].max() if not summary_spend.empty else None
    chart_png_path = None
    chart_buf = None
    if latest_month is not None and pd.notna(latest_month):
        latest = summary_spend[summary_spend["Month"] == latest_month].sort_values("Amount", ascending=False)
        if not latest.empty:
            fig = plt.figure(figsize=(8,5))
            plt.bar(latest["Category"], latest["Amount"])
            plt.title(f"Category Spend – {latest_month.strftime('%Y-%m')}")
            plt.ylabel("Amount")
            plt.xticks(rotation=30, ha="right")
            plt.tight_layout()

            # Save to disk
            chart_png_path = output_dir / "category_spend.png"
            fig.savefig(chart_png_path, dpi=160)

            # And to bytes
            chart_buf = io.BytesIO()
            fig.savefig(chart_buf, format="png", dpi=160)
            chart_buf.seek(0)

    return {
        "df": df,
        "summary_spend": summary_spend,
        "monthly_net": monthly_net,
        "clean_csv_path": clean_csv_path,
        "clean_csv_bytes": clean_csv_bytes,
        "excel_path": excel_path,
        "excel_bytes": excel_bytes,
        "chart_path": chart_png_path,
        "chart_bytes": chart_buf,
        "latest_month": latest_month,
    }

# -----------------------------
# Streamlit UI
# -----------------------------

st.set_page_config(page_title="Expense Report (Web)", layout="centered")
st.title("💸 Expense Report Builder – Web")
st.write("Upload your CSV/Excel statements, then generate a report. Outputs are saved into **./report_out/** and offered for download.")

with st.expander("Category keywords (edit as needed)", expanded=False):
    mapping_text = st.text_area(
        "Provide a JSON mapping of categories → keywords:",
        value=pd.Series(DEFAULT_CATEGORY_KEYWORDS).to_json(indent=2),
        height=220,
    )
    try:
        CATEGORY_KEYWORDS = pd.read_json(io.StringIO(mapping_text), typ="series").to_dict()
        # ensure list of str
        CATEGORY_KEYWORDS = {
            k: [str(x).lower() for x in (v if isinstance(v, list) else [])]
            for k, v in CATEGORY_KEYWORDS.items()
        }
        st.caption("Loaded category mapping ✔")
    except Exception as e:
        st.error(f"Invalid JSON mapping. Using defaults. Error: {e}")
        CATEGORY_KEYWORDS = DEFAULT_CATEGORY_KEYWORDS

uploads = st.file_uploader(
    "Select CSV/Excel files",
    type=["csv", "xlsx", "xls"],
    accept_multiple_files=True,
)

run = st.button("Generate Report", type="primary", use_container_width=True)

if run:
    if not uploads:
        st.warning("Please upload at least one file.")
    else:
        with st.spinner("Processing…"):
            out_dir = Path("report_out")
            result = build_report_from_uploads(uploads, out_dir, CATEGORY_KEYWORDS)

        st.success("Done!")

        # Show latest-month chart if present
        if result["chart_bytes"] is not None:
            st.subheader(f"Category Spend – {result['latest_month'].strftime('%Y-%m')}")
            st.image(result["chart_bytes"].getvalue(), caption="category_spend.png", use_column_width=True)

        # Show a sample of transactions
        st.subheader("Transactions (first 200 rows)")
        st.dataframe(result["df"].head(200))

        # Downloads
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                label="Download cleaned CSV",
                data=result["clean_csv_bytes"],
                file_name="transactions_clean.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with col2:
            st.download_button(
                label="Download Excel report",
                data=result["excel_bytes"].getvalue(),
                file_name="expense_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        with col3:
            if result["chart_bytes"] is not None:
                st.download_button(
                    label="Download chart PNG",
                    data=result["chart_bytes"].getvalue(),
                    file_name="category_spend.png",
                    mime="image/png",
                    use_container_width=True,
                )

        st.info("Files also saved to the local folder: ./report_out/")
