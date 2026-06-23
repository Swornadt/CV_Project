import cv2
import serial
import time
import os

# --- CONFIG ---
URL = "http://192.168.137.122/stream" 
PORT = 'COM3'
BAUD = 115200
SAVE_DIR = "detected_faces"
SAVE_COOLDOWN = 3.0  # Minimum seconds to wait before saving another picture

class StationaryCamTurret:
    def __init__(self):
        # Create storage folder if it doesn't exist
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)
            print(f"✓ Created storage directory: {SAVE_DIR}")

        # 1. Initialize Serial first
        print(f"Connecting to Serial {PORT}...")
        try:
            self.ser = serial.Serial()
            self.ser.port = PORT
            self.ser.baudrate = BAUD
            self.ser.timeout = 0.1
            self.ser.setDTR(False) 
            self.ser.setRTS(False) 
            self.ser.open()
            print("✓ Serial Connected. Waiting 5 seconds for ESP32 to reboot and connect to WiFi...")
            time.sleep(5) 
        except Exception as e:
            print(f"⚠ Serial Warning: {e}")
            self.ser = None

        # 2. Open Video
        print(f"Opening stream from {URL}...")
        self.cap = cv2.VideoCapture(URL)
        
        if not self.cap.isOpened():
            print("✗ Stream Error: Still getting -138. Is the IP correct?")
            exit()
            
        print("✓ Stream Connected! Running Face Detection...")
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.last_send_time = 0
        self.last_save_time = 0  # Track when we last saved a face

    def run(self):
        pan = 110
        tilt = 120
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to fetch frame.")
                break
            
            frame = cv2.flip(frame, -1)
            
            # Keep a completely clean copy of the frame for saving 
            # before drawing tracking boxes on it
            clean_snapshot = frame.copy()
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.2, 5)
            fire = 0

            if len(faces) > 0:
                (x, y, fw, fh) = faces[0]
                fx, fy = x + fw//2, y + fh//2
                
                # --- RATE-LIMITED FACE SAVING LOGIC ---
                current_time = time.time()
                if (current_time - self.last_save_time) > SAVE_COOLDOWN:
                    # Create a unique timestamped filename
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    
                    # Option A: Save just the cropped face box
                    # We add a small boundary padding so the crop isn't too tight
                    pad = 20
                    h, w, _ = frame.shape
                    y1, y2 = max(0, y - pad), min(h, y + fh + pad)
                    x1, x2 = max(0, x - pad), min(w, x + fw + pad)
                    cropped_face = clean_snapshot[y1:y2, x1:x2]
                    
                    filename = os.path.join(SAVE_DIR, f"face_{timestamp}.jpg")
                    cv2.imwrite(filename, cropped_face)
                    
                    # Option B: (If you prefer saving the full picture, uncomment below instead)
                    # filename = os.path.join(SAVE_DIR, f"full_{timestamp}.jpg")
                    # cv2.imwrite(filename, clean_snapshot)
                    
                    print(f"💾 Target logged and saved: {filename}")
                    self.last_save_time = current_time

                # Map to degrees
                PAN_CENTER = 90 
                TILT_CENTER = 55 
                SENSITIVITY = 0.1  

                dx = fx - (frame.shape[1] // 2) 
                dy = fy - (frame.shape[0] // 2) 

                pan = int(PAN_CENTER + (dx * SENSITIVITY))
                tilt = int(TILT_CENTER + (dy * SENSITIVITY))

                fire = 1
                box_color = (0, 0, 255) # Red
                cv2.rectangle(frame, (x, y), (x+fw, y+fh), box_color, 2)
            else: 
                fire = 0 

            # Only send if we have a serial connection and it's been 100ms
            if self.ser and (time.time() - self.last_send_time) > 0.1:
                pan = max(0, min(180, pan))
                tilt = max(0, min(180, tilt))
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