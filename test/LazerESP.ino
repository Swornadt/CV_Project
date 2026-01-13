#include <ESP32Servo.h>

Servo panServo; Servo tiltServo;
const int panPin = 12; 
const int tiltPin = 14;
const int laserPin = 13; // Connect laser (+) or transistor base here

void setup() {
  delay(1000); 
  Serial.begin(115200);
  
  pinMode(laserPin, OUTPUT);
  digitalWrite(laserPin, LOW); // Start with laser OFF

  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  panServo.attach(panPin);
  tiltServo.attach(tiltPin);
  
  panServo.write(90);
  tiltServo.write(90);
  
  delay(2000);
  while(Serial.available() > 0) { Serial.read(); }
  Serial.println("SYSTEM_READY");
}

void loop() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    static String inputString = "";

    if (c == '\n') {
      inputString.trim();
      
      int xIdx = inputString.indexOf('X');
      int yIdx = inputString.indexOf('Y');
      int zIdx = inputString.indexOf('Z'); // Laser command

      // Handle Pan/Tilt
      if (xIdx != -1 && yIdx != -1) {
        int xVal = inputString.substring(xIdx + 1, yIdx).toInt();
        int yVal = inputString.substring(yIdx + 1, zIdx != -1 ? zIdx : inputString.length()).toInt();
        panServo.write(constrain(xVal, 0, 180));
        tiltServo.write(constrain(yVal, 0, 180));
      }

      // Handle Laser
      if (zIdx != -1) {
        int zVal = inputString.substring(zIdx + 1).toInt();
        digitalWrite(laserPin, zVal == 1 ? HIGH : LOW);
      }
      
      inputString = ""; 
    } else {
      inputString += c;
    }
  }
}