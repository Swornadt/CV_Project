import cv2

# Port 81 is the default for the MJPEG stream
url = "http://192.168.137.196/stream"

cap = cv2.VideoCapture(url)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to fetch frame. Check if another client is connected.")
        break
    
    cv2.imshow('ESP32-CAM Stream', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
