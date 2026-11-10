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

WIFI_SSID = "XXXXX"
WIFI_PASSWORD = "XXXXX"
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
        crystal_glow_animation(tick_counter)
        tick_counter += 1  # Drive the plasma wave shape forward continuously
        
        # Monitor 30-second display window expiration
        if time.ticks_diff(current_time, animation_start) >= 30000:
            clear_leds()
            spell_active = False
            print("Animation cycle complete. Returning to standby.")
            
    time.sleep_ms(15)
