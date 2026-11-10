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

WIFI_SSID = "XXXXX"
WIFI_PASSWORD = "XXXXX"
WEB_SERVER_HOST = "192.168.86.52"
WEB_SERVER_PORT = 5000

MQ_LONG_PULSE = 840
MQ_SHORT_PULSE = 310
TOLERANCE = 100 

# --- Pin Definitions ---
ir_pin = Pin(11, Pin.IN)
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