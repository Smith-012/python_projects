# 🌡️ Temperature Converter (Celsius ↔ Fahrenheit)

A small Python project that converts temperatures between **Celsius** and **Fahrenheit**.  
Includes a **Tkinter desktop GUI** and a **Flask web app**.

---

## ✨ Features
- Convert °C ↔ °F accurately
- Clean Tkinter GUI with unit selector
- Simple Flask web UI (works on phone/desktop)
- Input validation and friendly messages

---

## 🖥️ Desktop GUI (Tkinter)

### Run
```bash
python temperature_gui.py
```

### What it does
- Choose the input unit (Celsius or Fahrenheit)
- Enter a temperature
- Click **Convert** to see the result with two-decimal precision

---

## 🌐 Web App (Flask)

### Install & Run
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
temperature-converter/
│── temperature_gui.py
│── app.py
│── templates/
│     └── index.html
│── static/
│     └── style.css
└── README.md
```

---

## 🧠 Conversion Formulas
- **C → F:** \( F = (C \times \tfrac{9}{5}) + 32 \)
- **F → C:** \( C = (F - 32) \times \tfrac{5}{9} \)

---

## 🧪 Quick Examples
- 0°C → 32°F  
- 100°C → 212°F  
- 32°F → 0°C  
- 212°F → 100°C

---

## 📜 License
Open-source. Use freely.
