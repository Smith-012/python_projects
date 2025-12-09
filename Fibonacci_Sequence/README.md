# 🧮 Fibonacci Sequence — GUI + Web (Range-limited + Jinja fix)

Generate the Fibonacci sequence up to **N terms** with:
- A **Tkinter desktop GUI**
- A **Flask web app**

## ✅ What’s new
- **Safe range limit:** Only allows `N` between **1 and 500**.
- **No Jinja errors:** Output string is prepared in Python (avoids `map` in Jinja).

## ✨ Features
- Compute Fibonacci numbers safely  
- Range-limited to prevent freezing  
- GUI supports copy button  
- Web UI clean and responsive  

## 🖥️ Desktop GUI
Run:
```bash
python fibonacci_gui.py
```

## 🌐 Web App (Flask)
Install & run:
```bash
pip install flask
python app.py
```

Open:
```
http://127.0.0.1:5000/
```

## 🧠 Core Logic
```python
def fibonacci(n: int):
    a, b = 0, 1
    seq = []
    for _ in range(n):
        seq.append(a)
        a, b = b, a + b
    return seq
```

## 📁 Structure
```
fibonacci/
│── fibonacci_gui.py
│── app.py
│── templates/
│     └── index.html
│── static/
│     └── style.css
└── README.md
```

## 📜 License
Open-source. Use freely.
