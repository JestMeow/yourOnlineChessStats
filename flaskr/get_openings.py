from collections import defaultdict

import chess.pgn

from io import StringIO

import csv
import re

def clean_move(san):
    return san.lower().replace("+", "").replace("#", "").replace("x", "").strip()

def is_move_token(token):
    return not re.match(r"^\d+\.$", token)

openings = []

tsv_files = [
    "datasets/a.tsv",
    "datasets/b.tsv",
    "datasets/c.tsv",
    "datasets/d.tsv",
    "datasets/e.tsv"
]

for file_path in tsv_files:
    with open(file_path, newline='', encoding="utf-8") as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        for row in reader:
            tokens = row["pgn"].strip().split()
            move_list = [clean_move(t) for t in tokens if is_move_token(t)]
            openings.append({
                "eco": row["eco"],
                "name": row["name"],
                "moves": move_list
            })

def detect_opening_from_moves(game_moves):
    if isinstance(game_moves, str):
        game_moves = game_moves.strip().lower().split()

    for opening in sorted(openings, key=lambda x: len(x["moves"]), reverse=True):
        if game_moves[:len(opening["moves"])] == opening["moves"]:
            return f'{opening["eco"]}: {opening["name"]}'
    
    return "Unknown"

def get_game(games_data):
    openings = defaultdict(list)

    time_classes = ['rapid', 'blitz', 'bullet', 'daily']

    losses = [
        'checkmated',
        'resigned',
        'timeout'
    ]

    for time_class in time_classes:
        for game in games_data[time_class]:
            result = game['result']
            color = game['color']

            pgn_str = game['pgn']
            pgn_io = StringIO(pgn_str)
            pgn_game = chess.pgn.read_game(pgn_io)

            board = pgn_game.board()
            moves_san = []
            for move in pgn_game.mainline_moves():
                moves_san.append(board.san(move))
                board.push(move)

            moves_str = ' '.join(moves_san)
            opening_name = detect_opening_from_moves(moves_str)

            existing = next(
                (o for o in openings[time_class] 
                if o['opening_name'] == opening_name and o['color'] == color),
                None
            )

            if existing:
                if result in losses:
                    existing['loss'] += 1
                elif result == 'win':
                    existing['win'] += 1
                else:
                    existing['draw'] += 1
            else:
                loss = 1 if result in losses else 0
                win = 1 if result == 'win' else 0
                draw = 1 if result not in losses and result != 'win' else 0

                openings[time_class].append({
                    'opening_name': opening_name,
                    'win': win,
                    'draw': draw,
                    'loss': loss,
                    'color': color
                })
        
    return openings



# {'opening_name': opening_name, 'win': win, 'draw': draw, 'loss': loss, 'color': color}