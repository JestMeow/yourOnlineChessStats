from flask import Flask, render_template, jsonify, request, redirect, url_for

from . import api_calls
from . import get_openings

import asyncio


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username")
        return redirect(f"/{username}")
    return render_template("index.html")


@app.route("/<setname>")
def serve_set(setname):
    try:
        async def load_all():
            games_task = api_calls.get_post(setname, 'games/archives')
            player_task = api_calls.get_post(setname, '')
            stats_task = api_calls.get_post(setname, 'stats')

            games_archives, player, stats = await asyncio.gather(
                games_task, player_task, stats_task
            )

            return {
                'player': player,
                'stats': stats,
                'rating_history': games_archives,
                'openings': get_openings.get_game(games_archives)
            }

        
        data = asyncio.run(load_all())

    except FileNotFoundError:
        return jsonify({"error": "Data not found."}), 404

    return render_template("dashboard.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)