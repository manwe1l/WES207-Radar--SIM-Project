import serial
import time
import threading

PORT = "COM4"          # Air Heltec COM port
BAUD = 115200
SEND_INTERVAL = 20.0   # One packet every 20 seconds

# Open serial port
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)   # Let the board reset

# Short status messages
commands = {
    "b": "M=B,H=OK,A=0\n",   # Booting
    "t": "M=T,H=OK,A=0\n",   # Standby
    "a": "M=A,H=OK,A=0\n",   # Active
    "s": "M=S,H=OK,A=0\n",   # Sleep
    "e": "M=E,H=F,A=1\n",    # Error
}

current_key = "t"   # Start in standby
running = True
lock = threading.Lock()

def sender_loop():
    global running

    # Send one full status packet at startup
    with lock:
        key = current_key

    if key in commands:
        msg = commands[key]
        ser.write(msg.encode())
        print("[TX startup]", msg.strip())

    # Send one status packet every 20 seconds
    while running:
        time.sleep(SEND_INTERVAL)

        with lock:
            key = current_key

        if key in commands:
            msg = commands[key]
            ser.write(msg.encode())
            print("[TX periodic]", msg.strip())

        # Read any replies from the Heltec
        time.sleep(0.1)
        while ser.in_waiting:
            response = ser.readline().decode(errors="ignore").strip()
            if response:
                print("[Heltec]", response)

# Start background sender
thread = threading.Thread(target=sender_loop, daemon=True)
thread.start()

print("=== Radar Telemetry Control ===")
print("b = BOOTING")
print("t = STANDBY")
print("a = ACTIVE")
print("s = SLEEP")
print("e = ERROR")
print("q = QUIT")
print("State changes are sent on the next 20-second update")
print("================================")

while True:
    key = input("Enter command: ").strip().lower()

    if key == "q":
        running = False
        break
    elif key in commands:
        with lock:
            current_key = key
        print("State changed to:", commands[key].strip())
    else:
        print("Invalid key.")

thread.join(timeout=1)
ser.close()
print("Exited cleanly.")
