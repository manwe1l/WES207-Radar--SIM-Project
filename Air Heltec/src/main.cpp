#include <Arduino.h>
#include <RadioLib.h>
#include <SPI.h>

// Heltec V3 LoRa pins
#define LORA_NSS_PIN   8
#define LORA_SCK_PIN   9
#define LORA_MOSI_PIN  10
#define LORA_MISO_PIN  11
#define LORA_RST_PIN   12
#define LORA_BUSY_PIN  13
#define LORA_DIO1_PIN  14

// SPI and radio objects
SPIClass spi(FSPI);
SPISettings spiSettings(2000000, MSBFIRST, SPI_MODE0);
SX1262 radio = new Module(LORA_NSS_PIN, LORA_DIO1_PIN, LORA_RST_PIN, LORA_BUSY_PIN, spi, spiSettings);

// Radio settings
#define LORA_CH   17
#define LORA_FREQ (902.3 + 0.2 * LORA_CH)   // 905.7 MHz
#define LORA_BW   125.0
#define LORA_SF   7
#define LORA_CR   5

// Safety settings
const unsigned long MIN_TX_GAP_MS = 20000;   // 20 seconds
const int MAX_PACKET_LEN = 40;               // Keep packet short

unsigned long packetId = 0;
unsigned long lastTxTime = 0;
bool firstPacket = true;

// Stop if radio setup fails
void error_message(const char* message, int16_t state) {
  Serial.printf("ERROR: %s (code %d)\n", message, state);
  while (true) {
    delay(1000);
  }
}

// Set up radio
void initRadio() {
  spi.begin(LORA_SCK_PIN, LORA_MISO_PIN, LORA_MOSI_PIN, LORA_NSS_PIN);

  int state = radio.begin(LORA_FREQ, LORA_BW, LORA_SF, LORA_CR, 0x34, 0, 8);
  if (state != RADIOLIB_ERR_NONE) {
    error_message("Radio init failed", state);
  }

  state = radio.setCurrentLimit(140.0);
  if (state != RADIOLIB_ERR_NONE) {
    error_message("Current limit setup failed", state);
  }

  state = radio.setDio2AsRfSwitch(true);
  if (state != RADIOLIB_ERR_NONE) {
    error_message("DIO2 RF switch setup failed", state);
  }

  state = radio.explicitHeader();
  if (state != RADIOLIB_ERR_NONE) {
    error_message("Explicit header setup failed", state);
  }

  state = radio.setCRC(2);
  if (state != RADIOLIB_ERR_NONE) {
    error_message("CRC setup failed", state);
  }
}

// Build final packet
String buildPacket(const String& msg, bool isInitPacket) {
  packetId++;

  String type;
  if (isInitPacket) {
    type = "T=INIT";
  } else {
    type = "T=STAT";
  }

  return type + ",ID=" + String(packetId) + "," + msg;
}

// Check if enough time has passed
bool canTransmitNow() {
  unsigned long now = millis();
  return (now - lastTxTime) >= MIN_TX_GAP_MS;
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  initRadio();

  Serial.println("AIR_HELTEC_READY");
  Serial.println("20-second safety lock enabled");
  Serial.println("Waiting for air laptop commands...");
}

void loop() {
  if (Serial.available()) {
    String incoming = Serial.readStringUntil('\n');
    incoming.trim();

    if (incoming.length() == 0) {
      return;
    }

    bool isInitPacket = firstPacket;

    // Allow the first packet right away
    if (!isInitPacket && !canTransmitNow()) {
      Serial.println("TX blocked: 20-second limit not reached");
      return;
    }

    String packet = buildPacket(incoming, isInitPacket);

    // Check packet length
    if (packet.length() > MAX_PACKET_LEN) {
      Serial.println("TX blocked: packet too long");
      return;
    }

    Serial.print("UART RX: ");
    Serial.println(incoming);

    Serial.print("LoRa TX: ");
    Serial.println(packet);

    int state = radio.transmit(packet);

    if (state == RADIOLIB_ERR_NONE) {
      lastTxTime = millis();

      if (firstPacket) {
        firstPacket = false;
      }

      Serial.println("LoRa TX: Complete!");
    } else {
      Serial.printf("LoRa TX error: %d\n", state);
    }
  }
}