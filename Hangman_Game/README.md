# 🎮 Hangman Game — Python (Tkinter) + Web (Flask + SweetAlert2)

This project contains **two fully featured versions** of the classic **Hangman** game:

- **Desktop Version** (Python Tkinter)
- **Web Browser Version** (Flask backend, HTML/CSS/JS frontend + SweetAlert2)

Both versions share the same game mechanics and modern UI style.

---

## 📌 Features (Both Versions)

### ✔ Runtime Word Generation (No Local Word List)
The game fetches a **real English word from the internet** using:

https://random-word-api.herokuapp.com/word?number=1

### ✔ 6 Lives + Animated SVG Hangman  
Each wrong guess draws a new piece of the hangman.

### ✔ Keyboard Support  
- On-screen buttons  
- Real keyboard input  

### ✔ Hint System  
- **3 hints**  
- Reveals random hidden letter  
- Uses SweetAlert2 toast  

### ✔ SweetAlert2  
Used for win/lose dialogs, error messages, confirmations.

### ✔ Exit Button (Web)  
Stops Flask server + closes active browser tab.

---

## 📁 Project Structure

```
Project/
│
├── hangman_gui.py
├── hangman_web.py
│
├── templates/
│   └── index.html
│
└── static/
    ├── style.css
    └── script.js
```

---

## 🖥️ Desktop Version (Tkinter)

### Run:

```
python hangman_gui.py
```

Features:
- Dark UI
- API-based words
- Hint system
- Canvas hangman drawing

---

## 🌐 Web Version (Flask)

### Install Flask:

```
pip install flask
```

### Run:

```
python hangman_web.py
```

Open:

```
http://127.0.0.1:5000/
```

Features:
- SweetAlert2 UI
- SVG hangman drawing
- API-generated word
- Exit button (shutdown server)

---

## 🧠 How It Works

1. New game fetches random word from online API  
2. Shows underscores for each letter  
3. Player guesses letters  
4. Wrong guesses draw body parts  
5. 6 total lives  
6. 3 hints  
7. SweetAlert2 handles win/lose  
8. Exit button stops server + closes tab  

---
