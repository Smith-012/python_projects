from flask import Flask, render_template, request
import re

app = Flask(__name__)

REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

def validate_email(email: str):
    email = email.strip()
    if " " in email:
        return False, "Email cannot contain spaces."
    if email.count("@") != 1:
        return False, "Email must contain exactly one '@'."
    local, domain = email.split("@")
    if not local:
        return False, "Username (before @) cannot be empty."
    if "." not in domain or domain.startswith(".") or domain.endswith("."):
        return False, "Domain must contain a dot and not start/end with it."
    if re.match(REGEX, email) is None:
        return False, "Contains invalid characters or bad format."
    return True, "Looks good!"

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/validate")
def validate():
    email = request.form.get("email", "")
    ok, msg = validate_email(email)
    return render_template("index.html", email=email, ok=ok, msg=msg)

if __name__ == "__main__":
    app.run(debug=True)
