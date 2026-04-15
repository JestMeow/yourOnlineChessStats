import requests
import json

from collections import defaultdict


def get_post(username):
    url = f'https://api.chess.com/pub/player/fizazmonkey/games/archives'

    print(url)

    try:
        headers = {
            'User-Agent': 'Eden'
        }

        response = requests.get(url, headers=headers)


        if response.status_code == 200:
            posts = response.json()
            games = defaultdict(list)

            for archive in posts['archives']:
                games_response = requests.get(archive, headers=headers)
                games_data = games_response.json()

                for game in games_data["games"]:
                    time_control = game.get('time_class')
                    if game["white"]["username"].lower() == username.lower():
                        rating = game["white"]["rating"]
                    else:
                        rating = game["black"]["rating"]

                    games[time_control].append({
                        "timestamp": game["end_time"],
                        "rating": rating
                    })

            return games
        else:
            print('Error:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None

def main():
    posts = get_post('fizazmonkey')
    print(posts['rapid'])
    


main()