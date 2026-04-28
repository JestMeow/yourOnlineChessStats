import requests
import datetime
from collections import defaultdict

import aiohttp
import asyncio


async def fetch_games(session, archive, headers):
    async with session.get(archive, headers=headers) as response:
        return await response.json()



async def get_post(username, types):
    url = f'https://api.chess.com/pub/player/{username}/{types}'

    print(url)

    try:
        headers = {
            'User-Agent': 'Eden'
        }



        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as response:

                if response.status == 200:
                    posts = await response.json()

                    if types == 'games/archives':
                        async with aiohttp.ClientSession() as session:
                            tasks = [
                                fetch_games(session, archive, headers)
                                for archive in posts['archives']
                            ]
                        
                            results = await asyncio.gather(*tasks, return_exceptions=True)

                        games = defaultdict(list)

                        for games_data in results:
                            if isinstance(games_data, Exception):
                                continue

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
                    return posts
                else:
                    print('Error:', response.status_code)
                    return None
    except Exception as e:
        print('Error:', e)
        return None
