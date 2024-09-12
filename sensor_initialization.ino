Initialization of sensor

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <EEPROM.h>

// Create an instance of the Adafruit_BNO055 class
Adafruit_BNO055 bno = Adafruit_BNO055(55);

void setup() {
  // Begin serial communication
  Serial.begin(115200);
  Serial.println("Orientation Sensor Test");
  Serial.println("");

  // Initialize the sensor
  if (!bno.begin()) {
    Serial.print("No BNO055 detected ... Check your wiring or I2C ADDR!");
    while (1);
  }

  // Optionally configure the sensor to use an external crystal for better accuracy
  bno.setExtCrystalUse(true);

  // Allow the sensor to stabilize
  delay(1000);

  // Load calibration data from EEPROM if available
  loadCalibration();

  // Check calibration status
  displayCalibrationStatus();
}

void loop() {
  // Read and display calibration status
  displayCalibrationStatus();

  // Read and display orientation data
  sensors_event_t event;
  bno.getEvent(&event);

  Serial.print("Orientation: ");
  Serial.print("Heading: ");
  Serial.print(event.orientation.x);
  Serial.print(" Roll: ");
  Serial.print(event.orientation.z);
  Serial.print(" Pitch: ");
  Serial.println(event.orientation.y);

  // Periodically save calibration data if fully calibrated
  uint8_t system, gyro, accel, mag;
  bno.getCalibration(&system, &gyro, &accel, &mag);
  if (system == 3 && gyro == 3 && accel == 3 && mag == 3) {
    saveCalibration();
  }

  delay(1000);
}

void saveCalibration() {
  adafruit_bno055_offsets_t calibrationData;
  bno.getSensorOffsets(calibrationData);

  EEPROM.put(0, calibrationData);
  EEPROM.commit(); // Ensure data is written to EEPROM
  Serial.println("Calibration data saved to EEPROM");
}

void loadCalibration() {
  adafruit_bno055_offsets_t calibrationData;
  EEPROM.get(0, calibrationData);

  bno.setSensorOffsets(calibrationData);
  Serial.println("Calibration data loaded from EEPROM");
}

void displayCalibrationStatus() {
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
}




