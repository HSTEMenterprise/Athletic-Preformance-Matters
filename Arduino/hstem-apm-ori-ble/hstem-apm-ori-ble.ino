/*Author: Oliver 
Date: 11/16/25
Last Updated: 11/16/25
Purpose: Getting the ESP32 to read data from the BN0O5 senor and transmit it via bluetooth to the UI
*/

#include <Adafruit_BNO055.h>
#include <NimBLEDevice.h>

Adafruit_BNO055 bno = Adafruit_BNO055(55);

/* 
   I (Oliver) generated these, so they're guaranteed to be unique.
   If you change these to new values, make sure to change them on 
   the python side as well.
*/
#define SERVICE_UUID        "f06a5de9-5c7e-4b20-aef9-c120fb6711e4"
#define CHARACTERISTIC_UUID "f2181a7e-86de-4c6f-8d0d-1df47cadcd30"

NimBLEServer* server = nullptr;
NimBLECharacteristic* characteristic = nullptr;
bool device_connected = false;

class ServerCallbacks : public NimBLEServerCallbacks {
  void onConnect(NimBLEServer* server, NimBLEConnInfo& connInfo) override {
    device_connected = true;
  }
  void onDisconnect(NimBLEServer* server, NimBLEConnInfo& connInfo, int reason) override {
    device_connected = false;
    ESP.restart();
  }
};

void setup() {
  Serial.begin(9600);  // Potentially set to 115200.
  Serial.println("INFO: Initializing.");

  /* Initialize BNO055. */
  if (!bno.begin()) {
    Serial.println("ERROR: BNO055 sensor not detected. Halting.");
    while (1);
  }
  bno.setExtCrystalUse(true);

  /* Initialize BLE system. */
  NimBLEDevice::init("ESP32_Ori_Sensor");
  server = NimBLEDevice::createServer();
  server->setCallbacks(new ServerCallbacks());

  NimBLEService* service = server->createService(SERVICE_UUID);

  characteristic = service->createCharacteristic(
    CHARACTERISTIC_UUID,
    NIMBLE_PROPERTY::READ | 
    NIMBLE_PROPERTY::NOTIFY
  );

  characteristic->setValue("waiting");
  service->start();

  /* Start advertising. */
  NimBLEAdvertising* advertising = NimBLEDevice::getAdvertising();
  advertising->addServiceUUID(SERVICE_UUID);
  advertising->setName("ESP32_Ori_Sensor");
  advertising->start();
  Serial.println("INFO: BLE advertising started.");
}

void loop() {
  sensors_event_t event;
  bno.getEvent(&event);

  char buffer[64];
  snprintf(buffer, sizeof(buffer), "%.2f %.2f %.2f", 
           event.orientation.x, event.orientation.y, event.orientation.z);

  // Serial.println(buffer);

  if (device_connected) {
    characteristic->setValue(buffer);
    characteristic->notify();
  }

  delay(200);
}
