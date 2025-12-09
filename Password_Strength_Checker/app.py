from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

SPECIALS = r"!@#$%^&*(),.?\":{}|<>"

def check_password(password: str):
    score = 0
    tips = []

    if len(password) >= 8: score += 1
    else: tips.append("Use at least 8 characters.")

    if re.search(r"[A-Z]", password): score += 1
    else: tips.append("Add an uppercase letter.")

    if re.search(r"[a-z]", password): score += 1
    else: tips.append("Add a lowercase letter.")

    if re.search(r"\d", password): score += 1
    else: tips.append("Include a digit.")

    if re.search(f"[{re.escape(SPECIALS)}]", password): score += 1
    else: tips.append(f"Include a special char ({SPECIALS}).")

    levels = ["Very Weak", "Weak", "Moderate", "Strong", "Very Strong"]
    level = levels[max(0, score - 1)] if score else levels[0]
    return {"score": score, "level": level, "tips": tips}

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/check")
def check():
    pw = request.form.get("password", "")
    result = check_password(pw)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
