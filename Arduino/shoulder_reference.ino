#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <EEPROM.h>

// Create the sensor object
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);

// Structure to hold the reference orientation
struct ReferenceOrientation {
  float x;
  float y;
  float z;
};

// Structure to hold the reference linear acceleration
struct ReferenceAcceleration {
  float x;
  float y;
  float z;
};

// Reference orientation and acceleration
ReferenceOrientation refOrient;
ReferenceAcceleration refAccel;

// Flag to indicate if the reference point is set
bool refPointSet = false;

void setup() {
  Serial.begin(115200);
  Serial.println("Orientation and Acceleration Sensor Reference Point Setup");
  Serial.println("");

  // Initialize the sensor
  if (!bno.begin()) {
    // There was a problem detecting the BNO055 ... check your connections
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while (1);
  }

  delay(1000);

  // Use external crystal for better accuracy
  bno.setExtCrystalUse(true);

  // Load calibration data from EEPROM
  adafruit_bno055_offsets_t calibrationData;
  EEPROM.get(0, calibrationData);
  bno.setSensorOffsets(calibrationData);

  // Indicate that the reference point has not been set yet
  refPointSet = false;
}

void loop() {
  // Check if the reference point has been set
  if (!refPointSet) {
    Serial.println("Move the sensor to the shoulder position and press the 'r' key to set the reference point.");
    if (Serial.available() > 0) {
      char c = Serial.read();
      if (c == 'r') {
        // Capture the initial orientation as the reference point
        sensors_event_t orientationEvent;
        bno.getEvent(&orientationEvent);

        refOrient.x = orientationEvent.orientation.x;
        refOrient.y = orientationEvent.orientation.y;
        refOrient.z = orientationEvent.orientation.z;

        // Capture the initial linear acceleration as the reference point
        imu::Vector<3> accel = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);

        refAccel.x = accel.x();
        refAccel.y = accel.y();
        refAccel.z = accel.z();

        Serial.println("Reference Point Set:");
        Serial.print("Orientation - X: "); Serial.print(refOrient.x);
        Serial.print(" Y: "); Serial.print(refOrient.y);
        Serial.print(" Z: "); Serial.println(refOrient.z);

        Serial.print("Acceleration - X: "); Serial.print(refAccel.x);
        Serial.print(" Y: "); Serial.print(refAccel.y);
        Serial.print(" Z: "); Serial.println(refAccel.z);

        refPointSet = true;
      }
    }
  } else {
    // Get a new sensor event
    sensors_event_t orientationEvent;
    bno.getEvent(&orientationEvent);

    // Get the linear acceleration
    imu::Vector<3> accel = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);

    // Get the gyroscope data
    imu::Vector<3> gyro = bno.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);

    // Compute the relative orientation
    float relOrientX = orientationEvent.orientation.x - refOrient.x;
    float relOrientY = orientationEvent.orientation.y - refOrient.y;
    float relOrientZ = orientationEvent.orientation.z - refOrient.z;

    // Compute the relative acceleration
    float relAccelX = accel.x() - refAccel.x;
    float relAccelY = accel.y() - refAccel.y;
    float relAccelZ = accel.z() - refAccel.z;

    // Display relative orientation data
    Serial.print("Relative Orientation: ");
    Serial.print("X: "); Serial.print(relOrientX);
    Serial.print(" Y: "); Serial.print(relOrientY);
    Serial.print(" Z: "); Serial.println(relOrientZ);

    // Display relative acceleration data
    Serial.print("Relative Acceleration: ");
    Serial.print("X: "); Serial.print(relAccelX);
    Serial.print(" Y: "); Serial.print(relAccelY);
    Serial.print(" Z: "); Serial.println(relAccelZ);

    // Display gyroscope data
    Serial.print("Gyroscope: ");
    Serial.print("X: "); Serial.print(gyro.x());
    Serial.print(" Y: "); Serial.print(gyro.y());
    Serial.print(" Z: "); Serial.println(gyro.z());

    delay(1000);
  }
}




