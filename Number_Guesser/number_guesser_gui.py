import random
import tkinter as tk
from tkinter import ttk, messagebox

class NumberGuesser(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=16)
        self.pack(fill="both", expand=True)
        self.secret = None
        self.attempts = 0
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="🎯 Number Guesser", font=("", 12, "bold")).grid(
            row=0, column=0, columnspan=4, sticky="w"
        )

        # Range inputs
        ttk.Label(self, text="Min").grid(row=1, column=0, sticky="w", pady=(8, 4))
        self.min_var = tk.StringVar(value="1")
        ttk.Entry(self, textvariable=self.min_var, width=10).grid(row=1, column=1, sticky="w", pady=(8,4))

        ttk.Label(self, text="Max").grid(row=1, column=2, sticky="w", pady=(8, 4))
        self.max_var = tk.StringVar(value="100")
        ttk.Entry(self, textvariable=self.max_var, width=10).grid(row=1, column=3, sticky="w", pady=(8,4))

        ttk.Button(self, text="Start / Reset", command=self.reset_game).grid(row=2, column=0, columnspan=4, pady=6, sticky="ew")

        ttk.Label(self, text="Your guess:").grid(row=3, column=0, sticky="w", pady=(8, 4))
        self.guess_var = tk.StringVar()
        entry = ttk.Entry(self, textvariable=self.guess_var, width=14)
        entry.grid(row=3, column=1, sticky="w", pady=(8, 4))
        entry.bind("<Return>", self.check_guess)

        ttk.Button(self, text="Check", command=self.check_guess).grid(row=3, column=2, sticky="w", padx=(8,0))

        self.status_var = tk.StringVar(value="Pick a range and press Start.")
        ttk.Label(self, textvariable=self.status_var).grid(row=4, column=0, columnspan=4, sticky="w", pady=(6,0))

        self.attempts_var = tk.StringVar(value="Attempts: 0")
        ttk.Label(self, textvariable=self.attempts_var).grid(row=5, column=0, columnspan=4, sticky="w")

        for i in range(4):
            self.columnconfigure(i, weight=1)

    def reset_game(self):
        try:
            lo = int(self.min_var.get().strip())
            hi = int(self.max_var.get().strip())
            if lo >= hi:
                raise ValueError
        except ValueError:
            messagebox.showerror("Range error", "Please enter a valid range (min < max).")
            return
        self.secret = random.randint(lo, hi)
        self.attempts = 0
        self.attempts_var.set("Attempts: 0")
        self.status_var.set(f"New round started! Guess a number between {lo} and {hi}.")
        self.guess_var.set("")

    def check_guess(self, *_):
        if self.secret is None:
            self.status_var.set("Press Start to begin.")
            return
        text = self.guess_var.get().strip()
        try:
            g = int(text)
        except ValueError:
            self.status_var.set("Please enter a whole number.")
            return

        lo = int(self.min_var.get()); hi = int(self.max_var.get())
        if not (lo <= g <= hi):
            self.status_var.set(f"Stay within {lo}–{hi}.")
            return

        self.attempts += 1
        self.attempts_var.set(f"Attempts: {self.attempts}")

        if g < self.secret:
            self.status_var.set("Too low! Try higher.")
        elif g > self.secret:
            self.status_var.set("Too high! Try lower.")
        else:
            self.status_var.set(f"🎉 Correct! {g} is the number.")
            messagebox.showinfo("You Win!", f"Nice! You guessed it in {self.attempts} attempts.")
            self.reset_game()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Number Guesser")
    root.geometry("520x240")
    NumberGuesser(root)
    root.mainloop()
