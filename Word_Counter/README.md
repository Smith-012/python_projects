# 📄 Word Counter — GUI + Web (Dark/Light Toggle)

Counts the occurrences of each word in a text file and displays results **alphabetically**.  
Includes a **Tkinter desktop GUI** and a **Flask web app** with a **Dark/Light theme toggle** (saved in `localStorage`).

---

## ✨ Features
- Case-insensitive counting
- Strips punctuation
- Results sorted A→Z with counts
- **GUI:** file picker, results area
- **Web:** upload `.txt` file, theme toggle 🌙/☀️

---

## 🖥️ Desktop GUI (Tkinter)
Run:
```bash
python word_counter_gui.py
```

---

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

---

## 📁 Project Structure
```
word-counter/
│── word_counter_gui.py
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
import string
def count_words(text: str) -> dict[str, int]:
    text = text.lower().translate(str.maketrans("", "", string.punctuation))
    counts = {}
    for w in text.split():
        counts[w] = counts.get(w, 0) + 1
    return dict(sorted(counts.items()))
```

---

## 📜 License
Open-source. Use freely.
