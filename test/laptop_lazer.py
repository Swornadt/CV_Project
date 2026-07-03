import serial
import cv2
import numpy as np
import time

# --- CONFIGURATION (Upgraded to Crisp Native Resolution) ---
PORT = 'COM3'
BAUD = 115200 
CAM_W, CAM_H = 640, 480
CENTER_X, CENTER_Y = 320, 240

class LaptopTurret:
    def __init__(self):
        print(f"Connecting to {PORT}...")
        self.ser = serial.Serial()
        self.ser.port = PORT
        self.ser.baudrate = BAUD
        self.ser.timeout = 0.1
        self.ser.dtr = False  
        self.ser.rts = False  
        self.ser.open()
        
        print("Waiting for ESP32 to initialize...")
        time.sleep(2)
        self.ser.reset_input_buffer() 
        
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Initialize camera and force hardware native 640x480 resolution
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_W)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)
        
        self.last_send_time = 0

    def run(self):
        print("System Active! HD Tracking starting now... Press 'q' to quit.")
        while True:
            ret, frame = self.cap.read()
            if not ret: 
                break
            
            # No more shrinking! We use the high-quality frame directly
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # minNeighbors=5 and minSize filters out small background false-positives
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))

            if len(faces) > 0:
                (x, y, w, h) = faces[0]
                fx, fy = x + w//2, y + h//2
                
                # --- ADJUSTED TRACKING LOGIC ---
                # Because the pixel canvas is larger, we scale down the multiplier 
                # to 0.12 so the motor movements stay smooth and don't over-correct violently.
                pan = int(110 - ((fx - CENTER_X) * 0.12))
                tilt = int(90 + ((fy - CENTER_Y) * 0.12)) 
                
                pan = max(0, min(180, pan))
                tilt = max(0, min(180, tilt))

                # Lock-on zone adjusted up to a 40x40 pixel bounding box for the higher resolution
                fire = 0
                if abs(fx - CENTER_X) < 40 and abs(fy - CENTER_Y) < 40:
                    fire = 1
                    cv2.putText(frame, "LOCKED", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                if (time.time() - self.last_send_time) > 0.06:
                    command = f"X{pan}Y{tilt}Z{fire}\n"
                    self.ser.write(command.encode('utf-8'))
                    self.ser.flush()  
                    self.last_send_time = time.time()
                    print(f"Sent: {command.strip()}")

                # Draw targeting indicator around face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Draw a clean reticle crosshair in the middle of the screen
            cv2.drawMarker(frame, (CENTER_X, CENTER_Y), (255, 0, 0), cv2.MARKER_CROSS, 20, 2)
            
            # Display the unmanipulated clean stream directly
            cv2.imshow("Turret View", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'): 
                break

        self.cap.release()
        self.ser.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    LaptopTurret().run()