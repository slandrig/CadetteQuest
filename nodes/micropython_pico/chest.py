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
WIFI_SSID = "CCCCC"
WIFI_PASSWORD = "CCCCC"
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
