from flask import Flask, render_template, request
import random

app = Flask(__name__)

@app.get("/")
def index():
    return render_template("index.html", result=None)

@app.post("/start")
def start():
    # Start a new round with provided bounds
    lo = request.form.get("min", "1").strip()
    hi = request.form.get("max", "100").strip()
    try:
        lo_i, hi_i = int(lo), int(hi)
        if lo_i >= hi_i:
            raise ValueError
    except ValueError:
        return render_template("index.html", result="Enter a valid range (min < max).")

    secret = random.randint(lo_i, hi_i)
    return render_template("index.html", secret=secret, lo=lo_i, hi=hi_i, attempts=0, result=f"Game started! Guess between {lo_i} and {hi_i}.")

@app.post("/guess")
def guess():
    try:
        secret = int(request.form.get("secret"))
        lo = int(request.form.get("lo"))
        hi = int(request.form.get("hi"))
        attempts = int(request.form.get("attempts"))
    except (TypeError, ValueError):
        return render_template("index.html", result="Start a game first.")

    text = request.form.get("guess", "").strip()
    try:
        g = int(text)
    except ValueError:
        return render_template("index.html", secret=secret, lo=lo, hi=hi, attempts=attempts,
                               result="Please enter a valid whole number.")

    if g < lo or g > hi:
        return render_template("index.html", secret=secret, lo=lo, hi=hi, attempts=attempts,
                               result=f"Guess must be in {lo}–{hi}.")

    attempts += 1
    if g < secret:
        msg = "Too low! Try higher."
    elif g > secret:
        msg = "Too high! Try lower."
    else:
        msg = f"🎉 Correct! The number was {secret}. Attempts: {attempts}"
        return render_template("index.html", result=msg)

    return render_template("index.html", secret=secret, lo=lo, hi=hi, attempts=attempts, result=msg)

if __name__ == "__main__":
    app.run(debug=True)
