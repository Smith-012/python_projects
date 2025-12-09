# app.py — Streamlit Data Visualization Web App (fixed library switching)
# pip install streamlit pandas matplotlib seaborn plotly

import io
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.set_page_config(page_title="Data Visualization Tool", layout="wide")

# ---------- helpers ----------
@st.cache_data
def generate_sample_csv(rows: int = 120) -> bytes:
    np.random.seed(42)
    depts = np.random.choice(["IT", "HR", "Finance", "Sales"], size=rows)
    names = [f"User_{i:03d}" for i in range(rows)]
    ages = np.random.randint(20, 60, size=rows)
    salary = np.random.randint(30000, 120000, size=rows)
    exp = np.maximum(0, ages - np.random.randint(18, 26, size=rows))
    df = pd.DataFrame({
        "Name": names,
        "Department": depts,
        "Age": ages,
        "Salary": salary,
        "Experience": exp,
    })
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")

@st.cache_data
def load_csv(file) -> pd.DataFrame:
    return pd.read_csv(file)

def is_numeric(series: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(series)

def needs_y(chart: str) -> bool:
    return chart in {"scatter", "line", "bar (aggregate)", "box"}

def needs_only_x(chart: str) -> bool:
    return chart in {"histogram", "pie"}

# ---------- top ----------
left, right = st.columns([2, 1], gap="large")
with left:
    st.title("📊 Data Visualization Tool (web version)")
    st.caption("No login • Open for everyone")

with right:
    st.subheader("Download sample CSV")
    sample_bytes = generate_sample_csv()
    st.download_button(
        "⬇️ Download sample",
        data=sample_bytes,
        file_name=f"sample_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )

st.divider()

# ---------- sidebar ----------
st.sidebar.header("1) Upload CSV")
file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

st.sidebar.header("2) Options")
lib = st.sidebar.selectbox("Library", ["Plotly", "Seaborn", "Matplotlib"])
chart = st.sidebar.selectbox(
    "Chart type",
    ["scatter", "line", "bar (aggregate)", "histogram", "box", "pie", "correlation heatmap"],
)

agg = st.sidebar.selectbox("Aggregation (bar)", ["count", "sum", "mean", "median", "min", "max"])
bins = st.sidebar.number_input("Bins (hist)", min_value=5, max_value=200, value=30, step=1)

if not file:
    st.info("Upload a CSV to begin or use the sample above.")
    st.stop()

df = load_csv(file)
st.subheader("Data preview")
st.dataframe(df.head(), use_container_width=True)
st.divider()

cols = list(df.columns)

# Inputs shown only when relevant
x = st.sidebar.selectbox("X", cols, index=0 if cols else None, key=f"x_{chart}_{lib}")
y_label = "Y" if needs_y(chart) else "Y (optional)"
y_opts = ["—"] + cols
y_default = 0 if not needs_y(chart) else (1 if len(cols) > 1 else 0)
y = st.sidebar.selectbox(y_label, y_opts, index=y_default, key=f"y_{chart}_{lib}")
y = None if y == "—" else y

hue = st.sidebar.selectbox("Color/Hue (optional)", ["—"] + cols, index=0, key=f"hue_{chart}_{lib}")
hue = None if hue == "—" else hue

# ---------- validation ----------
if needs_y(chart) and (not x or not y):
    st.warning(f"'{chart}' requires both X and Y.")
    st.stop()

# ---------- plotting ----------
st.subheader("Result")

if lib == "Plotly":
    fig = None
    if chart == "scatter":
        fig = px.scatter(df, x=x, y=y, color=hue)
    elif chart == "line":
        fig = px.line(df.sort_values(x), x=x, y=y, color=hue)
    elif chart == "bar (aggregate)":
        if not is_numeric(df[y]):
            st.error("Y must be numeric for aggregated bar.")
            st.stop()
        grouped = getattr(df.groupby(x)[y], agg)().reset_index()
        fig = px.bar(grouped, x=x, y=y)
    elif chart == "histogram":
        fig = px.histogram(df, x=x, nbins=bins)
    elif chart == "box":
        fig = px.box(df, x=x, y=y, color=hue)
    elif chart == "correlation heatmap":
        num = df.select_dtypes("number")
        if num.shape[1] >= 2:
            fig = px.imshow(num.corr(), origin="lower", color_continuous_scale="Viridis")
        else:
            st.info("Need at least two numeric columns.")
    elif chart == "pie":
        # counts or weighted sum
        if y and is_numeric(df[y]):
            data = df.groupby(x)[y].sum().reset_index()
            fig = px.pie(data, names=x, values=y)
        else:
            counts = df[x].value_counts().reset_index()
            counts.columns = [x, "count"]
            fig = px.pie(counts, names=x, values="count")
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

else:
    # Seaborn / Matplotlib
    sns.set_theme()
    fig, ax = plt.subplots(figsize=(8, 5))

    if chart == "scatter":
        if lib == "Seaborn":
            sns.scatterplot(df, x=x, y=y, hue=hue, ax=ax)
        else:
            if hue and hue in df.columns:
                for k, g in df.groupby(hue):
                    ax.scatter(g[x], g[y], label=str(k))
                ax.legend()
            else:
                ax.scatter(df[x], df[y])
        ax.set_xlabel(x); ax.set_ylabel(y)

    elif chart == "line":
        if lib == "Seaborn":
            sns.lineplot(df.sort_values(x), x=x, y=y, hue=hue, ax=ax)
        else:
            ax.plot(df.sort_values(x)[x], df.sort_values(x)[y])
        ax.set_xlabel(x); ax.set_ylabel(y)

    elif chart == "bar (aggregate)":
        if not is_numeric(df[y]):
            st.error("Y must be numeric for aggregated bar.")
            st.stop()
        grouped = getattr(df.groupby(x)[y], agg)().reset_index()
        if lib == "Seaborn":
            sns.barplot(grouped, x=x, y=y, ax=ax)
        else:
            ax.bar(grouped[x], grouped[y])
            ax.set_xticklabels(grouped[x], rotation=45, ha="right")
        ax.set_ylabel(f"{agg}({y})")

    elif chart == "histogram":
        if lib == "Seaborn":
            sns.histplot(df, x=x, bins=bins, ax=ax)
        else:
            ax.hist(df[x].dropna(), bins=bins)
        ax.set_xlabel(x); ax.set_ylabel("count")

    elif chart == "box":
        if lib == "Seaborn":
            sns.boxplot(df, x=x, y=y, hue=hue, ax=ax)
        else:
            df.boxplot(column=y, by=x, ax=ax, rot=45)
            fig.suptitle("")
        ax.set_ylabel(y)

    elif chart == "correlation heatmap":
        num = df.select_dtypes("number")
        if num.shape[1] >= 2:
            if lib == "Seaborn":
                sns.heatmap(num.corr(), cmap="viridis", ax=ax)
            else:
                im = ax.imshow(num.corr(), aspect="auto")
                fig.colorbar(im, ax=ax)
                ax.set_xticks(range(len(num.columns))); ax.set_xticklabels(num.columns, rotation=45, ha="right")
                ax.set_yticks(range(len(num.columns))); ax.set_yticklabels(num.columns)
        else:
            st.info("Need at least two numeric columns.")

    elif chart == "pie":
        if y and is_numeric(df[y]):
            data = df.groupby(x)[y].sum()
            ax.pie(data.values, labels=data.index, autopct="%1.1f%%")
            ax.set_title(f"{y} by {x}")
        else:
            counts = df[x].value_counts()
            ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%")
            ax.set_title(f"Distribution of {x}")

    st.pyplot(fig, use_container_width=True)
