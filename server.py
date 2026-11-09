from flask import Flask, request, jsonify, render_template_string, send_from_directory
import os

app = Flask(__name__)

# --- STRICT SEQUENTIAL NODE TRIGGER ORDER (1 to 10) ---
REVEAL_SEQUENCE = [3, 6, 10, 4, 1, 9, 7, 5, 2, 8]

# --- MAPPING EACH NODE TO ITS SPECIFIC PUZZLE PIECE IMAGE COORDINATE ---
NODE_TO_PIECE = {
    1: 3,   # Phone reveals Piece 3
    2: 6,   # Book reveals Piece 6
    3: 10,  # Lamp reveals Piece 10
    4: 4,   # Chest reveals Piece 4
    5: 1,   # Painting reveals Piece 1
    6: 9,   # Crystal Ball reveals Piece 9
    7: 7,   # Study reveals Piece 7
    8: 5,   # Barrel reveals Piece 5
    9: 2,   # Cauldron reveals Piece 2
    10: 8   # Statue reveals Piece 8
}

NODE_NAMES = {
    1: "Node A (The Telephone) - Puzzle Piece 3",
    2: "Node B (The Book) - Puzzle Piece 6",
    3: "Node C (The Moon Lamp) - Puzzle Piece 10",
    4: "Node D (The Treasure Chest) - Puzzle Piece 4",
    5: "Node E (The Painting) - Puzzle Piece 1",
    6: "Node F (The Crystal Ball) - Puzzle Piece 9",
    7: "Node G (The Alchemist Study) - Puzzle Piece 7",
    8: "Node H (The Barrel) - Puzzle Piece 5",
    9: "Node I (The Cauldron) - Puzzle Piece 2",
    10: "Node J (The Statue) - Puzzle Piece 8"
}

scoreboard_data = {
    "total_points": 0,    
    "max_points": 10,
    "unlocked_pieces": []  # Tracks exact puzzle layout pieces independently of score index
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cadette Quest Puzzle Scoreboard</title>
    <style>
        body { font-family: 'Arial', sans-serif; background: #0b0b16; color: #fff; text-align: center; padding: 10px; margin: 0; overflow-x: hidden; position: relative; min-height: 100vh; }
        .container { display: inline-block; padding: 25px 20px; border-radius: 24px; background: #13132b; box-shadow: 0 0 50px rgba(0, 255, 245, 0.15); width: 100%; max-width: 1250px; box-sizing: border-box; position: relative; z-index: 2; margin-top: 15px; border: 1px solid rgba(0, 255, 245, 0.2); }
        h1 { color: #00fff5; font-size: 2.5em; margin: 0 0 5px 0; text-transform: uppercase; letter-spacing: 4px; text-shadow: 0 0 15px rgba(0,255,245,0.6); font-weight: 900; }
        .subtitle { color: #b4be91; font-size: 1.3em; margin-bottom: 25px; font-weight: bold; letter-spacing: 1px; }
        
        /* DEBUG CONTROL PANEL HOUSING - Change 'display: flex' to 'display: none' to hide entirely after debugging */
        .debug-panel { display: flex; justify-content: center; gap: 15px; margin-bottom: 25px; padding: 15px; background: rgba(255,255,255,0.03); border: 1px dashed rgba(0,255,245,0.3); border-radius: 12px; }
        .btn { padding: 10px 20px; font-size: 0.95em; font-weight: bold; border-radius: 8px; cursor: pointer; border: none; transition: all 0.2s ease; text-transform: uppercase; letter-spacing: 1px; }
        .btn-sim { background: #00fff5; color: #0b0b16; box-shadow: 0 0 15px rgba(0,255,245,0.3); }
        .btn-sim:hover { background: #00cccc; transform: scale(1.02); }
        .btn-reset { background: #ff007f; color: #fff; box-shadow: 0 0 15px rgba(255,0,127,0.3); }
        .btn-reset:hover { background: #cc0066; transform: scale(1.02); }

        .puzzle-board { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; background: #05050f; padding: 15px; border-radius: 16px; border: 3px solid #00fff5; box-shadow: 0 0 30px rgba(0,0,0,0.9); margin: 0 auto; transition: all 1s ease; }
        .piece { width: 100%; aspect-ratio: 1 / 1; background-image: url('/static/puzzle.jpg'); background-size: 500% 200%; transition: all 0.8s cubic-bezier(0.25, 1, 0.5, 1); border-radius: 8px; box-sizing: border-box; border: 1px solid rgba(255,255,255,0.05); }
        .locked { filter: grayscale(100%) brightness(15%) contrast(140%); opacity: 0.2; box-shadow: inset 0 0 30px #000; transform: scale(0.96); }
        .unlocked { filter: grayscale(0%) brightness(100%); opacity: 1; box-shadow: 0 0 25px rgba(0, 255, 245, 0.4); transform: scale(1); animation: popIn 0.5s ease-out; }
        
        /* Grid Coordinates Mapping */
        .p1  { background-position: 0% 0%; } .p2  { background-position: 25% 0%; } .p3  { background-position: 50% 0%; } .p4  { background-position: 75% 0%; } .p5  { background-position: 100% 0%; }
        .p6  { background-position: 0% 100%; } .p7  { background-position: 25% 100%; } .p8  { background-position: 50% 100%; } .p9  { background-position: 75% 100%; } .p10 { background-position: 100% 100%; }
        
        /* Victory Graphic Overlays */
        .victory-msg { margin-top: 30px; font-size: 1.8em; color: #ff007f; font-weight: bold; text-shadow: 0 0 20px rgba(255,0,127,0.8), 0 0 40px rgba(0,255,245,0.5); animation: pulse 1.2s infinite alternate; display: none; }
        .victory-glow { border-color: #ff007f !important; box-shadow: 0 0 50px rgba(255, 0, 127, 0.6) !important; }
        
        #victory-canvas { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 1; pointer-events: none; display: none; }

        @keyframes popIn { 0% { transform: scale(0.6); filter: brightness(300%); } 100% { transform: scale(1); filter: brightness(100%); } }
        @keyframes pulse { 0% { transform: scale(1); } 100% { transform: scale(1.04); text-shadow: 0 0 30px rgba(255,0,127,1), 0 0 10px #fff; } }
        @media(min-width: 768px) { body { padding: 20px; } h1 { font-size: 3.8em; } .subtitle { font-size: 1.6em; } .victory-msg { font-size: 2.6em; } }
        @media(max-width: 500px) { .puzzle-board { grid-template-columns: repeat(2, 1fr); } }
    </style>
</head>
<body>
    <canvas id="victory-canvas"></canvas>

    <div class="container" id="main-container">
        <h1>✨ CADETTE QUEST ✨</h1>
        <div id="clues-display" class="subtitle">Clues: 0 / 10</div>
        
        <!-- --- HIDDEN CONTROL INTERFACE PANEL HOUSING --- -->
        <div class="debug-panel">
            <button class="btn btn-sim" onclick="triggerNextSimulatedStep()">🪄 Simulate Next Step</button>
            <button class="btn btn-reset" onclick="triggerEcosystemReset()">🔄 Reset Quest Board</button>
        </div>

        <div class="puzzle-board" id="board-element">
            <div id="piece-1" class="piece p1 locked"></div><div id="piece-2" class="piece p2 locked"></div><div id="piece-3" class="piece p3 locked"></div><div id="piece-4" class="piece p4 locked"></div><div id="piece-5" class="piece p5 locked"></div>
            <div id="piece-6" class="piece p6 locked"></div><div id="piece-7" class="piece p7 locked"></div><div id="piece-8" class="piece p8 locked"></div><div id="piece-9" class="piece p9 locked"></div><div id="piece-10" class="piece p10 locked"></div>
        </div>
        <div id="victory-banner" class="victory-msg">🎉 QUEST COMPLETE!<br>The Master Puzzle is Restored! 🎉</div>
    </div>

    <script>
        const soundMap = { 1: "/static/sound1.wav", 2: "/static/sound2.wav", 3: "/static/sound3.wav", 4: "/static/sound4.wav", 5: "/static/sound5.wav", 6: "/static/sound6.wav", 7: "/static/sound7.wav", 8: "/static/sound8.wav", 9: "/static/sound9.wav", 10: "/static/sound10.wav" };
        let lastKnownScore = -1;
        let victoryAudioPlayed = false;
        
        const canvas = document.getElementById('victory-canvas');
        const ctx = canvas.getContext('2d');
        let particles = [];
        let animationFrameId = null;

        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        class Particle {
            constructor() {
                this.x = Math.random() * canvas.width;
                this.y = canvas.height + Math.random() * 100;
                this.size = Math.random() * 3 + 2;
                this.speedX = Math.random() * 3 - 1.5;
                this.speedY = -(Math.random() * 4 + 2);
                this.color = Math.random() > 0.5 ? '#00fff5' : '#ff007f';
                this.alpha = 1;
                this.decay = Math.random() * 0.01 + 0.005;
            }
            update() {
                this.x += this.speedX;
                this.y += this.speedY;
                this.alpha -= this.decay;
            }
            draw() {
                ctx.save();
                ctx.globalAlpha = this.alpha;
                ctx.shadowBlur = 10;
                ctx.shadowColor = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
                ctx.restore();
            }
        }

        function animateParticles() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            if (particles.length < 120) {
                particles.push(new Particle());
            }
            for (let i = particles.length - 1; i >= 0; i--) {
                particles[i].update();
                particles[i].draw();
                if (particles[i].alpha <= 0 || particles[i].y < -20) {
                    particles.splice(i, 1);
                }
            }
            animationFrameId = requestAnimationFrame(animateParticles);
        }

        // JS DEBUG INJECTION: Simulate a physical node pulse sequentially via AJAX
        function triggerNextSimulatedStep() {
            fetch('/api/debug/simulate-next', { method: 'POST' })
                .then(r => r.json())
                .then(d => console.log("Debug Step Response:", d))
                .catch(e => console.error(e));
        }

        // JS DEBUG INJECTION: Clean wiping transaction request
        function triggerEcosystemReset() {
            fetch('/api/debug/reset', { method: 'POST' })
                .then(r => r.json())
                .then(d => {
                    console.log("System wiped:", d);
                    lastKnownScore = -1; // Force layout calculations to recalibrate
                })
                .catch(e => console.error(e));
        }

        function checkScoreboardUpdate() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    const currentScore = data.total_points;
                    const unlockedPieces = data.unlocked_pieces || [];
                    document.getElementById('clues-display').innerText = `Clues: ${currentScore} / 10`;

                    if (currentScore !== lastKnownScore) {
                        for (let i = 1; i <= 10; i++) {
                            const targetElement = document.getElementById(`piece-${i}`);
                            if (unlockedPieces.includes(i)) {
                                targetElement.className = `piece p${i} unlocked`;
                            } else {
                                targetElement.className = `piece p${i} locked`;
                            }
                        }
                        
                        if (currentScore >= 10) {
                            document.getElementById('victory-banner').style.display = "block";
                            document.getElementById('board-element').classList.add('victory-glow');
                            canvas.style.display = "block";
                            if (!animationFrameId) animateParticles();
                            
                            if (!victoryAudioPlayed) {
                                victoryAudioPlayed = true;
                                new Audio('/audio/victory.wav').play().catch(e => console.log("Victory audio blocked:", e));
                            }
                        } else {
                            document.getElementById('victory-banner').style.display = "none";
                            document.getElementById('board-element').classList.remove('victory-glow');
                            canvas.style.display = "none";
                            victoryAudioPlayed = false;
                            if (animationFrameId) {
                                cancelAnimationFrame(animationFrameId);
                                animationFrameId = null;
                            }
                        }
                        
                        if (lastKnownScore !== -1 && currentScore > lastKnownScore && currentScore < 10 && soundMap[currentScore]) {
                            new Audio(soundMap[currentScore]).play().catch(e => console.log("Audio blocked:", e));
                        }
                        lastKnownScore = currentScore;
                    }
                }).catch(err => console.error("Error connecting to server backend:", err));
        }
        setInterval(checkScoreboardUpdate, 1000);
        window.onload = checkScoreboardUpdate;
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def api_status():
    return jsonify(scoreboard_data)

@app.route('/score', methods=['POST'])
def receive_score():
    req_data = request.get_json()
    if not req_data or "node_id" not in req_data:
        return jsonify({"status": "error", "message": "Missing node_id parameter"}), 400

    incoming_node = int(req_data.get("node_id"))
    current_score = scoreboard_data["total_points"]

    if current_score >= scoreboard_data["max_points"]:
        return jsonify({"status": "ignored", "message": "Max score already reached"}), 200

    expected_node = REVEAL_SEQUENCE[current_score]

    # Handle Re-activation
    if incoming_node in REVEAL_SEQUENCE[:current_score]:
        print(f"🔄 Re-activation Event: {NODE_NAMES.get(incoming_node, 'Unknown Node')} triggered again.")
        return jsonify({"status": "success", "message": "Already unlocked. Proceed with animation physical output sequence."}), 200

    # Handle correct sequence hit
    if incoming_node == expected_node:
        scoreboard_data["total_points"] += 1
        assigned_piece = NODE_TO_PIECE.get(incoming_node)
        if assigned_piece:
            scoreboard_data["unlocked_pieces"].append(assigned_piece)

        print(f"🎯 Sequence Match! {NODE_NAMES.get(incoming_node)} hit successfully. Added Piece {assigned_piece}. Progress: {scoreboard_data['total_points']}/10")
        return jsonify({"status": "success", "new_score": scoreboard_data["total_points"]}), 200

    print(f"❌ Out-of-Order Block: {NODE_NAMES.get(incoming_node, 'Unknown Node')} attempted to connect, but the room is waiting on {NODE_NAMES.get(expected_node)}.")
    return jsonify({"status": "blocked", "message": f"Out of order sequence. Room is currently waiting for node {expected_node}."}), 200

## --- BACKEND SERVER DEBUG ROUTE: SIMULATE SEQUENTIAL HARDWARE PULSE ---
@app.route('/api/debug/simulate-next', methods=['POST'])
def debug_simulate_step():
    current_score = scoreboard_data["total_points"]
    if current_score >= scoreboard_data["max_points"]:
        return jsonify({"status": "ignored", "message": "Scoreboard already full."}), 200

    # Simulate the exact hardware node currently expected next in queue
    simulated_node = REVEAL_SEQUENCE[current_score]
    scoreboard_data["total_points"] += 1

    assigned_piece = NODE_TO_PIECE.get(simulated_node)
    if assigned_piece:
        scoreboard_data["unlocked_pieces"].append(assigned_piece)

    print(f"⚙️ DEBUG INJECTION: Successfully simulated hit on {NODE_NAMES.get(simulated_node)}. Fragment {assigned_piece} unlocked.")
    return jsonify({"status": "simulated", "injected_node": simulated_node, "revealed_piece": assigned_piece, "new_score": scoreboard_data["total_points"]}), 200

## --- BACKEND SERVER DEBUG ROUTE: COLD FLUSH DATA MEMORY ARRAYS ---
@app.route('/api/debug/reset', methods=['POST'])
def debug_reset_board():
    scoreboard_data["total_points"] = 0
    scoreboard_data["unlocked_pieces"] = []
    print("🧹 DEBUG INJECTION: Scoreboard arrays completely flushed to active zero state.")
    return jsonify({"status": "wiped", "total_points": 0, "unlocked_pieces": []}), 200

## --- AUDIO ASSET ROUTING ---
@app.route('/audio/barnaby.wav')
def stream_barrel_audio():
    return send_from_directory(os.getcwd(), 'barnaby.wav', as_attachment=True)

@app.route('/audio/victory.wav')
def stream_victory_audio():
    return send_from_directory(os.getcwd(), 'victory.wav', as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
