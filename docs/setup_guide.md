# Setup Guide

This guide explains how to set up and run the project.

---

## 1. What you need

You need:

- 1 air laptop
- 1 ground laptop
- 1 air Heltec WiFi LoRa 32 V3
- 1 ground Heltec WiFi LoRa 32 V3
- USB cables
- VS Code
- PlatformIO
- Python

---

## 2. Project folders

The main folders used for setup are:

- `air_heltec`
- `ground_heltec`
- `python`

The Python folder contains:
- `air_hmi.py`
- `ground_hmi.py`

---

## 3. Upload the air Heltec code

Open the `air_heltec` folder in VS Code with PlatformIO.

Then:

1. Connect the air Heltec to the air laptop
2. Build the project
3. Upload the code to the air Heltec

This loads the air-side LoRa firmware.

The air Heltec will:
- receive command packets over LoRa
- send commands to the air laptop
- receive updated status from the air laptop
- send updated status back over LoRa

---

## 4. Upload the ground Heltec code

Open the `ground_heltec` folder in VS Code with PlatformIO.

Then:

1. Connect the ground Heltec to the ground laptop
2. Build the project
3. Upload the code to the ground Heltec

This loads the ground-side LoRa firmware.

The ground Heltec will:
- receive commands from the ground laptop
- send commands over LoRa
- receive returned status from the air side
- send returned status to the ground laptop

---

## 5. Check the COM ports

Each Python file must use the correct COM port.

### Air laptop
Open:
- `python/air_hmi.py`

Find this line:

    PORT = "COM7"

Change it if needed so it matches the air Heltec COM port.

### Ground laptop
Open:
- `python/ground_hmi.py`

Find this line:

    PORT = "COM4"

Change it if needed so it matches the ground Heltec COM port.

You can find the COM port in:
- Device Manager on Windows
- or the PlatformIO device list

---

## 6. Make sure Python is installed

Both laptops need Python installed.

You may also need these Python modules:
- `pyserial`
- `tkinter`

If needed, install pyserial with:

    pip install pyserial

Tkinter is usually included with Python on Windows.

---

## 7. Start the ground side first

On the ground laptop:

1. Open a terminal in the `python` folder
2. Run:

    python ground_hmi.py

The ground HMI should open.

The ground HMI will:
- send commands
- receive returned status
- show RSSI, SNR, latency, and match result
- save CSV logs

---

## 8. Start the air side second

On the air laptop:

1. Open a terminal in the `python` folder
2. Run:

    python air_hmi.py

The air HMI should open.

The air HMI will:
- start with a random radar mode
- start with a random TX state
- receive commands from the ground side
- update the radar state
- send updated status back
- save CSV logs

---

## 9. Check that both HMIs are running

When both programs are open:

### Ground HMI
You should see:
- command buttons
- returned radar state
- RSSI
- SNR
- event log

### Air HMI
You should see:
- current radar state
- TX state
- command RSSI
- command SNR
- event log

---

## 10. Test the system

Use the ground HMI buttons to send commands such as:

- MTI
- SARVideo
- Maritime Large
- Maritime Small
- TX Enable
- TX Disable

After sending a command:

1. The ground laptop sends the command
2. The ground Heltec sends it over LoRa
3. The air Heltec receives it
4. The air laptop updates its state
5. The air side sends the updated status back
6. The ground side receives and logs the result

---

## 11. Check that the command worked

A good test should show:

### On the ground HMI
- the command was sent
- the returned mode matches
- the returned TX state matches
- the match field shows `YES`
- RSSI and SNR are shown

### On the air HMI
- the command was received
- the radar state changed
- the updated status was sent back

---

## 12. Check the logs

CSV logs are saved automatically.

### Air logs
Saved in:
- `logs/air_logs`

These logs include:
- commands received
- returned status sent
- RSSI and SNR for received commands

### Ground logs
Saved in:
- `logs/ground_logs`

These logs include:
- commands sent
- returned status received
- RSSI
- SNR
- latency
- match result

---

## 13. Bench test

Start with a simple bench test.

Suggested steps:
1. Place both systems close together
2. Send each radar mode
3. Send TX enable and disable
4. Confirm both HMIs update correctly
5. Confirm logs are saved

---

## 14. Distance test

After the bench test works:

1. Increase the distance between the air side and ground side
2. Repeat the same commands
3. Save the results
4. Record when the link becomes weak or fails

Suggested test distances:
- 20 feet
- 50 feet
- 100 feet
- 150 feet

---

## 15. Driving test

After the bench test works:

1. Place the air side in the vehicle
2. Keep the ground side in a fixed location
3. Drive slowly
4. Send commands during motion
5. Check whether the returned status still matches
6. Save the logs

Suggested speed:
- about 10 to 15 mph

---

## 16. How to stop the program

Both HMIs have an **Exit** button.

You can also close the window.

This will:
- stop the program
- close the serial port
- stop logging

---

## 17. Common problems

### Problem: HMI does not connect
Check:
- correct COM port
- Heltec is plugged in
- no other program is using the same port

### Problem: No packets are returned
Check:
- both Heltecs have the correct code
- both HMIs are running
- air side was started after the ground side
- both boards use the same LoRa settings

### Problem: No log file appears
Check:
- the `logs` folder exists
- the script has permission to create files
- the program actually started and ran long enough to log data

### Problem: Commands do not match returned status
Check:
- packet format was not changed
- the correct Python files are being used
- older code is not being run by mistake

---

## 18. Final check

Before testing, make sure:

- air Heltec code is uploaded
- ground Heltec code is uploaded
- correct COM ports are set
- ground HMI starts first
- air HMI starts second
- both HMIs show live updates
- logs are being saved

If all of these are true, the system is ready for testing.