import random
import tkinter as tk
from tkinter import ttk, messagebox

CHOICES = ["Rock", "Paper", "Scissors"]
EMOJI = {"Rock": "🪨", "Paper": "📄", "Scissors": "✂️"}

RULES = {
    ("Rock", "Scissors"): "Rock crushes Scissors",
    ("Scissors", "Paper"): "Scissors cut Paper",
    ("Paper", "Rock"): "Paper covers Rock",
}

def decide_winner(player, computer):
    if player == computer:
        return "Tie", "It's a tie!"
    if (player, computer) in RULES:
        return "Player", f"You win — {RULES[(player, computer)]}!"
    return "Computer", f"Computer wins — {RULES[(computer, player)]}!"

class RPSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rock • Paper • Scissors")
        self.geometry("560x500")
        self.minsize(520, 440)
        self.configure(bg="#0b1220")
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self._setup_styles()

        # Scores & state
        self.player_score = 0
        self.computer_score = 0
        self.round_num = 0
        self.history = []  # <-- store per-round results

        self._build_ui()
        self._bind_keys()

    def _setup_styles(self):
        self.style.configure("TFrame", background="#0b1220")
        self.style.configure("Title.TLabel", background="#0b1220", foreground="#e6edf7",
                            font=("Segoe UI", 18, "bold"))
        self.style.configure("Score.TLabel", background="#0b1220", foreground="#b3c0d6",
                            font=("Segoe UI", 12))
        self.style.configure("ChoiceTitle.TLabel", background="#0b1220", foreground="#9fb7ff",
                            font=("Segoe UI", 12, "bold"))
        self.style.configure("Big.TLabel", background="#0b1220", foreground="#e6edf7",
                            font=("Segoe UI Emoji", 42))
        self.style.configure("Result.TLabel", background="#0b1220", foreground="#f4f7ff",
                            font=("Segoe UI", 13, "bold"))
        self.style.configure("Muted.TLabel", background="#0b1220", foreground="#93a1bb",
                            font=("Segoe UI", 10))

        self.style.configure("RPS.TButton", font=("Segoe UI", 11, "bold"),
                             padding=10, background="#1b2a4a", foreground="#e6edf7")
        self.style.map("RPS.TButton",
                       background=[("active", "#23365f")])
        self.style.configure("Ghost.TButton", font=("Segoe UI", 10), padding=8,
                             background="#0f172a", foreground="#9fb7ff")
        self.style.map("Ghost.TButton", background=[("active", "#152039")])

    def _build_ui(self):
        container = ttk.Frame(self, padding=16)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Rock • Paper • Scissors",
                  style="Title.TLabel").pack(anchor="center", pady=(0, 12))

        score_frame = ttk.Frame(container)
        score_frame.pack(fill="x", pady=(0, 10))

        self.player_score_lbl = ttk.Label(score_frame, style="Score.TLabel")
        self.vs_lbl = ttk.Label(score_frame, style="Score.TLabel", text="—")
        self.computer_score_lbl = ttk.Label(score_frame, style="Score.TLabel")
        self.round_lbl = ttk.Label(score_frame, style="Muted.TLabel")

        self.player_score_lbl.grid(row=0, column=0, sticky="w")
        self.vs_lbl.grid(row=0, column=1, padx=6)
        self.computer_score_lbl.grid(row=0, column=2, sticky="e")
        self.round_lbl.grid(row=1, column=0, columnspan=3, pady=(4, 0))
        score_frame.columnconfigure(0, weight=1)
        score_frame.columnconfigure(2, weight=1)

        self._update_scoreboard()

        # Choices row
        choices_frame = ttk.Frame(container)
        choices_frame.pack(pady=6, fill="x")

        # Player/Computer choice display
        pc_frame = ttk.Frame(container)
        pc_frame.pack(pady=10, fill="x")

        p_col = ttk.Frame(pc_frame)
        p_col.grid(row=0, column=0, sticky="w")
        c_col = ttk.Frame(pc_frame)
        c_col.grid(row=0, column=2, sticky="e")
        pc_frame.columnconfigure(0, weight=1)
        pc_frame.columnconfigure(2, weight=1)

        ttk.Label(p_col, text="You chose", style="ChoiceTitle.TLabel").pack(anchor="w")
        self.player_choice_lbl = ttk.Label(p_col, text="—", style="Big.TLabel")
        self.player_choice_lbl.pack(anchor="w")

        ttk.Label(c_col, text="Computer chose", style="ChoiceTitle.TLabel").pack(anchor="e")
        self.computer_choice_lbl = ttk.Label(c_col, text="—", style="Big.TLabel")
        self.computer_choice_lbl.pack(anchor="e")

        # Result
        self.result_lbl = ttk.Label(container,
                                    text="Pick Rock, Paper, or Scissors to start.",
                                    style="Result.TLabel")
        self.result_lbl.pack(pady=8)

        # Buttons for choices
        for i, choice in enumerate(CHOICES):
            b = ttk.Button(choices_frame, text=f"{EMOJI[choice]}  {choice}",
                           style="RPS.TButton",
                           command=lambda c=choice: self.play(c))
            b.grid(row=0, column=i, padx=6, sticky="ew")
            choices_frame.columnconfigure(i, weight=1)

        # Footer buttons
        footer = ttk.Frame(container)
        footer.pack(side="bottom", fill="x", pady=(10, 0))

        ttk.Button(footer, text="Reset Scores", style="Ghost.TButton",
                   command=self.reset_scores).pack(side="left")

        ttk.Button(footer, text="Rules", style="Ghost.TButton",
                   command=self.show_rules).pack(side="left", padx=(8, 0))

        # NEW: Show all round results
        ttk.Button(footer, text="Show All Round Results", style="Ghost.TButton",
                   command=self.show_history).pack(side="left", padx=(8, 0))

        ttk.Label(footer, text="Shortcuts: R / P / S, Esc to quit",
                  style="Muted.TLabel").pack(side="right")

    def _bind_keys(self):
        self.bind("<Escape>", lambda e: self.destroy())
        for k, choice in [("r","Rock"), ("p","Paper"), ("s","Scissors"),
                          ("R","Rock"), ("P","Paper"), ("S","Scissors")]:
            self.bind(k, lambda e, c=choice: self.play(c))

    def _update_scoreboard(self):
        self.player_score_lbl.config(text=f"You: {self.player_score}")
        self.computer_score_lbl.config(text=f"Computer: {self.computer_score}")
        self.vs_lbl.config(text="—")
        self.round_lbl.config(text=f"Rounds played: {self.round_num}")

    def play(self, player_choice):
        computer_choice = random.choice(CHOICES)
        winner, message = decide_winner(player_choice, computer_choice)

        # Update state
        self.round_num += 1
        self.player_choice_lbl.config(text=EMOJI[player_choice])
        self.computer_choice_lbl.config(text=EMOJI[computer_choice])

        if winner == "Player":
            self.player_score += 1
        elif winner == "Computer":
            self.computer_score += 1

        self._update_scoreboard()
        self.result_lbl.config(text=message)
        self._flash_result(winner)

        # Record round in history
        self.history.append({
            "round": self.round_num,
            "player": player_choice,
            "computer": computer_choice,
            "winner": winner,
            "detail": message.replace("You win — ", "").replace("Computer wins — ", "").replace("It's a tie!", "Tie")
        })

    def _flash_result(self, winner):
        win = "#a7f3d0"   # green-ish
        lose = "#fecaca"  # red-ish
        tie = "#fde68a"   # amber
        color = tie if winner == "Tie" else (win if winner == "Player" else lose)
        self.result_lbl.configure(background=color)
        self.after(220, lambda: self.result_lbl.configure(background="#0b1220"))

    def reset_scores(self):
        self.player_score = 0
        self.computer_score = 0
        self.round_num = 0
        self.history.clear()  # <-- clear history when resetting
        self.player_choice_lbl.config(text="—")
        self.computer_choice_lbl.config(text="—")
        self.result_lbl.config(text="Pick Rock, Paper, or Scissors to start.")
        self._update_scoreboard()

    def show_rules(self):
        rules_text = (
            "• Rock beats Scissors\n"
            "• Scissors beat Paper\n"
            "• Paper beats Rock\n\n"
            "How to play:\n"
            "Click a button or press R / P / S to choose."
        )
        messagebox.showinfo("Rules", rules_text)

    # NEW: window that shows all round results
    def show_history(self):
        if not self.history:
            messagebox.showinfo("All Round Results", "No rounds played yet.")
            return

        win = tk.Toplevel(self)
        win.title("All Round Results")
        win.geometry("640x360")
        win.minsize(520, 280)

        # Table
        cols = ("Round", "You", "Computer", "Winner", "Detail")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=12)
        for c in cols:
            tree.heading(c, text=c)
        tree.column("Round", width=70, anchor="center")
        tree.column("You", width=110, anchor="center")
        tree.column("Computer", width=110, anchor="center")
        tree.column("Winner", width=100, anchor="center")
        tree.column("Detail", width=220, anchor="w")

        # Scrollbars
        vsb = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(win, orient="horizontal", command=tree.xview)
        tree.configure(yscroll=vsb.set, xscroll=hsb.set)

        tree.pack(fill="both", expand=True, side="left")
        vsb.pack(fill="y", side="right")
        hsb.pack(fill="x", side="bottom")

        # Fill table
        for item in self.history:
            tree.insert("", "end", values=(
                item["round"],
                f'{EMOJI[item["player"]]} {item["player"]}',
                f'{EMOJI[item["computer"]]} {item["computer"]}',
                item["winner"],
                item["detail"],
            ))

if __name__ == "__main__":
    app = RPSApp()
    app.mainloop()
