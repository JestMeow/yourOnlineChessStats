import requests
import datetime
from collections import defaultdict


def get_post(username, types):
    url = f'https://api.chess.com/pub/player/{username}/{types}'

    print(url)

    try:
        headers = {
            'User-Agent': 'Eden'
        }

        response = requests.get(url, headers=headers)


        if response.status_code == 200:
            posts = response.json()

            if types == 'games/archives':
                games = defaultdict(list)

                for archive in posts['archives']:
                    games_response = requests.get(archive, headers=headers)
                    games_data = games_response.json()

                    for game in games_data["games"]:
                        time_class = game.get('time_class')
                        if game["white"]["username"].lower() == username.lower():
                            rating = game["white"]["rating"]
                            result = game["white"]["result"]
                            color = 'white'
                        else:
                            rating = game["black"]["rating"]
                            result = game["black"]["result"]
                            color = 'black'
                        
                        end_time = datetime.datetime.utcfromtimestamp(game["end_time"]).strftime('%Y-%m-%d')
                        pgn = game['pgn']


                        games[time_class].append({
                            "timestamp": end_time,
                            "rating": rating,
                            "pgn": pgn,
                            "result": result,
                            'color': color
                        })


                return games
            else:
                return posts
        else:
            print('Error:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None
