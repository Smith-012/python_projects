from flask import Flask, render_template, request
import random

app = Flask(__name__)

@app.get("/")
def index():
    # create a new secret each page load; the page guides with higher/lower
    secret = random.randint(1, 100)
    return render_template("index.html", secret=secret, result=None, attempts=0)

@app.post("/guess")
def guess():
    secret = int(request.form.get("secret", "50"))
    attempts = int(request.form.get("attempts", "0"))
    text = request.form.get("guess", "").strip()

    message = None
    ok = False
    try:
        g = int(text)
        if g < 1 or g > 100:
            message = "Guess must be in 1–100."
        else:
            attempts += 1
            if g < secret: message = "Too low! Try higher."
            elif g > secret: message = "Too high! Try lower."
            else:
                message, ok = f"🎉 Correct! The number was {secret}. Attempts: {attempts}", True
    except ValueError:
        message = "Please enter a valid whole number."

    return render_template("index.html", secret=secret, result=message, ok=ok, attempts=attempts, last=text)

if __name__ == "__main__":
    app.run(debug=True)
