# Testing Plan

This file explains how the project will be tested.

The goal of testing is to check if commands are sent correctly, if the returned status matches, and how the link performs at different distances and during motion.

---

## 1. Main test goals

The project is tested to check:

- command sending
- returned status
- mode change success
- TX enable and disable
- signal strength
- signal quality
- latency
- motion performance
- distance performance

---

## 2. Bench test

The bench test is the first step.

### Bench test checks
- both HMIs start correctly
- commands can be sent from the ground side
- the air side receives the command
- the air side sends back updated status
- the ground side receives the returned status
- logs are saved on both laptops

### Bench test commands
- MTI
- SARVideo
- Maritime Large
- Maritime Small
- TX Enable
- TX Disable

---

## 3. Distance test

After the bench test works, the system is tested at longer distances.

### Suggested test distances
- 20 feet
- 50 feet
- 100 feet
- 150 feet

### Distance test checks
- command is sent
- returned status matches
- RSSI is recorded
- SNR is recorded
- latency is recorded
- success or failure is recorded

---

## 4. Driving test

After the bench test works, the system is tested during motion.

### Driving test method
- place the air side in the vehicle
- keep the ground side in a fixed location
- drive slowly
- send commands during motion
- check if returned status still matches
- save logs from both laptops

### Driving test speed
- about 10 to 15 mph

---

## 5. Data collected

The system collects:

- command ID
- commanded mode
- commanded TX state
- returned mode
- returned TX state
- health
- alarm
- RSSI
- SNR
- latency
- match or mismatch

---

## 6. Success check

A test is successful when:

- the ground side sends a command
- the air side receives the command
- the air side sends back the updated status
- the ground side receives the returned status
- the commanded and reported values match

---

## 7. Current results

Current results show:

- MVP is complete
- two-way communication is working
- bench testing worked
- range testing worked at 20 feet and 150 feet
- driving test worked at about 10 to 15 mph
- during motion, the system gave 100% matched responses up to about 40 to 50 yards
- beyond 50 yards, communication became unreliable during motion

---

## 8. Next testing work

The next testing work is:

- repeat bench tests
- repeat driving tests
- test more distances
- compare RSSI, SNR, and latency
- make graphs from the saved logs
- document results in the repo