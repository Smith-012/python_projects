import tkinter as tk
from tkinter import ttk, messagebox

def reverse_string(s: str) -> str:
    return s[::-1]

def on_reverse(*_):
    text = in_var.get()
    out = reverse_string(text)
    out_var.set(out)

def copy_output():
    if not out_var.get():
        messagebox.showinfo("Copy", "Nothing to copy yet.")
        return
    root.clipboard_clear()
    root.clipboard_append(out_var.get())
    messagebox.showinfo("Copy", "Reversed text copied to clipboard.")

root = tk.Tk()
root.title("String Reversal (GUI)")
root.geometry("520x220")

ttk.Label(root, text="Enter text:").pack(anchor="w", padx=16, pady=(16, 6))
in_var = tk.StringVar()
entry = ttk.Entry(root, textvariable=in_var, width=60)
entry.pack(fill="x", padx=16)
entry.bind("<KeyRelease>", on_reverse)

btn = ttk.Button(root, text="Reverse", command=on_reverse)
btn.pack(anchor="w", padx=16, pady=10)

sep = ttk.Separator(root, orient="horizontal")
sep.pack(fill="x", padx=16, pady=6)

ttk.Label(root, text="Reversed:").pack(anchor="w", padx=16, pady=(6, 4))
out_var = tk.StringVar()
out_entry = ttk.Entry(root, textvariable=out_var, width=60)
out_entry.pack(fill="x", padx=16)

copy_btn = ttk.Button(root, text="Copy Result", command=copy_output)
copy_btn.pack(anchor="e", padx=16, pady=12)

entry.focus()
root.mainloop()
