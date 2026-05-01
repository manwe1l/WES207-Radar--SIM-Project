import serial
import time
import csv
import os
import tkinter as tk
from tkinter import ttk

PORT = "COM4"      # Ground Heltec COM port
BAUD = 115200
LOG_FILE = "test_results.csv"

ser = serial.Serial(PORT, BAUD, timeout=0.1)
time.sleep(2)

command_id = 0
commanded_mode = "MTI"
commanded_tx = "EN"
last_packet_time = None

# Metrics
total_commands = 0
total_responses = 0
mode_change_count = 0
tx_change_count = 0
match_count = 0
mismatch_count = 0

pending_commands = {}   # CID -> send time

file_exists = os.path.isfile(LOG_FILE)


def parse_packet(packet):
    """Turn packet text into a dictionary."""
    fields = {}
    for part in packet.split(","):
        if "=" in part:
            key, value = part.split("=", 1)
            fields[key.strip()] = value.strip()
    return fields


def mode_label(code):
    names = {
        "MTI": "MTI",
        "SARV": "SARVideo",
        "MLV": "Maritime Large",
        "MSV": "Maritime Small"
    }
    return names.get(code, code)


def log_result(row):
    """Write one row to CSV."""
    with open(LOG_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists and file.tell() == 0:
            writer.writerow([
                "timestamp", "cid", "commanded_mode", "commanded_tx",
                "reported_mode", "reported_tx", "health", "alarm",
                "latency_sec", "match", "raw_packet"
            ])
        writer.writerow(row)


def add_log(text):
    log_box.insert(tk.END, text + "\n")
    log_box.see(tk.END)


def update_metrics_labels():
    total_commands_var.set(str(total_commands))
    total_responses_var.set(str(total_responses))
    mode_changes_var.set(str(mode_change_count))
    tx_changes_var.set(str(tx_change_count))
    matches_var.set(str(match_count))
    mismatches_var.set(str(mismatch_count))


def send_command():
    global command_id, total_commands

    command_id += 1
    total_commands += 1

    ts = time.time()
    packet = f"T=CMD,CID={command_id},TS={ts},MODE={commanded_mode},TX={commanded_tx}\n"
    ser.write(packet.encode())

    pending_commands[str(command_id)] = {
        "send_time": ts,
        "mode": commanded_mode,
        "tx": commanded_tx
    }

    commanded_mode_var.set(mode_label(commanded_mode))
    commanded_tx_var.set(commanded_tx)
    command_packet_var.set(packet.strip())
    add_log(f"TX CMD: {packet.strip()}")
    update_metrics_labels()


def set_mode(mode_code):
    global commanded_mode, mode_change_count
    if commanded_mode != mode_code:
        commanded_mode = mode_code
        mode_change_count += 1
    send_command()


def set_tx(tx_state):
    global commanded_tx, tx_change_count
    if commanded_tx != tx_state:
        commanded_tx = tx_state
        tx_change_count += 1
    send_command()


def resend_command():
    send_command()


def update_result():
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
    global last_packet_time, total_responses, match_count, mismatch_count

    while ser.in_waiting:
        line = ser.readline().decode(errors="ignore").strip()

        if not line:
            continue

        if line.startswith("T=STAT"):
            last_packet_time = time.time()
            total_responses += 1

            fields = parse_packet(line)
            cid = fields.get("CID", "")

            rep_mode = fields.get("MODE", "")
            rep_tx = fields.get("TX", "")
            rep_health = fields.get("H", "")
            rep_alarm = fields.get("A", "")

            packet_type_var.set(fields.get("T", ""))
            packet_id_var.set(cid)
            reported_mode_var.set(mode_label(rep_mode))
            reported_tx_var.set(rep_tx)
            health_var.set("OK" if rep_health == "OK" else "FAULT")
            alarm_var.set(rep_alarm)
            last_update_var.set(time.strftime("%Y-%m-%d %H:%M:%S"))
            raw_packet_var.set(line)

            latency = ""
            match_value = "NO"

            if cid in pending_commands:
                sent = pending_commands[cid]
                latency = round(time.time() - sent["send_time"], 2)

                if sent["mode"] == rep_mode and sent["tx"] == rep_tx and rep_health == "OK" and rep_alarm == "0":
                    match_value = "YES"
                    match_count += 1
                else:
                    match_value = "NO"
                    mismatch_count += 1

            add_log(f"RX STAT: {line} | latency={latency}s | match={match_value}")

            log_result([
                time.strftime("%Y-%m-%d %H:%M:%S"),
                cid,
                pending_commands.get(cid, {}).get("mode", ""),
                pending_commands.get(cid, {}).get("tx", ""),
                rep_mode,
                rep_tx,
                rep_health,
                rep_alarm,
                latency,
                match_value,
                line
            ])

            update_result()
            update_metrics_labels()

    if last_packet_time is None:
        link_var.set("NO DATA")
    else:
        age = time.time() - last_packet_time
        link_var.set("OK" if age <= 60 else "STALE")

    root.after(100, poll_serial)


# Build window
root = tk.Tk()
root.title("Radar Telemetry HMI")
root.geometry("1200x760")

# Status vars
link_var = tk.StringVar(value="NO DATA")
last_update_var = tk.StringVar(value="")
packet_id_var = tk.StringVar(value="")
packet_type_var = tk.StringVar(value="")
result_var = tk.StringVar(value="")

# Metrics vars
total_commands_var = tk.StringVar(value="0")
total_responses_var = tk.StringVar(value="0")
mode_changes_var = tk.StringVar(value="0")
tx_changes_var = tk.StringVar(value="0")
matches_var = tk.StringVar(value="0")
mismatches_var = tk.StringVar(value="0")

# Commanded state vars
commanded_mode_var = tk.StringVar(value=mode_label(commanded_mode))
commanded_tx_var = tk.StringVar(value=commanded_tx)
command_packet_var = tk.StringVar(value="")

# Reported state vars
reported_mode_var = tk.StringVar(value="")
reported_tx_var = tk.StringVar(value="")
health_var = tk.StringVar(value="")
alarm_var = tk.StringVar(value="")
raw_packet_var = tk.StringVar(value="")

# Top status
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

# Middle
middle = ttk.Frame(root)
middle.pack(fill="x", padx=10, pady=10)

cmd_frame = ttk.LabelFrame(middle, text="Commanded State")
cmd_frame.pack(side="left", fill="both", expand=True, padx=5)

ttk.Label(cmd_frame, text="Mode:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
ttk.Label(cmd_frame, textvariable=commanded_mode_var).grid(row=0, column=1, sticky="w", padx=5, pady=5)
ttk.Label(cmd_frame, text="TX:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
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

rep_frame = ttk.LabelFrame(middle, text="Reported Radar State")
rep_frame.pack(side="left", fill="both", expand=True, padx=5)

report_items = [
    ("Mode:", reported_mode_var),
    ("TX:", reported_tx_var),
    ("Health:", health_var),
    ("Alarm:", alarm_var),
    ("Raw Packet:", raw_packet_var)
]
for r, (label, var) in enumerate(report_items):
    ttk.Label(rep_frame, text=label).grid(row=r, column=0, sticky="w", padx=5, pady=5)
    ttk.Label(rep_frame, textvariable=var, wraplength=420).grid(row=r, column=1, sticky="w", padx=5, pady=5)

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

log_frame = ttk.LabelFrame(root, text="Event Log")
log_frame.pack(fill="both", expand=True, padx=10, pady=10)

log_box = tk.Text(log_frame, height=14)
log_box.pack(fill="both", expand=True, padx=5, pady=5)

poll_serial()

try:
    root.mainloop()
finally:
    ser.close()