from fastapi import FastAPI
from router import router
from analyzer import StockfishAnalyzer
from fastapi import FastAPI, WebSocket
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # או רשימת כתובות Frontend שלך
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
def startup_event():
    print("🔁 Launching Stockfish...")
    app.state.stockfish = StockfishAnalyzer()

@app.on_event("shutdown")
def shutdown_event():
    print("🛑 Shutting down Stockfish...")
    app.state.stockfish.close()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        print(f"📥 Received from client: {data}")
        await websocket.send_text(f"Server received: {data}")



app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    