# 🔁 Palindrome Checker — Python (GUI + Web)

A small project to check whether a given string is a **palindrome** (reads the same backward as forward).  
Includes a **Tkinter desktop GUI** and a **Flask web app**.

---

## ✨ Features
- Checks words *and* phrases
- Option to ignore case, spaces, and punctuation
- Live validation in GUI and Web
- Clean, minimal UI

---

## 🧠 Core Logic
```python
def is_palindrome(text: str, loose: bool = True) -> bool:
    if loose:
        cleaned = "".join(ch.lower() for ch in text if ch.isalnum())
    else:
        cleaned = text.lower()
    return cleaned == cleaned[::-1]
```

---

## 🖥️ Desktop GUI (Tkinter)

**Run**
```bash
python palindrome_gui.py
```

**What it does**
- Type text and see instant result
- Toggle “Ignore punctuation & spaces”

---

## 🌐 Web App (Flask)

**Install & run**
```bash
pip install flask
python app.py
```
Open your browser at:
```
http://127.0.0.1:5000/
```

---

## 📁 Suggested Project Structure
```
palindrome-checker/
│── palindrome_gui.py
│── app.py
│── templates/
│     └── index.html
│── static/
│     └── style.css
└── README.md
```

---

## 🧪 Examples
- `racecar` → palindrome
- `Madam` → palindrome (ignore-case)
- `Was it a car or a cat I saw?` → palindrome (ignore punctuation)
- `hello` → not a palindrome

---

## 📜 License
Open-source. Use freely.
