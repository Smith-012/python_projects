# 🧮 Basic Calculator (Python) — GUI + Web (Dark/Light Toggle)

This project is a simple calculator supporting five operations: **+ − × ÷ %**.  
It includes:
- A **Tkinter desktop GUI**
- A **Flask web app** with a **Dark / Light mode toggle**

---

## ✨ Features
- Add, subtract, multiply, divide, modulus
- Division-by-zero protection
- Clean Tkinter UI
- Web UI with theme toggle (persists in browser via `localStorage`)

---

## 🖥️ Desktop GUI (Tkinter)

**Run**
```bash
python calculator_gui.py
```

**What it does**
- Enter two numbers
- Pick an operator
- Get the result instantly

---

## 🌐 Web App (Flask) — with Dark/Light toggle

**Install & Run**
```bash
pip install flask
python app.py
```
Open your browser at:
```
http://127.0.0.1:5000/
```

### Theme Toggle
- Click the **🌙/☀️** button to switch between dark and light modes
- Your choice is saved and applied automatically next time

---

## 📁 Suggested Project Structure
```
calculator/
│── calculator_gui.py
│── app.py
│── templates/
│     └── index.html
│── static/
│     ├── style.css
│     └── script.js   # (optional: or inline in HTML)
└── README.md
```

---

## 🧠 Operation Rules
- `+` addition
- `-` subtraction
- `*` multiplication
- `/` division (error if divide by zero)
- `%` modulus (error if divide by zero)

---

## 🧪 Quick Checks
- 5 + 3 = 8
- 8 / 2 = 4
- 7 % 2 = 1
- 9 / 0 → error message

---
