import random
from flask import Flask, render_template, request, session, redirect, url_for
import os
from route import RouteManager

# Initialize Flask app
app = Flask(__name__, template_folder=r"templates")
app.secret_key = os.getenv("SESSION_KEY")  # Set the secret key for session storage

# Initialize the RouteManager
route_manager = RouteManager(
    routes_file=r"data/routes.csv",
    airports_file=r"data/airports.csv"
)

# Create a case-insensitive mapping of country names
country_map = {}
for country in route_manager.countries:
    country_map[country.lower()] = country


# Home Page - Start the Game
@app.route("/")
def home():
    # Use RouteManager to pick a random route with at least 2 stops
    source, destination, correct_path = route_manager.pick_random_route(min_path_length=2)

    if not source or not destination:
        return "Error: No valid routes found."

    # Store in session
    session["source"] = source
    session["destination"] = destination
    session["player_path"] = [source]
    session["correct_path"] = correct_path

    return render_template("game.html", source=source, destination=destination,
                           path_length=len(correct_path) - 1)


# Process Player's Input
@app.route("/play", methods=["POST"])
def play():
    # Get the input and standardize it to match our country names
    user_input = request.form.get("next_country", "").strip()
    next_country_lower = user_input.lower()

    # Look up the properly capitalized country name
    if next_country_lower in country_map:
        next_country = country_map[next_country_lower]
    else:
        # If we can't find an exact match, check for partial matches
        matches = [country for country_lower, country in country_map.items()
                   if next_country_lower in country_lower]

        if len(matches) == 1:
            next_country = matches[0]  # Use the single match
        else:
            # No unique match found, treat as invalid
            player_path = session.get("player_path", [])
            correct_path = session.get("correct_path", [])

            error_msg = "Country not found. Please check your spelling."
            if len(matches) > 1:
                error_msg = f"Ambiguous input. Did you mean one of: {', '.join(matches[:5])}"
                if len(matches) > 5:
                    error_msg += f", and {len(matches) - 5} others"

            return render_template("game.html", source=session["source"], destination=session["destination"],
                                   path_length=len(correct_path) - 1, player_path=" → ".join(player_path),
                                   error=error_msg)

    player_path = session.get("player_path", [])
    correct_path = session.get("correct_path", [])

    # Check if the selected country is a valid neighbor using RouteManager
    if not route_manager.check_valid_move(player_path[-1], next_country):
        return render_template("game.html", source=session["source"], destination=session["destination"],
                               path_length=len(correct_path) - 1, player_path=" → ".join(player_path),
                               error="Invalid move! You can't fly directly from " + player_path[
                                   -1] + " to " + next_country)

    # Valid move, append to player path
    player_path.append(next_country)
    session["player_path"] = player_path

    # Check if the player reached the destination
    if next_country == session["destination"]:
        # Calculate score based on optimal vs actual path length
        optimal_length = len(correct_path) - 1  # Number of flights in optimal path
        player_length = len(player_path) - 1  # Number of flights in player's path

        # Calculate score (100 points for optimal path, deduct points for extra steps)
        if player_length == optimal_length:
            score = 100  # Perfect score for optimal path
            score_message = "Perfect! You found the optimal route!"
        else:
            # Deduct points for each extra flight taken (10 points per extra flight)
            extra_flights = player_length - optimal_length
            score = max(0, 100 - (extra_flights * 10))
            score_message = f"You took {extra_flights} more flight(s) than the optimal route."

        # Find the optimal path for display
        optimal_path_display = " → ".join(correct_path)

        return render_template("win.html",
                               path=" → ".join(player_path),
                               score=score,
                               score_message=score_message,
                               optimal_path=optimal_path_display)

    # If not, show the current game state again
    return render_template("game.html", source=session["source"], destination=session["destination"],
                           path_length=len(correct_path) - 1, player_path=" → ".join(player_path))


# Restart Game
@app.route("/restart")
def restart():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)