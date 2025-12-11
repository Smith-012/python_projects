# Task Automation Toolbox

Two apps to streamline common chores:
- **Desktop GUI** (Tkinter) — move images, extract emails, scrape webpage titles.
- **Web App** (Flask) — same tools in the browser, with SweetAlert toasts and selection UI.

---

## ✨ Features

### 1) Move Images
- **Include subfolders** toggle:
  - ✅ ON → scans **recursively**.
  - ✅ OFF → moves images from the **selected folder only** (root, no recursion).
- **Manual selection** (both apps):
  - GUI: *Pick specific images…* opens multi-file chooser.
  - Web: *Preview & Select…* lists files with checkboxes; *Move Selected* moves only checked ones.
- **Undo Last Move**:
  - Restores the last batch to their **exact original paths**.
  - If a file already exists at the original location, it is restored as `*_restored_N.*`.
- **Supported image types**: JPG, JPEG, PNG, GIF, BMP, WEBP, TIF, TIFF, HEIC, HEIF, SVG.

### 2) Extract Emails
- Paste text (or choose a text file in GUI), app extracts all unique email addresses.
- Download/save the results as `.txt`.

### 3) Scrape Webpage Title
- Enter a URL, fetches the `<title>` tag.
- Save a text file containing **URL + Title**.

---

## 📁 Project Structure

```
Task_Automation/
├─ automation_gui.py
├─ automation_web.py
├─ templates/
│  └─ index.html
├─ static/
│  ├─ style.css
│  └─ script.js
└─ samples/
   └─ example_emails.txt
```

> The downloadable copy of `example_emails.txt` is also included at the root for convenience.

---

## 🧰 Requirements

- **Python 3.9+**
- Desktop GUI: built-in Tkinter (included with most Python distributions)
- Web App: `Flask`, `requests`, `beautifulsoup4`

Install web dependencies:
```bash
pip install flask requests beautifulsoup4
```

> If you plan to run both apps, installing the web deps is enough for all features used in this project.

---

## ▶️ Run

### Desktop GUI
```bash
python automation_gui.py
```

### Web App
From the project folder:
```bash
python automation_web.py
```
Then open:
```
http://127.0.0.1:5000/
```

To stop the server, click **Exit Server** in the UI (or press Ctrl+C in the terminal).

---

## 🖼️ Using “Move Images”

1. Choose **Source** and **Destination** folders.
2. (Optional) Toggle **Include subfolders**.
3. **Move All** (web) / **Move Images** (GUI) to move everything that matches.
4. Or **Preview & Select…** (web) / **Pick specific images…** (GUI) to move only selected files.
5. If you made a mistake, click **Undo Last Move** to restore the previous batch.

**Notes**
- When *Include subfolders* is **OFF**, only images in the root of the source folder are moved.
- Name collisions at destination are handled by appending `_1`, `_2`, …
- Undo will restore to original locations; if a path is already taken, a `*_restored_N.*` suffix is added.

---

## ✉️ Extract Emails

**GUI**: Choose input `.txt`, choose output `.txt`, click **Extract**.  
**Web**: Paste text into the text area, click **Extract**, then **Download .txt**.

---

## 🌐 Scrape Webpage Title

**GUI**: Enter a URL, choose an output file, click **Scrape Title**.  
**Web**: Enter a URL, click **Get Title**, then **Download .txt**.

Output format:
```
URL: https://example.com/
Title: Example Domain
```

---

## ❓Troubleshooting

- **No root images** when Include subfolders is OFF: the app didn’t find any images directly in the chosen folder. Put some images there or enable recursion.
- **Undo does nothing**: only the latest move batch is undoable. New moves overwrite the undo history.
- **Permissions**: On some OSes, moving from protected folders may require administrator privileges.

---