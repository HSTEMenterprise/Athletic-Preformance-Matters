#include </home/Adithya/.arduino15/packages/esp32/hardware/esp32/3.1.1/libraries/BLE/src/BLEDevice.h>
#include </home/Adithya/.arduino15/packages/esp32/hardware/esp32/3.1.1/libraries/BLE/src/BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <BLE2901.h>

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

BLEServer *pServer = NULL;
BLECharacteristic *pCharacteristic = NULL;
BLECharacteristic *charx = NULL;
BLECharacteristic *chary = NULL;
BLECharacteristic *charz = NULL;

BLE2901 *descriptor_2901 = NULL;

bool deviceConnected = false;
bool oldDeviceConnected = false;
uint32_t value = 0;

#define SERVICE_UUID "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define C_UUID_1 "e2f5435e-634f-44d3-9c7f-54bfe8c96e64"
#define C_UUID_2 "0eb71bcb-eb31-4f19-88b9-116a4e52a2c4"
#define C_UUID_3 "801b2ee2-e7b6-4aa8-ae2d-4e82b426d157"

#define BNO055_SAMPLERATE_DELAY_MS (100)

Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);

class MyServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer *pServer) {
    deviceConnected = true;
  };

  void onDisconnect(BLEServer *pServer) {
    deviceConnected = false;
  }
};

void setup() {
  Serial.begin(115200);
  BLEDevice::init("ESP32");

  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  BLEService *pService = pServer->createService(SERVICE_UUID);

  charx = pService->createCharacteristic(C_UUID_1, BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);
  chary = pService->createCharacteristic(C_UUID_2, BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);
  charz = pService->createCharacteristic(C_UUID_3, BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);

  pCharacteristic = pService->createCharacteristic(CHARACTERISTIC_UUID, BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);

  pCharacteristic->addDescriptor(new BLE2902());
  charx->addDescriptor(new BLE2902());
  chary->addDescriptor(new BLE2902());
  charz->addDescriptor(new BLE2902());
  
  descriptor_2901 = new BLE2901();
  descriptor_2901->setDescription("My own description for this characteristic.");
  descriptor_2901->setAccessPermissions(ESP_GATT_PERM_READ);
  pCharacteristic->addDescriptor(descriptor_2901);

  pService->start();

  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(false);
  pAdvertising->setMinPreferred(0x0);
  BLEDevice::startAdvertising();
  Serial.println("Waiting a client connection to notify...");

  if (!bno.begin()) {
    Serial.println("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while (1);
  }

  delay(1000);
  bno.setExtCrystalUse(true);
}

void loop() {
  if (deviceConnected) {
    sensors_event_t event;
    bno.getEvent(&event);
    
    float x = event.orientation.x;
    float y = event.orientation.y;
    float z = event.orientation.z;

    pCharacteristic->setValue((uint8_t *)&value, sizeof(value));
    pCharacteristic->notify();

    charx->setValue((uint8_t *)&x, sizeof(x));
    charx->notify();
    chary->setValue((uint8_t *)&y, sizeof(y));
    chary->notify();
    charz->setValue((uint8_t *)&z, sizeof(z));
    charz->notify();
    
    value++;
    delay(BNO055_SAMPLERATE_DELAY_MS);
  }

  if (!deviceConnected && oldDeviceConnected) {
    delay(500);
    pServer->startAdvertising();
    Serial.println("start advertising");
    oldDeviceConnected = deviceConnected;
  }

  if (deviceConnected && !oldDeviceConnected) {
    oldDeviceConnected = deviceConnected;
  }
}
