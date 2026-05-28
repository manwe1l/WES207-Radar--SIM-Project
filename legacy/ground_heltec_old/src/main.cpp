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

SPIClass spi(FSPI);
SPISettings spiSettings(2000000, MSBFIRST, SPI_MODE0);
SX1262 radio = new Module(
  LORA_NSS_PIN, LORA_DIO1_PIN, LORA_RST_PIN, LORA_BUSY_PIN, spi, spiSettings
);

#define LORA_CH   17
#define LORA_FREQ (902.3 + 0.2 * LORA_CH)
#define LORA_BW   125.0
#define LORA_SF   7
#define LORA_CR   5

volatile bool receivedFlag = false;

#if defined(ESP8266) || defined(ESP32)
ICACHE_RAM_ATTR
#endif
void receiveISR(void) {
  receivedFlag = true;
}

void error_message(const char* message, int16_t state) {
  Serial.printf("DBG: ERROR %s (code %d)\n", message, state);
  while (true) {
    delay(1000);
  }
}

void initRadio() {
  spi.begin(LORA_SCK_PIN, LORA_MISO_PIN, LORA_MOSI_PIN, LORA_NSS_PIN);

  int state = radio.begin(LORA_FREQ, LORA_BW, LORA_SF, LORA_CR, 0x34, 0, 8);
  if (state != RADIOLIB_ERR_NONE) error_message("Radio init failed", state);

  state = radio.setCurrentLimit(140.0);
  if (state != RADIOLIB_ERR_NONE) error_message("Current limit failed", state);

  state = radio.setDio2AsRfSwitch(true);
  if (state != RADIOLIB_ERR_NONE) error_message("RF switch failed", state);

  state = radio.explicitHeader();
  if (state != RADIOLIB_ERR_NONE) error_message("Header failed", state);

  state = radio.setCRC(2);
  if (state != RADIOLIB_ERR_NONE) error_message("CRC failed", state);

  radio.setDio1Action(receiveISR);

  state = radio.startReceive();
  if (state != RADIOLIB_ERR_NONE) error_message("Start receive failed", state);
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  initRadio();
  Serial.println("DBG: GROUND_HELTEC_READY");
}

void loop() {
  // Receive status from LoRa and forward to ground laptop
  if (receivedFlag) {
    receivedFlag = false;

    String packet;
    int state = radio.readData(packet);

    if (state == RADIOLIB_ERR_NONE) {
      if (packet.startsWith("T=STAT")) {
        Serial.println(packet);
      }
    }

    state = radio.startReceive();
    if (state != RADIOLIB_ERR_NONE) error_message("Resume receive failed", state);
  }

  // Receive commands from ground laptop and send over LoRa
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();

    if (line.length() == 0) return;

    if (line.startsWith("T=CMD")) {
      int state = radio.transmit(line);
      if (state != RADIOLIB_ERR_NONE) {
        Serial.printf("DBG: TX error %d\n", state);
      }

      state = radio.startReceive();
      if (state != RADIOLIB_ERR_NONE) error_message("Resume after TX failed", state);
    }
  }
}