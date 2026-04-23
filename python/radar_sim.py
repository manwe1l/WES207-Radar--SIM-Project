import serial
import time
import threading

PORT = "COM4"      # Air Heltec COM port
BAUD = 115200
SEND_INTERVAL = 10.0   # Send every 10 seconds

# Open the serial port
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)   # Give the board time to reset

# Short mode messages
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

    while running:
        # Get the current state
        with lock:
            key = current_key

        # Send the current state if valid
        if key in commands:
            msg = commands[key]
            ser.write(msg.encode())
            print("[TX]", msg.strip())

        # Read any reply from the Heltec
        time.sleep(0.1)
        while ser.in_waiting:
            response = ser.readline().decode(errors="ignore").strip()
            if response:
                print("[Heltec]", response)

        # Wait before sending again
        time.sleep(SEND_INTERVAL)

# Start the background sender
thread = threading.Thread(target=sender_loop, daemon=True)
thread.start()

print("=== Radar Telemetry Control ===")
print("b = BOOTING")
print("t = STANDBY")
print("a = ACTIVE")
print("s = SLEEP")
print("e = ERROR")
print("q = QUIT")
print("===============================")

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
