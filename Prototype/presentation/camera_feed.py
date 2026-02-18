import cv2
import mediapipe as mp

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # THUMB
    (0, 5), (5, 6), (6, 7), (7, 8),        # INDEX
    (0, 9), (9, 10), (10, 11), (11, 12),   # MIDDLE
    (0, 13), (13, 14), (14, 15), (15, 16), # RING
    (0, 17), (17, 18), (18, 19), (19, 20)  # PINKY
]

class CameraFeed:
    def __init__(self, camera_index: int=0):
        # camera
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"[CAMERA FEED] Cannot open camera ID: {camera_index}")
        # mediapipe tasks hand model
        model_path = "FYP-Rock-Paper-Scissors-Prediction-System/Prototype/presentation/model/hand_landmarker.task"

        baseOptions = mp.tasks.BaseOptions
        handLandMarker = mp.tasks.vision.HandLandmarker
        handLMOptions = mp.tasks.vision.HandLandmarkerOptions
        runningMode = mp.tasks.vision.RunningMode

        # configure detector - path to hand model, processing a video stream, number of hands
        options = handLMOptions(
            base_options=baseOptions(model_asset_path=model_path),
            running_mode=runningMode.VIDEO,
            num_hands=1
        )

        # create the actual detector
        self.detector = handLandMarker.create_from_options(options)
        # a timestamp detector so detection doesnt silently fail
        self.timestamp = 0;

    def get_frame(self):
        """ captures one frame from webcam, runs hand detection, and returns:
            frame for UI display, and landmarks for business logic """
        # read frame from webcam
        ret, frame = self.cap.read()
        # if frame wasnt captured properly
        if not ret:
            return None, None
        # flip horizontally to mirror it
        frame = cv2.flip(frame, 1)
        # convert it to RGB bc OpenCV uses BGR and mediapipe uses RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # convert to mediapipe image format
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        # inc timestamp
        self.timestamp += 1

        # run landmark detection
        result = self.detector.detect_for_video(mp_image, self.timestamp)
        # get the landmarks
        landmarks = []
        if result.hand_landmarks:
            h, w, _ = frame.shape
            for hand_landmarks in result.hand_landmarks:
                # extract normalised coordinates (0 - 1 range)
                hand_pts = [(lm.x, lm.y, lm.z) for lm in hand_landmarks]
                landmarks.append(hand_pts)
                
                # draw connecitons (blue for now, might add more settings)
                for start_idx, end_idx in HAND_CONNECTIONS:
                    x1, y1 = int(hand_pts[start_idx][0] * w), int(hand_pts[start_idx][1] * h)
                    x2, y2 = int(hand_pts[end_idx][0] * w), int(hand_pts[end_idx][1] * h)
                    cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

                # draw landmarks (green for now, might add more settings)
                for x, y, z in hand_pts:
                    cv2.circle(frame, (int(x * w), int(y * h)), 5, (0, 255, 0), -1)

        return frame, landmarks

    def release(self):
        """ releases resources """
        self.cap.release()
        self.detector.close()
        cv2.destroyAllWindows()