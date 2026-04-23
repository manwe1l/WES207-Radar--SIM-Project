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

unsigned long packetId = 0;
bool firstPacket = true;

// Print error and stop
void error_message(const char* message, int16_t state) {
  Serial.printf("ERROR: %s (code %d)\n", message, state);
  while (true) {
    delay(1000);
  }
}

// Set up the radio
void initRadio() {
  spi.begin(LORA_SCK_PIN, LORA_MISO_PIN, LORA_MOSI_PIN);

  int state = radio.begin(LORA_FREQ, LORA_BW, LORA_SF, LORA_CR);
  if (state != RADIOLIB_ERR_NONE) {
    error_message("Radio init failed", state);
  }
}

// Build the final packet
String buildPacket(const String& msg) {
  packetId++;

  String packetType;
  if (firstPacket) {
    packetType = "T=INIT";
    firstPacket = false;
  } else {
    packetType = "T=STAT";
  }

  return packetType + ",ID=" + String(packetId) + "," + msg;
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  initRadio();

  Serial.println("AIR_HELTEC_READY");
  Serial.println("Waiting for air laptop commands...");
}

void loop() {
  // Read one status line from the air laptop
  if (Serial.available()) {
    String incoming = Serial.readStringUntil('\n');
    incoming.trim();

    // Ignore empty lines
    if (incoming.length() == 0) {
      return;
    }

    // Build packet
    String packet = buildPacket(incoming);

    Serial.print("UART RX: ");
    Serial.println(incoming);

    Serial.print("LoRa TX: ");
    Serial.println(packet);

    // Send packet over LoRa
    int state = radio.transmit(packet);

    if (state == RADIOLIB_ERR_NONE) {
      Serial.println("LoRa TX: Complete!");
    } else {
      Serial.printf("LoRa TX error: %d\n", state);
    }
  }
}
