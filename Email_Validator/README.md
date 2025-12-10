# ✉️ Email Validator (Python) — GUI + Web

A small project to validate email addresses with two interfaces:
- **Tkinter Desktop GUI**
- **Flask Web App**

Validation rules include:
- exactly one `@`
- non-empty username
- domain contains a `.` (not at start or end)
- only common email characters (regex version)
- no spaces

---

## 🧠 Core Logic

### Simple checks
```python
def is_valid_email(email: str) -> bool:
    if " " in email: return False
    if email.count("@") != 1: return False
    user, domain = email.split("@")
    if not user: return False
    if "." not in domain: return False
    if domain.startswith(".") or domain.endswith("."): return False
    return True
```

### Regex (more accurate)
```python
import re
def is_valid_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None
```

---

## 🖥️ Desktop GUI (Tkinter)

**Run**
```bash
python email_gui.py
```

**What it does**
- Type an email and click **Validate** (or press Enter)
- Shows ✅ Valid or ❌ Invalid with reason

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
email-validator/
│── email_gui.py
│── app.py
│── templates/
│     └── index.html
│── static/
│     └── style.css
└── README.md
```

---

## 🧪 Quick Tests
```
valid:   alice@mail.com, dev.team+ci@company.co.uk
invalid: bob@@x.com, no-at.com, me@.com, me@host, space @bad.com
```

---
