from flask import Flask, render_template, request

app = Flask(__name__)

def c_to_f(c): return (c * 9/5) + 32
def f_to_c(f): return (f - 32) * 5/9

@app.get("/")
def index():
    return render_template("index.html", result=None, value="", unit="C")

@app.post("/convert")
def convert():
    value = request.form.get("value", "").strip()
    unit = request.form.get("unit", "C")
    error = None
    result = None

    try:
        num = float(value)
        if unit == "C":
            result = f"{c_to_f(num):.2f} °F"
        else:
            result = f"{f_to_c(num):.2f} °C"
    except ValueError:
        error = "Please enter a valid number."

    return render_template("index.html", result=result, value=value, unit=unit, error=error)

if __name__ == "__main__":
    app.run(debug=True)
