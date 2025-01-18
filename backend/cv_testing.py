# command for installation
# pip install opencv-python mediapipe fer tensorflow mtcnn

import cv2
import mediapipe as mp
from fer import FER

# Initialize mediapipe and FER
mp_hands = mp.solutions.hands   # this is getting a mediapipe tool for hand recongition?
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
emotion_detector = FER(mtcnn=True)

# Initialize Mediapipe Hands and Face Detection
# Can play around with these parameters cuz they just have to do with confidence
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

# Start Video Capture
cap = cv2.VideoCapture(0)

while cap.isOpened():
    # reading a frame at a time?
    ret, frame = cap.read()
    if not ret:
        break

    # Flip frame for natural viewing
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process Hand Tracking
    hand_results = hands.process(rgb_frame)
    if hand_results.multi_hand_landmarks:
        for hand_landmarks in hand_results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            # Example: Display "Gesture Detected"
            cv2.putText(frame, "Gesture Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Process Face Detection and Emotion Recognition
    face_results = face_detection.process(rgb_frame)
    # Detect any faces from mediapipes detection (algorithm)
    if face_results.detections:
        for detection in face_results.detections:
            # Extract the overall bounding box for the face from the detection (along with all the dimensions)
            bboxC = detection.location_data.relative_bounding_box
            ih, iw, _ = frame.shape
            x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
            face = frame[y:y+h, x:x+w]

            # Predict emotion if face is detected
            if face.size > 0:
                emotion, score = emotion_detector.top_emotion(face)
                cv2.putText(frame, f"Emotion: {emotion}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            # Draw bounding box on detected face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Display the frame
    cv2.imshow('Gesture and Emotion Recognition', frame)

    # Break on the 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release Resources
cap.release()
cv2.destroyAllWindows()
hands.close()
face_detection.close()

# it worked with no moviepy, no fer, and a version of tensorflow of 2.12, but you can use 2.16 if it ever works
