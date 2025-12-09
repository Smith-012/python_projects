from flask import Flask, render_template, request

app = Flask(__name__)

def compute(a, b, op):
    if op == "+": return a + b
    if op == "-": return a - b
    if op == "*": return a * b
    if op == "/":
        if b == 0: return "Error: division by zero"
        return a / b
    if op == "%":
        if b == 0: return "Error: division by zero"
        return a % b
    return "Invalid operator"

@app.get("/")
def index():
    return render_template("index.html", result=None, a="", b="", op="+")

@app.post("/calc")
def calc():
    a = request.form.get("a", "").strip()
    b = request.form.get("b", "").strip()
    op = request.form.get("op", "+")
    try:
        a_num = float(a)
        b_num = float(b)
        result = compute(a_num, b_num, op)
    except ValueError:
        result = "Please enter valid numbers"
    return render_template("index.html", result=result, a=a, b=b, op=op)

if __name__ == "__main__":
    app.run(debug=True)
