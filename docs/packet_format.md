# Packet Format

This file explains the packet format used in the project.

The system uses short text packets so they are easy to read and easy to debug.

---

## 1. Command Packet

The ground side sends a command packet to the air side.

Example:

    T=CMD,CID=3,TS=1714600000.15,MODE=SARV,TX=DIS

### Fields

- `T` = packet type
- `CMD` = command packet
- `CID` = command ID
- `TS` = timestamp
- `MODE` = radar mode
- `TX` = TX state

---

## 2. Status Packet

The air side sends a status packet back to the ground side.

Example:

    T=STAT,CID=3,MODE=SARV,TX=DIS,H=OK,A=0

### Fields

- `T` = packet type
- `STAT` = status packet
- `CID` = command ID
- `MODE` = radar mode
- `TX` = TX state
- `H` = health
- `A` = alarm

---

## 3. Signal Quality Fields

On the receive side, RSSI and SNR are added for logging.

Example:

    T=STAT,CID=3,MODE=SARV,TX=DIS,H=OK,A=0,RSSI=-82.00,SNR=11.25

### Extra fields

- `RSSI` = received signal strength
- `SNR` = signal-to-noise ratio

These values help explain why the link works or fails at different distances.

---

## 4. Mode Codes

The packets use short mode codes.

### Mode values
- `MTI` = MTI
- `SARV` = SARVideo
- `MLV` = Maritime Large
- `MSV` = Maritime Small

### TX values
- `EN` = Enabled
- `DIS` = Disabled

The GUI shows the full readable names.

---

## 5. Health and Alarm

### Health values
- `OK` = system health is normal
- other values can show a fault if needed

### Alarm values
- `0` = no alarm
- `1` = alarm active

---

## 6. Why this format was used

This format was chosen because it is:
- short
- easy to read
- easy to debug
- easy to log
- easy to parse in Python

It keeps the packets simple while still showing the important test data.