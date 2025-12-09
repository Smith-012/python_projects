import re
import tkinter as tk
from tkinter import ttk

SPECIALS = r"!@#$%^&*(),.?\":{}|<>"

def score_password(pw: str):
    score = 0
    tips = []

    if len(pw) >= 8: score += 1
    else: tips.append("Use at least 8 characters.")

    if re.search(r"[A-Z]", pw): score += 1
    else: tips.append("Add an uppercase letter (A–Z).")

    if re.search(r"[a-z]", pw): score += 1
    else: tips.append("Add a lowercase letter (a–z).")

    if re.search(r"\d", pw): score += 1
    else: tips.append("Include a digit (0–9).")

    if re.search(f"[{re.escape(SPECIALS)}]", pw): score += 1
    else: tips.append(f"Include a special char ({SPECIALS}).")

    levels = ["Very Weak", "Weak", "Moderate", "Strong", "Very Strong"]
    level = levels[max(0, score - 1)] if score else levels[0]
    return score, level, tips

def make_gui():
    root = tk.Tk()
    root.title("Password Strength Checker")
    root.geometry("520x260")

    ttk.Label(root, text="Enter password:").pack(anchor="w", padx=16, pady=(16, 6))
    pw_var = tk.StringVar()
    entry = ttk.Entry(root, textvariable=pw_var, show="•", width=48)
    entry.pack(fill="x", padx=16)

    # Progress bar styles per color
    style = ttk.Style()
    try:
        style.theme_use("clam")  # allows bar color changes
    except tk.TclError:
        pass
    for name, color in [
        ("red.Horizontal.TProgressbar",    "#dc2626"),
        ("orange.Horizontal.TProgressbar", "#ea580c"),
        ("yellow.Horizontal.TProgressbar", "#ca8a04"),
        ("green.Horizontal.TProgressbar",  "#16a34a"),
    ]:
        style.configure(name, troughcolor="#e5e7eb", background=color)

    bar = ttk.Progressbar(root, length=300, mode="determinate",
                          style="red.Horizontal.TProgressbar", maximum=100)
    bar.pack(padx=16, pady=12, fill="x")

    strength_lbl = ttk.Label(root, text="Strength: —")
    strength_lbl.pack(anchor="w", padx=16)

    tips_lbl = ttk.Label(root, text="Tips will appear here.", wraplength=480, justify="left")
    tips_lbl.pack(anchor="w", padx=16, pady=(6, 0))

    def update(*_):
        pw = pw_var.get()
        score, level, tips = score_password(pw)
        pct = int((score / 5) * 100)
        bar["value"] = pct

        # choose color
        if score <= 1:
            bar.configure(style="red.Horizontal.TProgressbar")
        elif score == 2:
            bar.configure(style="orange.Horizontal.TProgressbar")
        elif score == 3:
            bar.configure(style="yellow.Horizontal.TProgressbar")
        else:
            bar.configure(style="green.Horizontal.TProgressbar")

        strength_lbl.config(text=f"Strength: {level} ({score}/5)")
        tips_lbl.config(text=("Nice! ✅" if score == 5 else "• " + "\n• ".join(tips)) or " ")

    entry.bind("<KeyRelease>", update)
    update()
    entry.focus()
    root.mainloop()

if __name__ == "__main__":
    make_gui()
