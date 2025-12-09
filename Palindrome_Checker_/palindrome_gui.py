import tkinter as tk
from tkinter import ttk

def is_palindrome(text: str) -> bool:
    cleaned = "".join(ch.lower() for ch in text if ch.isalnum())
    return cleaned == cleaned[::-1]

def check(*_):
    text = in_var.get()
    ok = is_palindrome(text)
    status_var.set("✅ Palindrome" if ok else "❌ Not a palindrome")
    status_lbl.configure(foreground=("#16a34a" if ok else "#b91c1c"))

root = tk.Tk()
root.title("Palindrome Checker")
root.geometry("520x180")

ttk.Label(root, text="Enter word or phrase:").pack(anchor="w", padx=16, pady=(16, 6))
in_var = tk.StringVar()
entry = ttk.Entry(root, textvariable=in_var, width=56)
entry.pack(fill="x", padx=16)
entry.bind("<Return>", check)
entry.bind("<KeyRelease>", lambda e: None)  # keep focus behavior consistent

ttk.Button(root, text="Check", command=check).pack(anchor="w", padx=16, pady=10)

status_var = tk.StringVar(value="Waiting for input… (ignores case & punctuation)")
status_lbl = ttk.Label(root, textvariable=status_var)
status_lbl.pack(anchor="w", padx=16)

entry.focus()
root.mainloop()
