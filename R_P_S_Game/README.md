# Rock • Paper • Scissors — Full Project (GUI + Web App)

This repository contains **two versions** of the Rock–Paper–Scissors game:

### ✔ 1. Tkinter Desktop GUI App (`rps_gui.py`)  
### ✔ 2. Flask Web App (`rps_web.py`, `templates/`, `static/`)

Both versions share the same logic and provide a modern, smooth user experience.

---

## 📁 Project Structure

```
RPS_Project/
│  rps_gui.py
│  rps_web.py
│  README.md   ← documentation
│
├─ templates/
│    index.html
│
└─ static/
     style.css
     script.js
```

---

# 🖥 Desktop GUI (Tkinter Version)

### 📌 File: `rps_gui.py`

A modern Tkinter-based desktop GUI application featuring:

- Dark themed UI  
- Buttons with emojis  
- Player & computer choices  
- Scoreboard  
- Live round updates  
- Round history  
- Reset system  
- Keyboard shortcuts (R, P, S, Esc)  
- Smooth result animation  

### ▶ Run

```
python rps_gui.py
```

---

# 🌐 Web App (Flask Version)

### 📌 File: `rps_web.py`

This file contains:

- Flask server  
- API endpoint (`/api/play`)  
- Embedded game logic  
- HTML renderer for frontend  

### 📁 templates/index.html
The main web GUI layout with SweetAlert popups and game modal.

### 📁 static/style.css
Dark theme UI styling for the web app.

### 📁 static/script.js
Handles:

- Button clicks  
- Fetching results from `/api/play`  
- Updating UI  
- SweetAlert dialogs  
- Modal logic  
- Keyboard shortcuts  

---

# 🚀 Running the Web Application

Install Flask:

```
pip install flask
```

Run the server:

```
python rps_web.py
```

Visit the app in your browser:

```
http://127.0.0.1:5000
```

---

# ⭐ Features (Both Versions)

| Feature | GUI | Web |
|--------|-----|-----|
| Rock/Paper/Scissors choices | ✔ | ✔ |
| Emoji buttons | ✔ | ✔ |
| Scoreboard | ✔ | ✔ |
| Round tracking | ✔ | ✔ |
| Show All Round Results | ✔ | ✔ |
| Reset functionality | ✔ | ✔ |
| Rules popup | ✔ | ✔ |
| Keyboard shortcuts | ✔ | ✔ |
| SweetAlert2 popups | ❌ | ✔ |

---

# 📦 Ideal for GitHub

This project is designed to be:

- Beginner friendly  
- Easy to understand  
- Clean and modular  
- Ready for open-source publication  
- Useful for Python/Flask/Tkinter learners  

It includes both **desktop** and **web** versions for maximum flexibility.

---