#include <Arduino.h>
#include <RadioLib.h>
#include <SPI.h>

// ===== Heltec V3 LoRa pins =====
#define LORA_NSS_PIN   8
#define LORA_SCK_PIN   9
#define LORA_MOSI_PIN  10
#define LORA_MISO_PIN  11
#define LORA_RST_PIN   12
#define LORA_BUSY_PIN  13
#define LORA_DIO1_PIN  14

// ===== SPI and radio objects =====
SPIClass spi(FSPI);
SPISettings spiSettings(2000000, MSBFIRST, SPI_MODE0);
SX1262 radio = new Module(LORA_NSS_PIN, LORA_DIO1_PIN, LORA_RST_PIN, LORA_BUSY_PIN, spi, spiSettings);

// ===== Radio settings =====
#define LORA_CH   17
#define LORA_FREQ (902.3 + 0.2 * LORA_CH)   // 905.7 MHz
#define LORA_BW   125.0
#define LORA_SF   7
#define LORA_CR   5

// Flag that tells us a packet arrived
volatile bool receivedFlag = false;

// Count received packets
unsigned long rxCount = 0;

// This runs when a packet arrives
#if defined(ESP8266) || defined(ESP32)
ICACHE_RAM_ATTR
#endif
void receiveISR(void) {
  receivedFlag = true;
}

// Print an error and stop
void error_message(const char* message, int16_t state) {
  Serial.printf("ERROR: %s (code %d)\n", message, state);
  while (true) {
    delay(1000);
  }
}

// Set up the radio
void initRadio() {
  spi.begin(LORA_SCK_PIN, LORA_MISO_PIN, LORA_MOSI_PIN, LORA_NSS_PIN);

  Serial.print("Initializing radio...");
  int16_t state = radio.begin(LORA_FREQ, LORA_BW, LORA_SF, LORA_CR, 0x34, 0, 8);
  if (state != RADIOLIB_ERR_NONE) {
    error_message("Radio initialization failed", state);
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

  Serial.println("Complete!");

  // Tell the radio which function to run when a packet arrives
  radio.setDio1Action(receiveISR);

  // Start listening all the time
  Serial.print("Starting continuous receive...");
  state = radio.startReceive();
  if (state != RADIOLIB_ERR_NONE) {
    error_message("Start receive failed", state);
  }
  Serial.println("Complete!");
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("GROUND_HELTEC_READY");
  initRadio();
}

void loop() {
  // Only run when a packet has arrived
  if (receivedFlag) {
    receivedFlag = false;
    rxCount++;

    String packet;
    int state = radio.readData(packet);

    if (state == RADIOLIB_ERR_NONE) {
      Serial.print("RX COUNT: ");
      Serial.println(rxCount);

      Serial.print("TIME MS: ");
      Serial.println(millis());

      Serial.print("DATA: ");
      Serial.println(packet);

      Serial.print("RSSI: ");
      Serial.print(radio.getRSSI());
      Serial.println(" dBm");

      Serial.println("--------------------");
    } else if (state == RADIOLIB_ERR_CRC_MISMATCH) {
      Serial.println("CRC error");
    } else {
      Serial.print("Receive failed, code ");
      Serial.println(state);
    }

    // Start listening again
    state = radio.startReceive();
    if (state != RADIOLIB_ERR_NONE) {
      error_message("Resume receive failed", state);
    }
  }
}