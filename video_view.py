import serial
import cv2
import numpy as np

# --- CONFIG ---
PORT = 'COM10'
BAUD = 460800 
CAM_W, CAM_H = 160, 120 
CENTER_X, CENTER_Y = CAM_W // 2, CAM_H // 2

# Field of View (FOV) of the ESP32-CAM is usually about 53 degrees
# We use this to map pixels to physical angles
FOV_H = 53 
FOV_V = 40 

class SerialStreamer:
    def __init__(self, port, baud):
        self.ser = serial.Serial(port, baud, timeout=0.1, rtscts=False, dsrdtr=False)
        self.ser.dtr = False
        self.ser.rts = False
        self.buffer = b""

    def get_frame(self):
        #print("testing")
        if self.ser.in_waiting > 0:
            print("ser in waiting")
            self.buffer += self.ser.read(self.ser.in_waiting)
        
        # Look for the latest frame to keep latency low
        start = self.buffer.rfind(b'\xff\xd8')
        end = self.buffer.rfind(b'\xff\xd9')
        
        if start != -1 and end != -1 and end > start:
            jpg = self.buffer[start:end+2]
            self.buffer = b"" # Clear buffer after finding latest frame
            nparr = np.frombuffer(jpg, np.uint8)
            return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return None

class TargetProcessor:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def calculate_angles(self, fx, fy):
        """
        Converts pixel coordinates to servo angles.
        Assumes 90 degrees is the center for both servos.
        """
        # Calculate how many degrees per pixel
        deg_per_px_h = FOV_H / CAM_W
        deg_per_px_v = FOV_V / CAM_H

        # Calculate offset from center
        offset_x = fx - CENTER_X
        offset_y = fy - CENTER_Y

        # Map to servo degrees (90 is center)
        # Note: You might need to change '-' to '+' depending on servo orientation
        servo_x = 90 + (offset_x * deg_per_px_h)
        servo_y = 90 + (offset_y * deg_per_px_v)

        return int(servo_x), int(servo_y)

    def get_target_data(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
        
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            fx, fy = x + (w // 2), y + (h // 2)
            
            s_x, s_y = self.calculate_angles(fx, fy)
            return (x, y, w, h), (fx, fy), (s_x, s_y)
        return None, None, None

def main():
    streamer = SerialStreamer(PORT, BAUD)
    processor = TargetProcessor()

    while True:
        frame = streamer.get_frame()
        if frame is None:
            if cv2.waitKey(1) & 0xFF == ord('q'): break
            continue

        bbox, center, angles = processor.get_target_data(frame)

        # Crosshair represents the Laser's "Home" position (Center)
        cv2.line(frame, (CENTER_X-5, CENTER_Y), (CENTER_X+5, CENTER_Y), (255, 255, 255), 1)
        cv2.line(frame, (CENTER_X, CENTER_Y-5), (CENTER_X, CENTER_Y+5), (255, 255, 255), 1)

        if bbox:
            x, y, w, h = bbox
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 1)
            
            # Display target angles for Person 4 (Documentation)
            cv2.putText(frame, f"Pan: {angles[0]} Tilt: {angles[1]}", (5, 110), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 255), 1)

        # Show upscaled for the user
        cv2.imshow("Turret AI View", cv2.resize(frame, (640, 480)))
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()