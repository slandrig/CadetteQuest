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
