from __future__ import annotations

from pathlib import Path
import tempfile
import webbrowser
import threading

from flask import Flask, request, send_file, render_template_string
from werkzeug.utils import secure_filename
import win32com.client as win32  # Microsoft Office automation

app = Flask(__name__)

# All file extensions we support → PDF
ALLOWED_EXTENSIONS = {
    ".doc", ".docx",
    ".ppt", ".pptx",
    ".xls", ".xlsx",
    ".csv", ".txt",
    ".odt", ".ods",
}

SUPPORTED_EXTENSIONS_STR = ", ".join(sorted(ALLOWED_EXTENSIONS))

HTML = f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Convert to PDF</title>
  <style>
    body {{
      font-family: system-ui, sans-serif;
      display:flex;
      justify-content:center;
      align-items:center;
      min-height:100vh;
      background:#f5f5f5;
      margin:0;
    }}
    .wrapper {{
      background:white;
      padding:24px 28px;
      border-radius:16px;
      box-shadow:0 10px 30px rgba(0,0,0,.08);
      max-width:460px;
      width:100%;
    }}
    h1 {{
      margin-top:0;
      font-size:20px;
    }}
    #dropzone {{
      margin-top:16px;
      border:2px dashed #bbb;
      border-radius:12px;
      padding:32px 20px;
      text-align:center;
      cursor:pointer;
      transition:.2s border-color, .2s background;
    }}
    #dropzone.dragover {{
      border-color:#333;
      background:#fafafa;
    }}
    #file-input {{
      display:none;
    }}
    .btn {{
      margin-top:16px;
      padding:10px 18px;
      border-radius:999px;
      border:none;
      font-weight:600;
      cursor:pointer;
    }}
    .btn:disabled {{
      opacity:.5;
      cursor:default;
    }}
    #status {{
      margin-top:10px;
      font-size:14px;
      color:#666;
      min-height:18px;
    }}
    .note {{
      font-size:12px;
      color:#777;
      margin-top:8px;
    }}
  </style>
</head>
<body>
<div class="wrapper">
  <h1>Convert File to PDF</h1>
  <p>Drop a supported file below or click to browse.</p>
  <p class="note">
    Supported: {SUPPORTED_EXTENSIONS_STR}
  </p>

  <form id="form" enctype="multipart/form-data">
    <input
      type="file"
      id="file-input"
      name="file"
      accept=".doc,.docx,.ppt,.pptx,.xls,.xlsx,.csv,.txt,.odt,.ods"
    />
    <div id="dropzone">Drop file here or click to browse</div>
    <button class="btn" id="convert-btn" type="submit" disabled>Convert to PDF</button>
    <div id="status"></div>
  </form>
</div>

<script>
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const form = document.getElementById('form');
  const statusEl = document.getElementById('status');
  const convertBtn = document.getElementById('convert-btn');
  let currentFile = null;

  function setStatus(msg) {{
    statusEl.textContent = msg || "";
  }}

  function setErrorStyle() {{
    dropzone.style.borderColor = "red";
    dropzone.style.background = "#ffe6e6";
  }}

  function clearErrorStyle() {{
    dropzone.style.borderColor = "#bbb";
    dropzone.style.background = "";
  }}

  dropzone.addEventListener('click', () => fileInput.click());

  dropzone.addEventListener('dragover', e => {{
    e.preventDefault();
    dropzone.classList.add('dragover');
  }});

  dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));

  dropzone.addEventListener('drop', e => {{
    e.preventDefault();
    dropzone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    handleFile(file);
  }});

  fileInput.addEventListener('change', e => handleFile(e.target.files[0]));

  function handleFile(file) {{
    if (!file) return;

    // client-side extension check (now includes .doc and .xls)
    const allowedPattern = /\\.(doc|docx|ppt|pptx|xls|xlsx|csv|txt|odt|ods)$/i;

    if (!allowedPattern.test(file.name)) {{
      currentFile = null;
      convertBtn.disabled = true;
      setStatus("Unsupported file: " + file.name + ". Please use one of: {SUPPORTED_EXTENSIONS_STR}");
      setErrorStyle();
      return;
    }}

    // valid file → reset styles
    clearErrorStyle();
    currentFile = file;
    setStatus("Selected: " + file.name);
    convertBtn.disabled = false;
  }}

  form.addEventListener('submit', async e => {{
    e.preventDefault();
    if (!currentFile) return;

    convertBtn.disabled = true;
    setStatus('Converting…');
    clearErrorStyle();

    const formData = new FormData();
    formData.append('file', currentFile);

    try {{
      const res = await fetch('/convert', {{ method: 'POST', body: formData }});
      if (!res.ok) {{
        const text = await res.text();
        setStatus('Error: ' + text);
        setErrorStyle();
        convertBtn.disabled = false;
        return;
      }}

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;

      const baseName = currentFile.name.replace(/\\.[^/.]+$/, '');
      a.download = baseName + '.pdf';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      setStatus('Done! PDF downloaded.');
      clearErrorStyle();
    }} catch (err) {{
      console.error(err);
      setStatus('Conversion failed.');
      setErrorStyle();
    }} finally {{
      convertBtn.disabled = false;
    }}
  }});
</script>
</body>
</html>
"""

# -------- Microsoft Office based converters -------- #

def convert_with_word(src: Path, dst: Path) -> None:
    """Use Microsoft Word to export to PDF."""
    word = win32.DispatchEx("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(str(src))
        # 17 = wdFormatPDF
        doc.SaveAs(str(dst), FileFormat=17)
        doc.Close()
    finally:
        word.Quit()

def convert_with_powerpoint(src: Path, dst: Path) -> None:
    """Use Microsoft PowerPoint to export to PDF."""
    powerpoint = win32.DispatchEx("PowerPoint.Application")
    try:
        presentation = powerpoint.Presentations.Open(str(src), WithWindow=False)
        # 32 = ppSaveAsPDF
        presentation.SaveAs(str(dst), FileFormat=32)
        presentation.Close()
    finally:
        powerpoint.Quit()

def convert_with_excel(src: Path, dst: Path) -> None:
    """Use Microsoft Excel to export to PDF."""
    excel = win32.DispatchEx("Excel.Application")
    excel.Visible = False
    try:
        wb = excel.Workbooks.Open(str(src))
        # 0 = xlTypePDF
        wb.ExportAsFixedFormat(0, str(dst))
        wb.Close()
    finally:
        excel.Quit()

def office_convert(src: Path, out_dir: Path) -> Path:
    """
    Route file to the proper Microsoft Office app and export to PDF.
    """
    src = Path(src)
    out_dir = Path(out_dir)
    pdf_path = out_dir / (src.stem + ".pdf")
    ext = src.suffix.lower()

    if ext in {".doc", ".docx", ".txt", ".odt"}:
        convert_with_word(src, pdf_path)
    elif ext in {".ppt", ".pptx"}:
        convert_with_powerpoint(src, pdf_path)
    elif ext in {".xls", ".xlsx", ".csv", ".ods"}:
        convert_with_excel(src, pdf_path)
    else:
        raise RuntimeError(f"Unsupported extension for Office conversion: {ext}")

    if not pdf_path.exists():
        raise RuntimeError("Conversion failed, PDF not created.")
    return pdf_path


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/convert", methods=["POST"])
def convert_route():
    # Return plain text messages, not big HTML error pages
    if "file" not in request.files:
        return "No file uploaded", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    filename = secure_filename(file.filename)
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        msg = (
            f"Unsupported file type: {ext}. "
            f"Supported extensions: {SUPPORTED_EXTENSIONS_STR}"
        )
        return msg, 400

    tmpdir = Path(tempfile.mkdtemp())
    src_path = tmpdir / filename
    file.save(src_path)

    try:
        pdf_path = office_convert(src_path, tmpdir)
    except Exception as e:
        return f"Conversion error: {e}", 500

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=pdf_path.name,
        mimetype="application/pdf",
    )


if __name__ == "__main__":
    # Open browser ONCE (no debug reloader, so no double tabs)
    url = "http://127.0.0.1:5000"
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    # debug=False → no reloader → no second process → no 2 tabs
    app.run(debug=False)
