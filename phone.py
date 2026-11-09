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
