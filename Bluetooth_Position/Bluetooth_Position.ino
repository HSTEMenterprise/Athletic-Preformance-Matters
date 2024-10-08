#include "BluetoothSerial.h"
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

/* Set the delay between fresh samples */
#define BNO055_SAMPLERATE_DELAY_MS (100)
#define USE_PIN // Uncomment this to use PIN during pairing. The pin is specified on the line below
const char *pin = "1234"; // Change this to more secure PIN.

String device_name = "ESP32-BT-Sensor";

BluetoothSerial SerialBT;
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` and enable it
#endif

#if !defined(CONFIG_BT_SPP_ENABLED)
#error Serial Bluetooth not available or not enabled. It is only available for the ESP32 chip.
#endif

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

void setup() {
  Serial.begin(115200);
  SerialBT.begin(device_name); // Start Bluetooth device
  Serial.printf("The device with name \"%s\" is started.\nNow you can pair it with Bluetooth!\n", device_name.c_str());

  #ifdef USE_PIN
    SerialBT.setPin(pin);
    Serial.println("Using PIN");
  #endif

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
  sensors_event_t event;
  bno.getEvent(&event);

  // Print sensor data over Serial and Bluetooth
  String sensorData = "";
  sensorData += String((float)event.orientation.x) + "\t";
  sensorData += String((float)event.orientation.y) + "\t";
  sensorData += String((float)event.orientation.z) + "\n";

  Serial.print(sensorData);      // Print sensor data to Serial Monitor
  SerialBT.print(sensorData);    // Send sensor data over Bluetooth

  // Bluetooth communication from Serial Monitor
  if (Serial.available()) {
    SerialBT.write(Serial.read());
  }
  if (SerialBT.available()) {
    Serial.write(SerialBT.read());
  }

  delay(BNO055_SAMPLERATE_DELAY_MS);
}
