/*
    Video: https://www.youtube.com/watch?v=oCMOYS71NIU
    Based on Neil Kolban example for IDF: https://github.com/nkolban/esp32-snippets/blob/master/cpp_utils/tests/BLE%20Tests/SampleNotify.cpp
    Ported to Arduino ESP32 by Evandro Copercini
    updated by chegewara

   Create a BLE server that, once we receive a connection, will send periodic notifications.
   The service advertises itself as: 4fafc201-1fb5-459e-8fcc-c5c9c331914b
   And has a characteristic of: beb5483e-36e1-4688-b7f5-ea07361b26a8

   The design of creating the BLE server is:
   1. Create a BLE Server
   2. Create a BLE Service
   3. Create a BLE Characteristic on the Service
   4. Create a BLE Descriptor on the characteristic
   5. Start the service.
   6. Start advertising.

   A connect handler associated with the server starts a background task that performs notification
   every couple of seconds.
*/
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

// See the following for generating UUIDs:
// https://www.uuidgenerator.net/

#define SERVICE_UUID "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define C_UUID_1 "e2f5435e-634f-44d3-9c7f-54bfe8c96e64"
#define C_UUID_2 "0eb71bcb-eb31-4f19-88b9-116a4e52a2c4"
#define C_UUID_3 "801b2ee2-e7b6-4aa8-ae2d-4e82b426d157"

#define BNO055_SAMPLERATE_DELAY_MS (100)


Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);

void displaySensorDetails(void) {
   sensor_t sensor;
  bno.getSensor(&sensor);
  Serial.println("------------------------------------");
  Serial.print("Sensor:       "); Serial.println(sensor.name);
  Serial.print("Driver Ver:   "); Serial.println(sensor.version);
  Serial.print("Unique ID:    "); Serial.println(sensor.sensor_id);
  Serial.print("Max Value:    "); Serial.print(sensor.max_value); Serial.println(" xxx");
  Serial.print("Min Value:    "); Serial.print(" "); Serial.print(sensor.min_value); Serial.println(" xxx");
  Serial.print("Resolution:   "); Serial.print(sensor.resolution); Serial.println(" xxx");
  Serial.println("------------------------------------");
  Serial.println("");
  delay(500);
}


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

  // Create the BLE Device
  BLEDevice::init("ESP32");

  // Create the BLE Server
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  // Create the BLE Service
  BLEService *pService = pServer->createService(SERVICE_UUID);

  charx = pService->createCharacteristic(
    C_UUID_1,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_INDICATE);

  chary = pService->createCharacteristic(
    C_UUID_2,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_INDICATE);

  charz = pService->createCharacteristic(
    C_UUID_3,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_INDICATE);

  // Create a BLE Characteristic
  pCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_INDICATE);

  // Creates BLE Descriptor 0x2902: Client Characteristic Configuration Descriptor (CCCD)
  pCharacteristic->addDescriptor(new BLE2902());
  charx->addDescriptor(new BLE2902());
  chary->addDescriptor(new BLE2902());
  charz->addDescriptor(new BLE2902());
  
  // Adds also the Characteristic User Description - 0x2901 descriptor
  descriptor_2901 = new BLE2901();
  descriptor_2901->setDescription("My own description for this characteristic.");
  descriptor_2901->setAccessPermissions(ESP_GATT_PERM_READ);  // enforce read only - default is Read|Write
  pCharacteristic->addDescriptor(descriptor_2901);

  // Start the service
  pService->start();

  // Start advertising
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(false);
  pAdvertising->setMinPreferred(0x0);  // set value to 0x00 to not advertise this parameter
  BLEDevice::startAdvertising();
  Serial.println("Waiting a client connection to notify...");

  // Initialize the BNO055 sensor
  if (!bno.begin()) {
    Serial.println("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while (1);
  }

  delay(1000);

  // Use external crystal for better accuracy
  bno.setExtCrystalUse(true);
  displaySensorDetails();

}

void loop() {
  // notify changed value
  if (deviceConnected) {
    sensors_event_t event;
    bno.getEvent(&event);
    pCharacteristic->setValue((uint8_t *)&value, 4);
    pCharacteristic->notify();
    charx->setValue((uint8_t *)(int)event.orientation.x, 4);
    charx->notify();
    chary->setValue((uint8_t *)(int)event.orientation.y, 4);
    chary->notify();
    charz->setValue((uint8_t *)(int)event.orientation.z, 4);
    charz->notify();
    value++;

    delay(BNO055_SAMPLERATE_DELAY_MS);

  }
  // disconnecting
  if (!deviceConnected && oldDeviceConnected) {
    delay(500);                   // give the bluetooth stack the chance to get things ready
    pServer->startAdvertising();  // restart advertising
    Serial.println("start advertising");
    oldDeviceConnected = deviceConnected;
  }

  // connecting
  if (deviceConnected && !oldDeviceConnected) {
    // do stuff here on connecting
    oldDeviceConnected = deviceConnected;
  }
}