import serial
import time

ser = serial.Serial('COM10', 115200, timeout=1)
ser.setDTR(False)
time.sleep(0.1)
ser.setDTR(True)

print("Reading crash log...")
while True:
    data = ser.read(ser.in_waiting or 1)
    if data:
        try:
            # Try to decode the text
            print(data.decode('utf-8', errors='ignore'), end="")
        except:
            pass