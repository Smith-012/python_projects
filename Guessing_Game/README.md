# 🎯 Guessing Game — GUI + Web (Dark/Light Toggle)

A number guessing game where the app picks a random number between **1 and 100** and the player keeps guessing with hints (**Too high / Too low**) until correct. Includes:
- A **Tkinter desktop GUI**
- A **Flask web app** with a **Dark / Light mode toggle** (persisted via `localStorage`).

---

## ✨ Features
- Random number range: 1–100
- Hints: *Too high* / *Too low*
- Attempt counter
- Input validation
- **Web:** theme toggle 🌙/☀️ (remembered across visits)

---

## 🖥️ Desktop GUI (Tkinter)
Run:
```bash
python guessing_game_gui.py
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
- Click the **🌙/☀️** button in the header to switch themes.
- The choice is saved in your browser and applied automatically next time.

---

## 📁 Suggested Project Structure
```
guessing-game/
│── guessing_game_gui.py
│── app.py
│── templates/
│     └── index.html
│── static/
│     └── style.css
└── README.md
```

---

## 🧠 Game Logic (shared idea)
```python
import random

secret = random.randint(1, 100)
attempts = 0
# compare user's guess with secret and return hints until equal
```

---

## 📜 License
Open-source. Use freely.
