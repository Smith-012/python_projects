import tkinter as tk
from tkinter import ttk, messagebox

MIN_TERMS = 1
MAX_TERMS = 500   # limit to keep the app responsive

def fibonacci(n: int):
    a, b = 0, 1
    seq = []
    for _ in range(n):
        seq.append(a)
        a, b = b, a + b
    return seq

def generate():
    raw = n_var.get().strip()
    if not raw:
        status_var.set(f"Enter how many terms you want (between {MIN_TERMS} and {MAX_TERMS}).")
        return
    try:
        n = int(raw)
        if n < MIN_TERMS or n > MAX_TERMS:
            messagebox.showwarning(
                "Out of Range",
                f"Please enter a number between {MIN_TERMS} and {MAX_TERMS}."
            )
            return
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter a positive whole number.")
        return

    seq = fibonacci(n)
    out_var.set(", ".join(str(x) for x in seq))
    status_var.set(f"Generated {n} term(s).")

def copy_output():
    text = out_var.get()
    if not text:
        status_var.set("Nothing to copy yet.")
        return
    root.clipboard_clear()
    root.clipboard_append(text)
    status_var.set("Sequence copied to clipboard ✅")

root = tk.Tk()
root.title("Fibonacci Generator")
root.geometry("640x260")

pad = dict(padx=16, pady=6)
ttk.Label(root, text=f"How many terms? (range: {MIN_TERMS}–{MAX_TERMS})").grid(row=0, column=0, sticky="w", **pad)
n_var = tk.StringVar(value="10")
ttk.Entry(root, textvariable=n_var, width=20).grid(row=0, column=1, sticky="w", **pad)

ttk.Button(root, text="Generate", command=generate).grid(row=0, column=2, **pad)

ttk.Label(root, text="Sequence:").grid(row=1, column=0, sticky="nw", **pad)
out_var = tk.StringVar()
out = ttk.Entry(root, textvariable=out_var, width=80)
out.grid(row=1, column=1, columnspan=2, sticky="ew", **pad)

ttk.Button(root, text="Copy", command=copy_output).grid(row=2, column=2, sticky="e", **pad)

status_var = tk.StringVar(value="Ready.")
ttk.Label(root, textvariable=status_var).grid(row=3, column=0, columnspan=3, sticky="w", padx=16)

root.columnconfigure(1, weight=1)
root.mainloop()
