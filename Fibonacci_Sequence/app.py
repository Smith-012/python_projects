from flask import Flask, render_template, request

app = Flask(__name__)

MIN_TERMS = 1
MAX_TERMS = 500   # limit to prevent freezes and crashes

def fibonacci(n: int):
    a, b = 0, 1
    seq = []
    for _ in range(n):
        seq.append(a)
        a, b = b, a + b
    return seq

@app.get("/")
def index():
    return render_template("index.html", min_terms=MIN_TERMS, max_terms=MAX_TERMS)

@app.post("/generate")
def generate():
    raw = request.form.get("n", "").strip()
    error = None
    seq = None
    display_seq = None

    try:
        n = int(raw)
        if n < MIN_TERMS or n > MAX_TERMS:
            raise ValueError
        seq = fibonacci(n)
        # ✅ Jinja-safe: build the display string in Python
        display_seq = ", ".join(str(x) for x in seq)
    except ValueError:
        error = f"Please enter a number between {MIN_TERMS} and {MAX_TERMS}."

    return render_template(
        "index.html",
        n=raw,
        seq=seq,
        display_seq=display_seq,
        error=error,
        min_terms=MIN_TERMS,
        max_terms=MAX_TERMS
    )

if __name__ == "__main__":
    app.run(debug=True)
