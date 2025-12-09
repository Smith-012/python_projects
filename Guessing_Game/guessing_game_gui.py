import random
import tkinter as tk
from tkinter import ttk, messagebox

class GuessingGame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=16)
        self.pack(fill="both", expand=True)
        self.min_n, self.max_n = 1, 100
        self.reset_game()
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="🎯 Guess the Number (1–100)", font=("", 12, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w"
        )

        ttk.Label(self, text="Enter your guess:").grid(row=1, column=0, sticky="w", pady=(10, 4))
        self.guess_var = tk.StringVar()
        entry = ttk.Entry(self, textvariable=self.guess_var, width=18)
        entry.grid(row=1, column=1, sticky="w", pady=(10, 4))
        entry.bind("<Return>", self.check_guess)

        ttk.Button(self, text="Check", command=self.check_guess).grid(row=1, column=2, padx=(8, 0), pady=(10, 4))

        self.status_var = tk.StringVar(value="I picked a number… can you find it?")
        ttk.Label(self, textvariable=self.status_var).grid(row=2, column=0, columnspan=3, sticky="w", pady=(6, 2))

        self.attempts_var = tk.StringVar(value="Attempts: 0")
        ttk.Label(self, textvariable=self.attempts_var).grid(row=3, column=0, columnspan=3, sticky="w")

        btns = ttk.Frame(self)
        btns.grid(row=4, column=0, columnspan=3, sticky="w", pady=(10, 0))
        ttk.Button(btns, text="Reset Game", command=self.reset_game).pack(side="left")
        ttk.Button(btns, text="Show Answer", command=self.reveal_answer).pack(side="left", padx=8)

        for i in range(3):
            self.columnconfigure(i, weight=1)

    def reset_game(self):
        self.secret = random.randint(self.min_n, self.max_n)
        self.attempts = 0
        if hasattr(self, "attempts_var"):
            self.attempts_var.set("Attempts: 0")
            self.status_var.set("New round started! Guess between 1 and 100.")
        if hasattr(self, "guess_var"):
            self.guess_var.set("")

    def reveal_answer(self):
        messagebox.showinfo("Answer", f"The number is {self.secret}")

    def check_guess(self, *_):
        text = self.guess_var.get().strip()
        if not text:
            self.status_var.set("Enter a number to guess.")
            return
        try:
            guess = int(text)
        except ValueError:
            self.status_var.set("Numbers only, please.")
            return
        if not (self.min_n <= guess <= self.max_n):
            self.status_var.set(f"Stay within {self.min_n}–{self.max_n}.")
            return

        self.attempts += 1
        self.attempts_var.set(f"Attempts: {self.attempts}")

        if guess < self.secret:
            self.status_var.set("Too low! Try a larger number.")
        elif guess > self.secret:
            self.status_var.set("Too high! Try a smaller number.")
        else:
            self.status_var.set(f"🎉 Correct! {guess} is the number.")
            messagebox.showinfo("You Win!", f"Nice! You guessed it in {self.attempts} attempts.")
            self.reset_game()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Guessing Game")
    root.geometry("500x210")
    GuessingGame(root)
    root.mainloop()
