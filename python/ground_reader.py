import serial
import csv
import time

PORT = "COM5"      # Ground Heltec COM port
BAUD = 115200
LOG_FILE = "ground_log.csv"

# Open serial port
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)   # Give the board time to reset

print("Ground reader started.")
print("Logging to:", LOG_FILE)

# Open the CSV log file
with open(LOG_FILE, "a", newline="") as file:
    writer = csv.writer(file)

    # Add a header row if needed
    writer.writerow(["timestamp", "packet"])

    while True:
        if ser.in_waiting:
            line = ser.readline().decode(errors="ignore").strip()

            # Only log packet lines
            if line.startswith("DATA:"):
                packet = line.replace("DATA:", "").strip()
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

                print("[RX]", packet)
                writer.writerow([timestamp, packet])
                file.flush()
