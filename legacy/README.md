# WES207-Radar--SIM-Project
# Radar Telemetry Over LoRa

## Project Overview
This project builds a simple LoRa telemetry system that sends simulated radar status data from an air node to a ground node. 
The project idea came from work, where the radar team has limited access to the ground control station during integration events and flight testing. 
This project creates another way to gather status data while testing is taking place.
The air laptop acts as the radar simulator and sends mode commands to the air Heltec through USB serial. 
The air Heltec reads those commands, builds telemetry packets, and sends them over LoRa. 
The ground Heltec receives those packets and forwards them to the ground laptop, where the data can be displayed and logged.

## Project Goal
The goal of this project is to build a working end-to-end telemetry link that is simple, low cost, and realistic for an eight-week project.

## Hardware Used
- 1 air laptop
- 1 ground laptop
- 1 air Heltec WiFi LoRa 32 V3
- 1 ground Heltec WiFi LoRa 32 V3
- USB cables

## Software Used
- PlatformIO
- VS Code
- Python
- GitHub
- RadioLib

## System Interconnect Diagram

```text
Air Laptop
   |
   | USB Serial
   v
Air Heltec  ---- LoRa ---->  Ground Heltec
                                   |
                                   | USB Serial
                                   v
                             Ground Laptop
