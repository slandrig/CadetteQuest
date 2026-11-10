import machine
from machine import Pin
import time
import network
import socket

# --- Network Configuration ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.ifconfig(('192.168.86.207', '255.255.255.0', '192.168.86.1', '8.8.8.8'))

WIFI_SSID = "XXXXX"
WIFI_PASSWORD = "XXXXX"
WEB_SERVER_HOST = "192.168.86.52"  # Flask server host IP
WEB_SERVER_PORT = 5000

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
