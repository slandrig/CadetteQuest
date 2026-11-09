# CADETTE QUEST PROTOTYPE ARCHITECTURE & STATE

## 1. ECOSYSTEM OVERVIEW
The puzzle system consists of three independent hardware/software nodes operating over a local network. Game state and scoring logic are managed locally by a centralized Flask web panel, while edge components rely on local lockouts cleared explicitly via physical hardware power-cycles (resets) to fit a reliable room reset workflow.

*   **Central Server:** Flask Web Interface (`server.py`) running on `192.168.86.52:5000`.
*   **Node A (The Telephone):** Raspberry Pi 3/4/5 (`phone.py`) running Linux Python 3.
*   **Node B (The Book):** Raspberry Pi Pico W (`book.py`) running MicroPython.
*   **Node C (The Lamp):** Raspberry Pi Pico W (`lamp.py`) running MicroPython.
*   **Node D (The Chest):** Raspberry Pi Pico W (`chest.py`) running MicroPython.
*   **Node E (The Painting):** Raspberry Pi Pico W (`painting.py`) running MicroPython.
*   **Node F (The Crystal Ball):** Raspberry Pi Pico W (`crystal.py`) running MicroPython.
*   **Node G (The Alchemist Study):** Raspberry Pi Pico W (`study.py`) running MicroPython.
*   **Node H (The Barrel):** Raspberry Pi Pico W (`barrel.py`) running MicroPython.
*   **Node I (The Cauldron):** Raspberry Pi Pico W (`cauldron.py`) running MicroPython.
*   **Node J (The Statue):** Raspberry Pi Pico W (`statue.py`) running MicroPython.
Raspberry Pi B (`crystal.py`) running Linux Python 3.
---

## 2. HARDWARE MAP & WIRE TABLES

### NODE A: 3D-PRINTED TELEPHONE (Raspberry Pi Standalone)
*   **Processor:** Raspberry Pi Single Board Computer (SBC)
*   **Wand Detector:** TSOP IR Sensor Module
*   **Hook Tracking:** Photoelectric Sensor / Mechanical Microswitch tracking receiver position
*   **Audio Output:** Native ALSA layer (3.5mm jack or HDMI audio breakout mapped to `mplayer`)

### NODE B: 3D-PRINTED Book (Pico W)
*   **Microcontroller:** Raspberry Pi Pico W
*   **IR Receiver:** TSOP38238 (Tuned to MagiQuest DNA pulses: Long ~840µs / Short ~310µs)
*   **Visual Elements:** NeoPixel Ring x12

### NODE C: 3D-PRINTED Moon Lamp (Pico W)
*   **Microcontroller:** Raspberry Pi Pico W
*   **IR Receiver:** TSOP38238 (Tuned to MagiQuest DNA pulses: Long ~840µs / Short ~310µs)
*   **AC power outlet controlled by a gpio pin to power the lamp

### NODE D: 3D-PRINTED Treasure Chest (Pico W)
*   **Microcontroller:** Raspberry Pi Pico W
*   **IR Receiver:** TSOP38238 (Tuned to MagiQuest DNA pulses: Long ~840µs / Short ~310µs)
*   **Stepper Driver:** ULN2003 Driver Board powering a 28BYJ-48 Stepper Motor
*   **Visual Elements:** 3x Low-voltage LEDs chained in parallel or indexed individually

### NODE E: Painting (Pico W)
*   **Microcontroller:** Raspberry Pi Pico W
*   **IR Receiver:** TSOP38238 (Tuned to MagiQuest DNA pulses: Long ~840µs / Short ~310µs)
*   **Visual Elements:** NeoPixel Ring x24

### NODE F: Hologram Fan Projector depicting a crystal ball (Raspberry Pi Standalone)
*   **Microcontroller:** Raspberry Pi Pico W
*   **IR Receiver:** TSOP38238 (Tuned to MagiQuest DNA pulses: Long ~840µs / Short ~310µs)
*   **1 Channel DC 3V/3.3V Power Relay Module to control AC power to the projector
*   **Audio Output:** Native ALSA layer (3.5mm jack or HDMI audio breakout mapped to `mplayer`)

### NODE G: 3D-PRINTED Alchemist Study Diorama (Pico W)
*   **Microcontroller:** Raspberry Pi Pico W
*   **IR Receiver:** TSOP38238 (Tuned to MagiQuest DNA pulses: Long ~840µs / Short ~310µs)
*   ****AC power outlet controlled by a gpio pin to power the Diorama

### NODE H: 3D-PRINTED Barrel (Pico W)
*   **Microcontroller:** Raspberry Pi Pico W
*   **IR Receiver:** TSOP38238 (Tuned to MagiQuest DNA pulses: Long ~840µs / Short ~310µs)
*   **Audio Output:** NS4168 I2S Audio Amplifier & 3W Speaker Kit

### NODE I: Cauldron with normally on mister (Pico W)
*   **Microcontroller:** Raspberry Pi Pico W
*   **IR Receiver:** TSOP38238 (Tuned to MagiQuest DNA pulses: Long ~840µs / Short ~310µs)
*   ****AC power outlet controlled by a gpio pin to power the mister

### NODE J: 3D-PRINTED Dragon Statue (Pico W)
*   **Microcontroller:** Raspberry Pi Pico W
*   **IR Receiver:** TSOP38238 (Tuned to MagiQuest DNA pulses: Long ~840µs / Short ~310µs)
*   **Visual Elements:** NeoPixel Ring x16

---

## 3. PROGRAM FLOWS & LOGIC PATTERNS

### FLASK SERVER MAPPING (`server.py`)
*   Maintains a `scoreboard_data` dictionary in active RAM (`total_points`, `max_points`, `simulation_running`).
*   Serves an asynchronous HTML5 dashboard leveraging standard CSS Grid structure (swaps dynamically from a 5x2 landscape grid down to a clean 2x5 stack configuration for operator cell phone displays).
*   Exposes `/score` (POST payload handler) to process hardware event hits. Maps incremental indexing sequentially against an custom integer array layout (`REVEAL_SEQUENCE`) to build the puzzle logic.

### THE TELEPHONE ENGINE FLOW (`phone.py`)
1.  **Boot Up:** Allocates audio hardware tracks, balances master ALSA volume boundaries, sets `scoreboard_allowed = True`.
2.  **Wand Ignite:** Standby loop tracks `WAND_IR_SENSOR`. When hit, it transitions into a Ringing state.
3.  **Ringing Loop:** Executes an internal loop playing `Ring.mp3` through an isolated `subprocess.Popen` task wrapper. This loop monitors the hook line continuously.
4.  **Lift Event:** As soon as the player picks up the phone (`RECEIVER_SENSOR` reads Off-Hook), the ring process is terminated via `kill()`. 
5.  **Payload & Score:** Volume adjusts dynamically down to a comfortable 70%. The script kicks off the story asset (`Intro Song - OK.mp3`) and fires an HTTP POST tracking string to the Flask engine. It then engages a local lockout (`scoreboard_allowed = False`) until a manual system power cycle takes place.

### THE BOOK ENGINE FLOW (`book.py`)
1.  **Boot Up:** Joins Wi-Fi AP (`188 Holtzclaw`) and initializes internal logic loop gates with `scoreboard_allowed = True`.
2.  **Standby:** Loops through sub-100ms scans of the TSOP data pin. 
3.  **Spell Match:** If a magic pattern matches constraints, the ring LEDs preform a "moon beam" sequence for 30 seconds
4.  **Network Push:** Fires a raw HTTP POST straight out of low-level `socket` objects directly to `192.168.86.52:5000/score` (bypassing native `urequests` memory fragmentation crashes).
5.  **Local Lockout Engaged:** Sets `scoreboard_allowed = False`. Future spell casts will trigger the 30-second ring LED flash sequence, but will never issue network payloads until the board is physically rebooted.

### THE LAMP ENGINE FLOW (`lamp.py`)
1.  **Boot Up:** Joins Wi-Fi AP (`188 Holtzclaw`) and initializes internal logic loop gates with `scoreboard_allowed = True`.
2.  **Standby:** Loops through sub-100ms scans of the TSOP data pin. 
3.  **Spell Match:** If a magic pattern matches constraints, trigger the relay to apply AC power to the lamp for 60 seconds before turning back off.
4.  **Network Push:** Fires a raw HTTP POST straight out of low-level `socket` objects directly to `192.168.86.52:5000/score` (bypassing native `urequests` memory fragmentation crashes).
5.  **Local Lockout Engaged:** Sets `scoreboard_allowed = False`. Future spell casts will trigger the 60-second AC power toggle, but will never issue network payloads until the board is physically rebooted.

### THE CHEST ENGINE FLOW (`chest.py`)
1.  **Boot Up:** Joins Wi-Fi AP (`188 Holtzclaw`) and initializes internal logic loop gates with `scoreboard_allowed = True`.
2.  **Standby:** Loops through sub-100ms scans of the TSOP data pin. 
3.  **Spell Match:** If a magic pattern matches constraints, it bypasses network lag to drive the full-sequence stepper immediately to open the lid.
4.  **Network Push:** Fires a raw HTTP POST straight out of low-level `socket` objects directly to `192.168.86.52:5000/score` (bypassing native `urequests` memory fragmentation crashes).
5.  **Local Lockout Engaged:** Sets `scoreboard_allowed = False`. Future spell casts will trigger the 30-second LED flash window and run physical stepper mechanisms, but will never issue network payloads until the board is physically rebooted.

### THE PAINTING ENGINE FLOW (`painting.py`)
1.  **Boot Up:** Joins Wi-Fi AP (`188 Holtzclaw`) and initializes internal logic loop gates with `scoreboard_allowed = True`.
2.  **Standby:** Loops through sub-100ms scans of the TSOP data pin. 
3.  **Spell Match:** If a magic pattern matches constraints, the ring LEDs preform a "Crystal Ball" sequence for 30 seconds
4.  **Network Push:** Fires a raw HTTP POST straight out of low-level `socket` objects directly to `192.168.86.52:5000/score` (bypassing native `urequests` memory fragmentation crashes).
5.  **Local Lockout Engaged:** Sets `scoreboard_allowed = False`. Future spell casts will trigger the 30-second ring LED flash sequence, but will never issue network payloads until the board is physically rebooted.

### THE CRYSTAL BALL ENGINE FLOW (`crystal.py`)
1.  **Boot Up:** Allocates audio hardware tracks, balances master ALSA volume boundaries, sets `scoreboard_allowed = True`.
2.  **Wand Ignite:** Standby loop tracks `WAND_IR_SENSOR`. When hit, trigger the relay to apply AC power to the Hologram Fan Projector.  After a time delay, to align with the time needed for the projector to boot, an audio file will be triggered.
3.  **Payload & Score:** As soon as the wand is identified an HTTP POST tracking string to the Flask engine. It then engages a local lockout (`scoreboard_allowed = False`) until a manual system power cycle takes place.
4.  **Reset: The relay will remove power once the audio is finished playing.

### THE ALCHEMIST STUDY ENGINE FLOW (`study.py`)
1.  **Boot Up:** Joins Wi-Fi AP (`188 Holtzclaw`) and initializes internal logic loop gates with `scoreboard_allowed = True`.
2.  **Standby:** Loops through sub-100ms scans of the TSOP data pin. 
3.  **Spell Match:** If a magic pattern matches constraints, trigger the relay to apply AC power to the diorama for 180 seconds before turning back off.
4.  **Network Push:** Fires a raw HTTP POST straight out of low-level `socket` objects directly to `192.168.86.52:5000/score` (bypassing native `urequests` memory fragmentation crashes).
5.  **Local Lockout Engaged:** Sets `scoreboard_allowed = False`. Future spell casts will trigger the 180-second AC power toggle, but will never issue network payloads until the board is physically rebooted.

### THE BARREL ENGINE FLOW (`barrel.py`)
1.  **Boot Up:** Joins Wi-Fi AP (`188 Holtzclaw`) and initializes internal logic loop gates with `scoreboard_allowed = True`.
2.  **Standby:** Loops through sub-100ms scans of the TSOP data pin. 
3.  **Spell Match:** If a magic pattern matches constraints, trigger an audio file to be play through the speaker.
4.  **Network Push:** Fires a raw HTTP POST straight out of low-level `socket` objects directly to `192.168.86.52:5000/score` (bypassing native `urequests` memory fragmentation crashes).
5.  **Local Lockout Engaged:** Sets `scoreboard_allowed = False`. Future spell casts will trigger the audio file, but will never issue network payloads until the board is physically rebooted.

### THE CAULDRON ENGINE FLOW (`cauldron.py`)
1.  **Boot Up:** Joins Wi-Fi AP (`188 Holtzclaw`) and initializes internal logic loop gates with `scoreboard_allowed = True`.
2.  **Standby:** Loops through sub-100ms scans of the TSOP data pin. 
3.  **Spell Match:** If a magic pattern matches constraints, trigger the relay to remove apply AC power from the mister lamp for 180 seconds before turning back off.
4.  **Network Push:** Fires a raw HTTP POST straight out of low-level `socket` objects directly to `192.168.86.52:5000/score` (bypassing native `urequests` memory fragmentation crashes).
5.  **Local Lockout Engaged:** Sets `scoreboard_allowed = False`. Future spell casts will trigger the 180-second AC power toggle, but will never issue network payloads until the board is physically rebooted.

### THE STATUE ENGINE FLOW (`statue.py`)
1.  **Boot Up:** Joins Wi-Fi AP (`188 Holtzclaw`) and initializes internal logic loop gates with `scoreboard_allowed = True`.
2.  **Standby:** Loops through sub-100ms scans of the TSOP data pin. 
3.  **Spell Match:** If a magic pattern matches constraints, the LEDs ring play a sequence of rainbow lighting flashes followed by a fade up to white.
4.  **Network Push:** Fires a raw HTTP POST straight out of low-level `socket` objects directly to `192.168.86.52:5000/score` (bypassing native `urequests` memory fragmentation crashes).
5.  **Local Lockout Engaged:** If this is the final trigger the scoreboard will play the congratulations audio file. 

---

## 4. CURRENT PRODUCTION CODEBASE

### server.py

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

#############

### phone.py


#!/usr/bin/python3
import json # Make sure to add import json at the very top of phone.py
import subprocess
from gpiozero import Button
import time
import sys
import io
import requests
import threading
from flask import Flask, jsonify

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- Configuration ---
WEB_SERVER_HOST = "192.168.86.52"
WEB_SERVER_PORT = 5000
PHONE_LISTEN_PORT = 5001  

SOUND_RING = "Ring.mp3"
SOUND_MESSAGE = "Cadette_Quest.mp3"

WAND_IR_SENSOR = Button(27)       
RECEIVER_SENSOR = Button(17)      

scoreboard_allowed = True

# --- Local API Server for Remote Reset ---
phone_app = Flask(__name__)

@phone_app.route('/reset_lockout', methods=['POST'])
def remote_reset_lockout():
    global scoreboard_allowed
    scoreboard_allowed = True
    print("Score transmission unblocked remotely by Scoreboard Server!", flush=True)
    return jsonify({"status": "unlocked"}), 200

def start_local_api():
    phone_app.run(host='0.0.0.0', port=PHONE_LISTEN_PORT, debug=False, use_reloader=False, threaded=True)

threading.Thread(target=start_local_api, daemon=True).start()

def check_sequence_and_score():
    global scoreboard_allowed
    if not scoreboard_allowed:
        return True # Rule: Allow local physical re-trigger loop if already cleared earlier
        
    try:
        print("Checking puzzle sequence alignment with server...", flush=True)
        
        # FIX: Explicitly define the string variable before it gets passed to the post method
        payload_str = json.dumps({"node_id": 1}) # Node 1 = The Telephone'
        headers = {'Content-Type': 'application/json'}
        url = f"http://{WEB_SERVER_HOST}:{WEB_SERVER_PORT}/score"
        
        # Pass the verified payload string and custom headers configuration
        response = requests.post(url, data=payload_str, headers=headers, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                scoreboard_allowed = False # Locally latch point generation channel
                print("Server verified sequence alignment. Ring sequence unlocked!", flush=True)
                return True
        print(f"Server rejected activation request. Message: {response.text}", flush=True)
        return False
    except Exception as e:
        print(f"Scoreboard network connectivity error: {e}", flush=True)
        return False
                
def set_pi_alsa_volume(volume_percentage):
    val = max(0, min(volume_percentage, 100))
    subprocess.run(["amixer", "set", "Master", f"{val}%"], stdout=subprocess.DEVNULL)

# --- Main Program Loop ---
print("Waiting for audio layer to initialize...", flush=True)
time.sleep(5)   
set_pi_alsa_volume(100)

print("Phone System Ready! Wave wand to trigger ringing...", flush=True)

try:
    while True:
        # State 1: Standby Loop
        while not WAND_IR_SENSOR.is_pressed:
            time.sleep(0.05)
            
        print("Wand spell detected! Sending server-side check verification...", flush=True)
        
        # Enforce Server-Check Gate before ringing physical hardware lines
        if check_sequence_and_score():
            print("Beginning the phone ringing cycle...", flush=True)
            audio_proc = None
            
            # State 2: Ringing loop until phone is picked up (Off-Hook)
            while RECEIVER_SENSOR.is_pressed:
                if audio_proc is None or audio_proc.poll() is not None:
                    audio_proc = subprocess.Popen(["mplayer", SOUND_RING], shell=False)
                time.sleep(0.1)
                
            if audio_proc is not None:
                audio_proc.kill()
                audio_proc.wait()

            # State 3: Phone Answered (Receiver lifted)
            print("Phone lifted! Playing message asset...", flush=True)
            set_pi_alsa_volume(70)
            audio_proc = subprocess.Popen(["mplayer", SOUND_MESSAGE], shell=False)
            
            # Monitor loop: Keep playing until hung up or audio naturally completes
            while not RECEIVER_SENSOR.is_pressed:
                if audio_proc.poll() is not None:
                    break
                time.sleep(0.1)
                
            print("Phone hung up or audio completed. Ending audio playback.", flush=True)
            if audio_proc is not None and audio_proc.poll() is None:
                audio_proc.kill()
                audio_proc.wait()
        else:
            print("Wand hit rejected. Standing by for valid sequence step...", flush=True)
            
        time.sleep(1.0)
        print("Waiting for next wand wave...", flush=True)

except KeyboardInterrupt:
    print("\nShutting down Phone Script cleanly.", flush=True)

finally:
    print("Cleaning up GPIO pins...", flush=True)
    WAND_IR_SENSOR.close()
    RECEIVER_SENSOR.close()



#############

### book.py


import machine
from machine import Pin
import time
from time import sleep_ms
import network
import socket
from neopixel import NeoPixel

# --- Network Configuration ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.ifconfig(('192.168.86.202', '255.255.255.0', '192.168.86.1', '8.8.8.8'))

WIFI_SSID = "188 Holtzclaw"
WIFI_PASSWORD = "Rivette87"
WEB_SERVER_HOST = "192.168.86.52"
WEB_SERVER_PORT = 5000

MQ_LONG_PULSE = 840
MQ_SHORT_PULSE = 310
TOLERANCE = 100 

# --- Pin Definitions ---
ir_pin = Pin(11, Pin.IN) 
NUM_LEDS = 16
np_pin = Pin(10, Pin.OUT) 
np = NeoPixel(np_pin, NUM_LEDS)

scoreboard_allowed = True

def connect_wifi():
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Connecting to Wi-Fi...")
    while not wlan.isconnected():
        time.sleep(0.5)
    print("Connected! IP:", wlan.ifconfig()[0])

def send_score():
    """Checks sequence alignment with server. Returns True if approved, False if blocked."""
    global scoreboard_allowed
    if not scoreboard_allowed:
        return True

    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        try:
            json_data = '{"node_id": 2}'
            content_length = len(json_data)
            http_packet = (
                "POST /score HTTP/1.1\r\n"
                f"Host: {WEB_SERVER_HOST}:{WEB_SERVER_PORT}\r\n"
                "Content-Type: application/json\r\n"
                f"Content-Length: {content_length}\r\n"
                "Connection: close\r\n\r\n" + json_data
            )
            
            addr = socket.getaddrinfo(WEB_SERVER_HOST, WEB_SERVER_PORT)[0][-1]
            s = socket.socket()
            s.settimeout(3.0)
            s.connect(addr)
            s.send(bytes(http_packet, 'utf8'))
            
            response_chunks = []
            while True:
                data = s.recv(512)
                if not data:
                    break
                response_chunks.append(data.decode('utf8'))
                
            response = "".join(response_chunks)
            s.close()
            
            print("Complete Stream Payload Received:\n", response.strip())
            
            if "success" in response:
                scoreboard_allowed = False
                return True
                
        except Exception as e:
            print("Network check stream error:", e)
            
    return False

def read_ir_pulses():
    if ir_pin.value() == 0:
        pulse_durations = []
        last_state = 0
        last_time = time.ticks_us()
        timeout_start = time.ticks_us()
        while time.ticks_diff(time.ticks_us(), timeout_start) < 100000:
            current_state = ir_pin.value()
            if current_state != last_state:
                now = time.ticks_us()
                duration = time.ticks_diff(now, last_time)
                if duration > 120: pulse_durations.append(duration)
                last_state = current_state
                last_time = now
                if len(pulse_durations) >= 20: break
        return pulse_durations
    return None

def verify_wand_code(captured_pulses):
    if not captured_pulses or len(captured_pulses) < 5: return False
    long_pulse_count, short_pulse_count = 0, 0
    for pulse in captured_pulses:
        if abs(pulse - MQ_LONG_PULSE) <= TOLERANCE: long_pulse_count += 1
        elif abs(pulse - MQ_SHORT_PULSE) <= TOLERANCE: short_pulse_count += 1
    return long_pulse_count >= 2 and short_pulse_count >= 1

def clear_leds():
    for i in range(NUM_LEDS): np[i] = (0, 0, 0)
    np.write()

connect_wifi()
print("Book Engine Active...")

spell_active = False
animation_start = 0
anim_brightness = 0
anim_direction = 1

while True:
    current_time = time.ticks_ms()
    
    if not spell_active:
        raw_pulses = read_ir_pulses()
        if raw_pulses and verify_wand_code(raw_pulses):
            print("Wand pulse detected! Processing server verification...")
            if send_score():
                print("Server verified sequence alignment. Initiating animations!")
                spell_active = True
                animation_start = current_time
                anim_brightness = 0
                anim_direction = 1
            else:
                print("Ignored: Out-of-order interaction attempt.")
                time.sleep_ms(2000) 
    else:
        # Non-blocking breathing moon glow step
        for i in range(NUM_LEDS):
            r = (anim_brightness * 4) // 5  
            g = (anim_brightness * 9) // 10 
            b = anim_brightness
            np[i] = (r, g, b)
        np.write()
        
        anim_brightness += (5 * anim_direction)
        if anim_brightness >= 255:
            anim_brightness = 255
            anim_direction = -1
        elif anim_brightness <= 0:
            anim_brightness = 0
            anim_direction = 1
            
        if time.ticks_diff(current_time, animation_start) >= 30000:
            clear_leds()
            spell_active = False
            print("Animation window complete. Returning to Standby.")
            time.sleep_ms(500) 
            
    time.sleep_ms(15)


#############

### lamp.py


import machine
from machine import Pin
import time
from time import sleep_ms
import network
import socket

# --- Network Configuration ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.ifconfig(('192.168.86.203', '255.255.255.0', '192.168.86.1', '8.8.8.8'))

WIFI_SSID = "188 Holtzclaw"
WIFI_PASSWORD = "Rivette87"
WEB_SERVER_HOST = "192.168.86.52"
WEB_SERVER_PORT = 5000

MQ_LONG_PULSE = 840
MQ_SHORT_PULSE = 310
TOLERANCE = 100 

# --- Pin Definitions ---
ir_pin = Pin(11, Pin.IN)
relay_pin = Pin(10, Pin.OUT) 

# Ensure lamp starts completely OFF at boot
relay_pin.value(0) 
scoreboard_allowed = True

def connect_wifi():
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Lamp connecting to Wi-Fi...")
    while not wlan.isconnected():
        time.sleep(0.5)
    print("Connected! IP:", wlan.ifconfig()[0])

def send_score():
    """Checks sequence alignment with server. Returns True if approved, False if blocked."""
    global scoreboard_allowed
    if not scoreboard_allowed:
        return True # Latch override: allow local re-trigger loops

    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        try:
            # UNIQUE ID: Node 3 represents The Moon Lamp
            json_data = '{"node_id": 3}' 
            content_length = len(json_data)
            http_packet = (
                "POST /score HTTP/1.1\r\n"
                f"Host: {WEB_SERVER_HOST}:{WEB_SERVER_PORT}\r\n"
                "Content-Type: application/json\r\n"
                f"Content-Length: {content_length}\r\n"
                "Connection: close\r\n\r\n" + json_data
            )
            
            addr = socket.getaddrinfo(WEB_SERVER_HOST, WEB_SERVER_PORT)[0][-1]
            s = socket.socket()
            s.settimeout(3.0)
            s.connect(addr)
            s.send(bytes(http_packet, 'utf8'))
            
            # Stream all data packets out of the network buffer cleanly
            response_chunks = []
            while True:
                data = s.recv(512)
                if not data:
                    break
                response_chunks.append(data.decode('utf8'))
                
            response = "".join(response_chunks)
            s.close()
            
            print("Lamp Stream Payload Received:\n", response.strip())
            
            if "success" in response:
                scoreboard_allowed = False # Permanently latch score channel locally
                return True
                
        except Exception as e:
            print("Lamp network check stream error:", e)
            
    return False

def read_ir_pulses():
    if ir_pin.value() == 0:
        pulse_durations = []
        last_state = 0
        last_time = time.ticks_us()
        timeout_start = time.ticks_us()
        while time.ticks_diff(time.ticks_us(), timeout_start) < 100000:
            current_state = ir_pin.value()
            if current_state != last_state:
                now = time.ticks_us()
                duration = time.ticks_diff(now, last_time)
                if duration > 120: pulse_durations.append(duration)
                last_state = current_state
                last_time = now
                if len(pulse_durations) >= 20: break
        return pulse_durations
    return None

def verify_wand_code(captured_pulses):
    if not captured_pulses or len(captured_pulses) < 5: return False
    long_pulse_count, short_pulse_count = 0, 0
    for pulse in captured_pulses:
        if abs(pulse - MQ_LONG_PULSE) <= TOLERANCE: long_pulse_count += 1
        elif abs(pulse - MQ_SHORT_PULSE) <= TOLERANCE: short_pulse_count += 1
    return long_pulse_count >= 2 and short_pulse_count >= 1

# --- Run ---
connect_wifi()
print("Lamp Engine Active... Monitoring for precise MagiQuest IR signatures.")

relay_active = False
relay_start_time = 0
HOLD_WINDOW_MS = 60000  # Lamp holds open for exactly 60 seconds

while True:
    current_time = time.ticks_ms()
    
    if not relay_active:
        # Check if a transmission burst is actively starting
        if ir_pin.value() == 0:
            raw_pulses = read_ir_pulses()
            
            # Reject noise: ensure we captured a meaningful pulse payload before running checks
            if raw_pulses and len(raw_pulses) >= 5:
                if verify_wand_code(raw_pulses):
                    print("Valid wand signature confirmed! Checking sequence with server...")
                    if send_score():
                        print("Sequence slot confirmed. Snapping relay shut!")
                        relay_pin.value(1) # Fire AC relay closed
                        relay_active = True
                        relay_start_time = current_time
                    else:
                        print("Ignored: Out-of-order interaction attempt.")
                        time.sleep_ms(2000)
                else:
                    # Captured pulses but they didn't match the signature
                    time.sleep_ms(200)
    else:
        # Non-blocking check to see if the 60-second window has expired
        if time.ticks_diff(current_time, relay_start_time) >= HOLD_WINDOW_MS:
            print("Time up! Opening circuit to cut lamp power safely.")
            relay_pin.value(0) 
            relay_active = False
            time.sleep_ms(500)
            
    time.sleep_ms(15) # Relax the loop slightly to mimic the book/painting timing


#############

### chest.py

import machine
from machine import Pin
import time
from time import sleep_ms
import network
import socket

# --- Static IP Allocation ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.ifconfig(('192.168.86.205', '255.255.255.0', '192.168.86.1', '8.8.8.8'))

# --- Configuration ---
WIFI_SSID = "188 Holtzclaw"
WIFI_PASSWORD = "Rivette87"
WEB_SERVER_HOST = "192.168.86.52"
WEB_SERVER_PORT = 5000

MQ_LONG_PULSE = 840
MQ_SHORT_PULSE = 310
TOLERANCE = 100 

# --- Pin Definitions ---
ir_pin = machine.Pin(15, machine.Pin.IN)
leds = [machine.Pin(10, machine.Pin.OUT), machine.Pin(11, machine.Pin.OUT), machine.Pin(12, machine.Pin.OUT)]

in1 = Pin(28, Pin.OUT)
in2 = Pin(27, Pin.OUT)
in3 = Pin(26, Pin.OUT)
in4 = Pin(22, Pin.OUT)
pins = [in1, in2, in3, in4]

# Step pattern sequence matrix verified by the sanity check
full_sequence = [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1], [1, 0, 0, 1]]

scoreboard_allowed = True

def connect_wifi():
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Connecting to Wi-Fi...")
    while not wlan.isconnected():
        time.sleep(0.5)
    print("Connected! IP:", wlan.ifconfig()[0])

def send_score():
    """Checks with server. Returns True if activation is allowed, False if blocked."""
    global scoreboard_allowed
    
    if not scoreboard_allowed:
        return True 

    if wlan.isconnected():
        try:
            print("Checking sequence alignment with central server...")
            json_data = '{"node_id": 4}' # Node 4 = Chest
            content_length = len(json_data)
            
            http_packet = (
                "POST /score HTTP/1.1\r\n"
                f"Host: {WEB_SERVER_HOST}:{WEB_SERVER_PORT}\r\n"
                "Content-Type: application/json\r\n"
                f"Content-Length: {content_length}\r\n"
                "Connection: close\r\n\r\n"
                + json_data
            )
            
            addr = socket.getaddrinfo(WEB_SERVER_HOST, WEB_SERVER_PORT)[0][-1]
            
            s = socket.socket()
            s.settimeout(3.0)
            s.connect(addr) # This will now safely connect without throwing length errors!
            s.send(bytes(http_packet, 'utf8'))
            
            response_chunks = []
            while True:
                data = s.recv(512)
                if not data:
                    break
                response_chunks.append(data.decode('utf8'))
                
            response = "".join(response_chunks)
            s.close()
            
            print("Server Response Block:\n", response.strip())
            
            if "success" in response:
                print("Server approved activation. Point generated / re-entry allowed!")
                scoreboard_allowed = False 
                return True
            else:
                print("Server rejected activation: Out of order sequence layout.")
                return False
                
        except Exception as e:
            print("Scoreboard network socket loop error:", e)
            return False
            
    return False

def set_step(step):
    for i in range(4): pins[i].value(step[i])

def step_motor(steps, delay_ms=3, direction=1):
    seq = full_sequence if direction == 1 else full_sequence[::-1]
    for _ in range(steps):
        for step in seq:
            set_step(step)
            sleep_ms(delay_ms)
            
def release_motor():          
    for pin in pins: pin.value(0)

def read_ir_pulses():
    if ir_pin.value() == 0:
        pulse_durations = []
        last_state = 0
        last_time = time.ticks_us()
        timeout_start = time.ticks_us()
        
        while time.ticks_diff(time.ticks_us(), timeout_start) < 100000:
            current_state = ir_pin.value()
            if current_state != last_state:
                now = time.ticks_us()
                duration = time.ticks_diff(now, last_time)
                if duration > 120: pulse_durations.append(duration)
                last_state = current_state
                last_time = now
                if len(pulse_durations) >= 20: break
        return pulse_durations
    return None

def verify_wand_code(captured_pulses):
    if not captured_pulses or len(captured_pulses) < 5: return False
    long_pulse_count, short_pulse_count = 0, 0
    for pulse in captured_pulses:
        if abs(pulse - MQ_LONG_PULSE) <= TOLERANCE: long_pulse_count += 1
        elif abs(pulse - MQ_SHORT_PULSE) <= TOLERANCE: short_pulse_count += 1
    return long_pulse_count >= 2 and short_pulse_count >= 1

# --- Run Loop ---
connect_wifi()
print("Treasure Chest Watchdog Active and Armed...")

chest_is_open = False
open_start_time = 0
CHEST_HOLD_MS = 30000  

# Twinkle Timing Configurations
led_intervals = [150, 280, 410]              
led_last_times = [0, 0, 0]                   
led_states = [0, 0, 0]                       

while True:
    current_time = time.ticks_ms()

    if not chest_is_open:
        raw_pulses = read_ir_pulses()
        if raw_pulses and verify_wand_code(raw_pulses):
            print("Wand pulse detected! Requesting authorization payload...")
            
            server_approved = send_score()
            current_time = time.ticks_ms() # Wipe away transaction network latency clock shifts
            
            if server_approved:
                print("Sequence Verified! Opening Chest...")
                step_motor(286, delay_ms=3, direction=-1) # Matches test script parameter configuration
                chest_is_open = True
                open_start_time = current_time
                
                for i in range(len(leds)):
                    led_last_times[i] = current_time
            else:
                print("Spell ignored physically due to sequence block.")
                time.sleep_ms(2000)
    else:
        # --- Asynchronous Twinkle Loop ---
        for i in range(len(leds)):
            if time.ticks_diff(current_time, led_last_times[i]) >= led_intervals[i]:
                led_states[i] = 1 - led_states[i]
                leds[i].value(led_states[i])
                led_last_times[i] = current_time
            
        # Monitor expiration window
        if time.ticks_diff(current_time, open_start_time) >= CHEST_HOLD_MS:
            print("Time Up! Closing Chest Mechanism Safely...")
            for led in leds: 
                led.value(0)
                
            step_motor(286, delay_ms=3, direction=1)
            sleep_ms(500)
            release_motor()
            chest_is_open = False

    time.sleep_ms(10)

#############

### painting.py

import machine
from machine import Pin
import time
from time import sleep_ms
import network
import socket
from neopixel import NeoPixel

# --- Static IP Selection ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.ifconfig(('192.168.86.204', '255.255.255.0', '192.168.86.1', '8.8.8.8'))

WIFI_SSID = "188 Holtzclaw"
WIFI_PASSWORD = "Rivette87"
WEB_SERVER_HOST = "192.168.86.52" 
WEB_SERVER_PORT = 5000

MQ_LONG_PULSE = 840
MQ_SHORT_PULSE = 310
TOLERANCE = 100 

# --- Pin Definitions ---
ir_pin = Pin(11, Pin.IN)
NUM_LEDS = 31
np_pin = Pin(10, Pin.OUT)
np = NeoPixel(np_pin, NUM_LEDS)

scoreboard_allowed = True

def connect_wifi():
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Painting connecting to Wi-Fi...")
    while not wlan.isconnected():
        time.sleep(0.5)
    print("Painting Connected! IP:", wlan.ifconfig()[0])

def send_score():
    """Checks sequence alignment with server. Returns True if approved, False if blocked."""
    global scoreboard_allowed
    if not scoreboard_allowed:
        return True # Allow physical re-activation if already unlocked earlier

    if wlan.isconnected():
        try:
            json_data = '{"node_id": 5}' # Node 5 represents The Painting
            content_length = len(json_data)
            http_packet = (
                "POST /score HTTP/1.1\r\n"
                f"Host: {WEB_SERVER_HOST}:{WEB_SERVER_PORT}\r\n"
                "Content-Type: application/json\r\n"
                f"Content-Length: {content_length}\r\n"
                "Connection: close\r\n\r\n" + json_data
            )
            
            addr = socket.getaddrinfo(WEB_SERVER_HOST, WEB_SERVER_PORT)[0][-1]
            s = socket.socket()
            s.settimeout(3.0)
            s.connect(addr) 
            s.send(bytes(http_packet, 'utf8'))
            
            # --- FIXED: Using a continuous stream reader loop to prevent payload drops ---
            response_chunks = []
            while True:
                data = s.recv(512)
                if not data:
                    break
                response_chunks.append(data.decode('utf8'))
                
            response = "".join(response_chunks)
            s.close()
            
            if "success" in response:
                scoreboard_allowed = False # Permanently latch score channel locally
                return True
        except Exception as e:
            print("Network check error:", e)
    return False

def read_ir_pulses():
    if ir_pin.value() == 0:
        pulse_durations = []
        last_state = 0
        last_time = time.ticks_us()
        timeout_start = time.ticks_us()
        while time.ticks_diff(time.ticks_us(), timeout_start) < 100000:
            current_state = ir_pin.value()
            if current_state != last_state:
                now = time.ticks_us()
                duration = time.ticks_diff(now, last_time)
                if duration > 120: pulse_durations.append(duration)
                last_state = current_state
                last_time = now
                if len(pulse_durations) >= 20: break
        return pulse_durations
    return None

def verify_wand_code(captured_pulses):
    if not captured_pulses or len(captured_pulses) < 5: return False
    long_pulse_count, short_pulse_count = 0, 0
    for pulse in captured_pulses:
        if abs(pulse - MQ_LONG_PULSE) <= TOLERANCE: long_pulse_count += 1
        elif abs(pulse - MQ_SHORT_PULSE) <= TOLERANCE: short_pulse_count += 1
    return long_pulse_count >= 2 and short_pulse_count >= 1

def crystal_glow_animation(tick):
    # Magical swirling pattern 
    for i in range(NUM_LEDS):
        # Generates a moving plasma wave effect across the ring
        val = int((1 + round(127 * (1 + round(3.14 * (i + tick / 10.0)))))) % 255
        np[i] = (int(val * 0.3), 0, val) # Pinkish-purple arcane swirl
    np.write()

def clear_leds():
    for i in range(NUM_LEDS): np[i] = (0, 0, 0)
    np.write()

# --- Run Loop ---
connect_wifi()
print("Painting Engine Watchdog Armed and Standing By...")

spell_active = False
animation_start = 0
tick_counter = 0

while True:
    current_time = time.ticks_ms()
    
    if not spell_active:
        raw_pulses = read_ir_pulses()
        if raw_pulses and verify_wand_code(raw_pulses):
            print("Wand pulse detected at Painting! Checking verification payload...")
            if send_score():
                print("Server verified sequence alignment. Initiating crystal swirl!")
                spell_active = True
                animation_start = current_time
                tick_counter = 0
            else:
                print("Ignored: Out-of-order interaction attempt.")
    else:
        # --- FIXED: Call the correct, existing function with moving tick parameters ---
        crystal_glow_animation(tick_counter)
        tick_counter += 1  # Drive the plasma wave shape forward continuously
        
        # Monitor 30-second display window expiration
        if time.ticks_diff(current_time, animation_start) >= 30000:
            clear_leds()
            spell_active = False
            print("Animation cycle complete. Returning to standby.")
            
    time.sleep_ms(15)

#############

### crystal.py

import machine
from machine import Pin
import time
from time import sleep_ms
import network
import socket

# --- Network Configuration ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.ifconfig(('192.168.86.203', '255.255.255.0', '192.168.86.1', '8.8.8.8'))

WIFI_SSID = "188 Holtzclaw"
WIFI_PASSWORD = "Rivette87"
WEB_SERVER_HOST = "192.168.86.52"
WEB_SERVER_PORT = 5000

MQ_LONG_PULSE = 840
MQ_SHORT_PULSE = 310
TOLERANCE = 100 

# --- Pin Definitions ---
ir_pin = Pin(11, Pin.IN)
relay_pin = Pin(10, Pin.OUT) 

# Ensure crystal starts completely OFF at boot
relay_pin.value(0) 
scoreboard_allowed = True

def connect_wifi():
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Crystal connecting to Wi-Fi...")
    while not wlan.isconnected():
        time.sleep(0.5)
    print("Connected! IP:", wlan.ifconfig()[0])

def send_score():
    """Checks sequence alignment with server. Returns True if approved, False if blocked."""
    global scoreboard_allowed
    if not scoreboard_allowed:
        return True # Latch override: allow local re-trigger loops

    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        try:
            # UNIQUE ID: Node 6 represents The Crystal Ball
            json_data = '{"node_id": 6}' 
            content_length = len(json_data)
            http_packet = (
                "POST /score HTTP/1.1\r\n"
                f"Host: {WEB_SERVER_HOST}:{WEB_SERVER_PORT}\r\n"
                "Content-Type: application/json\r\n"
                f"Content-Length: {content_length}\r\n"
                "Connection: close\r\n\r\n" + json_data
            )
            
            addr = socket.getaddrinfo(WEB_SERVER_HOST, WEB_SERVER_PORT)[0][-1]
            s = socket.socket()
            s.settimeout(3.0)
            s.connect(addr)
            s.send(bytes(http_packet, 'utf8'))
            
            # Stream all data packets out of the network buffer cleanly
            response_chunks = []
            while True:
                data = s.recv(512)
                if not data:
                    break
                response_chunks.append(data.decode('utf8'))
                
            response = "".join(response_chunks)
            s.close()
            
            print("Crystal Stream Payload Received:\n", response.strip())
            
            if "success" in response:
                scoreboard_allowed = False # Permanently latch score channel locally
                return True
                
        except Exception as e:
            print("Crystal network check stream error:", e)
            
    return False

def read_ir_pulses():
    if ir_pin.value() == 0:
        pulse_durations = []
        last_state = 0
        last_time = time.ticks_us()
        timeout_start = time.ticks_us()
        while time.ticks_diff(time.ticks_us(), timeout_start) < 100000:
            current_state = ir_pin.value()
            if current_state != last_state:
                now = time.ticks_us()
                duration = time.ticks_diff(now, last_time)
                if duration > 120: pulse_durations.append(duration)
                last_state = current_state
                last_time = now
                if len(pulse_durations) >= 20: break
        return pulse_durations
    return None

def verify_wand_code(captured_pulses):
    if not captured_pulses or len(captured_pulses) < 5: return False
    long_pulse_count, short_pulse_count = 0, 0
    for pulse in captured_pulses:
        if abs(pulse - MQ_LONG_PULSE) <= TOLERANCE: long_pulse_count += 1
        elif abs(pulse - MQ_SHORT_PULSE) <= TOLERANCE: short_pulse_count += 1
    return long_pulse_count >= 2 and short_pulse_count >= 1

# --- Run ---
connect_wifi()
print("Crystal Engine Active...")

relay_active = False
relay_start_time = 0
HOLD_WINDOW_MS = 60000  # Crystal holds open for exactly 60 seconds

while True:
    current_time = time.ticks_ms()
    
    if not relay_active:
        raw_pulses = read_ir_pulses()
        if raw_pulses and verify_wand_code(raw_pulses):
            print("Wand pulse detected at Crystal! Checking sequence...")
            if send_score():
                print("Sequence slot confirmed. Snapping relay shut!")
                relay_pin.value(1) # Fire AC relay closed
                relay_active = True
                relay_start_time = current_time
            else:
                print("Ignored: Out-of-order interaction attempt.")
                time.sleep_ms(2000)
    else:
        # Non-blocking check to see if the 60-second window has expired
        if time.ticks_diff(current_time, relay_start_time) >= HOLD_WINDOW_MS:
            print("Time up! Opening circuit to cut Crystal power safely.")
            relay_pin.value(0) 
            relay_active = False
            time.sleep_ms(500)
            
    time.sleep_ms(10)

#############

### study.py

import machine
from machine import Pin
import time
from time import sleep_ms
import network
import socket

# --- Network Configuration ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.ifconfig(('192.168.86.203', '255.255.255.0', '192.168.86.1', '8.8.8.8'))

WIFI_SSID = "188 Holtzclaw"
WIFI_PASSWORD = "Rivette87"
WEB_SERVER_HOST = "192.168.86.52"
WEB_SERVER_PORT = 5000

MQ_LONG_PULSE = 840
MQ_SHORT_PULSE = 310
TOLERANCE = 100 

# --- Pin Definitions ---
ir_pin = Pin(11, Pin.IN)
relay_pin = Pin(10, Pin.OUT) 

# Ensure crystal starts completely OFF at boot
relay_pin.value(0) 
scoreboard_allowed = True

def connect_wifi():
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Crystal connecting to Wi-Fi...")
    while not wlan.isconnected():
        time.sleep(0.5)
    print("Connected! IP:", wlan.ifconfig()[0])

def send_score():
    global scoreboard_allowed
    if not scoreboard_allowed:
        return True 

    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        try:
            json_data = '{"node_id": 7}' # Node 7 = Alchemist Study
            content_length = len(json_data)
            http_packet = (
                "POST /score HTTP/1.1\r\n"
                f"Host: {WEB_SERVER_HOST}:{WEB_SERVER_PORT}\r\n"
                "Content-Type: application/json\r\n"
                f"Content-Length: {content_length}\r\n"
                "Connection: close\r\n\r\n" + json_data
            )
            
            # --- FIXED: Drill directly into the structure to extract exactly a length-2 (IP, PORT) object ---
            addr_info = socket.getaddrinfo(WEB_SERVER_HOST, WEB_SERVER_PORT)[-1]
            addr = addr_info if len(addr_info) == 2 else addr_info[-1]
            
            s = socket.socket()
            s.settimeout(3.0)
            s.connect(addr) # This will now safely connect without throwing length errors!
            s.send(bytes(http_packet, 'utf8'))
            
            # --- FIXED: Stream reader loop to ensure headers + payload body are fully read ---
            response_chunks = []
            while True:
                data = s.recv(512)
                if not data: break
                response_chunks.append(data.decode('utf8'))
            response = "".join(response_chunks)
            s.close()
            
            print("Study Server Response:\n", response.strip())
            
            if "success" in response:
                scoreboard_allowed = False
                return True
        except Exception as e:
            print("Study network check stream error:", e)
    return False

def read_ir_pulses():
    if ir_pin.value() == 0:
        pulse_durations = []
        last_state = 0
        last_time = time.ticks_us()
        timeout_start = time.ticks_us()
        while time.ticks_diff(time.ticks_us(), timeout_start) < 100000:
            current_state = ir_pin.value()
            if current_state != last_state:
                now = time.ticks_us()
                duration = time.ticks_diff(now, last_time)
                if duration > 120: pulse_durations.append(duration)
                last_state = current_state
                last_time = now
                if len(pulse_durations) >= 20: break
        return pulse_durations
    return None

def verify_wand_code(captured_pulses):
    if not captured_pulses or len(captured_pulses) < 5: return False
    long_pulse_count, short_pulse_count = 0, 0
    for pulse in captured_pulses:
        if abs(pulse - MQ_LONG_PULSE) <= TOLERANCE: long_pulse_count += 1
        elif abs(pulse - MQ_SHORT_PULSE) <= TOLERANCE: short_pulse_count += 1
    return long_pulse_count >= 2 and short_pulse_count >= 1

# --- Run ---
connect_wifi()
print("Crystal Engine Active...")

relay_active = False
relay_start_time = 0
HOLD_WINDOW_MS = 60000  # Crystal holds open for exactly 60 seconds

while True:
    current_time = time.ticks_ms()
    
    if not relay_active:
        raw_pulses = read_ir_pulses()
        if raw_pulses and verify_wand_code(raw_pulses):
            print("Wand pulse detected at Crystal! Checking sequence...")
            if send_score():
                print("Sequence slot confirmed. Snapping relay shut!")
                relay_pin.value(1) # Fire AC relay closed
                relay_active = True
                relay_start_time = current_time
            else:
                print("Ignored: Out-of-order interaction attempt.")
                time.sleep_ms(2000)
    else:
        # Non-blocking check to see if the 60-second window has expired
        if time.ticks_diff(current_time, relay_start_time) >= HOLD_WINDOW_MS:
            print("Time up! Opening circuit to cut Crystal power safely.")
            relay_pin.value(0) 
            relay_active = False
            time.sleep_ms(500)
            
    time.sleep_ms(10)

#############

### barrel.py

import machine
from machine import Pin
import time
import network
import socket

# --- Network Configuration ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.ifconfig(('192.168.86.207', '255.255.255.0', '192.168.86.1', '8.8.8.8'))

WIFI_SSID = "188 Holtzclaw"
WIFI_PASSWORD = "Rivette87"
WEB_SERVER_HOST = "192.168.86.52"  # Flask server host IP
WEB_SERVER_PORT = 5000

# --- FIXED: ADDED MISSING MAGIQUEST DNA VARIABLES ---
MQ_LONG_PULSE = 840
MQ_SHORT_PULSE = 310
TOLERANCE = 100 

#G-(Pin28_GND), V-(P39_VSYS), BCL-(Pin26_GPIO20), LRC-(Pin27_GPIO21), DIN-(Pin29_GPIO22)

# --- Pin Definitions ---
ir_pin = Pin(11, Pin.IN)
BCLK_PIN = 20
LRCK_PIN = 21
DOUT_PIN = 22

scoreboard_allowed = True

def connect_wifi():
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected(): 
        time.sleep(0.5)

def send_score():
    global scoreboard_allowed
    if not scoreboard_allowed: return True
    if wlan.isconnected():
        try:
            json_data = '{"node_id": 8}'
            content_length = len(json_data)
            http_packet = (
                "POST /score HTTP/1.1\r\n"
                f"Host: {WEB_SERVER_HOST}:{WEB_SERVER_PORT}\r\n"
                "Content-Type: application/json\r\n"
                f"Content-Length: {content_length}\r\n"
                "Connection: close\r\n\r\n" + json_data
            )
            
            # --- FIXED: Explicit tuple parsing to prevent length errors ---
            addr_info = socket.getaddrinfo(WEB_SERVER_HOST, WEB_SERVER_PORT)[-1]
            addr = addr_info if len(addr_info) == 2 else addr_info[-1]
            
            s = socket.socket()
            s.settimeout(3.0)
            s.connect(addr)
            s.send(bytes(http_packet, 'utf8'))
            
            response_chunks = []
            while True:
                data = s.recv(512)
                if not data: break
                response_chunks.append(data.decode('utf8'))
            response = "".join(response_chunks)
            s.close()
            
            if "success" in response:
                scoreboard_allowed = False
                return True
        except Exception as e: 
            print("Barrel network check stream error:", e)
    return False

def stream_audio_from_local_flash():
    """Plays barnaby.wav directly from the Pico W's internal flash memory with matched 8kHz parameters."""
    try:
        # --- FIXED: Set rate to exactly 8000 to match your downsampled file structure ---
        audio_out = machine.I2S(0, sck=Pin(BCLK_PIN), ws=Pin(LRCK_PIN), sd=Pin(DOUT_PIN), 
                                mode=machine.I2S.TX, bits=16, format=machine.I2S.MONO, rate=8000, ibuf=4096)
        
        print("Opening local 8kHz audio asset...")
        with open('barnaby.wav', 'rb') as f:
            # Skip the standard 44-byte WAV header safely
            f.seek(44)
            
            chunk_buffer = bytearray(1024)
            while True:
                num_read = f.readinto(chunk_buffer)
                if num_read == 0: 
                    break 
                audio_out.write(chunk_buffer[:num_read])
                
        audio_out.deinit()
        print("Local audio playback completed at the correct speed.")
        
    except Exception as local_audio_err:
        print("Local Flash Audio Playback Failure:", local_audio_err)


def read_ir_pulses():
    if ir_pin.value() == 0:
        pulse_durations = []
        last_state = 0
        last_time = time.ticks_us()
        timeout_start = time.ticks_us()
        while time.ticks_diff(time.ticks_us(), timeout_start) < 100000:
            current_state = ir_pin.value()
            if current_state != last_state:
                now = time.ticks_us()
                duration = time.ticks_diff(now, last_time)
                if duration > 120: pulse_durations.append(duration)
                last_state = current_state
                last_time = now
                if len(pulse_durations) >= 20: break
        return pulse_durations
    return None

def verify_wand_code(captured_pulses):
    if not captured_pulses or len(captured_pulses) < 5: return False
    long_pulse_count, short_pulse_count = 0, 0
    for pulse in captured_pulses:
        if abs(pulse - MQ_LONG_PULSE) <= TOLERANCE: long_pulse_count += 1
        elif abs(pulse - MQ_SHORT_PULSE) <= TOLERANCE: short_pulse_count += 1
    return long_pulse_count >= 2 and short_pulse_count >= 1

# --- Run Loop ---
connect_wifi()
print("Barrel Watchdog Online and Listening...")

while True:
    raw_pulses = read_ir_pulses()
    if raw_pulses and verify_wand_code(raw_pulses):
        print("Wand pulse detected at Barrel! Checking verification...")
        if send_score():
            print("Barrel Spell Cast Confirmed! Playing local asset...")
            stream_audio_from_local_flash()
        else:
            print("Ignored: Out-of-order interaction attempt.")
            time.sleep_ms(2000)
    time.sleep_ms(50)

#############

### cauldron.py

import machine
from machine import Pin
import time
from time import sleep_ms
import network
import socket

# --- Network Configuration ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.ifconfig(('192.168.86.209', '255.255.255.0', '192.168.86.1', '8.8.8.8'))

WIFI_SSID = "188 Holtzclaw"
WIFI_PASSWORD = "Rivette87"
WEB_SERVER_HOST = "192.168.86.52"
WEB_SERVER_PORT = 5000

MQ_LONG_PULSE = 840
MQ_SHORT_PULSE = 310
TOLERANCE = 100

# --- Pin Definitions ---
ir_pin = Pin(11, Pin.IN)
relay_pin = Pin(10, Pin.OUT) 

# Mist maker is normally ON at boot
relay_pin.value(1) 
scoreboard_allowed = True

def connect_wifi():
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Crystal connecting to Wi-Fi...")
    while not wlan.isconnected():
        time.sleep(0.5)
    print("Connected! IP:", wlan.ifconfig()[0])

def send_score():
    global scoreboard_allowed
    if not scoreboard_allowed:
        return True 

    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        try:
            json_data = '{"node_id": 9}' # Node 9 = The Cauldron
            content_length = len(json_data)
            http_packet = (
                "POST /score HTTP/1.1\r\n"
                f"Host: {WEB_SERVER_HOST}:{WEB_SERVER_PORT}\r\n"
                "Content-Type: application/json\r\n"
                f"Content-Length: {content_length}\r\n"
                "Connection: close\r\n\r\n" + json_data
            )
            
            addr_info = socket.getaddrinfo(WEB_SERVER_HOST, WEB_SERVER_PORT)[-1]
            addr = addr_info if len(addr_info) == 2 else addr_info[-1]
            
            s = socket.socket()
            s.settimeout(3.0)
            s.connect(addr) # This will now safely connect without throwing length errors!
            s.send(bytes(http_packet, 'utf8'))
            
            response_chunks = []
            while True:
                data = s.recv(512)
                if not data: break
                response_chunks.append(data.decode('utf8'))
            response = "".join(response_chunks)
            s.close()
            
            print("Study Server Response:\n", response.strip())
            
            if "success" in response:
                scoreboard_allowed = False
                return True
        except Exception as e:
            print("Cauldron network check stream error:", e)
    return False

def read_ir_pulses():
    if ir_pin.value() == 0:
        pulse_durations = []
        last_state = 0
        last_time = time.ticks_us()
        timeout_start = time.ticks_us()
        while time.ticks_diff(time.ticks_us(), timeout_start) < 100000:
            current_state = ir_pin.value()
            if current_state != last_state:
                now = time.ticks_us()
                duration = time.ticks_diff(now, last_time)
                if duration > 120: pulse_durations.append(duration)
                last_state = current_state
                last_time = now
                if len(pulse_durations) >= 20: break
        return pulse_durations
    return None

def verify_wand_code(captured_pulses):
    if not captured_pulses or len(captured_pulses) < 5: return False
    long_pulse_count, short_pulse_count = 0, 0
    for pulse in captured_pulses:
        if abs(pulse - MQ_LONG_PULSE) <= TOLERANCE: long_pulse_count += 1
        elif abs(pulse - MQ_SHORT_PULSE) <= TOLERANCE: short_pulse_count += 1
    return long_pulse_count >= 2 and short_pulse_count >= 1

# --- Run Loop ---
connect_wifi()
print("Cauldron Fog Watchdog Armed and Waiting...")

cauldron_cleared = False
clear_start_time = 0

while True:
    current_time = time.ticks_ms()
    if not cauldron_cleared:
        raw_pulses = read_ir_pulses()
        if raw_pulses and verify_wand_code(raw_pulses):
            print("Wand wave identified at Cauldron! Sending verification...")
            if send_score():
                print("Cauldron clearing sequence verified! Clearing fog screen...")
                relay_pin.value(0) # Cut power to reveal sign
                cauldron_cleared = True
                
                # --- FIXED: Refresh clock time right after the server returns to eliminate network lag ---
                clear_start_time = time.ticks_ms() 
            else:
                print("Mister clear sequence blocked out-of-order.")
                time.sleep_ms(2000)
    else:
        if time.ticks_diff(current_time, clear_start_time) >= 180000: # 3 mins
            print("Time up! Re-engaging mister to conceal the sign...")
            relay_pin.value(1) # Turn fog maker back on to conceal sign
            cauldron_cleared = False
    time.sleep_ms(10)

#############

### statue.py

import machine
from machine import Pin
import time
from time import sleep_ms
import network
import socket
from neopixel import NeoPixel
import random

# --- Static IP Selection ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.ifconfig(('192.168.86.210', '255.255.255.0', '192.168.86.1', '8.8.8.8'))

WIFI_SSID = "188 Holtzclaw"
WIFI_PASSWORD = "Rivette87"
WEB_SERVER_HOST = "192.168.86.52"
WEB_SERVER_PORT = 5000

MQ_LONG_PULSE = 840
MQ_SHORT_PULSE = 310
TOLERANCE = 100 

# --- Pin Definitions ---
ir_pin = Pin(11, Pin.IN)
# --- FIXED: Buffered configuration matching your expanded pixel size discovery ---
NUM_LEDS = 24  
np_pin = Pin(10, Pin.OUT)
np = NeoPixel(np_pin, NUM_LEDS)

scoreboard_allowed = True

def connect_wifi():
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Dragon Tower connecting to Wi-Fi...")
    while not wlan.isconnected(): 
        time.sleep(0.5)
    print("Connected! IP:", wlan.ifconfig())

def send_score():
    global scoreboard_allowed
    if not scoreboard_allowed: return True
    if wlan.isconnected():
        try:
            json_data = '{"node_id": 10}'
            content_length = len(json_data)
            http_packet = (
                "POST /score HTTP/1.1\r\n"
                f"Host: {WEB_SERVER_HOST}:{WEB_SERVER_PORT}\r\n"
                "Content-Type: application/json\r\n"
                f"Content-Length: {content_length}\r\n"
                "Connection: close\r\n\r\n" + json_data
            )
            
            addr_info = socket.getaddrinfo(WEB_SERVER_HOST, WEB_SERVER_PORT)[-1]
            addr = addr_info if len(addr_info) == 2 else addr_info[-1]
            
            s = socket.socket()
            s.settimeout(7.0)
            s.connect(addr)
            s.send(bytes(http_packet, 'utf8'))
            
            response_chunks = []
            while True:
                data = s.recv(512)
                if not data: break
                response_chunks.append(data.decode('utf8'))
            response = "".join(response_chunks)
            s.close()
            
            print("Statue Server Response:\n", response.strip())
            
            # --- FIXED: Treat "success" OR "ignored" (max score reached) as valid for physical animations ---
            if "success" in response or "ignored" in response:
                print("Server confirmation verified. Unlocking local animations!")
                scoreboard_allowed = False
                return True
        except Exception as e:
            print("Statue network error:", e)
    return False

def read_ir_pulses():
    if ir_pin.value() == 0:
        pulse_durations = []
        last_state = 0
        last_time = time.ticks_us()
        timeout_start = time.ticks_us()
        while time.ticks_diff(time.ticks_us(), timeout_start) < 100000:
            current_state = ir_pin.value()
            if current_state != last_state:
                now = time.ticks_us()
                duration = time.ticks_diff(now, last_time)
                if duration > 120: pulse_durations.append(duration)
                last_state = current_state
                last_time = now
                if len(pulse_durations) >= 20: break
        return pulse_durations
    return None

def verify_wand_code(captured_pulses):
    if not captured_pulses or len(captured_pulses) < 5: return False
    long_pulse_count, short_pulse_count = 0, 0
    for pulse in captured_pulses:
        if abs(pulse - MQ_LONG_PULSE) <= TOLERANCE: long_pulse_count += 1
        elif abs(pulse - MQ_SHORT_PULSE) <= TOLERANCE: short_pulse_count += 1
    return long_pulse_count >= 2 and short_pulse_count >= 1

def wheel(pos):
    """Generates absolute integer-forced rainbow color wave distributions."""
    pos = int(pos) & 255  # Hard-clamp and force to clean integer typing up front
    if pos < 85:
        return (int(pos * 3), int(255 - pos * 3), 0)
    elif pos < 170:
        pos -= 85
        return (int(255 - pos * 3), 0, int(pos * 3))
    else:
        pos -= 170
        return (0, int(pos * 3), int(255 - pos * 3))

def get_fire_color():
    """Generates an unpredictable, chaotic dragon fire color profile."""
    # High red, medium-shifting orange/yellow, zero blue
    r = random.getrandbits(8)  # 0-255
    r = max(200, r)           # Force a bright base roar
    g = random.randint(20, 85) # Simulates shifting heat bands
    return (r, g, 0)

def get_arcane_color():
    """Generates a crackling, pulsing magical counter-spell blast profile."""
    # Zero red, vibrant neon cyan, deep blues, and flashing purples
    g = random.randint(50, 255)
    b = random.randint(180, 255)
    r = random.choice([0, int(b // 2)]) # Randomly shifts between pure Cyan and intense Purple
    return (r, g, b)

def run_victory_sequence():
    print("CRITICAL ENGINE IGNITION: Initiating Arcane Dragon Battle!")
    
    start_time = time.ticks_ms()
    duration_ms = 60000  # Run the intense flashing sequence for exactly 60 seconds
    
    frame_delay = 80     # Start with a distinct structural pulsing pace (milliseconds)
    
    while time.ticks_diff(time.ticks_ms(), start_time) < duration_ms:
        current_progress = time.ticks_diff(time.ticks_ms(), start_time) / duration_ms
        
        # --- PHASE 1: GENERATE CHAOTIC CLASH PATTERNS ---
        # As time ticks forward, the battle intensifies and speed escalates!
        for i in range(NUM_LEDS):
            # Split the ring randomly between fighting elements to look like a clash
            if random.random() > 0.45:
                np[i] = get_fire_color()
            else:
                np[i] = get_arcane_color()
                
        # Inject raw maximum power explosions randomly as the battle peaks
        if random.random() > (0.95 - (current_progress * 0.15)):
            flash_color = random.choice([(255, 255, 255), (0, 255, 245), (255, 0, 127)])
            for i in range(NUM_LEDS): 
                np[i] = flash_color
                
        np.write()
        
        # Accelerate frame changes dynamically as the timer runs down
        current_delay = int(frame_delay - (current_progress * 55)) 
        current_delay = max(20, current_delay) # Hard safety limit on MicroPython timing execution
        time.sleep_ms(current_delay)
        
    print("Battle concluded! Quenching flames. Initiating smooth cool down fade-off...")
    
    # --- PHASE 2: SMOOTH FADE TO BLACK ---
    # Captures the aesthetic of the magic settling and fading out completely
    # Capture final color state to fade out accurately from whatever colors were active
    current_colors = [np[i] for i in range(NUM_LEDS)]
    
    for step in range(50, -1, -1):
        scaler = step / 50.0  # Transition smooth fractions down to zero
        for i in range(NUM_LEDS):
            r = int(current_colors[i][0] * scaler)
            g = int(current_colors[i][1] * scaler)
            b = int(current_colors[i][2] * scaler)
            np[i] = (r, g, b)
        np.write()
        time.sleep_ms(25)  # Creates a clean 1.25 second final fade curve
        
    print("Ecosystem stabilized. Statue dormant.")

# --- Run Loop ---
connect_wifi()
print("Dragon Tower Statue Watchdog Armed and Waiting...")

for i in range(NUM_LEDS): np[i] = (0, 0, 0)
np.write()

while True:
    raw_pulses = read_ir_pulses()
    if raw_pulses and verify_wand_code(raw_pulses):
        print("Final Quest Spell Confirmed at Dragon Tower! Validating position...")
        
        # Pull check validation state directly
        server_approved = send_score()
        
        # Trigger if server accepted it, max score is hit, or locally locked out
        if server_approved or not scoreboard_allowed:
            print("Authorization confirmed! Activating victory sequence...")
            
            # --- OVERRIDE HARDWARE SANITY FLASH ---
            for i in range(NUM_LEDS): np[i] = (255, 0, 0)
            np.write()
            time.sleep_ms(1000)
            
            run_victory_sequence()
            print("Quest Finished! Holding display indefinitely until system restart.")
            break
        else:
            print("Ignored: Final step attempted out of sequence.")
            time.sleep_ms(2000)
    time.sleep_ms(10)

#############


## 4. STORYLINE

### Prop 1: The Initial Scroll (Context Reference)
*   **Location:** Printer Room
*   **Goal:** The Player's Knowledge Base: At this stage, they know they must find 10 objects, use the wand, and restore the puzzle pieces. The phone is right in front of them as the logical first step.
*   **Resource:** Scroll Text - TBD

### Prop 2: Phone - The Wizard’s Telephone Audio Message
*   **Location:** Printer Room
*   **Goal:** Provide narrative depth, explain why the phone is magic, give a cryptic clue for the next prop, and set the emotional stakes.  Make note that the props must be found in the correct order.  This will encourage the player not to just run as fast as they can and point the wand at anything and everything they can find. Collect the 1st shard and the scoreboard is iterated.
*   **Resource:** 3D Printed Phone Complete, Message Script - Tone: Crackly, distorted by magic, frantic but encouraging. Script Concept: "The Echo Chamber" (Sound Effects: Loud magical static, followed by a heavy mechanical clicking sound. The Wizard's voice filters in, sounding like he is speaking down a long metallic pipe.) "Hello? Can you hear me through the temporal static? Ah! The wand has re-established the connection!
Listen closely—I am Eldrin, the Keeper of the Cadette Realm. When the Dragon Ignis tore my magic from me, it fractured. My essence was shattered into ten distinct shards and sealed inside everyday items to hide them from his sight. You hold the first shard right now. This very telephone carries the echo of my voice. By lifting the receiver, you have freed my ability to speak to you! Look at the Great Quest board—the master puzzle is beginning to wake up. But our time is short. The other nine shards are nearby, hidden in plain sight. They will hum with a faint energy, waiting for the wand's counter-spell. Seek the place where shadows gather near the bookshelves next... and beware the dragon’s gaze. Find the shards, restore the master puzzle, and bring back the magic before the hour expires!" - Voice is generated using: https://inworld.ai/voice-generator (Theodore Storyteller)

### Prop 3: Book on a shelf that lights up an image of the moon
*   **Location:** Living Room
*   **Goal:** The player collects the 2nd shard and the scoreboard is iterated. The clue for the next prop is "Moon"
*   **Resource:** 3D Printed Book: https://makerworld.com/en/models/1753318-the-book-of-the-moon?from=search#profileId-1864227

### Prop 4: Moon lamp with an image of a pirate saying message “where’s me treasure chest”. 
*   **Location:** Attic
*   **Goal:** The player collects the 3rd shard and the scoreboard is iterated. The clue for the next prop is "Treasure Chest"
*   **Resource:** 3D Printed Moon Lamp Lithophane: https://makerworld.com/en/models/457912-customizable-moon-lamp-with-photo#profileId-3507486, Table Lamp Base: https://www.amazon.com/gp/product/B0G94JY7VV/ref=ox_sc_act_image_2?smid=A2FUQYPSMW6KBA&psc=1

### Prop 5: Treasure Chest with one coin with an Owl that says AOE
*   **Location:** Office
*   **Goal:** The player collects the 4th shard and the scoreboard is iterated. The clue for the next prop is "Owl" and "AOE
*   **Resource:** 3D Printed Chest is complete, 3D Printed Coin: https://makerworld.com/en/models/1206556-owl-of-athena-tetradrachma-coin-w-magnet-space?from=search#profileId-1220539

### Prop 6: Painting depicting a Owl and incorporates a crystal ball with the letters AOE written at the base. The crystal ball is illuminated by a led ring position behind the painting.
*   **Location:** Hallway
*   **Goal:** The player collects the 5th shard and the scoreboard is iterated. The clue for the next prop is "Crystal Ball" 
*   **Resource:** Printed painting

### Prop 7: Crystal Ball - Video/Audio message
*   **Location:** Dinning Room
*   **Goal:** Goal: Celebrate a major mid-game milestone, introduce a dramatic twist (e.g., the dragon is waking up or fighting back), provide a clue for the next prop, and pivot the players into the final stage of the game.  Collect the 6th shard and the scoreboard is iterated. The clue for the next prop is "Alchemist Study"
*   **Resource:** Message Script - Visual Direction: A hooded figure in a dark stone chamber. A large magical crystal ball or glowing arcane energy floats near him. The video should look slightly unstable, flickering with magical interference.  Video Script & Action Map: "The Dragon's Shadow" The video screen snaps on with a flash of blue light. The Wizard is looking frantically off-camera as smoke passes by. Loud rumbling sound effects, crackling fire.  He turns directly to the camera, gripping his staff. He looks relieved but exhausted. "You’ve done it! You've freed more than half of my splintered power! The magic is flowing back into the master grid. I can feel my strength returning... but so can he." A massive shadow shifts across the back wall behind the wizard. Red light illuminates the stone chamber. "Ignis has realized the shards are breaking! He is breathing fire to keep me trapped.”  The Wizard points directly at the screen. The video begins to heavily glitch and pixelate. The next shard is hiding inside my Alchemist Study. Hurry, before the connection is severed completely! Trust the wand!" The screen cuts to static, leaving a faint glowing symbol or sequence on the monitor for the players to write down. Sharp audio pop, tracking static.  - Voice is generated using: https://inworld.ai/voice-generator (Theodore Storyteller)  - TBD video to accompany voice

### Prop 8: Alchemist Study - Hidden within the study are letters that spell "Barrel"
*   **Location:** Living Room
*   **Goal:** The player collects the 7th shard and the scoreboard is iterated. The clue for the next prop is "Barrel" 
*   **Resource:** 3D Printed diorama: https://makerworld.com/en/models/2951017-the-alchemist-s-study-a-magical-diorama?from=search#profileId-3306437

### Prop 9: Barrel with a speaker inside of it that plays a message. “Stop the potion in the cauldron, it’s gonna blow”
*   **Location:** Pantry
*   **Goal:** The player collects the 8th shard and the scoreboard is iterated. The clue for the next prop is "Barrel" 
*   **Resource:** Message Script - (Muffled thumping from inside the barrel) Ahoy! Shh! Keep yer voice down, matey, or they'll hear ya!  Aye, it’s me—Captain Barnaby. I’m crammed in this blimey pickle barrel like a salted herring! But there's no time for proper introductions. We’ve got a massive problem out there, and I need yer help now! Look over at the wizard's cauldron. Do ya see it? It's fixin' to bubble over, and if that wicked brew spills, it's lights out for the both of us! Listen close. You’ve got the magic power in yer hands. Ready yer wand! You need to aim it straight at that bubbling cauldron and cast yer spell to halt the brew! Go on, wave the wand before the whole room goes up in smoke! Quick, matey, do it now!" https://inworld.ai/voice-generator (Salvador Commentator).  3D Printed Barrel: https://makerworld.com/en/models/190357-barrel-with-hinged-lid?from=search#profileId-210123

### Prop 10: Cauldron Foundation with mister. When turned off there is a message in floating in the water that says ‘Statue”
*   **Location:** Front Door 
*   **Goal:** The player collects the 9th shard and the scoreboard is iterated. The clue for the next prop is "Statue"
*   **Resource:** 3D Printed Mist Floater: https://makerworld.com/en/models/1229949-diy-air-humidifier-floater-for-mist-maker#profileId-1248550, Floating Sign: https://makerworld.com/en/models/3185035-no-pee-zone-floating-pool-sign?from=search#profileId-3602723

### Prop 11: Statue in front of the scoreboard - Living Room
*   **Location:** Living Room
*   **Goal:** The player collects the final 10th shard and the scoreboard is iterated. The scoreboard displays flashing magic attaches while the audio plays.  The completed puzzle is displayed with audio to congratulate the player.
*   **Resource:** 3d Printed Dragon Statue: https://makerworld.com/en/models/2806073-dragon-tower-lamp-fantasy-led-dragon-sculpture#profileId-3122444, Message Script - "The final piece has clicked! Look at the Great Quest board—the master puzzle is fully restored and glowing with pure, unbroken light!  The fractured essence has reunited, and the magic of the realm is reborn. Ignis has retreated into the shadows, his fire quenched by the power of your determination.  Congratulations, Cadette! You have done what many thought impossible. 

Through your bravery, quick thinking, and the true spark of magic within you, you have restored my power and saved the realm. The Cadette Realm is forever in your debt, young wizard.  Now, step forward and claim your reward—the magic is safe once more!"

