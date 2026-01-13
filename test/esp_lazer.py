import cv2, urllib.request, numpy as np, serial, time

# --- CONFIG ---
URL = "http://192.168.4.1/stream" # Check Serial Monitor for this!
PORT = 'COM10'
BAUD = 115200

class StationaryCamTurret:
    def __init__(self):
        print(f"Connecting to {PORT}...")
        # Fix: changed dtr=False to dsrdtr=False
        self.ser = serial.Serial(PORT, BAUD, timeout=0.1, dsrdtr=False) 
        
        # Give the ESP32 a moment to wake up after Serial connection
        time.sleep(2) 
        
        print(f"Opening Video Stream from {URL}...")
        self.stream = urllib.request.urlopen(URL)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.bytes = b''
        self.last_send_time = 0

    def run(self):
        while True:
            # MJPEG stream decoding
            self.bytes += self.stream.read(4096)
            a = self.bytes.find(b'\xff\xd8')
            b = self.bytes.find(b'\xff\xd9')
            
            if a != -1 and b != -1:
                jpg = self.bytes[a:b+2]
                self.bytes = self.bytes[b+2:]
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                if frame is not None:
                    h, w = frame.shape[:2]
                    cx, cy = w // 2, h // 2  # This will correctly find 80, 60
                    
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)

                    if len(faces) > 0:
                        (x, y, fw, fh) = faces[0]
                        fx, fy = x + fw//2, y + fh//2
                        
                        # Absolute calculation (Center is 90)
                        # We use a 0.3 multiplier to prevent "overshooting"
                        pan = int(90 - (fx - cx) * 0.3) 
                        tilt = int(90 + (fy - cy) * 0.3) 

                        fire = 1 if (abs(fx-cx) < 20 and abs(fy-cy) < 20) else 0
                        
                        if (time.time() - self.last_send_time) > 0.1:
                            cmd = f"X{pan}Y{tilt}Z{fire}\n"
                            self.ser.write(cmd.encode())
                            self.last_send_time = time.time()
                            print(f"Sent: {cmd.strip()}")

                        cv2.rectangle(frame, (x, y), (x+fw, y+fh), (0, 255, 0), 2)
                        if fire: cv2.putText(frame, "LOCKED", (10, 30), 1, 2, (0,0,255), 2)

                    cv2.imshow('Stationary ESP-CAM Tracking', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'): break

if __name__ == "__main__":
    StationaryCamTurret().run()