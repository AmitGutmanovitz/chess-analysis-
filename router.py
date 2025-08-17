from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
import chess.pgn
import io
import asyncio

class AnalyzeRequest(BaseModel):
    pgn: str

router = APIRouter()

@router.post("/analyze")
async def analyze_game(request_body: AnalyzeRequest, request: Request):
    try:
        game = chess.pgn.read_game(io.StringIO(request_body.pgn))
        if game is None:
            raise ValueError("Invalid PGN")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid PGN format: {e}")

    # קח את ה-Stockfish מהשרת (נשמר בזמן עליית השרת)
    analyzer = request.app.state.stockfish

    move_data, total, matched_opening = analyzer.analysis(game)


    # החזרת המידע
    return {
        "moves": [
            {
                "move": move["move"],
                "turn": move["turn"],
                "accuracy": move["accuracy"],
                "classification": move["classification"],
                "eval": move["eval"]
                
            }
            for move in move_data[:-1]
        ],"accurcy": total[-1],
   "opening": matched_opening if matched_opening else None
    }
       
        



