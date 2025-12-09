# viz_tool.py
# GUI Data Visualization Tool supporting Matplotlib, Seaborn, Plotly
# Optional: Altair & Bokeh (if installed) for HTML output

import os
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import pandas as pd

# Try optional libs (don’t fail if missing)
try:
    import altair as alt  # optional
    ALT_OK = True
except Exception:
    ALT_OK = False

try:
    from bokeh.plotting import figure, output_file, save  # optional
    from bokeh.io import show as bokeh_show
    BOKEH_OK = True
except Exception:
    BOKEH_OK = False

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


SUPPORTED_LIBS = ["Matplotlib", "Seaborn", "Plotly"] + (["Altair"] if ALT_OK else []) + (["Bokeh"] if BOKEH_OK else [])

CHARTS = [
    "scatter",
    "line",
    "bar (aggregate)",
    "histogram",
    "box",
    "pie",
    "correlation heatmap",
]

AGGS = ["count", "sum", "mean", "median", "min", "max"]


def is_numeric(series: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(series)


class VizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Visualization Tool — Matplotlib • Seaborn • Plotly")
        self.df = None
        self.filepath = None

        self._build_ui()

    # ---------------- UI ----------------
    def _build_ui(self):
        pad = 10
        frm = ttk.Frame(self.root, padding=pad)
        frm.grid(sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # File row
        self.path_var = tk.StringVar()
        ttk.Label(frm, text="Dataset (CSV):").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.path_var, width=60).grid(row=0, column=1, sticky="we", padx=(5, 5))
        ttk.Button(frm, text="Browse…", command=self.browse).grid(row=0, column=2, sticky="e")
        frm.columnconfigure(1, weight=1)

        # Library + chart row
        self.lib_var = tk.StringVar(value=SUPPORTED_LIBS[0])
        self.chart_var = tk.StringVar(value=CHARTS[0])
        ttk.Label(frm, text="Library:").grid(row=1, column=0, sticky="w", pady=(8,0))
        ttk.Combobox(frm, textvariable=self.lib_var, values=SUPPORTED_LIBS, state="readonly", width=20)\
            .grid(row=1, column=1, sticky="w", padx=(5, 5), pady=(8,0))
        ttk.Label(frm, text="Chart:").grid(row=1, column=2, sticky="w", pady=(8,0))
        ttk.Combobox(frm, textvariable=self.chart_var, values=CHARTS, state="readonly", width=24)\
            .grid(row=1, column=3, sticky="w", pady=(8,0))

        # Column selectors
        self.x_var = tk.StringVar()
        self.y_var = tk.StringVar()
        self.hue_var = tk.StringVar()
        self.agg_var = tk.StringVar(value=AGGS[0])
        self.bins_var = tk.StringVar(value="30")

        row = 2
        ttk.Label(frm, text="X:").grid(row=row, column=0, sticky="w", pady=(8,0))
        self.x_combo = ttk.Combobox(frm, textvariable=self.x_var, values=[], state="readonly", width=24)
        self.x_combo.grid(row=row, column=1, sticky="w", padx=(5, 5), pady=(8,0))

        ttk.Label(frm, text="Y:").grid(row=row, column=2, sticky="w", pady=(8,0))
        self.y_combo = ttk.Combobox(frm, textvariable=self.y_var, values=[], state="readonly", width=24)
        self.y_combo.grid(row=row, column=3, sticky="w", pady=(8,0))

        row += 1
        ttk.Label(frm, text="Color/Hue:").grid(row=row, column=0, sticky="w")
        self.hue_combo = ttk.Combobox(frm, textvariable=self.hue_var, values=[], state="readonly", width=24)
        self.hue_combo.grid(row=row, column=1, sticky="w", padx=(5, 5))

        ttk.Label(frm, text="Aggregation (bar):").grid(row=row, column=2, sticky="w")
        ttk.Combobox(frm, textvariable=self.agg_var, values=AGGS, state="readonly", width=16)\
            .grid(row=row, column=3, sticky="w")

        row += 1
        ttk.Label(frm, text="Bins (hist):").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.bins_var, width=10).grid(row=row, column=1, sticky="w", padx=(5,0))

        # Buttons
        row += 1
        btns = ttk.Frame(frm)
        btns.grid(row=row, column=0, columnspan=4, pady=(12,0), sticky="we")
        ttk.Button(btns, text="Generate Chart", command=self.generate).pack(side="left")
        ttk.Button(btns, text="Save Figure…", command=self.save_figure).pack(side="left", padx=6)

        # Help
        row += 1
        help_text = (
            "Tips:\n"
            "- For pie/hist, set X only (Y optional).\n"
            "- Bar (aggregate) groups by X and aggregates Y.\n"
            "- Correlation heatmap ignores selections and uses numeric columns."
        )
        ttk.Label(frm, text=help_text, foreground="#555").grid(row=row, column=0, columnspan=4, sticky="w", pady=(8,0))

    # ------------- Data loading -------------
    def browse(self):
        path = filedialog.askopenfilename(
            title="Select CSV",
            filetypes=[("CSV files","*.csv"), ("All files","*.*")]
        )
        if not path:
            return
        self.path_var.set(path)
        try:
            self.df = pd.read_csv(path)
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not read CSV:\n{e}")
            return

        cols = list(self.df.columns)
        for cb in (self.x_combo, self.y_combo, self.hue_combo):
            cb["values"] = cols
            cb.set("")

        # Preselect sensible defaults
        if cols:
            self.x_var.set(cols[0])
        if len(cols) > 1:
            # pick first numeric for Y if possible
            num_cols = [c for c in cols if is_numeric(self.df[c])]
            self.y_var.set(num_cols[0] if num_cols else cols[1])

    # ------------- Chart generation -------------
    def generate(self):
        if self.df is None:
            messagebox.showwarning("No Data", "Please load a CSV first.")
            return

        lib = self.lib_var.get()
        chart = self.chart_var.get()
        x = self.x_var.get().strip()
        y = self.y_var.get().strip()
        hue = self.hue_var.get().strip() or None
        bins = None
        try:
            bins = int(self.bins_var.get())
        except Exception:
            bins = 30

        # Validate simple requirements
        if chart in ["scatter", "line", "bar (aggregate)", "box"] and (not x or not y):
            messagebox.showwarning("Need Columns", f"Chart '{chart}' requires both X and Y.")
            return
        if chart in ["histogram", "pie"] and not x:
            messagebox.showwarning("Need Columns", f"Chart '{chart}' requires X.")
            return

        try:
            if lib == "Matplotlib":
                self._plot_matplotlib(chart, x, y, hue, bins)
            elif lib == "Seaborn":
                self._plot_seaborn(chart, x, y, hue, bins)
            elif lib == "Plotly":
                self._plot_plotly(chart, x, y, hue, bins)
            elif lib == "Altair" and ALT_OK:
                self._plot_altair(chart, x, y, hue, bins)
            elif lib == "Bokeh" and BOKEH_OK:
                self._plot_bokeh(chart, x, y, hue, bins)
            else:
                messagebox.showerror("Library Missing", f"{lib} is not available.")
        except Exception as e:
            messagebox.showerror("Plot Error", str(e))

    # -------- Matplotlib --------
    def _plot_matplotlib(self, chart, x, y, hue, bins):
        plt.figure(figsize=(8, 5))
        df = self.df

        if chart == "scatter":
            if hue and hue in df.columns:
                for key, g in df.groupby(hue):
                    plt.scatter(g[x], g[y], label=str(key))
                plt.legend()
            else:
                plt.scatter(df[x], df[y])
            plt.xlabel(x); plt.ylabel(y)

        elif chart == "line":
            if hue and hue in df.columns:
                for key, g in df.groupby(hue):
                    g_sorted = g.sort_values(x)
                    plt.plot(g_sorted[x], g_sorted[y], label=str(key))
                plt.legend()
            else:
                df_sorted = df.sort_values(x)
                plt.plot(df_sorted[x], df_sorted[y])
            plt.xlabel(x); plt.ylabel(y)

        elif chart == "bar (aggregate)":
            if not is_numeric(df[y]):
                raise ValueError("Y must be numeric for aggregated bar.")
            agg = self.agg_var.get()
            grouped = getattr(df.groupby(x)[y], agg)().reset_index()
            plt.bar(grouped[x], grouped[y])
            plt.xticks(rotation=45, ha="right")
            plt.ylabel(f"{agg}({y})")

        elif chart == "histogram":
            plt.hist(df[x].dropna(), bins=bins)
            plt.xlabel(x); plt.ylabel("count")

        elif chart == "box":
            if hue and hue in df.columns:
                df.boxplot(column=y, by=[x, hue], rot=45)
                plt.suptitle("")
            else:
                df.boxplot(column=y, by=x, rot=45)
                plt.suptitle("")
            plt.ylabel(y)

        elif chart == "correlation heatmap":
            corr = df.select_dtypes("number").corr()
            plt.imshow(corr, aspect="auto")
            plt.xticks(range(len(corr.columns)), corr.columns, rotation=45, ha="right")
            plt.yticks(range(len(corr.columns)), corr.columns)
            plt.colorbar(label="corr")

        elif chart == "pie":
            counts = df[x].value_counts().reset_index()
            counts.columns = [x, "count"]
            plt.pie(counts["count"], labels=counts[x], autopct="%1.1f%%")
            plt.title(f"Distribution of {x}")

        plt.tight_layout()
        plt.show()

    # -------- Seaborn --------
    def _plot_seaborn(self, chart, x, y, hue, bins):
        sns.set_theme()
        df = self.df

        if chart == "scatter":
            sns.scatterplot(df, x=x, y=y, hue=hue)
        elif chart == "line":
            sns.lineplot(df, x=x, y=y, hue=hue)
        elif chart == "bar (aggregate)":
            if not is_numeric(df[y]):
                raise ValueError("Y must be numeric for aggregated bar.")
            agg = self.agg_var.get()
            grouped = getattr(df.groupby(x)[y], agg)().reset_index()
            sns.barplot(grouped, x=x, y=y)
            plt.ylabel(f"{agg}({y})")
            plt.xticks(rotation=45, ha="right")
        elif chart == "histogram":
            sns.histplot(df, x=x, bins=bins)
        elif chart == "box":
            sns.boxplot(df, x=x, y=y, hue=hue)
            plt.xticks(rotation=45, ha="right")
        elif chart == "correlation heatmap":
            corr = df.select_dtypes("number").corr()
            sns.heatmap(corr, annot=False, cmap="viridis")
        elif chart == "pie":
            counts = df[x].value_counts().reset_index()
            counts.columns = [x, "count"]
            plt.pie(counts["count"], labels=counts[x], autopct="%1.1f%%")
            plt.title(f"Distribution of {x}")

        plt.tight_layout()
        plt.show()

    # -------- Plotly --------
    def _plot_plotly(self, chart, x, y, hue, bins):
        df = self.df
        fig = None

        if chart == "scatter":
            fig = px.scatter(df, x=x, y=y, color=hue)
        elif chart == "line":
            fig = px.line(df.sort_values(x), x=x, y=y, color=hue)
        elif chart == "bar (aggregate)":
            if not is_numeric(df[y]):
                raise ValueError("Y must be numeric for aggregated bar.")
            agg = self.agg_var.get()
            grouped = getattr(df.groupby(x)[y], agg)().reset_index()
            fig = px.bar(grouped, x=x, y=y)
        elif chart == "histogram":
            fig = px.histogram(df, x=x, nbins=bins)
        elif chart == "box":
            fig = px.box(df, x=x, y=y, color=hue)
        elif chart == "correlation heatmap":
            corr = df.select_dtypes("number").corr()
            fig = px.imshow(corr, text_auto=False, aspect="auto", origin="lower", color_continuous_scale="Viridis")
        elif chart == "pie":
            counts = df[x].value_counts().reset_index()
            counts.columns = [x, "count"]
            fig = px.pie(counts, values="count", names=x, title=f"Distribution of {x}")

        if fig is None:
            raise ValueError("Unsupported Plotly chart.")

        fig.update_layout(template="plotly_white")
        fig.show()

    # -------- Altair (optional) --------
    def _plot_altair(self, chart, x, y, hue, bins):
        if not ALT_OK:
            raise RuntimeError("Altair not installed.")
        df = self.df
        chart_obj = None

        if chart == "scatter":
            chart_obj = alt.Chart(df).mark_point().encode(x=x, y=y, color=hue)
        elif chart == "line":
            chart_obj = alt.Chart(df).mark_line().encode(x=x, y=y, color=hue)
        elif chart == "bar (aggregate)":
            agg = self.agg_var.get()
            chart_obj = alt.Chart(df).mark_bar().encode(
                x=x, y=alt.Y(f"{agg}({y})"), color=hue
            )
        elif chart == "histogram":
            chart_obj = alt.Chart(df).mark_bar().encode(alt.X(x, bin=alt.Bin(maxbins=bins)), y="count()")
        elif chart == "box":
            chart_obj = alt.Chart(df).mark_boxplot().encode(x=x, y=y, color=hue)
        elif chart == "correlation heatmap":
            corr = df.select_dtypes("number").corr().stack().reset_index()
            corr.columns = ["x", "y", "corr"]
            chart_obj = alt.Chart(corr).mark_rect().encode(x="x:N", y="y:N", color="corr:Q")
        elif chart == "pie":
            counts = df[x].value_counts().reset_index()
            counts.columns = [x, "count"]
            chart_obj = alt.Chart(counts).mark_arc().encode(theta="count", color=x)

        out = "altair_chart.html"
        chart_obj.save(out)
        webbrowser.open(os.path.abspath(out))

    # -------- Bokeh (optional) --------
    def _plot_bokeh(self, chart, x, y, hue, bins):
        if not BOKEH_OK:
            raise RuntimeError("Bokeh not installed.")
        df = self.df.copy()
        out = "bokeh_chart.html"
        output_file(out)

        p = None
        if chart == "scatter":
            p = figure(x_axis_label=x, y_axis_label=y)
            p.circle(df[x], df[y], size=6)
        elif chart == "line":
            df = df.sort_values(x)
            p = figure(x_axis_label=x, y_axis_label=y)
            p.line(df[x], df[y])
        elif chart == "bar (aggregate)":
            from bokeh.transform import dodge
            agg = self.agg_var.get()
            grouped = getattr(df.groupby(x)[y], agg)().reset_index()
            p = figure(x_range=grouped[x].astype(str).tolist())
            p.vbar(x=grouped[x].astype(str), top=grouped[y], width=0.9)
        elif chart == "histogram":
            import numpy as np
            hist, edges = np.histogram(df[x].dropna(), bins=bins)
            p = figure()
            p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:])
        elif chart == "box":
            # Simple fallback via Matplotlib shown if complex grouping needed
            raise RuntimeError("Bokeh box example omitted; use Matplotlib/Seaborn/Plotly for box.")
        elif chart == "correlation heatmap":
            raise RuntimeError("Use Plotly/Seaborn/Matplotlib for correlation heatmap.")
        elif chart == "pie":
            raise RuntimeError("Use Plotly/Matplotlib for pie.")

        if p is None:
            raise RuntimeError("Unsupported Bokeh chart.")
        save(p)
        bokeh_show(p)

    # ------------- Save figure (Matplotlib only) -------------
    def save_figure(self):
        # Saves current matplotlib figure to file
        if plt.get_fignums():
            ftypes = [("PNG", "*.png"), ("PDF", "*.pdf"), ("SVG", "*.svg")]
            path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=ftypes)
            if path:
                try:
                    plt.gcf().savefig(path, bbox_inches="tight")
                    messagebox.showinfo("Saved", f"Saved figure to:\n{path}")
                except Exception as e:
                    messagebox.showerror("Save Error", str(e))
        else:
            messagebox.showinfo("No Figure", "Generate a Matplotlib/Seaborn plot first to save.")


if __name__ == "__main__":
    root = tk.Tk()
    app = VizApp(root)
    root.mainloop()
