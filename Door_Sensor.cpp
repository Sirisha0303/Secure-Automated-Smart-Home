#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu(0x68);

const float doorOpenThreshold = 2.20; // Adjust this value as needed
const float degreeThreshold = 6000;
const float MPU6050_ACCEL_SENSITIVITY = 16384.0; // LSB/g

void setup() {
  Serial.begin(1200);
  Wire.begin();
  mpu.initialize();
}

void loop() {
  int16_t ax, ay, az, gx, gy, gz;
  mpu.getRotation(&gx, &gy, &gz);
  mpu.getAcceleration(&ax, &ay, &az);
  float Ax = ax / MPU6050_ACCEL_SENSITIVITY;
  float Ay = ay / MPU6050_ACCEL_SENSITIVITY;
  float Az = az / MPU6050_ACCEL_SENSITIVITY;

  // Calculate the magnitude of acceleration
  float acceleration = sqrt(Ax * Ax + Ay * Ay + Az * Az);
  float degree = sqrt(gx * gx + gy * gy + gz * gz);

  // Calculate the magnitude of acceleration
  //float magnitude = sqrt(ax*ax + ay*ay + az*az);

  if(Ax > 0)
  {
    Serial.println("Door is OPEN");
    // Add code here to trigger actions or notifications
  }

  else if(Ax < 0)
  {
    Serial.println("Door is CLOSED");
    // Add code here if needed
  }

  //Serial.print(acceleration);
  //Serial.println(Ax);
  delay(1000); // Adjust the delay based on your requirements
}
