#pylint:disable=no-member

import cv2 as cv

vid = cv.VideoCapture(0)

while True:
    #read each frame
    state, frame = vid.read()

    #frame read check
    if not state:
        print("Error: did not get frame")
        break

    #convert frame to gray for the ML tp detect
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    #pre-trained classifier algorithm runs and detects face
    haar_cascade = cv.CascadeClassifier('haar_face.xml')
    faces_rect = haar_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=1) #list of detected faces
    
    #number of faces (if needed)
    ##print(f'Number of faces found = {len(faces_rect)}')
    
    #creating boundary boxes for each of the faces
    for (x,y,w,h) in faces_rect:
        cv.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), thickness=2)
    resizedFrame = cv.resize(frame, (700,500), interpolation=cv.INTER_CUBIC) #resized as required
    cv.imshow('Detected Faces', resizedFrame)
    
    #exit condition
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

vid.release()
cv.destroyAllWindows()