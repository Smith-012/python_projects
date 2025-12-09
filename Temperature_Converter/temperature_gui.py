import tkinter as tk
from tkinter import ttk, messagebox

def c_to_f(c: float) -> float:
    return (c * 9/5) + 32

def f_to_c(f: float) -> float:
    return (f - 32) * 5/9

def convert():
    try:
        value = float(in_var.get())
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter a numeric temperature.")
        return

    unit = unit_var.get()
    if unit == "Celsius (°C)":
        result = c_to_f(value)
        out_var.set(f"{result:.2f} °F")
    else:
        result = f_to_c(value)
        out_var.set(f"{result:.2f} °C")

root = tk.Tk()
root.title("Temperature Converter (°C ↔ °F)")
root.geometry("460x220")

frm = ttk.Frame(root, padding=16)
frm.pack(fill="both", expand=True)

ttk.Label(frm, text="Enter temperature:").grid(row=0, column=0, sticky="w")
in_var = tk.StringVar()
ttk.Entry(frm, textvariable=in_var, width=24).grid(row=0, column=1, padx=8, sticky="ew")

ttk.Label(frm, text="Unit:").grid(row=1, column=0, sticky="w", pady=(8,0))
unit_var = tk.StringVar(value="Celsius (°C)")
ttk.Combobox(frm, textvariable=unit_var, values=["Celsius (°C)", "Fahrenheit (°F)"], state="readonly", width=22)\
    .grid(row=1, column=1, padx=8, pady=(8,0), sticky="w")

ttk.Button(frm, text="Convert", command=convert).grid(row=2, column=0, columnspan=2, pady=12)

ttk.Label(frm, text="Result:").grid(row=3, column=0, sticky="w")
out_var = tk.StringVar()
ttk.Entry(frm, textvariable=out_var, state="readonly").grid(row=3, column=1, padx=8, sticky="ew")

frm.columnconfigure(1, weight=1)
root.mainloop()
