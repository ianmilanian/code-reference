import cv2
import dlib
import numpy as np
from queue import Queue
from threading import Thread

# dlib toolkit generates HOG descriptors to detect face regions in the frame.
# Identified face regions are used to predict the shape's pose and generate landmarks.

landmark_map = {"mouth":  list(range(48, 68)),
                "r_brow": list(range(17, 22)),
                "l_brow": list(range(22, 27)),
                "r_eye":  list(range(36, 42)),
                "l_eye":  list(range(42, 48)),
                "nose":   list(range(27, 35)),
                "jaw":    list(range( 0, 17))}

face_model = "data/shape_predictor_68_face_landmarks.dat" # pre-trained face detection model
face_pose  = dlib.shape_predictor(face_model)

# IMPORTANT: A clever use of contour properties can save you from training complicated machine learning models.

def update():
    global state
    global frames
    while state:
        state,frame = video.read() # I/O heavy reads in separate thread
        try:
            h,w = frame.shape[:2]
            r   = 0.5
            dim = (int(w * r), int(h * r))
        except:
            continue
        frames.put(cv2.resize(frame, dim, interpolation=cv2.INTER_AREA))
    return

state  = True    # Global!
frames = Queue() # Global!
video  = cv2.VideoCapture("data/jonsnow.mp4")
thread = Thread(target=update, args=())
thread.daemon = True
thread.start()

while state or frames.qsize():
    if not frames.qsize():
        continue
    frame = frames.get()
    faces = dlib.get_frontal_face_detector()(frame, 1)
    for i, box in enumerate(faces):        
        landmarks = face_pose(frame, box)
        for feature, points in landmark_map.items():
            for point in points:
                if point+1 in points:
                    x = (landmarks.part(point).x,   landmarks.part(point).y)
                    y = (landmarks.part(point+1).x, landmarks.part(point+1).y)
                    cv2.line(frame, x, y, (255, 0, 0), 2)

        cv2.rectangle(frame, (box.left(), box.top()), (box.right(), box.bottom()), (0, 255, 0), 2)
        for point in range(0, 68):
            cv2.circle(frame, (landmarks.part(point).x, landmarks.part(point).y), 2, (0, 0, 255), -1)
            
    cv2.imshow("Output", frame)
    cv2.waitKey(1)
cv2.destroyAllWindows()
