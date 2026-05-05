import serial
import time
import csv
import os
import random
import tkinter as tk
from tkinter import ttk, messagebox

PORT = "COM7"      # Air Heltec COM port
BAUD = 115200
LOG_FILE = f"air_log_{time.strftime('%Y%m%d_%H%M%S')}.csv"

# Pick a random startup state
startup_modes = ["MTI", "SARV", "MLV", "MSV"]
current_mode = random.choice(startup_modes)
current_tx = random.choice(["EN", "DIS"])
current_health = "OK"
current_alarm = "0"

last_command_packet = ""
last_status_packet = ""

# Open serial link to air Heltec
ser = serial.Serial(PORT, BAUD, timeout=0.1)
time.sleep(2)


def mode_label(code):
    """Convert short mode code to readable text."""
    names = {
        "MTI": "MTI",
        "SARV": "SARVideo",
        "MLV": "Maritime Large",
        "MSV": "Maritime Small"
    }
    return names.get(code, code)


def tx_label(code):
    """Convert TX code to readable text."""
    names = {
        "EN": "Enabled",
        "DIS": "Disabled"
    }
    return names.get(code, code)


def ensure_csv_header():
    """Create CSV header if file is new."""
    if not os.path.isfile(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
        with open(LOG_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "timestamp",
                "event_type",
                "command_id",
                "mode",
                "tx_state",
                "health",
                "alarm",
                "raw_packet"
            ])


def log_row(event_type, cid, mode, tx, health, alarm, raw_packet):
    """Save one log row."""
    with open(LOG_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            event_type,
            cid,
            mode_label(mode),
            tx_label(tx),
            health,
            alarm,
            raw_packet
        ])


def parse_packet(packet):
    """Break packet into key/value fields."""
    fields = {}
    for part in packet.split(","):
        if "=" in part:
            key, value = part.split("=", 1)
            fields[key.strip()] = value.strip()
    return fields


def add_log(text):
    """Show one line in the event log."""
    log_box.insert(tk.END, text + "\n")
    log_box.see(tk.END)


def build_status_packet(cid):
    """Build one status packet to send back."""
    return (
        f"T=STAT,CID={cid},MODE={current_mode},TX={current_tx},"
        f"H={current_health},A={current_alarm}\n"
    )


def send_status(cid):
    """Send current radar state to the air Heltec."""
    global last_status_packet

    packet = build_status_packet(cid)
    ser.write(packet.encode())
    last_status_packet = packet.strip()

    # Update GUI
    status_packet_var.set(last_status_packet)
    mode_var.set(mode_label(current_mode))
    tx_var.set(tx_label(current_tx))
    health_var.set(current_health)
    alarm_var.set(current_alarm)
    last_update_var.set(time.strftime("%Y-%m-%d %H:%M:%S"))

    # Update log window
    add_log(
        f"AIR TX | Type=Status | CID={cid} | "
        f"Mode={mode_label(current_mode)} | TX={tx_label(current_tx)} | "
        f"Health={current_health} | Alarm={current_alarm}"
    )

    # Save to CSV
    log_row(
        "STATUS_SENT",
        cid,
        current_mode,
        current_tx,
        current_health,
        current_alarm,
        last_status_packet
    )


def poll_serial():
    """Check for incoming commands from the air Heltec."""
    global current_mode, current_tx, last_command_packet

    while ser.in_waiting:
        line = ser.readline().decode(errors="ignore").strip()

        if not line:
            continue

        # Only handle command packets
        if line.startswith("T=CMD"):
            last_command_packet = line
            command_packet_var.set(line)

            fields = parse_packet(line)
            cid = fields.get("CID", "0")

            # Update local radar state
            if "MODE" in fields:
                current_mode = fields["MODE"]
            if "TX" in fields:
                current_tx = fields["TX"]

            # Update GUI
            mode_var.set(mode_label(current_mode))
            tx_var.set(tx_label(current_tx))
            health_var.set(current_health)
            alarm_var.set(current_alarm)
            last_update_var.set(time.strftime("%Y-%m-%d %H:%M:%S"))

            # Update log window
            add_log(
                f"AIR RX | Type=Command | CID={cid} | "
                f"Mode={mode_label(current_mode)} | TX={tx_label(current_tx)}"
            )

            # Save to CSV
            log_row(
                "COMMAND_RECEIVED",
                cid,
                current_mode,
                current_tx,
                current_health,
                current_alarm,
                line
            )

            # Send updated status back
            send_status(cid)

    # Check again soon
    root.after(100, poll_serial)


def resend_status():
    """Manually resend current status."""
    send_status("0")


def on_close():
    """Close program cleanly."""
    if messagebox.askokcancel("Exit", "Close the air HMI and stop logging?"):
        try:
            ser.close()
        except:
            pass
        root.destroy()


# Build GUI window
root = tk.Tk()
root.title("Air Radar Simulator HMI")
root.geometry("920x680")
root.protocol("WM_DELETE_WINDOW", on_close)

# GUI variables
mode_var = tk.StringVar(value=mode_label(current_mode))
tx_var = tk.StringVar(value=tx_label(current_tx))
health_var = tk.StringVar(value=current_health)
alarm_var = tk.StringVar(value=current_alarm)
last_update_var = tk.StringVar(value="")
command_packet_var = tk.StringVar(value="")
status_packet_var = tk.StringVar(value="")
log_file_var = tk.StringVar(value=LOG_FILE)

# Current state frame
top = ttk.LabelFrame(root, text="Current Radar State")
top.pack(fill="x", padx=10, pady=10)

ttk.Label(top, text="Mode:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
ttk.Label(top, textvariable=mode_var).grid(row=0, column=1, padx=5, pady=5, sticky="w")

ttk.Label(top, text="TX State:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
ttk.Label(top, textvariable=tx_var).grid(row=0, column=3, padx=5, pady=5, sticky="w")

ttk.Label(top, text="Health:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
ttk.Label(top, textvariable=health_var).grid(row=1, column=1, padx=5, pady=5, sticky="w")

ttk.Label(top, text="Alarm:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
ttk.Label(top, textvariable=alarm_var).grid(row=1, column=3, padx=5, pady=5, sticky="w")

ttk.Label(top, text="Last Update:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
ttk.Label(top, textvariable=last_update_var).grid(row=2, column=1, padx=5, pady=5, sticky="w")

ttk.Label(top, text="Log File:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
ttk.Label(top, textvariable=log_file_var, wraplength=700).grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky="w")

# Packet frame
mid = ttk.LabelFrame(root, text="Packets")
mid.pack(fill="x", padx=10, pady=10)

ttk.Label(mid, text="Last Command Packet:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
ttk.Label(mid, textvariable=command_packet_var, wraplength=780).grid(row=1, column=0, padx=5, pady=5, sticky="w")

ttk.Label(mid, text="Last Status Packet:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
ttk.Label(mid, textvariable=status_packet_var, wraplength=780).grid(row=3, column=0, padx=5, pady=5, sticky="w")

# Buttons
btn_frame = ttk.Frame(root)
btn_frame.pack(fill="x", padx=10, pady=5)

ttk.Button(btn_frame, text="Resend Current Status", command=resend_status).pack(side="left", padx=5)
ttk.Button(btn_frame, text="Exit", command=on_close).pack(side="right", padx=5)

# Event log
log_frame = ttk.LabelFrame(root, text="Event Log")
log_frame.pack(fill="both", expand=True, padx=10, pady=10)

log_box = tk.Text(log_frame, height=18)
log_box.pack(fill="both", expand=True, padx=5, pady=5)

# Start logging and polling
ensure_csv_header()
add_log("Air HMI started.")
add_log(f"Random startup state: Mode={mode_label(current_mode)}, TX={tx_label(current_tx)}")
send_status("0")
poll_serial()

root.mainloop()