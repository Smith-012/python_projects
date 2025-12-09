# 🛡️ Password Strength Checker

A Python-based project that evaluates the strength of a password using both a **Desktop GUI (Tkinter)** and a **Web Application (Flask)**.  
The tool provides real-time feedback, color-coded strength bars, and suggestions for improving passwords.

## 🚀 Features
- Length check (≥ 8 characters)
- Uppercase, lowercase, digits, and special character checks
- Tkinter GUI with live strength bar
- Flask web app with AJAX-based live updates
- Color‑coded strength indicator

## 🖥️ Tkinter GUI
Run:
```bash
python password.py
```

## 🌍 Flask Web App
Install & run:
```bash
pip install flask
python app.py
```

Open:
```
http://127.0.0.1:5000/
```

## 📁 Project Structure
```
project/
│── password_gui.py
│── app.py
│── templates/index.html
│── static/style.css
└── README.md
```

## 🧠 Logic Summary
Score = 1 point each for:
- length ≥ 8
- uppercase letter
- lowercase letter
- digit
- special character

Strength levels: Very Weak → Very Strong
