import serial
import cv2
import numpy as np

# Try 460800 - the middle ground speed
ser = serial.Serial('COM10', 460800, timeout=0.5, rtscts=False, dsrdtr=False)
ser.dtr = False
ser.rts = False

buffer = b""

while True:
    if ser.in_waiting > 0:
        buffer += ser.read(ser.in_waiting)
        
    # Find markers
    start = buffer.find(b'\xff\xd8')
    end = buffer.find(b'\xff\xd9')
    
    if start != -1 and end != -1 and end > start:
        jpg = buffer[start:end+2]
        # RECOVERY: Always keep the data AFTER the current frame
        buffer = buffer[end+2:] 
        
        nparr = np.frombuffer(jpg, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is not None:
            cv2.imshow("Stable Stream", img)
    
    # RECOVERY: If we have a start but no end for too long, 
    # the frame is likely corrupted. Clear it.
    elif start != -1 and len(buffer) > 15000: 
        buffer = b""

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

ser.close()
cv2.destroyAllWindows()