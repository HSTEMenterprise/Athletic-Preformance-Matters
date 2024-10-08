#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <EEPROM.h> // Include EEPROM library to save calibration data

Adafruit_BNO055 bno = Adafruit_BNO055(55);

void setup() {
  Serial.begin(115200);
  if (!bno.begin()) {
    Serial.print("No BNO055 detected ... Check your wiring or I2C ADDR!");
    while (1);
  }
  delay(1000);

  // Load calibration data from EEPROM
  loadCalibration();

  // Allow the sensor to initialize and calibrate
  delay(1000);

  Serial.println("BNO055 Calibration and Initialization");

  // Attach the sensor to your shoulder and move it in different orientations
  Serial.println("Move the sensor slowly in all directions to calibrate...");
}

void loop() {
  uint8_t system, gyro, accel, mag;
  bno.getCalibration(&system, &gyro, &accel, &mag);
  Serial.print("Calibration status - System: ");
  Serial.print(system);
  Serial.print(" Gyro: ");
  Serial.print(gyro);
  Serial.print(" Accel: ");
  Serial.print(accel);
  Serial.print(" Mag: ");
  Serial.println(mag);

  // If fully calibrated, save the calibration data
  if (system == 3 && gyro == 3 && accel == 3 && mag == 3) {
    saveCalibration();
    setReferencePoint();
    while (1); // Stop further execution since calibration is done
  }

  delay(1000);
}

// Function to save calibration data to EEPROM
void saveCalibration() {
  adafruit_bno055_offsets_t calibrationData;
  bno.getSensorOffsets(calibrationData);

  EEPROM.put(0, calibrationData);
  EEPROM.commit(); // Make sure to commit changes to EEPROM
  Serial.println("Calibration data saved to EEPROM");
}

// Function to load calibration data from EEPROM
void loadCalibration() {
  adafruit_bno055_offsets_t calibrationData;
  EEPROM.get(0, calibrationData);

  bno.setSensorOffsets(calibrationData);
  Serial.println("Calibration data loaded from EEPROM");
}

// Function to set the reference point
void setReferencePoint() {
  sensors_event_t event;
  bno.getEvent(&event);
  Serial.println("Reference Point Set:");
  Serial.print("Orientation - X: ");
  Serial.print(event.orientation.x);
  Serial.print(" Y: ");
  Serial.print(event.orientation.y);
  Serial.print(" Z: ");
  Serial.println(event.orientation.z);

  Serial.print("Acceleration - X: ");
  Serial.print(event.acceleration.x);
  Serial.print(" Y: ");
  Serial.print(event.acceleration.y);
  Serial.print(" Z: ");
  Serial.println(event.acceleration.z);
}

