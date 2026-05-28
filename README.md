# Radar Telemetry Over LoRa

## Project Overview

This project is a two-way LoRa telemetry system for radar mode testing.

The ground laptop sends radar commands to the air side. The air side updates the simulated radar state and sends the updated status back to the ground side. Both sides display the data and save logs.

The goal of this project is to help verify radar mode changes and help tell whether a problem is in the radar or in the ground control station network.

---

## Project Goal

Build a working wireless command and status link that is simple, low cost, and easy to test.

The system should:
- send commands from the ground side to the air side
- return updated radar status from the air side
- display live data on both laptops
- save test logs for later review

---

## Final System Operation

The final system works like this:

1. The ground laptop sends a command
2. The ground Heltec sends the command over LoRa
3. The air Heltec receives the command
4. The air Heltec forwards the command to the air laptop
5. The air laptop updates the radar mode and TX state
6. The air laptop sends the updated status back
7. The air Heltec sends the status over LoRa
8. The ground Heltec receives the status
9. The ground Heltec forwards the status to the ground laptop
10. The ground laptop displays and logs the result

---

## Modes Tested

- MTI
- SARVideo
- Maritime Large
- Maritime Small
- TX Enable
- TX Disable

---

## Folder Overview

### `air_heltec`
Final PlatformIO project for the air Heltec

### `ground_heltec`
Final PlatformIO project for the ground Heltec

### `python`
Final Python HMI files:
- `air_hmi.py`
- `ground_hmi.py`

### `docs`
Extra project information such as:
- setup steps
- packet format
- testing plan
- screenshots
- graphs
- storyboard

### `logs`
Saved CSV log files from testing

### `legacy`
Older code and test files that are not part of the final version

---

## Main Results

- MVP is complete
- Two-way communication is working
- Ground-to-air command sending works
- Air-to-ground status return works
- Both HMIs display live data
- Both HMIs save CSV logs
- Bench testing worked
- Range testing worked at 20 feet and 150 feet
- Driving test worked at about 10 to 15 mph
- During motion, the system gave 100% matched responses up to about 40 to 50 yards
- Beyond 50 yards, communication became unreliable during motion

---

## How to Run

1. Upload the firmware in `air_heltec` to the air Heltec
2. Upload the firmware in `ground_heltec` to the ground Heltec
3. Set the correct COM ports in the Python files
4. Run `ground_hmi.py`
5. Run `air_hmi.py`
6. Test commands and review the logs

More setup details are in the `docs` folder.

---

## Current Status

The main coding work is complete.

The main work left is:
- repeated testing
- more data collection
- more graphs
- documentation
- final video and presentation work

---

## More Information

See the `docs` folder for:
- setup guide
- packet format
- testing plan
- screenshots
- graphs
- storyboard

