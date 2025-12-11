# Expense Report Automation (GUI + Web App)

This project provides two complete applications for automating expense report creation from **CSV or Excel bank statements**:

* **Tkinter GUI Application** – Desktop-based, user-friendly file-browser interface.
* **Streamlit Web Application** – Browser-based, supports file uploads and instant downloads.

Both apps generate:

* `transactions_clean.csv` – cleaned combined dataset
* `expense_report.xlsx` – multi-sheet report (transactions, category summary, income vs spend)
* `category_spend.png` – chart for latest month

All outputs are saved inside the `report_out/` folder.

---

## 📁 Project Directory Structure

Your final project directory looks like this:

```
Task-1/
│
├── expense_report_gui.py        # Desktop GUI App (Tkinter)
├── expense_report_web.py        # Web App (Streamlit)
├── bank_statement_jan.csv       # Sample File 1
├── bank_statement_feb.csv       # Sample File 2
│
├── report_out/                  # Generated Output Folder
│   ├── category_spend.png
│   ├── expense_report.xlsx
│   └── transactions_clean.csv
│
└── README.md                    # Project Documentation
```

---

## 📌 Features (Both GUI & Web)

### ✔ Accepts CSV and Excel files

* Supports multiple files at once.
* Automatically detects columns like Date, Description, Amount.

### ✔ Auto-categorization

Based on editable keyword mapping:

* Groceries, Dining, Utilities, Rent, Shopping, etc.
* Income handled automatically.

### ✔ Generates professional output

* Clean merged CSV
* Excel report with 3 sheets:

  * `Transactions`
  * `CategoryByMonth`
  * `Income_vs_Spend`
* Latest-month bar chart

### ✔ Saves all results to `report_out/`

* Files are overwritten on every run.

---

## 🖥 GUI Application (Tkinter)

### Run

```
python expense_report_gui.py
```

### Features

* Browse and select files from local system
* Choose output folder
* Edit categories
* Background threading (UI never freezes)
* Shows success dialog with file paths

---

## 🌐 Web Application (Streamlit)

### Install dependencies

```
pip install streamlit pandas matplotlib openpyxl
```

### Run the web app

```
streamlit run expense_report_web.py
```

### Features

* Upload multiple CSV/Excel files
* Live preview of table
* Category editor (JSON)
* Download buttons for:

  * Cleaned CSV
  * Excel report
  * Chart PNG
* Saves the same files inside `report_out/`

---

## 📄 Sample Input Files

Two example CSV files are included:

* `bank_statement_jan.csv`
* `bank_statement_feb.csv`

These allow you to test the flow end-to-end.

---

## 📂 Output Files (Generated)

After running either GUI or Web App, the following files appear inside `report_out/`:

### **1. transactions_clean.csv**

Merged + cleaned version of all inputs.

### **2. expense_report.xlsx**

Includes:

* Transactions Sheet
* CategoryByMonth Pivot Sheet
* Income_vs_Spend Summary Sheet

### **3. category_spend.png**

A bar chart showing expenses per category for the latest month.

---

## ⭐ Recommended Workflow

1. Place your CSV/Excel files inside the project folder.
2. Run either the GUI app or Web App.
3. Review and download outputs.
4. All results will be saved inside `report_out/`.

---

## 🤝 Support / Customization

You can extend this project with:

* PDF export
* Dashboard with filters
* Database integration
* Multi-month combined charts
* ZIP download bundle

Ask anytime if you'd like new features added!

---

## 🎉 You're all set!

Use either the GUI or Web app to automate your monthly financial reporting with ease.
