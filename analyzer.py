import chess.pgn
import io
import chess
import chess.engine

from secrfice import brillant
from accucrcy import classify_move
from secrifing import is_potential_sacrifice
import math


import json
import os

base_path = os.path.dirname(__file__)  # path to current .py file
file_path = os.path.join(base_path, "open.json")

with open(file_path, "r") as file:
    openings = json.load(file)
# Load and prepare the opening lookup dictionary

    opening_lookup = {
        entry["fen"].split(" ")[0]: entry for entry in openings
    }

# Define the lookup function (no default for opening_lookup)
opening_lookup = {
    entry["fen"].split(" ")[0]: entry for entry in openings
}
def get_opening(fen: str):
    fen = fen.split(' ')[0]  # normalize
    
    return opening_lookup.get(fen)


def load_game(filename):
    with open(filename, "r") as f:
        game = chess.pgn.read_game(f)
    
        return game





def delta_to_penalty(delta):
    delta = abs(delta)
    if delta <= 10:
        return 100.0
    elif delta <= 20:
        return 99.8 - (delta - 10) * 0.05  # Very minor loss
    elif delta <= 50:
        return 99.3 - (delta - 20) * 0.15  # Small loss
    elif delta <= 100:
        return 94.8 - (delta - 50) * 0.1   # Inaccuracy
    elif delta <= 300:
        return 89.8 - (delta - 100) * 0.2  # Mistake range
    elif delta <= 700:
        return 49.8 - (delta - 300) * 0.1  # Blunder range
    else:
        # Smoothly decay toward 0, slower
        return max(0.0, 9.8 - math.log(delta - 700 + 1) * 3)

class StockfishAnalyzer:
    base_dir = os.path.dirname(__file__)
    stockfish_path = os.path.join(base_dir, 'stockfish', 'stockfish-windows-x86-64-avx2.exe')
    def __init__(self, path: str =stockfish_path):
        self.engine = chess.engine.SimpleEngine.popen_uci(path)
        self.engine.configure({
            "Hash": 4096,
            "Skill Level": 12
        })

    def analysis(self, game):
        board = game.board()
        move_data = []
        matched_opening = None
        
        for move in game.mainline_moves():
            fen = board.fen()
            info = self.engine.analyse(board, chess.engine.Limit(depth=15))
          
           
            eval_cp = info['score'].white().score(mate_score=10000)
            move_data.append({
                "move": board.san(move),
                "fen": fen,
                "eval": eval_cp,
                "turn": "white" if board.turn == chess.WHITE else "black"
                
            })
            board.push(move)
            
        for i in range(len(move_data) - 1):
            current = move_data[i]
            next_eval = move_data[i + 1]["eval"]
            
            if current["turn"] == "white":
                delta = next_eval - current["eval"]
            else:
                delta = current["eval"] - next_eval

            penalty = delta_to_penalty(delta)
            accuracy = round(max(0, penalty))
            

            board.set_fen(current["fen"])
            move_obj = board.parse_san(current["move"])
            uci_move = move_obj.uci()
            
            opening_name = get_opening(current["fen"])

            if opening_name:
                classification = "theory"
                matched_opening = opening_name

                
            else:
                if delta == 0:
                    is_sacrifice, is_hanging, _ = is_potential_sacrifice(board, chess.Move.from_uci(uci_move))
                    if (is_sacrifice or is_hanging) and delta < 2:
                        classification = "Brilliant"
                else:
                        classification = classify_move(delta=delta)

            
     

            current.update({
                "delta": delta,
                "penalty": penalty,
                "accuracy": accuracy,
                "classification": classification,
                "uci": uci_move
                
            })

        white_total, white_count = 0, 0
        black_total, black_count = 0, 0

        for move in move_data[:-1]:
            if move["turn"] == "white":
                white_total += move["accuracy"]
                white_count += 1
            else:
                black_total += move["accuracy"]
                black_count += 1

     
        
        accuracyForWhite = (f"White: {round(white_total / max(1, white_count), 2)}")
        accuracyForBlack = (f"Black: {round(black_total / max(1, black_count), 2)}")
        total = [{
            "black": accuracyForBlack,
            "white": accuracyForWhite
        }]
        return move_data, total, matched_opening

    def close(self):
        self.engine.quit()
    


path = "C:\\Users\\miti\\chessAnalysis\\algorthiem\\py\\chess-review\\chess.pgn"
game = load_game(path)
analyzer = StockfishAnalyzer()
analyzer.analysis(game)
analyzer.close()
