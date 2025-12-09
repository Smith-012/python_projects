from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def reverse_string(s: str) -> str:
    return s[::-1]

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/reverse")
def reverse():
    text = request.form.get("text", "")
    return jsonify({"reversed": reverse_string(text)})

if __name__ == "__main__":
    app.run(debug=True)
