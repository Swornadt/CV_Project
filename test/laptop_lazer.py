import serial, cv2, numpy as np, time

# --- CONFIGURATION ---
PORT = 'COM10'
BAUD = 115200 
CAM_W, CAM_H = 160, 120
CENTER_X, CENTER_Y = 80, 60

class LaptopTurret:
    def __init__(self):
        print(f"Connecting to {PORT}...")
        # Open port, but explicitly disable hardware flow control
        self.ser = serial.Serial()
        self.ser.port = PORT
        self.ser.baudrate = BAUD
        self.ser.timeout = 0.1
        self.ser.dtr = False  # Ensure DTR is LOW (not resetting)
        self.ser.rts = False  # Ensure RTS is LOW
        self.ser.open()
        
        # IMPORTANT: Wait for the ESP32 to finish its natural boot
        print("Waiting 5 seconds for ESP32 to finish boot sequence...")
        time.sleep(5)
        self.ser.reset_input_buffer() 
        
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.cap = cv2.VideoCapture(0)
        self.last_send_time = 0

    def run(self):
        print("System Active! Tracking starting now...")
        while True:
            ret, frame = self.cap.read()
            if not ret: break
            
            frame_small = cv2.resize(frame, (CAM_W, CAM_H))
            gray = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)

            if len(faces) > 0:
                (x, y, w, h) = faces[0]
                fx, fy = x + w//2, y + h//2
                
                pan = int(90 - ((fx - CENTER_X) * 0.3))
                tilt = int(80 + ((fy - CENTER_Y) * 0.3)) #offset correction
                pan = max(0, min(180, pan))
                tilt = max(0, min(180, tilt))

                # Check if centered (within a 10-pixel box)
                fire = 0
                if abs(fx - CENTER_X) < 20 and abs(fy - CENTER_Y) < 20:
                    fire = 1
                    cv2.putText(frame_small, "LOCKED", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                if (time.time() - self.last_send_time) > 0.15:
                    # New command format including Z
                    command = f"X{pan}Y{tilt}Z{fire}\n"
                    self.ser.write(command.encode('utf-8'))
                    self.last_send_time = time.time()
                    print(f"Sent: {command.strip()}")
                cv2.rectangle(frame_small, (x, y), (x+w, y+h), (0, 255, 0), 2)

            cv2.imshow("Turret View", cv2.resize(frame_small, (640, 480)))
            if cv2.waitKey(1) & 0xFF == ord('q'): break

        self.cap.release()
        self.ser.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    LaptopTurret().run()