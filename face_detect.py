#pylint:disable=no-member

import cv2 as cv

vid = cv.VideoCapture(0)
ws, hs = 1280, 720

#pre-trained classifier algorithm runs and detects face
haar_cascade = cv.CascadeClassifier('haar_face.xml')

while True:
    #read each frame
    state, frame = vid.read()

    #frame read check
    if not state:
        print("Error: did not get frame")
        break

    #convert frame to gray for the ML to detect
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    #face detection
    faces_rect = haar_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10) #list of detected faces
    
    #number of faces (if needed)
    num_faces = len(faces_rect)
    
    #creating boundary boxes for each of the faces
    for (x,y,w,h) in faces_rect:
        cv.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), thickness=2)
    
    teks = "Number of Faces Detected = " + str(len(faces_rect))

    font = cv.FONT_HERSHEY_SIMPLEX
    cv.putText(frame, teks, (0, 30), font, 1, (255, 0, 0), 1)
    
    # --- COORDINATE TRACKING AND TARGETING LOGIC ---
    if num_faces > 0:
        # Get the coordinates of the first detected face (x, y, w, h)
        x, y, w, h = faces_rect[0]

        # Calculate the center coordinates (fx, fy)
        fx = int(x + w / 2)
        fy = int(y + h / 2)
        pos = (fx, fy)
        
        # Drawing targeting elements on the *original* frame
        cv.circle(frame, pos, 100, (0, 0, 255), 2) # Larger circle for target area
        cv.putText(frame, str(pos), (fx+15, fy-15), cv.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2 )
        cv.line(frame, (0, fy), (ws, fy), (0, 0, 0), 2)  # X-axis line (horizontal)
        cv.line(frame, (fx, hs), (fx, 0), (0, 0, 0), 2)  # Y-axis line (vertical)
        cv.circle(frame, pos, 6, (0, 0, 255), cv.FILLED) # Center dot
        cv.putText(frame, "TARGET LOCKED", (int(ws * 0.7), 50), cv.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 3 )
    # --- END TARGETING LOGIC ---

    #display
    resizedFrame = cv.resize(frame, (700,500), interpolation=cv.INTER_CUBIC) #resized as required
    cv.imshow('Detected Faces', resizedFrame)
    
    #exit condition
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

vid.release()
cv.destroyAllWindows()