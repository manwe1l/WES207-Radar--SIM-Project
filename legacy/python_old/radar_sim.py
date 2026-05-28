import serial
import time

PORT = "COM5"      # Air Heltec COM port
BAUD = 115200

# Current simulated radar state
current_mode = "MTI"
current_tx = "EN"
current_health = "OK"
current_alarm = "0"


def parse_packet(packet):
    """Split packet text into fields."""
    fields = {}
    for part in packet.split(","):
        if "=" in part:
            key, value = part.split("=", 1)
            fields[key.strip()] = value.strip()
    return fields


def build_status_packet(cid):
    """Build one returned status packet."""
    return (
        f"T=STAT,CID={cid},MODE={current_mode},TX={current_tx},"
        f"H={current_health},A={current_alarm}\n"
    )


def main():
    global current_mode, current_tx

    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)

    print("Air radar simulator started.")
    print("Waiting for command packets...")

    try:
        while True:
            if ser.in_waiting:
                line = ser.readline().decode(errors="ignore").strip()

                if not line:
                    continue

                print("[AIR RX]", line)

                if not line.startswith("T=CMD"):
                    continue

                fields = parse_packet(line)

                # Update simulated radar state
                if "MODE" in fields:
                    current_mode = fields["MODE"]
                if "TX" in fields:
                    current_tx = fields["TX"]

                cid = fields.get("CID", "0")

                # Send status back
                status = build_status_packet(cid)
                ser.write(status.encode())
                print("[AIR TX]", status.strip())

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        ser.close()
        print("Serial port closed.")


if __name__ == "__main__":
    main()