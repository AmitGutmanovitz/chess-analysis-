import chess

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

def is_potential_sacrifice(board: chess.Board, move: chess.Move) -> tuple:
    
    ##Detects if a move is a potential sacrifice by either:
    ##1. Immediate material loss (direct sacrifice), OR
   ## 2. Leaving material vulnerable to capture (hanging pieces)
    
    ##Returns: (is_sacrifice, is_hanging, hanging_info)


    
    temp_board = board.copy()
    player = temp_board.turn

    capture_value = 0
    if board.is_capture(move):
        captured_piece = board.piece_at(move.to_square)
        if captured_piece:
            capture_value = PIECE_VALUES[captured_piece.piece_type]

    moved_piece = board.piece_at(move.from_square)
    moved_value = PIECE_VALUES[moved_piece.piece_type] if moved_piece else 0

    if capture_value >= moved_value:

        return (False, False, None)



    material_before = sum(
        PIECE_VALUES[p.piece_type] 
        for p in temp_board.piece_map().values() 
        if p.color == player
    )
    
    temp_board.push(move)
    material_after = sum(
        PIECE_VALUES[p.piece_type] 
        for p in temp_board.piece_map().values() 
        if p.color == player
    )
    

    if board.is_capture(move):
        captured_piece = board.piece_at(move.to_square)
        if captured_piece:
            material_after += PIECE_VALUES[captured_piece.piece_type]
    
    immediate_sacrifice = (material_after - material_before) < 0 
 
    hanging_pieces = []
    opponent = not player
    
    for square in chess.SQUARES:
        piece = temp_board.piece_at(square)
        if not piece or piece.color != player: 
            continue
            
        attackers = temp_board.attackers(opponent, square)
        if not attackers:
            continue
            

        best_capture_gain = -999
        best_attacker = None
        
        for attacker_sq in attackers:
            attacker = temp_board.piece_at(attacker_sq)
            if not attacker:
                continue
                

            capture_gain = PIECE_VALUES[piece.piece_type] - PIECE_VALUES[attacker.piece_type]
            
            if capture_gain > best_capture_gain:
                best_capture_gain = capture_gain
                best_attacker = attacker_sq
        

        if best_capture_gain >= 0:
            hanging_pieces.append({
                'piece': piece,
                'square': square,
                'best_capture': chess.Move(best_attacker, square),
                'material_gain': best_capture_gain
            })
    
    is_hanging = len(hanging_pieces) > 0

    is_sacrifice = immediate_sacrifice or is_hanging
    
    return (
        is_sacrifice,
        is_hanging,
        hanging_pieces if is_hanging else None
    )


