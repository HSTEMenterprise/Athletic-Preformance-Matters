#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

#define BNO055_SAMPLERATE_DELAY_MS (100)

Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);
float referenceOffsets[3] = {0, 0, 0};
float zeroedOffsets[3] = {0, 0, 0};

void displaySensorDetails(void) {
  sensor_t sensor;
  bno.getSensor(&sensor);
  Serial.println("------------------------------------");
  Serial.print("Sensor:       "); Serial.println(sensor.name);
  Serial.print("Driver Ver:   "); Serial.println(sensor.version);
  Serial.print("Unique ID:    "); Serial.println(sensor.sensor_id);
  Serial.print("Max Value:    "); Serial.print(sensor.max_value); Serial.println(" xxx");
  Serial.print("Min Value:    "); Serial.print(sensor.min_value); Serial.println(" xxx");
  Serial.print("Resolution:   "); Serial.print(sensor.resolution); Serial.println(" xxx");
  Serial.println("------------------------------------");
  Serial.println("");
  delay(500);
}

void calibrateAxis(const char* position, float offsets[3]) {
  Serial.print("Hold your ");
  Serial.print(position);
  Serial.println(" steady for 10 seconds.");

  for (int i = 10; i > 0; i--) {
    Serial.print("Hold for ");
    Serial.print(i);
    Serial.println(" seconds...");
    delay(1000);
  }

  Serial.println("Calibrating sensors...");
  sensors_event_t event;
  bno.getEvent(&event);

  offsets[0] = event.orientation.x;
  offsets[1] = event.orientation.y;
  offsets[2] = event.orientation.z;

  Serial.print(position);
  Serial.println(" calibration complete.");
  Serial.print("X: "); Serial.println(offsets[0]);
  Serial.print("Y: "); Serial.println(offsets[1]);
  Serial.print("Z: "); Serial.println(offsets[2]);
}

void setup(void) {
  Serial.begin(115200);
  Serial.println("Orientation Sensor Test");

  if (!bno.begin()) {
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while (1);
  }

  delay(1000);
  bno.setExtCrystalUse(true);
  displaySensorDetails();

  Serial.println("Do you want to calibrate/zero the sensor? (y/n)");
  while (!Serial.available());
  char response = Serial.read();
  if (response == 'y' || response == 'Y') {
    float zOffsets[3] = {0, 0, 0};
    float xOffsets[3] = {0, 0, 0};
    float yOffsets[3] = {0, 0, 0};

    // Calibrate each axis
    calibrateAxis("arm at side (Z axis)", zOffsets);
    calibrateAxis("arm out at side (X axis)", xOffsets);
    calibrateAxis("arm in front (Y axis)", yOffsets);

    // Create the final reference offsets
    referenceOffsets[0] = xOffsets[0]; // X-axis
    referenceOffsets[1] = yOffsets[1]; // Y-axis
    referenceOffsets[2] = zOffsets[2]; // Z-axis

    Serial.println("Final reference axis offsets:");
    Serial.print("X: "); Serial.println(referenceOffsets[0]);
    Serial.print("Y: "); Serial.println(referenceOffsets[1]);
    Serial.print("Z: "); Serial.println(referenceOffsets[2]);

    // Zero the offsets (treat the reference as zero point)
    zeroedOffsets[0] = referenceOffsets[0];
    zeroedOffsets[1] = referenceOffsets[1];
    zeroedOffsets[2] = referenceOffsets[2];

    Serial.println("Offsets zeroed. Calibration complete.");
  }

  Serial.println("Press 'S' to start recording or 'E' to end.");
}

void recordData() {
  Serial.println("Recording will start in 3 seconds...");
  delay(3000);

  while (true) {
    if (Serial.available()) {
      char command = Serial.read();
      if (command == 'E' || command == 'e') {
        Serial.println("Recording stopped.");
        break;
      }
    }

    sensors_event_t event;
    bno.getEvent(&event);

    // Calculate the relative orientation as differences from zeroed offsets
    float x = event.orientation.x - zeroedOffsets[0];
    float y = event.orientation.y - zeroedOffsets[1];
    float z = event.orientation.z - zeroedOffsets[2];

    Serial.print("Orientation (relative to zeroed reference): ");
    Serial.print("X: "); Serial.print(x); Serial.print(", ");
    Serial.print("Y: "); Serial.print(y); Serial.print(", ");
    Serial.print("Z: "); Serial.println(z);

    delay(BNO055_SAMPLERATE_DELAY_MS);
  }
}

void loop(void) {
  if (Serial.available()) {
    char command = Serial.read();
    if (command == 'S' || command == 's') {
      recordData();
    }
  }
}
