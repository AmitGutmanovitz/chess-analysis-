



<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Chess } from 'chess.js'

// Don't import ChessBoard - it might not be available as ES module
const myBoard = ref(null)

const chess = new Chess()
const pgn = ref("")
const fen = ref("")
const moveList = ref([])
const moveClassifications = ref([])  // Store move classifications
const currentMoveInfo = ref(null)    // Currently displayed move info
const username = ref("")
let currentMoveIndex = 0
const i = ref(null)
const opening = ref("star ting postion")
const totalAccurcyWhite = ref(100)
const totalAccurcyblack = ref(100)
const openingFen = ref("")
const j = ref(0)
const analyzeing = ref(null)
const evalution = ref(0)

  


// Classification icon mapping - you can customize these paths
import bestMove from "@/assets/download(2).png"
import excellent from "@/assets/exellent.png"
import good from "@/assets/ok.png"
import inaccuracy from "@/assets/download(1).jpeg"
import mistake from "@/assets/download(1).png"
import blunder from "@/assets/download.png"
import brilliant from "@/assets/brilliant.jpg"
import thory from "@/assets/thory.png"
const classificationIcons = {
  
  'Best Move':{icon: bestMove, color: "lime" },     // Green checkmark or star
  'Excellent': {icon: excellent, color: "green"},        // Double star
  'Good':{icon: good, color: "gray"},                  // Single star
  'Inaccuracy': {icon: inaccuracy, color: "yellow"},     // Yellow warning
  'Mistake': {icon: mistake,  color: "orange"},          // Orange X
  'Blunder': {icon: blunder, color: "red"},            // Red X or skull
  'Brilliant': {icon: brilliant, color: "cyan"},        // Purple star
  'theory': {icon:thory, color: "tan"}                  // Book icon
}

// Check if ChessBoard is available and initialize
onMounted(() => {
  console.log('Component mounted, checking for ChessBoard...')
  console.log('window.ChessBoard:', window.ChessBoard)
  console.log('window.Chessboard:', window.Chessboard)

  setTimeout(() => {
    try {
      // Try different ways ChessBoard might be available
      const ChessBoardConstructor = window.ChessBoard || window.Chessboard || window.chessboard
      
      if (ChessBoardConstructor) {
        // Option 1: Use a different piece theme
        myBoard.value = ChessBoardConstructor('myBoard', {
          position: 'start',
          pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png',
          
          
          // Other popular themes:
          // pieceTheme: 'https://chessboardjs.com/img/chesspieces/alpha/{piece}.png'
          // pieceTheme: 'path/to/your/pieces/{piece}.png'
          
        })
        
        
        // Option 2: If you want to use your own images, put them in public/pieces/ folder
        // and use: pieceTheme: '/pieces/{piece}.png'
        
        console.log('Chess board initialized successfully')
      } else {
        console.error('ChessBoard constructor not found on window object')
        console.log('Available on window:', Object.keys(window).filter(key => key.toLowerCase().includes('chess')))
      }
    } catch (error) {
      console.error('Failed to initialize chess board:', error)
    }
  }, 500)
})
function rotateBoard() {
  const current = myBoard.value.orientation()
  myBoard.value.orientation(current === 'white' ? 'black' : 'white')
}
function clearMoveIndicators() {
  const icons = document.querySelectorAll('.classification-icon')
  icons.forEach(icon => icon.remove())
}

async function getPgn() {
  analyzeing.value = true
  try {
    const res = await fetch("http://192.168.1.191:8000/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pgn: pgn.value })
    })
    
    pgn.value = ""

    const data = await res.json()
    console.log("Server Response:", data)

    // Reset the game and clear indicators
    chess.reset()
    currentMoveIndex = 0
    currentMoveInfo.value = null
    clearMoveIndicators()

    // Store the move list and classifications
    moveList.value = data.moves.map(move => move.move)
    moveClassifications.value = data.moves.map(move => ({
      classification: move.classification,
      accuracy: move.accuracy,
      move: move.move,
      evalution: move.eval
    }))
    opening.value = data.opening.name
    totalAccurcyWhite.value = data.accurcy.white
    totalAccurcyblack.value = data.accurcy.black

    // Start the animation
    
  } catch (err) {
    console.error("Error in PGN request:", err)
  }finally{
    analyzeing.value = false
  }
}

function playMoves() {
  chess.reset()
  const interval = setInterval(() => {
    if (currentMoveIndex >= moveList.value.length) {
      clearInterval(interval)
      return
    }

    const move = moveList.value[currentMoveIndex]

    try {
      chess.move(move)
      fen.value = chess.fen()

      // 🟢 Set the move info here!
      currentMoveInfo.value = moveClassifications.value[currentMoveIndex]

      // Update the board
      if (myBoard.value && myBoard.value.position) {
        myBoard.value.position(fen.value)
      } else {
        console.error('Board not initialized or position method not available')
      }

      currentMoveIndex++
    } catch (error) {
      console.error("Invalid move:", move, error)
      clearInterval(interval)
    }
  }, 1350)
}function startBoard(){
  myBoard.value.start()
}
function toogleMove(index) {
  try {
    chess.reset() // ✅ חשוב!
    for (let i = 0; i <= index; i++) {
      chess.move(moveList.value[i])
    }

    fen.value = chess.fen()
    currentMoveInfo.value = moveClassifications.value[index]

    if (myBoard.value && myBoard.value.position) {
      myBoard.value.position(fen.value)
    } else {
      console.error('Board not initialized or position method not available')
    }
  } catch (error) {
    console.error("Invalid move:", moveList.value[index], error)
  }
}

function replayMoves() {
  chess.reset();
  currentMoveIndex = 0;
  currentMoveInfo.value = null;

  if (myBoard.value && myBoard.value.position) {
    myBoard.value.position('start');
  }

  playMoves();
}
async function chessCom() {
  try {
    const realUserName = username.value;
    const time = new Date();
    const year = time.getFullYear();
    const month = String(time.getMonth() + 1).padStart(2, '0');

    const response = await fetch(
      `https://api.chess.com/pub/player/${realUserName}/games/${year}/${month}`,
      {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      }
    );

    const data = await response.json();

    if (data.games && data.games.length > 0) {
      
      const pgnFull = data.games[data.games.length - 1].pgn;
    const moves = pgnFull.split('\n\n')[1]; // This grabs the moves section (may be multiline)
    
      
const pgnClean = moves.replace(/\{[^}]*\}/g, '').trim();
pgn.value = pgnClean



 

     
    } else {
      console.log("No games found.");
      pgn.value = "[no games has been found]";
    }
    }catch(err){
      console.error(err)
    }
}


</script>

<template>
  <main class="app">
    <!-- Form Section with Move Info Below -->
    <section class="form-section">
      <h1 class="title" >Chess PGN Analysis</h1>
      <input v-if="!analyzeing" v-model="pgn" type="text" placeholder="Enter PGN" class="input" style="height: 120px; " />
      <div v-else>
        <h1 style="color: orange;">loading... </h1>
      </div>
      
      <!-- Add this right after your username input section -->
<div v-if="data?.games?.length" class="game-buttons-container">
  <div class="game-buttons-scroll">
    <button 
      v-for="(game, index) in data.games" 
      :key="index"
      @click="pgn = game.pgn.split('\n\n')[1].replace(/\{[^}]*\}/g, '').trim()"
      class="game-btn"
    >
      {{ new Date(game.end_time * 1000).toLocaleDateString() }}
    </button>
  </div>
</div>
      <!-- Move Classification Display -->
      <div class="move-classification-container" v-if="currentMoveInfo">
        <div class="move-classification-panel" :style="{ backgroundColor: classificationIcons[currentMoveInfo.classification]?.color }">
          <div class="move-header">
            <h2 class="move-text">{{ currentMoveInfo.move }}</h2>
          </div>
          <div class="classification-display">
            <img v-if="classificationIcons[currentMoveInfo.classification]"
              :src="classificationIcons[currentMoveInfo.classification].icon"
              class="classification-badge" />
            <div class="classification-text">
              <span class="classification-label">{{ currentMoveInfo.classification }}</span>
              <span v-if="currentMoveInfo.accuracy" class="accuracy-text">
                Accuracy: {{ currentMoveInfo.accuracy }}%
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="form-buttons">
        <button @click="getPgn" class="btn">Analyze</button>
        <button @click="i = !i" class="btn secondary">Chess.com Username</button>
      </div>
      <div v-if="i" class="username-box">
        <input type="text" v-model="username" placeholder="Enter your username" class="input" />
        <button @click="chessCom" class="btn">Submit</button>
      </div>
      <!-- Add this right after your username input section -->
<div v-if="data?.games?.length" class="game-choices">
  <div 
    v-for="(game, index) in data.games" 
    :key="index"
    @click="pgn = game.pgn.split('\n\n')[1].replace(/\{[^}]*\}/g, '').trim()"
    class="game-choice"
  >
    Game {{ index + 1 }} ({{ new Date(game.end_time * 1000).toLocaleDateString() }})
  </div>
</div>
    </section>

    <!-- Board Section -->
    <section class="board-section">
      <div class="board-container">
        <div id="myBoard" class="board"></div>
        <section>
          <div class="eval-bar-container">
            <div class="eval-bar-white" 
                 :style="{ height: (50 + (currentMoveInfo?.evalution / 18)) + '%' }"></div>
            <div class="eval-bar-black" 
                 :style="{ height: (50 - (currentMoveInfo?.evalution / 18)) + '%' }"></div>
          </div>
          <h2 v-if="currentMoveInfo?.evalution" class="eval-text">{{ currentMoveInfo.evalution <= 0 ?  + (currentMoveInfo.evalution / 100).toFixed(2): "+"+(currentMoveInfo.evalution / 100).toFixed(2)}}</h2>
        </section>
      </div>

      <div class="controls">
        <button @click="playMoves" class="control-btn play-btn">Play Game</button>
        <button @click="() => { if (j < moveList.length - 1) toogleMove(++j) }" class="control-btn forward-btn">Move Forward</button>
        <button @click="() => { if (j > 0) toogleMove(--j) }" class="control-btn backward-btn">Move Backward</button>  
        <button @click="replayMoves" class="control-btn replay-btn">Replay</button>
        <button @click="rotateBoard" class="control-btn flip-btn">Flip Board</button>
        <button @click="startBoard" class="control-btn start-btn">Start Board</button>
      </div>

      <div class="stats-panel">
        <h3 class="stat-item"><strong>White Accuracy:</strong> {{ totalAccurcyWhite }}%</h3>
        <hr class="divider">
        <h3 class="stat-item"><strong>Black Accuracy:</strong> {{ totalAccurcyblack }}%</h3>
        <hr class="divider">
        <h3 class="stat-item"><strong>Opening:</strong> {{ opening }}</h3>
      </div>
    </section>

    <p v-if="!myBoard" class="loading">Loading chess board...</p>
  </main>
</template>

<style>

:root {
  --primary: #6366f1;
  --primary-hover: #4f46e5;
  --secondary: #71717a;
  --dark: #18181b;
  --darker: #09090b;
  --light: #f4f4f5;
  --success: #22c55e;
  --warning: #f59e0b;
  --danger: #ef4444;
  --border: #3f3f46;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.app {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
  font-family: 'Courier New', Courier, monospace;
}

@media (min-width: 1024px) {
  .app {
    grid-template-columns: 350px 1fr;
  }
}
.game-choices {
  margin-top: 15px;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #3d566e;
  border-radius: 5px;
}

.game-choice {
  padding: 10px;
  cursor: pointer;
  border-bottom: 1px solid #3d566e;
  transition: background 0.2s;
}

.game-choice:hover {
  background: #3d566e;
}

.game-choice:last-child {
  border-bottom: none;
}
.game-choice:hover {
  background: #3d566e;
}

.game-choice:last-child {
  border-bottom: none;
}
/* Add this to your CSS */
.game-buttons-container {
  margin: 15px 0;
  padding: 10px;
  background: #2d3e50;
  border-radius: 8px;
}

.game-buttons-scroll {  
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 5px 0;
}

.game-btn {
  flex: 0 0 auto;  
  padding: 8px 12px;
  background: #34495e;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap;
}

.game-btn:hover {
  background: #3d566e;
}
/* Form Section */
.form-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
  background: #1e1e1e;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.title {
  color: white;
  text-align: center;
  margin-bottom: 1rem;
}

.input {
  padding: 0.75rem 1rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--darker);
  color: white;
  font-size: 1rem;
  width: 100%;
}

.btn {
  padding: 0.75rem;
  border: none;
  border-radius: 8px;
  background: var(--primary);
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.btn.secondary {
  background: var(--secondary);
}

.form-buttons {
  display: flex;
  gap: 0.5rem;
}

.username-box {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

/* Move Classification Panel */
.move-classification-container {
  margin-top: 1rem;
}

.move-classification-panel {
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.move-header {
  margin-bottom: 1rem;
}

.move-text {
  color: black;
  font-size: 1.5rem;
  text-align: center;
  margin-bottom: 1rem;
}

.classification-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.9);
}

.classification-badge {
  width: 60px;
  height: 60px;
}

.classification-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.classification-label {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
}

.accuracy-text {
  font-size: 1.1rem;
  color: #555;
}

/* Board Section */
.board-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.board-container {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.board {
  width: 600px;
  height: 600px;
  border: 5px solid burlywood;
  border-radius: 3px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

/* Evaluation Bar */
.eval-bar-container {
  width: 24px;
  height: 300px;
  display: flex;
  flex-direction: column;
  border: 1px solid #333;
  border-radius: 10px;
  overflow: hidden;
  background: #444;
}

.eval-bar-white {
  background-color: #f0f0f0;
  transition: height 0.3s ease;
}

.eval-bar-black {
  background-color: #222;
  transition: height 0.3s ease;
}

.eval-text {
  color: white;
  font-size: 1.2rem;
  font-weight: bold;
  text-align: center;
  margin-top: 0.5rem;
}

/* Controls */
.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: center;
  margin-top: 1rem;
}

.control-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 120px;
}

.play-btn { background-color: #3b82f6; color: white; }
.forward-btn { background-color: #10b981; color: white; }
.backward-btn { background-color: #10b981; color: white; }
.replay-btn { background-color: #ef4444; color: white; }
.flip-btn { background-color: #f97316; color: white; }
.start-btn { background-color: #8b5cf6; color: white; }

.control-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

/* Stats Panel */
.stats-panel {
  background: palevioletred;
  border: 2px dotted white;
  border-radius: 12px;
  padding: 1.5rem;
  width: 300px;
  margin: 0 auto;
}

.stat-item {
  margin: 0.5rem 0;
  text-align: center;
  color: black;
  font-size: 1.1rem;
}

.divider {
  border: none;
  border-top: 1px solid rgba(0, 0, 0, 0.2);
  margin: 0.75rem 0;
}

/* Responsive Adjustments */
@media (max-width: 1200px) {
  .board {
    width: 500px;
    height: 500px;
  }
}

@media (max-width: 768px) {
  .board {
    width: 100%;
    height: auto;
    aspect-ratio: 1/1;
  }
  
  .stats-panel {
    width: 100%;
  }
}

.loading {
  text-align: center;
  color: white;
  margin-top: 2rem;
}
</style>