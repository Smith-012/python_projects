import math
import string
import secrets
import tkinter as tk
from tkinter import ttk, messagebox

# Optional nicer theme
THEME_OK = False
try:
    import ttkbootstrap as ttkb  # pip install ttkbootstrap
    THEME_OK = True
except Exception:
    pass


AMBIGUOUS = set("O0oIl1|`'\"{}[]()<>;,.:")
DEFAULT_LEN = 16
MIN_LEN = 8
MAX_LEN = 64


def estimate_strength(length, pool_size):
    """Return (score_0_to_1, bits_of_entropy, verdict)."""
    if pool_size <= 1 or length <= 0:
        return 0.0, 0.0, "Very weak"
    # Shannon-ish estimate: log2(pool_size^length) = length * log2(pool)
    bits = length * math.log2(pool_size)
    # Map entropy to verdict
    if bits < 28:
        verdict = "Very weak"
    elif bits < 36:
        verdict = "Weak"
    elif bits < 60:
        verdict = "Good"
    elif bits < 80:
        verdict = "Strong"
    else:
        verdict = "Excellent"
    # Normalize 0..1 for progress bar (~0..128 bits considered)
    score = min(bits / 128.0, 1.0)
    return score, bits, verdict


def secure_choice(seq):
    return seq[secrets.randbelow(len(seq))]


def generate_password(length, use_lower, use_upper, use_digits, use_symbols,
                      avoid_ambiguous, must_include_each, start_with_letter):
    # Build pools
    pool = ""
    lowers = string.ascii_lowercase
    uppers = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*_-+=?:~"  # curated clean set

    if avoid_ambiguous:
        def filt(s): return "".join(ch for ch in s if ch not in AMBIGUOUS)
        lowers, uppers, digits, symbols = map(filt, (lowers, uppers, digits, symbols))

    pools = []
    if use_lower and lowers:
        pool += lowers
        pools.append(lowers)
    if use_upper and uppers:
        pool += uppers
        pools.append(uppers)
    if use_digits and digits:
        pool += digits
        pools.append(digits)
    if use_symbols and symbols:
        pool += symbols
        pools.append(symbols)

    if not pool:
        raise ValueError("You must select at least one character set.")

    if length < 1:
        raise ValueError("Length must be >= 1.")

    # Start with a letter if requested
    first_char = ""
    if start_with_letter:
        letters = ""
        if use_lower: letters += lowers
        if use_upper: letters += uppers
        if not letters:
            raise ValueError("To start with a letter, enable upper and/or lower case.")
        first_char = secure_choice(letters)

    # Must include one of each selected type
    required = []
    if must_include_each:
        for p in pools:
            required.append(secure_choice(p))

    # Fill the rest from the full pool
    remaining = length - len(first_char) - len(required)
    if remaining < 0:
        raise ValueError("Length too short for chosen options (increase length).")

    body = [secure_choice(pool) for _ in range(remaining)]
    chars = list(first_char) + required + body

    # Shuffle using Fisher–Yates with secrets
    for i in range(len(chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        chars[i], chars[j] = chars[j], chars[i]

    # If we forced first char to be a letter, swap a letter into position 0
    if start_with_letter:
        # Find a letter index
        letters = set(string.ascii_letters)
        idx = None
        for i, ch in enumerate(chars):
            if ch in letters:
                idx = i
                break
        if idx is not None:
            chars[0], chars[idx] = chars[idx], chars[0]

    return "".join(chars), len(pool)


class AppBase:
    def __init__(self, root):
        self.root = root
        root.title("Password Generator")
        root.minsize(560, 420)

        # Main container
        pad = 12
        self.wrap = ttk.Frame(root, padding=pad)
        self.wrap.pack(fill="both", expand=True)

        self.build_ui()
        self.update_strength()

    # ---------------------- UI ----------------------
    def build_ui(self):
        # Title
        title = ttk.Label(self.wrap, text="Password Generator",
                          font=("Segoe UI", 16, "bold"))
        title.grid(row=0, column=0, columnspan=3, sticky="w")

        # Output field + buttons row
        self.var_pwd = tk.StringVar()
        out_row = ttk.Frame(self.wrap)
        out_row.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(8, 4))
        self.entry = ttk.Entry(out_row, textvariable=self.var_pwd, font=("Consolas", 14))
        self.entry.pack(side="left", fill="x", expand=True)

        self.show_var = tk.BooleanVar(value=False)
        self.entry.configure(show="•")
        self.btn_show = ttk.Checkbutton(out_row, text="Show", variable=self.show_var,
                                        command=self.toggle_show)
        self.btn_show.pack(side="left", padx=(8, 4))

        self.btn_copy = ttk.Button(out_row, text="Copy", command=self.copy_pwd)
        self.btn_copy.pack(side="left", padx=4)

        # Options panel
        opts = ttk.LabelFrame(self.wrap, text="Options")
        opts.grid(row=2, column=0, columnspan=3, sticky="ew", pady=8)

        # Length
        ttk.Label(opts, text="Length:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.var_len = tk.IntVar(value=DEFAULT_LEN)
        self.scale = ttk.Scale(opts, from_=MIN_LEN, to=MAX_LEN,
                               orient="horizontal",
                               command=lambda v: self.sync_length(int(float(v))))
        self.scale.set(DEFAULT_LEN)
        self.scale.grid(row=0, column=1, sticky="ew", padx=6, pady=6)
        opts.grid_columnconfigure(1, weight=1)
        self.len_label = ttk.Label(opts, text=str(DEFAULT_LEN), width=3)
        self.len_label.grid(row=0, column=2, sticky="e", padx=8)

        # Char set checkboxes
        self.use_lower = tk.BooleanVar(value=True)
        self.use_upper = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        self.avoid_amb = tk.BooleanVar(value=True)
        self.must_each = tk.BooleanVar(value=True)
        self.start_letter = tk.BooleanVar(value=True)

        row = 1
        ttk.Checkbutton(opts, text="Lowercase (a–z)", variable=self.use_lower,
                        command=self.update_strength).grid(row=row, column=0, sticky="w", padx=8)
        ttk.Checkbutton(opts, text="Uppercase (A–Z)", variable=self.use_upper,
                        command=self.update_strength).grid(row=row, column=1, sticky="w", padx=8)
        ttk.Checkbutton(opts, text="Digits (0–9)", variable=self.use_digits,
                        command=self.update_strength).grid(row=row, column=2, sticky="w", padx=8)

        row += 1
        ttk.Checkbutton(opts, text="Symbols (!@#$…)", variable=self.use_symbols,
                        command=self.update_strength).grid(row=row, column=0, sticky="w", padx=8)
        ttk.Checkbutton(opts, text="Avoid ambiguous", variable=self.avoid_amb,
                        command=self.update_strength).grid(row=row, column=1, sticky="w", padx=8)
        ttk.Checkbutton(opts, text="Include one of each", variable=self.must_each,
                        command=self.update_strength).grid(row=row, column=2, sticky="w", padx=8)

        row += 1
        ttk.Checkbutton(opts, text="Start with letter", variable=self.start_letter,
                        command=self.update_strength).grid(row=row, column=0, sticky="w", padx=8)

        # Strength bar
        bar_row = ttk.Frame(self.wrap)
        bar_row.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(2, 10))
        ttk.Label(bar_row, text="Strength:").pack(side="left")
        self.strength = ttk.Progressbar(bar_row, mode="determinate", length=240)
        self.strength.pack(side="left", padx=8, fill="x", expand=True)
        self.var_verdict = tk.StringVar(value="")
        ttk.Label(bar_row, textvariable=self.var_verdict).pack(side="left", padx=6)

        # Buttons row
        btns = ttk.Frame(self.wrap)
        btns.grid(row=4, column=0, columnspan=3, sticky="ew")
        ttk.Button(btns, text="Generate", command=self.on_generate).pack(side="left")
        ttk.Button(btns, text="Regenerate", command=self.on_generate).pack(side="left", padx=6)
        ttk.Button(btns, text="Clear", command=lambda: self.var_pwd.set("")).pack(side="left", padx=6)

        # Footer
        foot = ttk.Label(self.wrap,
                         text="Uses cryptographically secure randomness (secrets).",
                         foreground="#6f7c91")
        foot.grid(row=5, column=0, columnspan=3, sticky="w", pady=(10, 0))

        self.root.bind("<Control-c>", lambda e: self.copy_pwd())
        self.root.bind("<Return>", lambda e: self.on_generate())

    # ---------------------- helpers ----------------------
    def toggle_show(self):
        self.entry.configure(show="" if self.show_var.get() else "•")

    def copy_pwd(self):
        pwd = self.var_pwd.get()
        if not pwd:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(pwd)
        self.root.update()  # keep on clipboard after app closes
        messagebox.showinfo("Copied", "Password copied to clipboard.")

    def sync_length(self, n):
        n = max(MIN_LEN, min(MAX_LEN, int(n)))
        self.var_len.set(n)
        self.len_label.config(text=str(n))
        self.update_strength()

    def current_pool_size(self):
        size = 0
        lowers = string.ascii_lowercase
        uppers = string.ascii_uppercase
        digits = string.digits
        symbols = "!@#$%^&*_-+=?:~"

        if self.avoid_amb.get():
            def filt(s): return "".join(ch for ch in s if ch not in AMBIGUOUS)
            lowers, uppers, digits, symbols = map(filt, (lowers, uppers, digits, symbols))

        if self.use_lower.get(): size += len(lowers)
        if self.use_upper.get(): size += len(uppers)
        if self.use_digits.get(): size += len(digits)
        if self.use_symbols.get(): size += len(symbols)
        return size

    def update_strength(self):
        ps = self.current_pool_size()
        score, bits, verdict = estimate_strength(self.var_len.get(), ps)
        self.strength["value"] = score * 100
        self.var_verdict.set(f"{verdict}  ({bits:.0f} bits)")

    # ---------------------- actions ----------------------
    def on_generate(self):
        try:
            pwd, pool_size = generate_password(
                length=self.var_len.get(),
                use_lower=self.use_lower.get(),
                use_upper=self.use_upper.get(),
                use_digits=self.use_digits.get(),
                use_symbols=self.use_symbols.get(),
                avoid_ambiguous=self.avoid_amb.get(),
                must_include_each=self.must_each.get(),
                start_with_letter=self.start_letter.get(),
            )
        except Exception as e:
            messagebox.showwarning("Cannot generate", str(e))
            return

        self.var_pwd.set(pwd)
        score, bits, verdict = estimate_strength(len(pwd), pool_size)
        self.strength["value"] = score * 100
        self.var_verdict.set(f"{verdict}  ({bits:.0f} bits)")


def main():
    if THEME_OK:
        root = ttkb.Window(themename="darkly")
    else:
        root = tk.Tk()
        # basic darkish background for default ttk
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
    AppBase(root)
    root.mainloop()


if __name__ == "__main__":
    main()
