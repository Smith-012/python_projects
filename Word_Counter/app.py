from flask import Flask, render_template, request
import string

app = Flask(__name__)

def count_words(text: str):
    text = text.lower().translate(str.maketrans("", "", string.punctuation))
    counts = {}
    for w in text.split():
        counts[w] = counts.get(w, 0) + 1
    return dict(sorted(counts.items()))

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/upload")
def upload():
    file = request.files.get("file")
    if not file or file.filename == "":
        return render_template("index.html", error="Please choose a .txt file to upload.")
    try:
        text = file.read().decode("utf-8", errors="ignore")
        results = count_words(text)
        return render_template("index.html", results=results, filename=file.filename)
    except Exception as e:
        return render_template("index.html", error=f"Failed to read file: {e}")

if __name__ == "__main__":
    app.run(debug=True)
