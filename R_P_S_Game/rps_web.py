# rps_web.py
# Single-file Flask app that includes BOTH the game logic and the web server.

from flask import Flask, render_template, request, jsonify
import random

# -----------------------------
# Game logic (from rps.py)
# -----------------------------
CHOICES = ["Rock", "Paper", "Scissors"]
EMOJI = {"Rock": "🪨", "Paper": "📄", "Scissors": "✂️"}

RULES = {
    ("Rock", "Scissors"): "Rock crushes Scissors",
    ("Scissors", "Paper"): "Scissors cut Paper",
    ("Paper", "Rock"): "Paper covers Rock",
}

def decide_winner(player: str, computer: str):
    if player == computer:
        return "Tie", "It's a tie!"
    if (player, computer) in RULES:
        return "Player", RULES[(player, computer)]
    return "Computer", RULES[(computer, player)]

def play_round(player_choice: str):
    computer_choice = random.choice(CHOICES)
    winner, detail = decide_winner(player_choice, computer_choice)
    return {
        "player": player_choice,
        "computer": computer_choice,
        "player_emoji": EMOJI[player_choice],
        "computer_emoji": EMOJI[computer_choice],
        "winner": winner,
        "detail": detail,
    }

# -----------------------------
# Flask app (from app.py)
# -----------------------------
app = Flask(__name__)

@app.get("/")
def index():
    # Renders templates/index.html
    return render_template("index.html")

@app.post("/api/play")
def api_play():
    data = request.get_json(force=True) or {}
    player_choice = data.get("choice")
    if player_choice not in CHOICES:
        return jsonify({"error": "Invalid choice"}), 400
    return jsonify(play_round(player_choice)), 200

# Optional: simple health check
@app.get("/healthz")
def healthz():
    return {"ok": True}

if __name__ == "__main__":
    # Run with:  python rps_web.py
    # Ensure your templates/index.html and static/style.css are present.
    app.run(debug=True)
