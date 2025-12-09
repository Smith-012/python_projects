# 🎯 Number Guesser — GUI + Web (Dark/Light Toggle)

A number guessing game where the program chooses a random number **within a user-specified range** and you guess it with feedback (*Too high / Too low*). Includes a **Tkinter desktop GUI** and a **Flask web app** with a **Dark/Light theme toggle** (stored in `localStorage`).

---

## ✨ Features
- Choose custom range (min & max)
- Hints: *Too high* / *Too low*
- Attempt counter
- Input validation
- **Web:** dark/light toggle 🌙/☀️ that persists across visits

---

## 🖥️ Desktop GUI (Tkinter)
Run:
```bash
python number_guesser_gui.py
```

---

## 🌐 Web App (Flask) — with Dark/Light toggle
Install & run:
```bash
pip install flask
python app.py
```
Open:
```
http://127.0.0.1:5000/
```

### Theme Toggle
Click the **🌙/☀️** button in the header to switch themes. Your choice is saved and applied automatically next time.

---

## 📁 Suggested Project Structure
```
number-guesser/
│── number_guesser_gui.py
│── app.py
│── templates/
│     └── index.html
│── static/
│     └── style.css
└── README.md
```

---

## 🧠 Core Logic
```python
import random
secret = random.randint(low, high)
# compare user's guess with secret and return hints until equal
```

---

## 📜 License
Open-source. Use freely.
