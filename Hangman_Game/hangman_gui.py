# hangman_gui.py
import json
import random
import string
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request

# ---------------------- Config ----------------------
MAX_MISSES = 6
MAX_HINTS = 3
WORD_API_URL = "https://random-word-api.herokuapp.com/word?number=1"

# ---------------------- Fetch runtime word (online) ----------------------
def fetch_online_word():
    """
    Fetch one English-looking word from a public API.
    Raises RuntimeError if it cannot fetch a valid word.
    """
    try:
        with urllib.request.urlopen(WORD_API_URL, timeout=8) as r:
            data = json.loads(r.read().decode("utf-8"))
            if isinstance(data, list) and data:
                word = str(data[0]).strip()
                # keep letters only; reject weird tokens
                if word.isalpha() and 3 <= len(word) <= 14:
                    return word.lower()
    except Exception as e:
        # print for console debugging; GUI will show a messagebox
        print("Fetch error:", e, file=sys.stderr)
    raise RuntimeError("Cannot fetch word from internet API.")

# ---------------------- Game Logic ----------------------
class Hangman:
    def __init__(self):
        self.reset()

    def reset(self):
        self.secret = fetch_online_word().upper()
        self.revealed = ["_" for _ in self.secret]
        self.misses = 0
        self.guessed = set()
        self.hints_left = MAX_HINTS

    def guess(self, ch):
        ch = ch.upper()
        if ch in self.guessed or not ch.isalpha() or len(ch) != 1:
            return False, None  # ignored
        self.guessed.add(ch)

        if ch in self.secret:
            for i, c in enumerate(self.secret):
                if c == ch:
                    self.revealed[i] = ch
            return True, "_" not in self.revealed
        else:
            self.misses += 1
            return False, self.misses >= MAX_MISSES

    def use_hint(self):
        """Reveal a random unrevealed letter. Returns (char, won) or (None, None) if not available."""
        if self.hints_left <= 0 or "_" not in self.revealed:
            return None, None
        self.hints_left -= 1
        hidden = [i for i, ch in enumerate(self.revealed) if ch == "_"]
        idx = random.choice(hidden)
        ch = self.secret[idx]
        self.guessed.add(ch)
        for i, c in enumerate(self.secret):
            if c == ch:
                self.revealed[i] = ch
        return ch, "_" not in self.revealed

# ---------------------- UI ----------------------
class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=16)
        self.master.title("Hangman — Tkinter Edition")
        self.master.minsize(720, 520)
        self.master.configure(bg="#0f172a")  # dark theme
        self.create_style()

        # Layout
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Canvas (left)
        self.canvas = tk.Canvas(self, bg="#0b1220", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=(0, 8))

        # Right panel
        right = ttk.Frame(self)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)

        # Word label
        self.word_var = tk.StringVar()
        ttk.Label(right, textvariable=self.word_var, style="Word.TLabel").grid(row=0, column=0, sticky="ew", pady=(8, 12))

        # Info row: lives + hints + guessed
        info = ttk.Frame(right)
        info.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        info.columnconfigure(0, weight=1)
        info.columnconfigure(1, weight=1)
        self.lives_var = tk.StringVar()
        self.hints_var = tk.StringVar()
        self.guessed_var = tk.StringVar()
        ttk.Label(info, textvariable=self.lives_var, style="Info.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(info, textvariable=self.hints_var, style="Info.TLabel").grid(row=0, column=1, sticky="e")
        ttk.Label(info, textvariable=self.guessed_var, style="Info.TLabel").grid(row=1, column=0, columnspan=2, sticky="ew")

        # Keyboard
        kb_frame = ttk.LabelFrame(right, text="Pick a letter")
        kb_frame.grid(row=2, column=0, sticky="nsew")
        for r in range(3): kb_frame.rowconfigure(r, weight=1)
        for c in range(9): kb_frame.columnconfigure(c, weight=1)
        self.buttons = {}
        letters = list(string.ascii_uppercase)
        layout = [letters[:9], letters[9:18], letters[18:]]
        for r, row in enumerate(layout):
            for c, ch in enumerate(row):
                b = ttk.Button(kb_frame, text=ch, style="Key.TButton",
                               command=lambda ch=ch: self.on_guess(ch))
                b.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
                self.buttons[ch] = b

        # Controls
        controls = ttk.Frame(right)
        controls.grid(row=3, column=0, pady=12, sticky="ew")
        controls.columnconfigure((0,1,2), weight=1)

        self.hint_btn = ttk.Button(controls, text=f"Hint ({MAX_HINTS})", style="Accent.TButton", command=self.on_hint)
        self.hint_btn.grid(row=0, column=0, sticky="ew", padx=(0,6))

        self.new_btn = ttk.Button(controls, text="New Game", command=self.new_game)
        self.new_btn.grid(row=0, column=1, sticky="ew", padx=6)

        ttk.Button(controls, text="Quit", command=self.master.destroy).grid(row=0, column=2, sticky="ew", padx=(6,0))

        self.grid(sticky="nsew")

        # Start game (with API error handling)
        try:
            self.game = Hangman()
        except RuntimeError as e:
            messagebox.showerror("Network error", f"{e}\n\nCheck your internet or try again.")
            # Disable controls if we couldn't start
            self.disable_all()
            return

        self.post_create_bindings()
        self.refresh_all(first_draw=True)

    def post_create_bindings(self):
        self.master.bind("<Key>", self.handle_keypress)

    # -------- Styling --------
    def create_style(self):
        style = ttk.Style()
        try: style.theme_use("clam")
        except Exception: pass
        style.configure("TFrame", background="#0f172a")
        style.configure("TLabelframe", background="#0f172a", foreground="#dbeafe")
        style.configure("TLabelframe.Label", background="#0f172a", foreground="#a5b4fc")
        style.configure("TLabel", background="#0f172a", foreground="#e2e8f0")
        style.configure("Info.TLabel", font=("Inter", 11, "normal"), foreground="#cbd5e1")
        style.configure("Word.TLabel", font=("Fira Code", 28, "bold"), foreground="#f8fafc")
        style.configure("TButton", padding=10)
        style.map("TButton", background=[("active", "#1e293b")])
        style.configure("Key.TButton", font=("Inter", 13, "bold"))
        style.configure("Accent.TButton", foreground="#0f172a", background="#a7f3d0")
        style.map("Accent.TButton", background=[("active", "#6ee7b7")])

    # -------- Game control handlers --------
    def new_game(self):
        try:
            self.game.reset()
        except RuntimeError as e:
            messagebox.showerror("Network error", f"{e}\n\nCheck your internet or try again.")
            return
        self.enable_all()
        self.refresh_all(first_draw=True)

    def on_guess(self, ch):
        correct, finished = self.game.guess(ch)
        self.buttons[ch].state(["disabled"])  # disable regardless

        if correct:
            self.update_word()
            if finished:
                self.end_game(win=True)
        else:
            self.update_info()
            self.draw_stage(self.game.misses)
            if finished:
                self.end_game(win=False)

        self.update_hint_button()

    def on_hint(self):
        ch, won = self.game.use_hint()
        self.update_word()
        self.update_info()
        self.update_hint_button()
        if ch and ch in self.buttons:
            self.buttons[ch].state(["disabled"])
        if won:
            self.end_game(win=True)

    def end_game(self, win):
        for b in self.buttons.values():
            b.state(["disabled"])
        self.hint_btn.state(["disabled"])
        if win:
            self.word_var.set(" ".join(self.game.revealed))
            messagebox.showinfo("You win!", f"You guessed it: {self.game.secret}")
        else:
            self.word_var.set(" ".join(list(self.game.secret)))
            messagebox.showerror("Out of lives", f"The word was: {self.game.secret}")

    def handle_keypress(self, event):
        ch = event.char.upper()
        if ch in self.buttons and "disabled" not in self.buttons[ch].state():
            self.on_guess(ch)

    # -------- UI updates --------
    def refresh_all(self, first_draw=False):
        self.update_word()
        self.update_info()
        self.update_hint_button()
        if first_draw:
            self.canvas.delete("all")
            self.draw_gallows()
            # re-enable all keys
            for b in self.buttons.values():
                b.state(["!disabled"])

    def update_word(self):
        self.word_var.set(" ".join(self.game.revealed))

    def update_info(self):
        left = MAX_MISSES - self.game.misses
        self.lives_var.set(f"Lives: {left} / {MAX_MISSES}")
        self.hints_var.set(f"Hints: {self.game.hints_left} / {MAX_HINTS}")
        guessed = "".join(sorted(self.game.guessed)) or "—"
        self.guessed_var.set(f"Guessed: {guessed}")

    def update_hint_button(self):
        self.hint_btn.config(text=f"Hint ({self.game.hints_left})")
        if self.game.hints_left <= 0 or "_" not in self.game.revealed:
            self.hint_btn.state(["disabled"])
        else:
            self.hint_btn.state(["!disabled"])

    def disable_all(self):
        for b in self.buttons.values(): b.state(["disabled"])
        self.hint_btn.state(["disabled"])
        self.new_btn.state(["disabled"])

    def enable_all(self):
        for b in self.buttons.values(): b.state(["!disabled"])
        self.hint_btn.state(["!disabled"])
        self.new_btn.state(["!disabled"])

    # -------- Drawing --------
    def draw_gallows(self):
        w = self.canvas.winfo_width() or 10
        h = self.canvas.winfo_height() or 10
        self.canvas.create_rectangle(12, h-20, w-12, h-12, fill="#1e293b", outline="")  # base shadow
        self.canvas.create_line(80, h-20, 80, 40, width=6, fill="#64748b")
        self.canvas.create_line(80, 40, 250, 40, width=6, fill="#64748b")
        self.canvas.create_line(250, 40, 250, 80, width=6, fill="#64748b")

    def draw_stage(self, stage):
        x, y = 250, 100
        if stage >= 1:  # head
            self.canvas.create_oval(x-25, y-25, x+25, y+25, outline="#eab308", width=4)
        if stage >= 2:  # body
            self.canvas.create_line(x, y+25, x, y+110, width=4, fill="#eab308")
        if stage >= 3:  # left arm
            self.canvas.create_line(x, y+50, x-35, y+80, width=4, fill="#eab308")
        if stage >= 4:  # right arm
            self.canvas.create_line(x, y+50, x+35, y+80, width=4, fill="#eab308")
        if stage >= 5:  # left leg
            self.canvas.create_line(x, y+110, x-30, y+155, width=4, fill="#eab308")
        if stage >= 6:  # right leg
            self.canvas.create_line(x, y+110, x+30, y+155, width=4, fill="#eab308")

def main():
    try:
        root = tk.Tk()
    except tk.TclError as e:
        print("Tkinter failed to start:", e, file=sys.stderr)
        sys.exit(1)
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
