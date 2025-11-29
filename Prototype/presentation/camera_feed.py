import cv2
import mediapipe as mp

class CameraFeed:
    def __init__(self, camera_index=0):
        # initialise webcam
        self.capture = cv2.VideoCapture(camera_index)
        
        # initialise hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        # 
        self.mp_draw = mp.solutions.drawing_utils

    def get_frame(self):
        """ capture a frame from the camera """
        if not self.capture.isOpened():
            return None

        ret, frame = self.capture.read()
        if not ret:
            return None

        # flip frame to mirror 
        frame = cv2.flip(frame, 1)

        # convert bgr > rgb for mediapipe
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)

        # draw hand landmarks if detected
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        return frame

    def release(self):
        """ release camera resources """
        self.capture.release()
        cv2.destroyAllWindows()
