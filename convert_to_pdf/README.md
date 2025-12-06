📄 Universal Office to PDF Converter (Flask + Microsoft Office)

A fast and user-friendly local web app that converts multiple Office formats to PDF using drag & drop.


-------------------------------
🚀 Supported Input Formats
-------------------------------
.doc   ✔
.docx  ✔
.ppt   ✔
.pptx  ✔
.xls   ✔
.xlsx  ✔
.csv   ✔
.txt   ✔
.odt   ✔
.ods   ✔
Output → PDF ✔


-------------------------------
💡 Features
-------------------------------
• Upload or drag-and-drop interface
• Automatically downloads converted PDF
• Works fully offline
• Opens in browser automatically
• Fast conversion using Microsoft Office (Word / Excel / PowerPoint)
• No cloud upload — completely local and secure


-------------------------------
🔧 Requirements
-------------------------------
• Windows OS
• Python 3.8+
• Microsoft Office installed (Word, Excel, PowerPoint)
• Browser (automatically opens)
• pip dependencies listed below


-------------------------------
📦 Installation
-------------------------------
Install required packages:

    pip install flask werkzeug pywin32

📌 No LibreOffice required  
📌 No docx2pdf required — Office handles all formats automatically


-------------------------------
▶ Run the Application
-------------------------------
    python app.py

After starting:
• The application automatically opens in your browser
• If not, open manually in a browser:
      http://127.0.0.1:5000


-------------------------------
📁 Project Structure
-------------------------------
project/
│ app.py
│ README.txt
│ requirements.txt


-------------------------------
❗ Common Troubleshooting
-------------------------------
Issue: PDF not generated  
Solution: Open the file manually once in Microsoft Office and retry

Issue: Conversion failed  
Solution: Ensure Microsoft Office is activated

Issue: File rejected  
Solution: File format must be one of the supported formats

Issue: Excel/PowerPoint window flashes or opens  
Solution: Normal behavior during export — it closes automatically

Issue: pywin32 error  
Solution: install using → pip install pywin32


-------------------------------
🔮 Future Upgrade Ideas
-------------------------------
• Batch upload (convert multiple files at once)
• ZIP download for multiple PDFs
• Dark/Light theme toggle
• Create .exe desktop version (PyInstaller)
• PDF preview before download


-------------------------------
📝 License
-------------------------------
Free to modify and distribute for personal and commercial use.
-------------------------------
