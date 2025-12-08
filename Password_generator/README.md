# 🔐 Google‑Style Password Generator (Python + Tkinter)

A modern, secure **Password Generator** with a clean Google‑like UI.  
It uses Python’s `secrets` for cryptographically‑secure randomness, shows a live strength meter, and offers smart options (avoid ambiguous characters, must include each type, start with letter, etc.).

![Banner](banner.svg)

---

## 🚀 Features

- Secure randomness via **`secrets`** (no `random`)
- Length slider (8–64)
- Choose: lowercase, uppercase, digits, symbols
- Options: avoid ambiguous, include one of each, start with letter
- Live strength meter with entropy (bits)
- Show/Hide password, **Copy** button, **Regenerate**
- Keyboard: **Enter** = generate, **Ctrl+C** = copy
- Works with plain Tkinter; auto‑uses `ttkbootstrap` if installed

---

## 📦 Requirements

- Python **3.7+**
- Optional better theme:
  ```bash
  pip install ttkbootstrap
  ```

---

## ▶️ Run

Save the script as `password_gui.py` (from this repo) and run:

```bash
python password_gui.py
```

---

## 📁 Project Structure

```
📦 Password-Generator
 ┣ 📜 password_gui.py
 ┣ 📜 README.md
 ┗ 🖼  banner.svg
```

---

## 🧠 Security & Entropy

- Secure shuffle and character picking with `secrets`
- Entropy ≈ `length * log2(pool_size)`
- Strength verdicts: Very weak → Weak → Good → Strong → Excellent

---

## 💻 Build a Windows EXE (no console)

1) Install PyInstaller:
```bash
pip install pyinstaller
```

2) Build:
```bash
pyinstaller --onefile --noconsole --name PasswordGenerator --icon=NONE password_gui.py
```
Output EXE will be in `dist/PasswordGenerator.exe`.

> Tip: add `--add-data "banner.svg;."` if you want to ship the banner alongside the app.

---

## 📱 Android Build Options

### Option A — **Kivy/KivyMD + Buildozer** (recommended for rich mobile UI)
- Port logic to a small Kivy app (UI in KV language)
- Build on Linux using Buildozer:
  ```bash
  pip install kivy buildozer
  buildozer init           # edit buildozer.spec (package name, permissions, etc.)
  buildozer -v android debug
  ```

### Option B — **BeeWare (Toga)**
- Cross‑platform native widgets with Python:
  ```bash
  pip install briefcase
  briefcase new            # pick Toga + Android
  briefcase dev
  briefcase create android
  briefcase build android
  briefcase run android
  ```
Choose A if you want material‑style mobile UI; choose B for native widgets.

---

## ✨ Chrome‑Popup Style (Web‑like UI)

If you want a **Chrome‑extension‑like popup** look, you have two easy paths:

**1) Tkinter + ttkbootstrap**
- Use `darkly` or `cosmo` theme for flat, web‑like styling.
- Keep the current script; it will auto‑use `ttkbootstrap` if installed.

**2) PyWebview (HTML/CSS inside a desktop window)**
```bash
pip install pywebview
```
Create an `index.html` with your favorite CSS framework (e.g., Tailwind/Material). Then:

```python
import webview
webview.create_window('Password Generator', 'index.html', width=420, height=560, resizable=False)
webview.start()
```

This yields a crisp, Chrome‑popup feel while keeping Python logic.

---

## 🧪 Example Passwords

```
A7g$Pm2v@K9!zDf
hxQf79!RkW2@Uh
Tn4@pM7*Yg9$Bc
```

---

## 🗺 Roadmap Ideas

- Export N passwords at once
- History panel & clipboard audit
- Theme toggle (Light/Dark/System)
- QR code export
- Settings persistence

---

## ⭐ Support

If this helped you, please **star** the repo!  
Have a feature request? Open an issue and I’ll jump on it.

