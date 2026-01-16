import cv2
import serial
import time

# --- CONFIG ---
URL = "http://192.168.137.196/stream" # Use the IP that worked in your test
PORT = 'COM10'
BAUD = 115200

class StationaryCamTurret:
    def __init__(self):
        # 1. Initialize Serial first
        print(f"Connecting to Serial {PORT}...")
        try:
            # We open the port and then WAIT. This allows the ESP32 to 
            # finish its "reboot" caused by the USB connection.
            self.ser = serial.Serial()
            self.ser.port = PORT
            self.ser.baudrate = BAUD
            self.ser.timeout = 0.1
            self.ser.setDTR(False) # Prevent Reset
            self.ser.setRTS(False) # Prevent Reset
            self.ser.open()
            print("✓ Serial Connected. Waiting 5 seconds for ESP32 to reboot and connect to WiFi...")
            time.sleep(5) 
        except Exception as e:
            print(f"⚠ Serial Warning: {e}")
            self.ser = None

        # 2. Open Video (Identical to your working test script)
        print(f"Opening stream from {URL}...")
        self.cap = cv2.VideoCapture(URL)
        
        if not self.cap.isOpened():
            print("✗ Stream Error: Still getting -138. Is the IP correct?")
            exit()
            
        print("✓ Stream Connected! Running Face Detection...")
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.last_send_time = 0

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to fetch frame.")
                break
            
            # AI Logic
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.2, 5)

            if len(faces) > 0:
                (x, y, fw, fh) = faces[0]
                fx, fy = x + fw//2, y + fh//2
                
                # Draw on frame
                cv2.rectangle(frame, (x, y), (x+fw, y+fh), (0, 255, 0), 2)
                
                # Map to degrees
                pan = int(90 - (fx - (frame.shape[1]//2)) * 0.2)
                tilt = int(80 + (fy - (frame.shape[0]//2)) * 0.2) # offset correction
                fire = 1 if (abs(fx - (frame.shape[1]//2)) < 30) else 0

                # Only send if we have a serial connection and it's been 100ms
                if self.ser and (time.time() - self.last_send_time) > 0.1:
                    cmd = f"X{pan}Y{tilt}Z{fire}\n"
                    self.ser.write(cmd.encode())
                    self.ser.flush()
                    self.last_send_time = time.time()
                    print(f"Targeting: {cmd.strip()}")

            cv2.imshow('Turret AI View', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        if self.ser: self.ser.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    StationaryCamTurret().run()