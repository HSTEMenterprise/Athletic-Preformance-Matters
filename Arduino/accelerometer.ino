#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

// Create an instance of the BNO055 sensor
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);

void setup() {
  // Initialize Serial Monitor
  Serial.begin(115200);
  Serial.println("BNO055 Accelerometer Test");

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
  // Get a new accelerometer event
  sensors_event_t event;
  bno.getEvent(&event, Adafruit_BNO055::VECTOR_ACCELEROMETER);

  // Print accelerometer values (in m/s^2)
  Serial.print("Accelerometer (m/s^2): ");
  Serial.print("X: ");
  Serial.print(event.acceleration.x, 2);
  Serial.print(" | Y: ");
  Serial.print(event.acceleration.y, 2);
  Serial.print(" | Z: ");
  Serial.println(event.acceleration.z, 2);

  // Add a delay to control sampling rate
  delay(100);
}
