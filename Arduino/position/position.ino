6#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <EEPROM.h>

// Constants
#define BNO055_SAMPLERATE_DELAY_MS 10 // Sampling rate in milliseconds
#define PRINT_DELAY_MS 500 // How often to print the data

// Create an instance of the BNO055 sensor
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);

// Variables for position, velocity, acceleration, and orientation
double xPos = 0, yPos = 0, zPos = 0;
double xVel = 0, yVel = 0, zVel = 0;
double xAcc = 0, yAcc = 0, zAcc = 0;
double initOrientationX = 0, initOrientationY = 0, initOrientationZ = 0;

// Variables for calibration data
struct CalibrationData {
  adafruit_bno055_offsets_t offsets;
};

CalibrationData savedCalibration;

// Function prototypes
void loadCalibration();
void applyCalibration();
void printSensorData(sensors_event_t* orientationData, sensors_event_t* linearAccelData);

void setup() {
  Serial.begin(115200);

  if (!bno.begin()) {
    Serial.print("No BNO055 detected");
    while (1);
  }

  // Load calibration data from EEPROM
  loadCalibration();

  // Apply calibration data to sensor
  applyCalibration();

  // Initialize orientation to zero
  sensors_event_t orientationData;
  bno.getEvent(&orientationData, Adafruit_BNO055::VECTOR_EULER);

  initOrientationX = orientationData.orientation.x;
  initOrientationY = orientationData.orientation.y;
  initOrientationZ = orientationData.orientation.z;

  // Initialize position, velocity, and acceleration to zero
  xPos = 0;
  yPos = 0;
  zPos = 0;
  xVel = 0;
  yVel = 0;
  zVel = 0;
  xAcc = 0;
  yAcc = 0;
  zAcc = 0;

  Serial.println("Sensor initialized and calibrated.");
  delay(1000);
}

void loop() {
  unsigned long tStart = micros();

  sensors_event_t orientationData, linearAccelData;
  bno.getEvent(&orientationData, Adafruit_BNO055::VECTOR_EULER);
  bno.getEvent(&linearAccelData, Adafruit_BNO055::VECTOR_LINEARACCEL);

  // Get acceleration data
  xAcc = linearAccelData.acceleration.x;
  yAcc = linearAccelData.acceleration.y;
  zAcc = linearAccelData.acceleration.z;

  // Update velocity and position
  double dt = BNO055_SAMPLERATE_DELAY_MS / 1000.0; // Convert milliseconds to seconds
  xVel += xAcc * dt;
  yVel += yAcc * dt;
  zVel += zAcc * dt;

  xPos += xVel * dt + 0.5 * xAcc * dt * dt;
  yPos += yVel * dt + 0.5 * yAcc * dt * dt;
  zPos += zVel * dt + 0.5 * zAcc * dt * dt;

  // Calculate relative orientation based on initial orientation
  double relOrientationX = orientationData.orientation.x - initOrientationX;
  double relOrientationY = orientationData.orientation.y - initOrientationY;
  double relOrientationZ = orientationData.orientation.z - initOrientationZ;

  // Print the data at the defined interval
  static uint16_t printCount = 0;
  if (printCount * BNO055_SAMPLERATE_DELAY_MS >= PRINT_DELAY_MS) {
    printSensorData(&orientationData, &linearAccelData);

    printCount = 0;
  } else {
    printCount++;
  }

  // Wait until the next sample is ready
  while ((micros() - tStart) < (BNO055_SAMPLERATE_DELAY_MS * 1000)) {
    // Poll until the next sample is ready
  }
}

// Function to load calibration data from EEPROM
void loadCalibration() {
  EEPROM.get(0, savedCalibration.offsets);
  Serial.println("Calibration data loaded from EEPROM.");
}

// Function to apply calibration data to the sensor
void applyCalibration() {
  bno.setSensorOffsets(savedCalibration.offsets);
  Serial.println("Calibration data applied to the sensor.");
}

// Function to print sensor data
void printSensorData(sensors_event_t* orientationData, sensors_event_t* linearAccelData) {
  // Calculate relative orientation based on initial orientation
  double relOrientationX = orientationData->orientation.x - initOrientationX;
  double relOrientationY = orientationData->orientation.y - initOrientationY;
  double relOrientationZ = orientationData->orientation.z - initOrientationZ;

  Serial.print("Relative Orientation (Degrees): ");
  Serial.print("X: ");
  Serial.print(relOrientationX);
  Serial.print(" , Y: ");
  Serial.print(relOrientationY);
  Serial.print(" , Z: ");
  Serial.println(relOrientationZ);

  Serial.print("Position (Meters): ");
  Serial.print("X: ");
  Serial.print(xPos);
  Serial.print(" , Y: ");
  Serial.print(yPos);
  Serial.print(" , Z: ");
  Serial.println(zPos);

  Serial.print("Acceleration (m/s^2): ");
  Serial.print("X: ");
  Serial.print(xAcc);
  Serial.print(" , Y: ");
  Serial.print(yAcc);
  Serial.print(" , Z: ");
  Serial.println(zAcc);

  Serial.print("Velocity (m/s): ");
  Serial.print("X: ");
  Serial.print(xVel);
  Serial.print(" , Y: ");
  Serial.print(yVel);
  Serial.print(" , Z: ");
  Serial.println(zVel);

  Serial.println("-------");
}
