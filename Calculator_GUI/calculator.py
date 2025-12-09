import tkinter as tk
from tkinter import messagebox
from decimal import Decimal, getcontext, InvalidOperation

getcontext().prec = 28  # reasonable calculator precision

# --- Simple expression engine (no eval) ---------------------------------------
OPS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "×": lambda a, b: a * b,
    "÷": lambda a, b: (a / b),
}

def is_operator(ch: str) -> bool:
    return ch in OPS

def format_decimal(d: Decimal) -> str:
    # Strip trailing zeros and useless decimal point
    s = f"{d.normalize():f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s or "0"

# --- Calculator State ----------------------------------------------------------
class CalcState:
    def __init__(self):
        self.reset_all()

    def reset_all(self):
        self.acc = None         # Decimal or None
        self.op = None          # '+','-','×','÷' or None
        self.cur = "0"          # string of current input
        self.just_evaluated = False

    def clear_entry(self):
        self.cur = "0"
        self.just_evaluated = False

    def backspace(self):
        if self.just_evaluated:
            # Samsung clears the entry after result if you hit backspace
            self.clear_entry()
            return
        if len(self.cur) <= 1:
            self.cur = "0"
        else:
            self.cur = self.cur[:-1]

    def input_digit(self, d: str):
        assert d in "0123456789"
        if self.just_evaluated:
            # start fresh after showing a result
            self.cur = d
            self.just_evaluated = False
            return
        if self.cur == "0":
            self.cur = d
        else:
            self.cur += d

    def input_decimal_point(self):
        if self.just_evaluated:
            self.cur = "0."
            self.just_evaluated = False
            return
        if "." not in self.cur:
            self.cur += "."  # allow only one dot in current number

    def toggle_sign(self):
        if self.cur.startswith("-"):
            self.cur = self.cur[1:]
        else:
            if self.cur != "0":
                self.cur = "-" + self.cur

    def percent(self):
        # Simple calculator behavior: turn current entry into a percent
        try:
            val = Decimal(self.cur) / Decimal(100)
            self.cur = format_decimal(val)
        except InvalidOperation:
            self.cur = "0"

    def set_operator(self, op: str):
        # pressing operator sequences like 5 + + should replace operator
        if self.op and not self.just_evaluated:
            # compute first if we already have acc/op and user entered a number
            self.equals()
        else:
            # move current to accumulator
            try:
                self.acc = Decimal(self.cur)
            except InvalidOperation:
                self.acc = Decimal(0)
        self.op = op
        self.just_evaluated = False
        self.cur = "0"

    def equals(self):
        if self.op is None or self.acc is None:
            # nothing to compute, just confirm current
            try:
                self.acc = Decimal(self.cur)
            except InvalidOperation:
                self.acc = Decimal(0)
            self.op = None
            self.cur = format_decimal(self.acc)
            self.just_evaluated = True
            return

        try:
            b = Decimal(self.cur)
            if self.op == "÷" and b == 0:
                raise ZeroDivisionError
            result = OPS[self.op](self.acc, b)
            self.acc = result
            self.cur = format_decimal(result)
            self.op = None
            self.just_evaluated = True
        except ZeroDivisionError:
            self.reset_all()
            raise
        except InvalidOperation:
            self.reset_all()
            raise

# --- UI ------------------------------------------------------------------------
class SamsungCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.configure(bg="#0e1116")  # One UI-ish dark background

        # ✅ Enable maximize & resizing
        self.resizable(True, True)
        try:
            # Start maximized on Windows; harmless elsewhere
            self.state("zoomed")
        except Exception:
            pass

        self.state = CalcState()

        # Colors (One UI inspired)
        self.bg = "#0e1116"
        self.panel_bg = "#141a22"
        self.num_bg = "#1b2430"
        self.num_fg = "#e8eef7"
        self.op_bg = "#223042"
        self.op_fg = "#b7c9e6"
        self.eq_bg = "#00c853"   # Samsung-ish green
        self.eq_fg = "#0b0f12"
        self.ac_bg = "#2a3545"
        self.ac_fg = "#fcae60"   # amber-ish for AC/DEL

        # Display
        self.display_var = tk.StringVar(value="0")
        self.secondary_var = tk.StringVar(value="")  # to show pending op

        display_frame = tk.Frame(self, bg=self.panel_bg)
        display_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 6))

        self.secondary = tk.Label(
            display_frame, textvariable=self.secondary_var,
            font=("Segoe UI", 12), anchor="e", bg=self.panel_bg, fg="#7e8aa6",
            padx=12, pady=4, width=18
        )
        self.secondary.pack(fill="x")

        self.display = tk.Label(
            display_frame, textvariable=self.display_var,
            font=("Segoe UI", 36, "bold"), anchor="e",
            bg=self.panel_bg, fg="#f3f7ff", padx=12, pady=10
        )
        self.display.pack(fill="x")

        # Make top-level grid expand with window (for nicer maximize)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Button grid
        grid = tk.Frame(self, bg=self.bg)
        grid.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        for r in range(5):
            grid.grid_rowconfigure(r, weight=1)
        for c in range(4):
            grid.grid_columnconfigure(c, weight=1)

        def make_btn(text, r, c, cmd, bg, fg, w=4, h=2, font=("Segoe UI", 14, "bold")):
            b = tk.Button(
                grid, text=text, command=cmd, width=w, height=h,
                bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
                bd=0, relief="flat", font=font
            )
            b.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
            return b

        # First row: AC, DEL, %, ÷
        make_btn("AC", 0, 0, self.on_ac, self.ac_bg, self.ac_fg)
        make_btn("DEL",0, 1, self.on_del, self.ac_bg, self.ac_fg, w=5)
        make_btn("%", 0, 2, self.on_percent, self.op_bg, self.op_fg)
        make_btn("÷", 0, 3, lambda: self.on_operator("÷"), self.op_bg, self.op_fg)

        # Second: 7 8 9 ×
        make_btn("7", 1, 0, lambda: self.on_digit("7"), self.num_bg, self.num_fg)
        make_btn("8", 1, 1, lambda: self.on_digit("8"), self.num_bg, self.num_fg)
        make_btn("9", 1, 2, lambda: self.on_digit("9"), self.num_bg, self.num_fg)
        make_btn("×", 1, 3, lambda: self.on_operator("×"), self.op_bg, self.op_fg)

        # Third: 4 5 6 −
        make_btn("4", 2, 0, lambda: self.on_digit("4"), self.num_bg, self.num_fg)
        make_btn("5", 2, 1, lambda: self.on_digit("5"), self.num_bg, self.num_fg)
        make_btn("6", 2, 2, lambda: self.on_digit("6"), self.num_bg, self.num_fg)
        make_btn("−", 2, 3, lambda: self.on_operator("-"), self.op_bg, self.op_fg)

        # Fourth: 1 2 3 +
        make_btn("1", 3, 0, lambda: self.on_digit("1"), self.num_bg, self.num_fg)
        make_btn("2", 3, 1, lambda: self.on_digit("2"), self.num_bg, self.num_fg)
        make_btn("3", 3, 2, lambda: self.on_digit("3"), self.num_bg, self.num_fg)
        make_btn("+", 3, 3, lambda: self.on_operator("+"), self.op_bg, self.op_fg)

        # Fifth: ± 0 . =
        make_btn("±", 4, 0, self.on_sign, self.op_bg, self.op_fg)
        make_btn("0", 4, 1, lambda: self.on_digit("0"), self.num_bg, self.num_fg)
        make_btn(".", 4, 2, self.on_dot, self.num_bg, self.num_fg)
        make_btn("=", 4, 3, self.on_equals, self.eq_bg, self.eq_fg)

        # Keyboard bindings
        self.bind("<Key>", self.on_key)
        self.bind("<Return>", lambda e: self.on_equals())
        self.bind("=", lambda e: self.on_equals())
        self.bind("<Escape>", lambda e: self.on_ac())
        self.bind("<BackSpace>", lambda e: self.on_del())
        self.update_secondary()

    # --- UI update helpers -----------------------------------------------------
    def update_display(self):
        self.display_var.set(self.state.cur)

    def update_secondary(self):
        if self.state.op and self.state.acc is not None:
            self.secondary_var.set(f"{format_decimal(self.state.acc)} {self.state.op}")
        else:
            self.secondary_var.set("")

    # --- Button handlers -------------------------------------------------------
    def on_digit(self, d):
        self.state.input_digit(d)
        self.update_display()
        self.update_secondary()

    def on_dot(self):
        self.state.input_decimal_point()
        self.update_display()

    def on_sign(self):
        self.state.toggle_sign()
        self.update_display()

    def on_percent(self):
        self.state.percent()
        self.update_display()

    def on_operator(self, op):
        try:
            self.state.set_operator(op)
        except Exception:
            messagebox.showerror("Error", "Invalid operation.")
            self.state.reset_all()
        self.update_display()
        self.update_secondary()

    def on_equals(self):
        try:
            self.state.equals()
        except ZeroDivisionError:
            messagebox.showwarning("Math error", "Cannot divide by zero.")
        except Exception:
            messagebox.showerror("Error", "Invalid calculation.")
        self.update_display()
        self.update_secondary()

    def on_ac(self):
        self.state.reset_all()
        self.update_display()
        self.update_secondary()

    def on_del(self):
        self.state.backspace()
        self.update_display()

    # --- Keyboard input with validation ---------------------------------------
    def on_key(self, event: tk.Event):
        ch = event.char
        if ch.isdigit():
            self.on_digit(ch)
        elif ch == ".":
            self.on_dot()
        elif ch in "+-*/xX":
            mapping = {"+": "+", "-": "-", "*": "×", "x": "×", "X": "×", "/": "÷"}
            self.on_operator(mapping[ch])
        elif ch == "%":
            self.on_percent()
        elif ch in ("\r", "\n"):
            self.on_equals()
        # ignore everything else (prevents letters etc.)

if __name__ == "__main__":
    SamsungCalculator().mainloop()
