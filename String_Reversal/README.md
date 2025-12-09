# 🔁 String Reversal – Python (GUI + Web)

A simple project demonstrating string reversal using:
- A **Tkinter GUI**
- A **Flask Web App**
- A standalone Python function

## ✨ Features
- Reverse any text (works with emojis)
- Live update in GUI and Web version
- User‑friendly UI

## 🖥️ Tkinter GUI
Run:
```bash
python string_reversal_gui.py
```

## 🌐 Flask Web App
Install & run:
```bash
pip install flask
python app.py
```

Visit:
```
http://127.0.0.1:5000/
```

## 📁 Project Structure
```
project/
│── string_reversal_gui.py
│── app.py
│── templates/index.html
│── static/style.css
└── README.md
```

## 🧠 Core Logic
```python
def reverse_string(s):
    return s[::-1]
```
