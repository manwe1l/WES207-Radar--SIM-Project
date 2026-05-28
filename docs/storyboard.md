# Video Storyboard

## Video Title
Radar Telemetry Over LoRa

---

## Scene 1 — Project Introduction

### Visual
- Title slide
- Project name
- Your name

### Narration
This project is a two-way LoRa telemetry system for radar mode testing. The goal is to send commands from the ground side to the air side and then send the updated radar status back to the ground side.

### Main Point
Explain what the project is in simple terms.

---

## Scene 2 — Problem and Motivation

### Visual
- Simple text slide
- Maybe block diagram or system image

### Narration
This project came from a real work problem. The radar team does not always have easy access to the ground control station during testing. Because of that, this project builds another way to send commands and read radar status during testing.

### Main Point
Explain why the project matters.

---

## Scene 3 — System Overview

### Visual
- Interconnect diagram
- Ground laptop, ground Heltec, LoRa link, air Heltec, air laptop

### Narration
The ground laptop sends commands to the ground Heltec. The ground Heltec sends the command over LoRa. The air Heltec receives the command and forwards it to the air laptop. The air laptop updates the radar mode and sends the updated status back through the same path to the ground side.

### Main Point
Show how the system works.

---

## Scene 4 — Hardware and Software

### Visual
- Photo or screenshots of the setup
- List of main hardware and software

### Narration
The project uses two laptops, two Heltec WiFi LoRa 32 V3 boards, Python HMIs, and C++ firmware on the Heltecs. The HMIs display the data and save CSV logs during testing.

### Main Point
Show what was used to build the project.

---

## Scene 5 — Modes and Functions

### Visual
- Modes tested slide

### Narration
The system supports radar modes and functions including MTI, SARVideo, Maritime Large, Maritime Small, TX Enable, and TX Disable.

### Main Point
Show what commands the system can test.

---

## Scene 6 — HMI Demo

### Visual
- Ground HMI screenshot
- Air HMI screenshot

### Narration
The ground HMI sends commands and shows the returned radar status. The air HMI simulates the radar side, updates the radar state, and sends the updated status back. Both HMIs also save CSV log files.

### Main Point
Show the working software tools.

---

## Scene 7 — MVP and Progress

### Visual
- MVP status slide
- Short bullet list

### Narration
The MVP is complete. The ground laptop can send commands, the air laptop can receive them, and the updated radar status comes back correctly. Both sides display and log the results.

### Main Point
Clearly state that the MVP is complete.

---

## Scene 8 — Bench Test Results

### Visual
- CSV screenshot
- Test result summary
- Maybe one graph later

### Narration
Bench testing was completed first. The system worked at short distance and also worked at 150 feet during stationary testing. This showed that the main communication path was working before motion testing began.

### Main Point
Show technical progress and proof.

---

## Scene 9 — Driving Test Results

### Visual
- Driving test results slide
- Graph of success vs distance
- Summary bullets

### Narration
The driving test was done at about 10 to 15 miles per hour. The system gave 100 percent matched responses up to about 40 to 50 yards. Beyond 50 yards, communication became unreliable during motion. This happened in both driving runs.

### Main Point
Show the most important real test result.

---

## Scene 10 — What the Results Mean

### Visual
- Simple summary slide
- Maybe graph with short conclusion

### Narration
The results show that the system works well at short range and during low-speed motion. The drop in performance at longer range during motion is likely related to the test environment, antenna placement, and signal quality, not just the code.

### Main Point
Explain the meaning of the results.

---

## Scene 11 — Future Work

### Visual
- Future work slide
- 4-week plan or short bullet list

### Narration
The next steps are to repeat the driving test, collect more data, test more distances, make graphs from the saved logs, and finish the final report, GitHub updates, and presentation.

### Main Point
Show that there is still clear work left and that the plan is realistic.

---

## Scene 12 — Closing

### Visual
- Final summary slide

### Narration
This project built a working two-way LoRa radar telemetry link. The MVP is complete, the main system is working, and the next work is focused on repeated testing, results analysis, and final documentation.

### Main Point
End with a clear project summary.