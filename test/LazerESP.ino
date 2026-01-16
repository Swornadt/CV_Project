#include <ESP32Servo.h>
#include <Wire.h> 
#include <LiquidCrystal_I2C.h>

// --- LCD CONFIG ---
// Address 0x27 is standard. SDA=2, SCL=4
LiquidCrystal_I2C lcd(0x27, 16, 2); 

Servo panServo; Servo tiltServo;
const int panPin = 12; 
const int tiltPin = 13;
const int laserPin = 14; 

bool lastLockedState = false;

void updateLCD(bool locked) {
  lcd.setCursor(0,0);
  if (locked) {
    lcd.print("> TARGET LOCKED <");
    lcd.setCursor(0, 1);
    lcd.print("LASER: ENGAGED  ");
  } else {
    lcd.setCursor(0, 0);
    lcd.print("SYSTEM: ACTIVE  ");
    lcd.setCursor(0, 1);
    lcd.print("MODE: SCANNING  ");
  }
}

void setup() {
  Serial.begin(115200);

  // 1. Initialize LCD
  delay(500);
  Wire.begin(15, 16); // SDA=15, SCL=16

  lcd.init();
  delay(100);
  lcd.backlight();
  lcd.clear(); // Initial State

  updateLCD(false);
  
  // 2. Hardware Pins
  pinMode(laserPin, OUTPUT);
  digitalWrite(laserPin, LOW); 

  // 3. Servo Setup
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
      int zIdx = inputString.indexOf('Z'); 

      if (xIdx != -1 && yIdx != -1) {
        int xVal = inputString.substring(xIdx + 1, yIdx).toInt();
        int yVal = inputString.substring(yIdx + 1, zIdx != -1 ? zIdx : inputString.length()).toInt();
        panServo.write(constrain(xVal, 0, 180));
        tiltServo.write(constrain(yVal, 0, 180));
      }

      if (zIdx != -1) {
        int zVal = inputString.substring(zIdx + 1).toInt();
        bool isLocked = (zVal == 1);
        digitalWrite(laserPin, isLocked ? HIGH : LOW);

        // Update LCD only on change to prevent flicker
        if (isLocked != lastLockedState) {
          updateLCD(isLocked);
          lastLockedState = isLocked;
        }
      }
      
      inputString = ""; 
    } else {
      inputString += c;
    }
  }
}