# 📊 Data Visualization Tool — GUI & Web

Two ways to turn CSV data into beautiful charts:

- **Desktop GUI:** `viz_tool.py` (Tkinter + Matplotlib/Seaborn/Plotly)
- **Web App:** `app.py` (Streamlit + Plotly/Seaborn/Matplotlib)

Both support: **scatter, line, bar (aggregate), histogram, box, pie, correlation heatmap**.

---

## 🔧 Requirements

```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

Install shared dependencies:

```bash
pip install pandas matplotlib seaborn plotly
```

For the web app:

```bash
pip install streamlit
```

---

## 📁 Files

- `viz_tool.py` — Desktop GUI  
- `app.py` — Web App  
- `sample_dataset.csv` — Example CSV  

---

## 🧪 Sample CSV

```csv
Name,Age,Salary,Department,Experience
Alice,25,50000,IT,2
Bob,30,60000,HR,5
Charlie,35,70000,Finance,8
Diana,28,65000,IT,3
Ethan,40,80000,HR,10
```

---

## 🖥️ Desktop GUI (`viz_tool.py`)

### Run
```bash
python viz_tool.py
```

### Usage
- Load CSV  
- Choose Library  
- Choose Chart  
- Select X/Y/Hue  
- Generate chart  
- Save figure (Matplotlib/Seaborn)

---

## 🌐 Web App (`app.py`)

### Run
```bash
streamlit run app.py
```

### Usage
- Download or upload CSV  
- Pick library and chart  
- Select X/Y  
- Interactive charts  
- Pie, Histogram, Heatmap supported  

---

## 🛠️ Chart Input Rules

| Chart Type | Needs X | Needs Y | Notes |
|------------|--------|---------|-------|
| Scatter | ✔ | ✔ | Y must be numeric |
| Line | ✔ | ✔ | X should be sortable |
| Bar (aggregate) | ✔ | ✔ | Y must be numeric |
| Histogram | ✔ | ✖ | Only X required |
| Box | ✔ | ✔ | - |
| Pie | ✔ | (optional) | Y = weighted pie |
| Correlation Heatmap | ✖ | ✖ | Needs ≥ 2 numeric columns |

---

## 🙌 Credits
Made using **Pandas**, **Matplotlib**, **Seaborn**, **Plotly**, **Streamlit**.
