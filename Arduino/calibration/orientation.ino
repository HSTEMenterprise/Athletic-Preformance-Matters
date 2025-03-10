#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

// Create an instance of the BNO055 sensor
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);

void setup() {
  // Initialize Serial Monitor
  Serial.begin(115200);
  Serial.println("BNO055 Orientation Data");

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
  // Get the orientation event (heading, pitch, roll)
  sensors_event_t event;
  bno.getEvent(&event, Adafruit_BNO055::VECTOR_EULER);

  // Extract and print heading, pitch, and roll
  float heading = event.orientation.x; // Heading (0 to 360 degrees)
  float pitch = event.orientation.y;   // Pitch (-90 to +90 degrees)
  float roll = event.orientation.z;    // Roll (-180 to +180 degrees)

  Serial.print("Heading: ");
  Serial.print(heading, 2);
  Serial.print("°, Pitch: ");
  Serial.print(pitch, 2);
  Serial.print("°, Roll: ");
  Serial.print(roll, 2);
  Serial.println("°");

  // Add a delay to control sampling rate
  delay(100);
}
