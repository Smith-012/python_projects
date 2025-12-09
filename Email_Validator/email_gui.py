import re
import tkinter as tk
from tkinter import ttk

REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

def is_valid_email(email: str) -> tuple[bool, str]:
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

def validate(*_):
    ok, msg = is_valid_email(var.get().strip())
    status_var.set(("✅ Valid  • " if ok else "❌ Invalid  • ") + msg)
    status_lbl.configure(foreground=("#16a34a" if ok else "#b91c1c"))

root = tk.Tk()
root.title("Email Validator")
root.geometry("520x180")

ttk.Label(root, text="Enter email:").pack(anchor="w", padx=16, pady=(16, 6))
var = tk.StringVar()
entry = ttk.Entry(root, textvariable=var, width=56)
entry.pack(fill="x", padx=16)
entry.bind("<KeyRelease>", validate)

ttk.Button(root, text="Validate", command=validate).pack(anchor="w", padx=16, pady=10)

status_var = tk.StringVar(value="Waiting for input…")
status_lbl = ttk.Label(root, textvariable=status_var)
status_lbl.pack(anchor="w", padx=16)

entry.focus()
root.mainloop()
