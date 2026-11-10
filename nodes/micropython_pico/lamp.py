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

WIFI_SSID = "XXXXX"
WIFI_PASSWORD = "XXXXX"
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
