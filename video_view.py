import serial
import cv2
import numpy as np

# Change 'COM3' to your actual port
ser = serial.Serial('COM3', 1000000) 

while True:
    # Look for our header [0xAA, 0xBB]
    if ser.read() == b'\xaa':
        if ser.read() == b'\xbb':
            # Read 4 bytes for size
            size_bytes = ser.read(4)
            size = int.from_bytes(size_bytes, byteorder='big')
            
            # Read the image data
            img_data = ser.read(size)
            
            # Convert to image
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is not None:
                cv2.imshow('ESP32-CAM Stream', img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break