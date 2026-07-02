import cv2 as cv;

#getting native webcam video
vid = cv.VideoCapture(0)

#display
while True:
    #read each frame
    state, frame = vid.read()

    #frame read check
    if not state:
        print("Error: did not get frame")
        break
    #resize and display captured frame
    resized = cv.resize(frame, (700,500), interpolation=cv.INTER_CUBIC)
    cv.imshow('Webcam Feed', resized)

    #Wait for key press "q" to exit
    if cv.waitKey(1) & 0xFF == ord('q'):
        break
    
vid.release()
cv.destroyAllWindows()
