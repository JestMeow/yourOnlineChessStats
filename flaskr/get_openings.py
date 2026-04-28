from collections import defaultdict
import chess.pgn
from io import StringIO
import csv


# Clean move helper
def clean_move(token):
    return token.lower().replace("+", "").replace("#", "").replace("x", "").strip()


def is_move_token(token):
    return not token.endswith(".")

raw_openings = []

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

            raw_openings.append({
                "eco": row["eco"],
                "name": row["name"],
                "moves": tuple(move_list)
            })

OPENINGS_SORTED = sorted(raw_openings, key=lambda x: len(x["moves"]), reverse=True)


def detect_opening_from_moves(moves):
    """
    moves = list of SAN moves
    """
    moves = tuple(moves)

    for opening in OPENINGS_SORTED:
        omoves = opening["moves"]

        if len(moves) < len(omoves):
            continue

        if moves[:len(omoves)] == omoves:
            return f"{opening['eco']}: {opening['name']}"

    return "Unknown"

# Main stuff
def get_game(games_data):
    result_by_time = defaultdict(dict)

    losses = {'checkmated', 'resigned', 'timeout'}
    time_classes = ['rapid', 'blitz', 'bullet', 'daily']

    for time_class in time_classes:

        for game in games_data[time_class]:
            result = game['result']
            color = game['color']

            pgn_game = chess.pgn.read_game(StringIO(game['pgn']))

            board = pgn_game.board()
            moves_san = []

            for move in pgn_game.mainline_moves():
                moves_san.append(board.san(move))
                board.push(move)

            opening_name = detect_opening_from_moves(moves_san)

            key = (opening_name, color)

            entry = result_by_time[time_class].get(key)

            if entry:
                if result in losses:
                    entry['loss'] += 1
                elif result == 'win':
                    entry['win'] += 1
                else:
                    entry['draw'] += 1

            else:
                result_by_time[time_class][key] = {
                    'opening_name': opening_name,
                    'win': 1 if result == 'win' else 0,
                    'draw': 1 if result not in losses and result != 'win' else 0,
                    'loss': 1 if result in losses else 0,
                    'color': color
                }
                
    openings_list = {
        tc: list(data.values())
        for tc, data in result_by_time.items()
    }

    return openings_list