#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

// Create an instance of the BNO055 sensor
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);

void setup() {
  // Initialize Serial Monitor
  Serial.begin(115200);
  Serial.println("BNO055 Gyroscope Test");

  // Initialize the BNO055 sensor
  if (!bno.begin()) {
    Serial.println("Error: BNO055 not detected. Check wiring!");
    while (1);
  }

  // Use external crystal for better accuracy
  bno.setExtCrystalUse(true);

  // Delay to allow sensor to initialize
  delay(1000);
}

void loop() {
  // Get a new gyroscope event
  sensors_event_t event;
  bno.getEvent(&event, Adafruit_BNO055::VECTOR_GYROSCOPE);

  // Print gyroscope values (in rad/s)
  Serial.print("Gyroscope (rad/s): ");
  Serial.print("X: ");
  Serial.print(event.gyro.x, 2);
  Serial.print(" | Y: ");
  Serial.print(event.gyro.y, 2);
  Serial.print(" | Z: ");
  Serial.println(event.gyro.z, 2);

  // Add a delay to control sampling rate
  delay(100);
}
