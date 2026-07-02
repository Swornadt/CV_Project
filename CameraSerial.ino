#include <ESP32Servo.h>

Servo panServo; Servo tiltServo;
const int panPin = 12; 
const int tiltPin = 14;

void setup() {
  // Use a slightly longer delay at the very start 
  // to let the USB-Serial chip stabilize
  delay(1000); 
  Serial.begin(115200);
  
  // Initialize servos...
  panServo.attach(12);
  tiltServo.attach(14);
  
  // DO NOT print anything in a loop here. Just one message.
  delay(2000);
  while(Serial.available() > 0) { Serial.read(); }
  Serial.println("SYSTEM_READY");
}

void loop() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    static String inputString = "";

    if (c == '\n') { // End of command reached
      inputString.trim();
      
      int xIdx = inputString.indexOf('X');
      int yIdx = inputString.indexOf('Y');

      if (xIdx != -1 && yIdx != -1) {
        int xVal = inputString.substring(xIdx + 1, yIdx).toInt();
        int yVal = inputString.substring(yIdx + 1).toInt();

        panServo.write(constrain(xVal, 0, 180));
        tiltServo.write(constrain(yVal, 0, 180));

        // Send a detailed ACK back
        Serial.print("ACK_RECEIVED:X"); Serial.print(xVal); 
        Serial.print("Y"); Serial.println(yVal);
      }
      inputString = ""; // Clear for next command
    } else {
      inputString += c; // Keep building the string
    }
  }
}