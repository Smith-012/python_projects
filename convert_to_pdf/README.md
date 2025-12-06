
# 📄 Universal Office to PDF Converter (Flask + LibreOffice)

A fast and user‑friendly local web app that converts **multiple office formats to PDF** using drag & drop.

---

## 🚀 Supported Input Formats

| File Type | Supported |
|----------|------------|
| `.doc` | ✔ |
| `.docx` | ✔ |
| `.ppt` | ✔ |
| `.pptx` | ✔ |
| `.xls` | ✔ |
| `.xlsx` | ✔ |
| `.csv` | ✔ |
| `.txt` | ✔ |
| `.odt` | ✔ |
| `.ods` | ✔ |
| **Output** | PDF ✔ |

---

## 💡 Features

- Upload or drag‑and‑drop interface
- Automatically downloads converted PDF
- Works offline
- Opens in browser automatically
- Fast conversion using **LibreOffice**
- No file upload to cloud — fully local

---

## 🔧 Requirements

| Requirement | Notes |
|-------------|-------|
| Python 3.8+ | required |
| LibreOffice | must be installed (conversion engine) |
| Browser | opens automatically |
| pip dependencies | shown below |

---

## 📦 Installation

```bash
pip install flask werkzeug
```

> **docx2pdf is not required anymore. LibreOffice handles all formats.**

⚠ Install **LibreOffice** if not installed already:  
https://www.libreoffice.org/download/download-libreoffice/

Make sure `soffice` is available in PATH.  
If not, add the LibreOffice program folder to PATH manually.

---

## ▶ Run the Application

```bash
python app.py
```

After starting:
- The application **automatically opens in your browser**
- If not, open: `http://127.0.0.1:5000`

---

## 📁 Project Structure

```
project/
│ app.py
│ README.md
```

---

## ❗ Common Troubleshooting

| Issue | Solution |
|-------|----------|
| PDF not produced | Ensure LibreOffice is installed |
| `soffice` not found | Add LibreOffice folder to PATH |
| Browser opens twice | Debug mode must be disabled (`debug=False`) |
| Some formats rejected | Must be in the supported list above |

---

## 🔮 Future Upgrade Ideas

- Batch upload (convert multiple files at once)
- Zip download for multiple PDFs
- Dark/Light theme toggle
- Create `.exe` desktop version (PyInstaller)
- PDF preview before download

---

## 📝 License

Free to modify and distribute for personal and commercial use.

---
