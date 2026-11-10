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
---

## 2. HARDWARE MAP & WIRE TABLES

### NODE A: 3D-PRINTED TELEPHONE
*   **Processor:** Raspberry Pi Single Board Computer (SBC)
*   **Wand Detector:** TSOP IR Sensor Module
*   **Hook Tracking:** Photoelectric Sensor / Mechanical Microswitch tracking receiver position
*   **Audio Output:** Native ALSA layer (3.5mm jack or HDMI audio breakout mapped to `mplayer`)

### NODE B: 3D-PRINTED Book
*   **Microcontroller:** Raspberry Pi Pico W
*   **IR Receiver:** TSOP38238 (Tuned to MagiQuest DNA pulses: Long ~840µs / Short ~310µs)
*   **Visual Elements:** NeoPixel Ring x12

### NODE C: 3D-PRINTED Moon Lamp
*   **Microcontroller:** Raspberry Pi Pico W
*   **IR Receiver:** TSOP38238 (Tuned to MagiQuest DNA pulses: Long ~840µs / Short ~310µs)
*   **AC power outlet controlled by a gpio pin to power the lamp

### NODE D: 3D-PRINTED Treasure Chest
*   **Microcontroller:** Raspberry Pi Pico W
*   **IR Receiver:** TSOP38238 (Tuned to MagiQuest DNA pulses: Long ~840µs / Short ~310µs)
*   **Stepper Driver:** ULN2003 Driver Board powering a 28BYJ-48 Stepper Motor
*   **Visual Elements:** 3x Low-voltage LEDs chained in parallel or indexed individually

### NODE E: Painting
*   **Microcontroller:** Raspberry Pi Pico W
*   **IR Receiver:** TSOP38238 (Tuned to MagiQuest DNA pulses: Long ~840µs / Short ~310µs)
*   **Visual Elements:** NeoPixel Ring x24

### NODE F: Hologram Fan Projector depicting a crystal ball
*   **Microcontroller:** Raspberry Pi Pico W
*   **IR Receiver:** TSOP38238 (Tuned to MagiQuest DNA pulses: Long ~840µs / Short ~310µs)
*   **1 Channel DC 3V/3.3V Power Relay Module to control AC power to the projector
*   **Audio Output:** Native ALSA layer (3.5mm jack or HDMI audio breakout mapped to `mplayer`)

### NODE G: 3D-PRINTED Alchemist Study Diorama 
*   **Microcontroller:** Raspberry Pi Pico W
*   **IR Receiver:** TSOP38238 (Tuned to MagiQuest DNA pulses: Long ~840µs / Short ~310µs)
*   ****AC power outlet controlled by a gpio pin to power the Diorama

### NODE H: 3D-PRINTED Barrel 
*   **Microcontroller:** Raspberry Pi Pico W
*   **IR Receiver:** TSOP38238 (Tuned to MagiQuest DNA pulses: Long ~840µs / Short ~310µs)
*   **Audio Output:** NS4168 I2S Audio Amplifier & 3W Speaker Kit

### NODE I: Cauldron with normally on mister 
*   **Microcontroller:** Raspberry Pi Pico W
*   **IR Receiver:** TSOP38238 (Tuned to MagiQuest DNA pulses: Long ~840µs / Short ~310µs)
*   ****AC power outlet controlled by a gpio pin to power the mister

### NODE J: 3D-PRINTED Dragon Statue 
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
1.  **Boot Up:** Joins Wi-Fi AP and initializes internal logic loop gates with `scoreboard_allowed = True`.
2.  **Standby:** Loops through sub-100ms scans of the TSOP data pin. 
3.  **Spell Match:** If a magic pattern matches constraints, the ring LEDs preform a "moon beam" sequence for 30 seconds
4.  **Network Push:** Fires a raw HTTP POST straight out of low-level `socket` objects directly to `192.168.86.52:5000/score` (bypassing native `urequests` memory fragmentation crashes).
5.  **Local Lockout Engaged:** Sets `scoreboard_allowed = False`. Future spell casts will trigger the 30-second ring LED flash sequence, but will never issue network payloads until the board is physically rebooted.

### THE LAMP ENGINE FLOW (`lamp.py`)
1.  **Boot Up:** Joins Wi-Fi AP and initializes internal logic loop gates with `scoreboard_allowed = True`.
2.  **Standby:** Loops through sub-100ms scans of the TSOP data pin. 
3.  **Spell Match:** If a magic pattern matches constraints, trigger the relay to apply AC power to the lamp for 60 seconds before turning back off.
4.  **Network Push:** Fires a raw HTTP POST straight out of low-level `socket` objects directly to `192.168.86.52:5000/score` (bypassing native `urequests` memory fragmentation crashes).
5.  **Local Lockout Engaged:** Sets `scoreboard_allowed = False`. Future spell casts will trigger the 60-second AC power toggle, but will never issue network payloads until the board is physically rebooted.

### THE CHEST ENGINE FLOW (`chest.py`)
1.  **Boot Up:** Joins Wi-Fi AP and initializes internal logic loop gates with `scoreboard_allowed = True`.
2.  **Standby:** Loops through sub-100ms scans of the TSOP data pin. 
3.  **Spell Match:** If a magic pattern matches constraints, it bypasses network lag to drive the full-sequence stepper immediately to open the lid.
4.  **Network Push:** Fires a raw HTTP POST straight out of low-level `socket` objects directly to `192.168.86.52:5000/score` (bypassing native `urequests` memory fragmentation crashes).
5.  **Local Lockout Engaged:** Sets `scoreboard_allowed = False`. Future spell casts will trigger the 30-second LED flash window and run physical stepper mechanisms, but will never issue network payloads until the board is physically rebooted.

### THE PAINTING ENGINE FLOW (`painting.py`)
1.  **Boot Up:** Joins Wi-Fi AP and initializes internal logic loop gates with `scoreboard_allowed = True`.
2.  **Standby:** Loops through sub-100ms scans of the TSOP data pin. 
3.  **Spell Match:** If a magic pattern matches constraints, the ring LEDs preform a "Crystal Ball" sequence for 30 seconds
4.  **Network Push:** Fires a raw HTTP POST straight out of low-level `socket` objects directly to `192.168.86.52:5000/score` (bypassing native `urequests` memory fragmentation crashes).
5.  **Local Lockout Engaged:** Sets `scoreboard_allowed = False`. Future spell casts will trigger the 30-second ring LED flash sequence, but will never issue network payloads until the board is physically rebooted.

### THE CRYSTAL BALL ENGINE FLOW (`crystal.py`)
1.  **Boot Up:** Joins Wi-Fi AP and initializes internal logic loop gates with `scoreboard_allowed = True`.
2.  **Standby:** Loops through sub-100ms scans of the TSOP data pin. 
2.  **Spell Match:** Standby loop tracks `WAND_IR_SENSOR`. When hit, trigger the relay to apply AC power to the Hologram Fan Projector. 
3.  **Payload & Score:** As soon as the wand is identified an HTTP POST tracking string to the Flask engine. It then engages a local lockout (`scoreboard_allowed = False`) until a manual system power cycle takes place.
4.  **Reset: The relay will remove power once after a set delay.

### THE ALCHEMIST STUDY ENGINE FLOW (`study.py`)
1.  **Boot Up:** Joins Wi-Fi AP and initializes internal logic loop gates with `scoreboard_allowed = True`.
2.  **Standby:** Loops through sub-100ms scans of the TSOP data pin. 
3.  **Spell Match:** If a magic pattern matches constraints, trigger the relay to apply AC power to the diorama for 180 seconds before turning back off.
4.  **Network Push:** Fires a raw HTTP POST straight out of low-level `socket` objects directly to `192.168.86.52:5000/score` (bypassing native `urequests` memory fragmentation crashes).
5.  **Local Lockout Engaged:** Sets `scoreboard_allowed = False`. Future spell casts will trigger the 180-second AC power toggle, but will never issue network payloads until the board is physically rebooted.

### THE BARREL ENGINE FLOW (`barrel.py`)
1.  **Boot Up:** Joins Wi-Fi AP and initializes internal logic loop gates with `scoreboard_allowed = True`.
2.  **Standby:** Loops through sub-100ms scans of the TSOP data pin. 
3.  **Spell Match:** If a magic pattern matches constraints, trigger an audio file to be play through the speaker.
4.  **Network Push:** Fires a raw HTTP POST straight out of low-level `socket` objects directly to `192.168.86.52:5000/score` (bypassing native `urequests` memory fragmentation crashes).
5.  **Local Lockout Engaged:** Sets `scoreboard_allowed = False`. Future spell casts will trigger the audio file, but will never issue network payloads until the board is physically rebooted.

### THE CAULDRON ENGINE FLOW (`cauldron.py`)
1.  **Boot Up:** Joins Wi-Fi AP and initializes internal logic loop gates with `scoreboard_allowed = True`.
2.  **Standby:** Loops through sub-100ms scans of the TSOP data pin. 
3.  **Spell Match:** If a magic pattern matches constraints, trigger the relay to remove apply AC power from the mister lamp for 180 seconds before turning back off.
4.  **Network Push:** Fires a raw HTTP POST straight out of low-level `socket` objects directly to `192.168.86.52:5000/score` (bypassing native `urequests` memory fragmentation crashes).
5.  **Local Lockout Engaged:** Sets `scoreboard_allowed = False`. Future spell casts will trigger the 180-second AC power toggle, but will never issue network payloads until the board is physically rebooted.

### THE STATUE ENGINE FLOW (`statue.py`)
1.  **Boot Up:** Joins Wi-Fi AP and initializes internal logic loop gates with `scoreboard_allowed = True`.
2.  **Standby:** Loops through sub-100ms scans of the TSOP data pin. 
3.  **Spell Match:** If a magic pattern matches constraints, the LEDs ring play a sequence of rainbow lighting flashes followed by a fade up to white.
4.  **Network Push:** Fires a raw HTTP POST straight out of low-level `socket` objects directly to `192.168.86.52:5000/score` (bypassing native `urequests` memory fragmentation crashes).
5.  **Local Lockout Engaged:** If this is the final trigger the scoreboard will play the congratulations audio file. 

---

#############


## 3. STORYLINE

### Prop 1: The Initial Scroll (Context Reference)
*   **Location:** Printer Room
*   **Goal:** The Player's Knowledge Base: At this stage, they know they must find 10 objects, use the wand, and restore the puzzle pieces. The phone is right in front of them as the logical first step.
*   **Resource:** Scroll Text - TBD

### Prop 2: Phone - The Wizard’s Telephone Audio Message
*   **Location:** Printer Room
*   **Goal:** Provide narrative depth, explain why the phone is magic, give a cryptic clue for the next prop, and set the emotional stakes.  Make note that the props must be found in the correct order.  This will encourage the player not to just run as fast as they can and point the wand at anything and everything they can find. Collect the 1st shard and the scoreboard is iterated.
*   **Resource:** 3D Printed Phone, Message Script - Tone: Crackly, distorted by magic, frantic but encouraging. Script Concept: "The Echo Chamber" (Sound Effects: Loud magical static, followed by a heavy mechanical clicking sound. The Wizard's voice filters in, sounding like he is speaking down a long metallic pipe.) "Hello? Can you hear me through the temporal static? Ah! The wand has re-established the connection!
Listen closely—I am Eldrin, the Keeper of the Cadette Realm. When the Dragon Ignis tore my magic from me, it fractured. My essence was shattered into ten distinct shards and sealed inside everyday items to hide them from his sight. You hold the first shard right now. This very telephone carries the echo of my voice. By lifting the receiver, you have freed my ability to speak to you! Look at the Great Quest board—the master puzzle is beginning to wake up. But our time is short. The other nine shards are nearby, hidden in plain sight. They will hum with a faint energy, waiting for the wand's counter-spell. Seek the place where shadows gather near the bookshelves next... and beware the dragon’s gaze. Find the shards, restore the master puzzle, and bring back the magic before the hour expires!" - Voice is generated using: https://inworld.ai/voice-generator (Theodore Storyteller)

### Prop 3: Book on a shelf that lights up an image of the moon
*   **Location:** Living Room
*   **Goal:** The player collects the 2nd shard and the scoreboard is iterated. The clue for the next prop is "Moon"
*   **Resource:** 3D Printed Book: https://makerworld.com/en/models/1753318-the-book-of-the-moon?from=search#profileId-1864227

### Prop 4: Moon lamp with an image of a pirate saying message “where’s me treasure chest”. 
*   **Location:** Attic
*   **Goal:** The player collects the 3rd shard and the scoreboard is iterated. The clue for the next prop is "Treasure Chest"
*   **Resource:** 3D Printed Moon Lamp Lithophane: https://makerworld.com/en/models/457912-customizable-moon-lamp-with-photo#profileId-3507486, Table Lamp Base: 

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
*   **Goal:** The player collects the 9th shard and the scoreboard is iterated. The clue for the next prop is "Don't Pee on the Statue"
*   **Resource:** 3D Printed Mist Floater: https://makerworld.com/en/models/1229949-diy-air-humidifier-floater-for-mist-maker#profileId-1248550, Floating Sign: https://makerworld.com/en/models/3185035-no-pee-zone-floating-pool-sign?from=search#profileId-3602723

### Prop 11: Statue in front of the scoreboard - Living Room
*   **Location:** Living Room
*   **Goal:** The player collects the final 10th shard and the scoreboard is iterated. The scoreboard displays flashing magic attaches while the audio plays.  The completed puzzle is displayed with audio to congratulate the player.
*   **Resource:** 3d Printed Dragon Statue: https://makerworld.com/en/models/2806073-dragon-tower-lamp-fantasy-led-dragon-sculpture#profileId-3122444, Message Script - "The final piece has clicked! Look at the Great Quest board—the master puzzle is fully restored and glowing with pure, unbroken light!  The fractured essence has reunited, and the magic of the realm is reborn. Ignis has retreated into the shadows, his fire quenched by the power of your determination.  Congratulations, Cadette! You have done what many thought impossible. Through your bravery, quick thinking, and the true spark of magic within you, you have restored my power and saved the realm. The Cadette Realm is forever in your debt, young wizard.  Now, step forward and claim your reward—the magic is safe once more!"

