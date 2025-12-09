import tkinter as tk
from tkinter import ttk, messagebox

def calculate():
    try:
        a = float(num1_var.get())
        b = float(num2_var.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter numeric values.")
        return

    op = op_var.get()
    try:
        if op == "+": res = a + b
        elif op == "-": res = a - b
        elif op == "*": res = a * b
        elif op == "/":
            if b == 0: raise ZeroDivisionError
            res = a / b
        elif op == "%":
            if b == 0: raise ZeroDivisionError
            res = a % b
        else:
            messagebox.showerror("Invalid Operator", "Choose a valid operator.")
            return
        result_var.set(f"{res}")
    except ZeroDivisionError:
        result_var.set("Error: division by zero")

root = tk.Tk()
root.title("Basic Calculator")
root.geometry("480x220")

pad = dict(padx=14, pady=6)

ttk.Label(root, text="First number").grid(row=0, column=0, sticky="w", **pad)
num1_var = tk.StringVar()
ttk.Entry(root, textvariable=num1_var).grid(row=0, column=1, sticky="ew", **pad)

ttk.Label(root, text="Operator").grid(row=1, column=0, sticky="w", **pad)
op_var = tk.StringVar(value="+")
ttk.Combobox(root, textvariable=op_var, values=["+","-","*","/","%"], width=6, state="readonly")\
    .grid(row=1, column=1, sticky="w", **pad)

ttk.Label(root, text="Second number").grid(row=2, column=0, sticky="w", **pad)
num2_var = tk.StringVar()
ttk.Entry(root, textvariable=num2_var).grid(row=2, column=1, sticky="ew", **pad)

ttk.Button(root, text="Calculate", command=calculate).grid(row=3, column=0, columnspan=2, **pad)

ttk.Label(root, text="Result").grid(row=4, column=0, sticky="w", **pad)
result_var = tk.StringVar()
ttk.Entry(root, textvariable=result_var, state="readonly").grid(row=4, column=1, sticky="ew", **pad)

root.columnconfigure(1, weight=1)
root.mainloop()
