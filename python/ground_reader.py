import serial
import csv
import time

PORT = "COM5"      # Ground Heltec COM port
BAUD = 115200
LOG_FILE = "ground_log.csv"
MIN_EXPECTED_GAP = 20.0   # seconds

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)

print("Ground reader started.")
print("Logging to:", LOG_FILE)

last_rx_time = None

with open(LOG_FILE, "a", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["timestamp", "delta_sec", "packet"])

    while True:
        if ser.in_waiting:
            line = ser.readline().decode(errors="ignore").strip()

            if line.startswith("DATA:"):
                packet = line.replace("DATA:", "").strip()
                now = time.time()
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

                if last_rx_time is None:
                    delta = ""
                    print(f"[RX] {timestamp}  {packet}")
                else:
                    delta = round(now - last_rx_time, 2)
                    print(f"[RX] {timestamp}  dt={delta}s  {packet}")

                    if delta < MIN_EXPECTED_GAP:
                        print("[WARN] Packet arrived sooner than 20 seconds")

                writer.writerow([timestamp, delta, packet])
                file.flush()
                last_rx_time = now