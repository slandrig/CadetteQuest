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