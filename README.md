# Cadette Quest Prototype Architecture

This repository hosts a multi-node, distributed physical puzzle escape room space. 
A centralized Flask control hub dictates scoring matrices while standalone edge components 
listen for precise IR patterns to alter physical relay outputs and lock states.

## Puzzle Progression Matrix (`REVEAL_SEQUENCE`)
The Central Server forces strict step-order progression. Elements triggered out of order will execute their local physical output animations but will be rejected on the master scoring table:

| Step | Target Object | Node Mapping | Unlocked Image Component |
| :--- | :--- | :--- | :--- |
| 1 | Node C (The Moon Lamp) | ID: 3 | Piece 10 |
| 2 | Node F (The Crystal Ball) | ID: 6 | Piece 9 |
| 3 | Node J (The Statue) | ID: 10 | Piece 8 |
| 4 | Node D (The Treasure Chest)| ID: 4 | Piece 4 |
| 5 | Node A (The Telephone) | ID: 1 | Piece 3 |
| 6 | Node I (The Cauldron) | ID: 9 | Piece 2 |
| 7 | Node G (The Alchemist Study)| ID: 7 | Piece 7 |
| 8 | Node E (The Painting) | ID: 5 | Piece 1 |
| 9 | Node B (The Book) | ID: 2 | Piece 6 |
| 10 | Node H (The Barrel) | ID: 8 | Piece 5 |

## Cold Start / Operator Reset Guide
1. Launch the master panel on the control machine:
   ```bash
   cd server && pip install -r requirements.txt
   python server.py
   ```
2. Navigate to `http://192.168.86.52:5000` to monitor status.
3. **Hardware Room Reset:** Because edge modules utilize a secure local lockout state machine (`scoreboard_allowed = False`) to minimize network drops, you must physically power-cycle or click the hardware reset button on all MicroPython boards to start a new game.
