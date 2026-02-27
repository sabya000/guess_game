from flask import Flask, render_template, request, session
import random

app = Flask(__name__)
app.secret_key = "guess-game-secret-key-2024"  # Required for session usage


@app.route("/", methods=["GET", "POST"])
def home():
    # If it's a fresh GET (page load/refresh), reset everything
    if request.method == "GET":
        session.clear()
        session["secret"] = random.randint(1, 100)
        session["guesses"] = []
        session["won"] = False

    message = ""
    hint = ""  # "low", "high", "win", or ""

    if request.method == "POST":
        # Restore session or reinitialise if somehow missing
        if "secret" not in session:
            session["secret"] = random.randint(1, 100)
            session["guesses"] = []
            session["won"] = False

        if not session.get("won"):
            try:
                guess = int(request.form["guess"])
                if 1 <= guess <= 100:
                    secret = session["secret"]
                    guesses = session["guesses"]

                    if guess not in guesses:
                        guesses.append(guess)
                        session["guesses"] = guesses  # mark session as modified

                    if guess == secret:
                        message = f"🎉 Correct! The number was {secret}. You got it in {len(guesses)} guess{'es' if len(guesses) != 1 else ''}!"
                        hint = "win"
                        session["won"] = True
                    elif guess < secret:
                        message = f"📈 {guess} is too LOW — go higher!"
                        hint = "low"
                    else:
                        message = f"📉 {guess} is too HIGH — go lower!"
                        hint = "high"
                else:
                    message = "⚠ Please enter a number between 1 and 100."
            except (ValueError, TypeError):
                message = "⚠ Invalid input. Enter a whole number."

    guesses = session.get("guesses", [])
    won = session.get("won", False)

    # Compute the narrowed range for the range indicator
    secret = session.get("secret", 50)
    low_bound = max((g for g in guesses if g < secret), default=1)
    high_bound = min((g for g in guesses if g > secret), default=100)

    # Build guess chips: each item is (number, type)
    # type = "win" | "low" | "high"
    guess_chips = []
    for g in guesses:
        if g == secret:
            guess_chips.append((g, "win"))
        elif g < secret:
            guess_chips.append((g, "low"))
        else:
            guess_chips.append((g, "high"))

    return render_template(
        "index.html",
        message=message,
        hint=hint,
        guess_chips=guess_chips,
        won=won,
        attempts=len(guesses),
        low_bound=low_bound,
        high_bound=high_bound,
    )


if __name__ == "__main__":
    app.run(debug=True)