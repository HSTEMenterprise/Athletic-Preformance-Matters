#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>

// Create an instance of the BNO055 sensor
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);

void setup() {
  Serial.begin(115200);
  if (!bno.begin()) {
    Serial.println("No BNO055 detected. Check your wiring or I2C address.");
    while (1);
  }

  // Calibrate the sensor and wait for a while for sensor stabilization
  delay(1000); // Delay for sensor initialization
  Serial.println("Magnetometer data is being read...");
}

void loop() {
  sensors_event_t magData;
  
  // Get magnetometer data
  bno.getEvent(&magData, Adafruit_BNO055::VECTOR_MAGNETOMETER);

  // Print magnetometer data in microTesla (uT)
  Serial.print("Magnetic Field (uT): ");
  Serial.print("X: "); 
  Serial.print(magData.magnetic.x);
  Serial.print(" , Y: "); 
  Serial.print(magData.magnetic.y);
  Serial.print(" , Z: "); 
  Serial.println(magData.magnetic.z);

  // Delay between readings
  delay(500); // Adjust the delay as necessary
}
