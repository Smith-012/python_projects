from flask import Flask, render_template, request

app = Flask(__name__)

def is_palindrome(text: str) -> bool:
    cleaned = "".join(ch.lower() for ch in text if ch.isalnum())
    return cleaned == cleaned[::-1]

@app.get("/")
def index():
    return render_template("index.html", text="", result=None)

@app.post("/check")
def check():
    text = request.form.get("text", "")
    ok = is_palindrome(text)
    return render_template("index.html", text=text, result=ok)

if __name__ == "__main__":
    app.run(debug=True)
