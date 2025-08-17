import chess
import chess.pgn

def classify_move(delta):
    delta = abs(delta)
    if delta <= 5:
        return 'exellent'
    elif delta <= 10:
        return "Excellent"
    elif delta < 30:
        return "Good"
    elif delta < 80:
        return "Inaccuracy"
    elif delta < 200:
        return "Mistake"
    else:
        return "Blunder"




PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 1000  # רק למניעת בעיות, לא רלוונטי לתקיפה רגילה
}

def static_exchange_eval(board: chess.Board, square: chess.Square) -> int:
    """
    מבצע הערכה סטטית של חילופים על משבצת (SEE).
    מחזיר את הרווח הצפוי של היריב אם יתחיל לאכול את הכלי.
    """
    board = board.copy()  # לא לשנות את הלוח המקורי

    target_piece = board.piece_at(square)
    if not target_piece:
        return 0  # אין מה לאכול

    gains = []
    side = not board.turn  # היריב מתחיל לתקוף
    attackers = {True: list(board.attackers(True, square)), False: list(board.attackers(False, square))}

    def get_least_valuable_attacker(color):
        # החזר את הכלי הכי זול שתוקף את המשבצת
        min_value = float('inf')
        min_square = None
        for sq in attackers[color]:
            piece = board.piece_at(sq)
            if piece:
                value = PIECE_VALUES[piece.piece_type]
                if value < min_value:
                    min_value = value
                    min_square = sq
        return min_square

    # התחלה: היריב אוכל את הכלי שעל המשבצת
    gains.append(PIECE_VALUES[target_piece.piece_type])

    while True:
        attacker_sq = get_least_valuable_attacker(side)
        if attacker_sq is None:
            break

        # הסר את הכלי שתוקף
        piece_type = board.piece_at(attacker_sq).piece_type
        attackers[side].remove(attacker_sq)
        board.remove_piece_at(attacker_sq)

        # הוסף רווח/הפסד לפי הסדר ההתקפי
        gain = PIECE_VALUES[piece_type] - gains[-1]
        gains.append(gain)

        side = not side  # החלף צד

    # חישוב הרווח המצטבר הטוב ביותר
    for i in range(len(gains) - 2, -1, -1):
        gains[i] = max(-gains[i + 1], gains[i])

    return gains[0]



def analyze_square(board: chess.Board, square: chess.Square):
    piece = board.piece_at(square)
    if not piece:
        return {"error": "No piece on that square."}

    color = piece.color
    enemy_color = not color

    attackers = board.attackers(enemy_color, square)
    defenders = board.attackers(color, square)

    attackers_info = [
        {
            "square": chess.square_name(sq),
            "piece": board.piece_at(sq).symbol(),
            "value": PIECE_VALUES[board.piece_at(sq).piece_type]
        }
        for sq in attackers
    ]

    defenders_info = [
        {
            "square": chess.square_name(sq),
            "piece": board.piece_at(sq).symbol(),
            "value": PIECE_VALUES[board.piece_at(sq).piece_type]
        }
        for sq in defenders
    ]




        


    total_attack_value = sum(a["value"] for a in attackers_info)
    total_defend_value = sum(d["value"] for d in defenders_info)

    is_protected = len(defenders) > 0
    is_attacked = len(attackers) > 0

    # קביעת האם הכלי "תלוי" לפי SEE
    see_gain = static_exchange_eval(board, square)
    piece_value = PIECE_VALUES[piece.piece_type]
    is_hanging = see_gain >= piece_value

    # אם היריב ירוויח — הכלי בסכנה
    
    return {
        "square": chess.square_name(square),
        "piece": piece.symbol(),
        "is_attacked": is_attacked,
        "is_protected": is_protected,
        "is_hanging": is_hanging,
        "see_gain": see_gain,
        "attackers": attackers_info,
        "defenders": defenders_info,
        "attack_value_sum": total_attack_value,
        "defend_value_sum": total_defend_value,
    }




# נבדוק את החייל ב-d4
import chess

def brillant(fen: str, uci_move: str, delta: float):
    """
    Determines whether a move is 'brilliant'.

    Parameters:
        fen (str): The FEN string before the move
        uci_move (str): The move in UCI format (e.g., 'e2e4')
        delta (float): Evaluation difference after the move (positive is worse)
        mate (bool): True if the move leads to a mate sequence

    Returns:
        bool: True if the move is brilliant
    """
    try:
        board = chess.Board(fen)
        move = chess.Move.from_uci(uci_move)

        if move not in board.legal_moves:
            return False  # invalid move

        # Apply the move before analyzing the destination square
        board.push(move)

        info = analyze_square(board, move.to_square)

        if not info or "error" in info:
            return False  # can't analyze the piece after the move

        is_sacrifice = info["see_gain"] >= 2 
        is_low_delta = delta <= 0.5  # still a great move
        is_brilliant_mate = board.is_checkmate()

    
        if is_sacrifice and (is_low_delta or is_brilliant_mate):
            return True  # a good sacrifice = brilliant
        else:
            return False

    except Exception as e:
        print(f"Error in brillant(): {e}")
        return False



    