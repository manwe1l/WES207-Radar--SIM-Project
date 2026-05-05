import serial
import time
import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox

PORT = "COM5"      # Ground Heltec COM port
BAUD = 115200
LOG_FILE = f"ground_log_{time.strftime('%Y%m%d_%H%M%S')}.csv"

# Open serial link to ground Heltec
ser = serial.Serial(PORT, BAUD, timeout=0.1)
time.sleep(2)

# Current command state
command_id = 0
commanded_mode = "MTI"
commanded_tx = "EN"
last_packet_time = None

# Test counters
total_commands = 0
total_responses = 0
mode_change_count = 0
tx_change_count = 0
match_count = 0
mismatch_count = 0

# Save sent commands by CID
pending_commands = {}


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


def packet_type_label(code):
    """Convert packet type to readable text."""
    names = {
        "CMD": "Command",
        "STAT": "Status"
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
                "commanded_mode",
                "commanded_tx_state",
                "reported_mode",
                "reported_tx_state",
                "health",
                "alarm",
                "latency_sec",
                "match",
                "raw_packet"
            ])


def log_result(row):
    """Save one row to CSV."""
    with open(LOG_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(row)


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


def update_metrics_labels():
    """Refresh metric counters on screen."""
    total_commands_var.set(str(total_commands))
    total_responses_var.set(str(total_responses))
    mode_changes_var.set(str(mode_change_count))
    tx_changes_var.set(str(tx_change_count))
    matches_var.set(str(match_count))
    mismatches_var.set(str(mismatch_count))


def send_command():
    """Send one command packet to the ground Heltec."""
    global command_id, total_commands

    command_id += 1
    total_commands += 1

    ts = time.time()
    packet = f"T=CMD,CID={command_id},TS={ts},MODE={commanded_mode},TX={commanded_tx}\n"
    ser.write(packet.encode())

    # Save pending command info
    pending_commands[str(command_id)] = {
        "send_time": ts,
        "mode": commanded_mode,
        "tx": commanded_tx
    }

    # Update GUI
    commanded_mode_var.set(mode_label(commanded_mode))
    commanded_tx_var.set(tx_label(commanded_tx))
    command_packet_var.set(packet.strip())

    # Update log window
    add_log(
        f"GROUND TX | Type=Command | CID={command_id} | "
        f"Mode={mode_label(commanded_mode)} | TX={tx_label(commanded_tx)}"
    )

    # Save to CSV
    log_result([
        time.strftime("%Y-%m-%d %H:%M:%S"),
        "COMMAND_SENT",
        command_id,
        mode_label(commanded_mode),
        tx_label(commanded_tx),
        "",
        "",
        "",
        "",
        "",
        "",
        packet.strip()
    ])

    update_metrics_labels()


def set_mode(mode_code):
    """Change radar mode and send command."""
    global commanded_mode, mode_change_count
    if commanded_mode != mode_code:
        commanded_mode = mode_code
        mode_change_count += 1
    send_command()


def set_tx(tx_state):
    """Change TX state and send command."""
    global commanded_tx, tx_change_count
    if commanded_tx != tx_state:
        commanded_tx = tx_state
        tx_change_count += 1
    send_command()


def resend_command():
    """Resend the current command."""
    send_command()


def update_result():
    """Compare commanded and reported state."""
    cmd_mode = commanded_mode_var.get()
    cmd_tx = commanded_tx_var.get()
    rep_mode = reported_mode_var.get()
    rep_tx = reported_tx_var.get()
    rep_health = health_var.get()
    rep_alarm = alarm_var.get()

    if rep_health == "FAULT" or rep_alarm == "1":
        result_var.set("FAULT")
    elif cmd_mode == rep_mode and cmd_tx == rep_tx:
        result_var.set("MATCH")
    else:
        result_var.set("MISMATCH")


def poll_serial():
    """Check for returned status packets."""
    global last_packet_time, total_responses, match_count, mismatch_count

    while ser.in_waiting:
        line = ser.readline().decode(errors="ignore").strip()

        if not line:
            continue

        # Only handle status packets
        if line.startswith("T=STAT"):
            last_packet_time = time.time()
            total_responses += 1

            fields = parse_packet(line)
            cid = fields.get("CID", "")

            rep_mode = fields.get("MODE", "")
            rep_tx = fields.get("TX", "")
            rep_health = fields.get("H", "")
            rep_alarm = fields.get("A", "")

            # Update GUI
            packet_type_var.set(packet_type_label(fields.get("T", "")))
            packet_id_var.set(cid)
            reported_mode_var.set(mode_label(rep_mode))
            reported_tx_var.set(tx_label(rep_tx))
            health_var.set("OK" if rep_health == "OK" else "FAULT")
            alarm_var.set(rep_alarm)
            last_update_var.set(time.strftime("%Y-%m-%d %H:%M:%S"))
            raw_packet_var.set(line)

            latency = ""
            match_value = "NO"

            # Match response to sent command
            if cid in pending_commands:
                sent = pending_commands[cid]
                latency = round(time.time() - sent["send_time"], 2)

                if sent["mode"] == rep_mode and sent["tx"] == rep_tx and rep_health == "OK" and rep_alarm == "0":
                    match_value = "YES"
                    match_count += 1
                else:
                    match_value = "NO"
                    mismatch_count += 1

            # Update log window
            add_log(
                f"GROUND RX | Type=Status | CID={cid} | "
                f"Mode={mode_label(rep_mode)} | TX={tx_label(rep_tx)} | "
                f"Health={'OK' if rep_health == 'OK' else 'FAULT'} | "
                f"Alarm={rep_alarm} | Latency={latency}s | Match={match_value}"
            )

            # Save to CSV
            log_result([
                time.strftime("%Y-%m-%d %H:%M:%S"),
                "STATUS_RECEIVED",
                cid,
                mode_label(pending_commands.get(cid, {}).get("mode", "")),
                tx_label(pending_commands.get(cid, {}).get("tx", "")),
                mode_label(rep_mode),
                tx_label(rep_tx),
                "OK" if rep_health == "OK" else "FAULT",
                rep_alarm,
                latency,
                match_value,
                line
            ])

            update_result()
            update_metrics_labels()

    # Update link status
    if last_packet_time is None:
        link_var.set("NO DATA")
    else:
        age = time.time() - last_packet_time
        link_var.set("OK" if age <= 60 else "STALE")

    # Check again soon
    root.after(100, poll_serial)


def on_close():
    """Close program cleanly."""
    if messagebox.askokcancel("Exit", "Close the ground HMI and stop logging?"):
        try:
            ser.close()
        except:
            pass
        root.destroy()


# Build GUI window
root = tk.Tk()
root.title("Ground Radar Telemetry HMI")
root.geometry("1220x780")
root.protocol("WM_DELETE_WINDOW", on_close)

# GUI variables
link_var = tk.StringVar(value="NO DATA")
last_update_var = tk.StringVar(value="")
packet_id_var = tk.StringVar(value="")
packet_type_var = tk.StringVar(value="")
result_var = tk.StringVar(value="")
log_file_var = tk.StringVar(value=LOG_FILE)

total_commands_var = tk.StringVar(value="0")
total_responses_var = tk.StringVar(value="0")
mode_changes_var = tk.StringVar(value="0")
tx_changes_var = tk.StringVar(value="0")
matches_var = tk.StringVar(value="0")
mismatches_var = tk.StringVar(value="0")

commanded_mode_var = tk.StringVar(value=mode_label(commanded_mode))
commanded_tx_var = tk.StringVar(value=tx_label(commanded_tx))
command_packet_var = tk.StringVar(value="")

reported_mode_var = tk.StringVar(value="")
reported_tx_var = tk.StringVar(value="")
health_var = tk.StringVar(value="")
alarm_var = tk.StringVar(value="")
raw_packet_var = tk.StringVar(value="")

# Link status frame
top = ttk.LabelFrame(root, text="Link Status")
top.pack(fill="x", padx=10, pady=10)

labels = [
    ("Link:", link_var), ("Last Update:", last_update_var),
    ("Packet Type:", packet_type_var), ("CID:", packet_id_var),
    ("Result:", result_var)
]
for i, (label, var) in enumerate(labels):
    ttk.Label(top, text=label).grid(row=0, column=i*2, sticky="w", padx=5, pady=5)
    ttk.Label(top, textvariable=var).grid(row=0, column=i*2+1, sticky="w", padx=5, pady=5)

ttk.Label(top, text="Log File:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
ttk.Label(top, textvariable=log_file_var, wraplength=900).grid(row=1, column=1, columnspan=9, sticky="w", padx=5, pady=5)

# Middle frame
middle = ttk.Frame(root)
middle.pack(fill="x", padx=10, pady=10)

# Command frame
cmd_frame = ttk.LabelFrame(middle, text="Commanded State")
cmd_frame.pack(side="left", fill="both", expand=True, padx=5)

ttk.Label(cmd_frame, text="Mode:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
ttk.Label(cmd_frame, textvariable=commanded_mode_var).grid(row=0, column=1, sticky="w", padx=5, pady=5)
ttk.Label(cmd_frame, text="TX State:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
ttk.Label(cmd_frame, textvariable=commanded_tx_var).grid(row=1, column=1, sticky="w", padx=5, pady=5)

ttk.Button(cmd_frame, text="MTI", command=lambda: set_mode("MTI")).grid(row=2, column=0, padx=5, pady=5)
ttk.Button(cmd_frame, text="SARVideo", command=lambda: set_mode("SARV")).grid(row=2, column=1, padx=5, pady=5)
ttk.Button(cmd_frame, text="Maritime Large", command=lambda: set_mode("MLV")).grid(row=3, column=0, padx=5, pady=5)
ttk.Button(cmd_frame, text="Maritime Small", command=lambda: set_mode("MSV")).grid(row=3, column=1, padx=5, pady=5)
ttk.Button(cmd_frame, text="TX Enable", command=lambda: set_tx("EN")).grid(row=4, column=0, padx=5, pady=5)
ttk.Button(cmd_frame, text="TX Disable", command=lambda: set_tx("DIS")).grid(row=4, column=1, padx=5, pady=5)
ttk.Button(cmd_frame, text="Resend Command", command=resend_command).grid(row=5, column=0, columnspan=2, padx=5, pady=10)

ttk.Label(cmd_frame, text="Last Command Packet:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
ttk.Label(cmd_frame, textvariable=command_packet_var, wraplength=420).grid(row=7, column=0, columnspan=2, sticky="w", padx=5, pady=5)

# Report frame
rep_frame = ttk.LabelFrame(middle, text="Reported Radar State")
rep_frame.pack(side="left", fill="both", expand=True, padx=5)

report_items = [
    ("Mode:", reported_mode_var),
    ("TX State:", reported_tx_var),
    ("Health:", health_var),
    ("Alarm:", alarm_var),
    ("Raw Packet:", raw_packet_var)
]
for r, (label, var) in enumerate(report_items):
    ttk.Label(rep_frame, text=label).grid(row=r, column=0, sticky="w", padx=5, pady=5)
    ttk.Label(rep_frame, textvariable=var, wraplength=420).grid(row=r, column=1, sticky="w", padx=5, pady=5)

# Metric frame
metrics = ttk.LabelFrame(root, text="Test Metrics")
metrics.pack(fill="x", padx=10, pady=10)

metric_items = [
    ("Total Commands:", total_commands_var),
    ("Total Responses:", total_responses_var),
    ("Mode Changes:", mode_changes_var),
    ("TX Changes:", tx_changes_var),
    ("Matches:", matches_var),
    ("Mismatches:", mismatches_var),
]
for i, (label, var) in enumerate(metric_items):
    ttk.Label(metrics, text=label).grid(row=0, column=i*2, sticky="w", padx=5, pady=5)
    ttk.Label(metrics, textvariable=var).grid(row=0, column=i*2+1, sticky="w", padx=5, pady=5)

# Exit button
btn_frame = ttk.Frame(root)
btn_frame.pack(fill="x", padx=10, pady=5)
ttk.Button(btn_frame, text="Exit", command=on_close).pack(side="right", padx=5)

# Event log
log_frame = ttk.LabelFrame(root, text="Event Log")
log_frame.pack(fill="both", expand=True, padx=10, pady=10)

log_box = tk.Text(log_frame, height=14)
log_box.pack(fill="both", expand=True, padx=5, pady=5)

# Start logging and polling
ensure_csv_header()
add_log("Ground HMI started.")
poll_serial()

root.mainloop()