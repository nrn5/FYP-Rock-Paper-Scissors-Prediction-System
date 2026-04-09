# { CAMERA FEED }
import cv2
import mediapipe as mp
from config.paths import HAND_LANDMARK_PATH

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # THUMB
    (0, 5), (5, 6), (6, 7), (7, 8),        # INDEX
    (0, 9), (9, 10), (10, 11), (11, 12),   # MIDDLE
    (0, 13), (13, 14), (14, 15), (15, 16), # RING
    (0, 17), (17, 18), (18, 19), (19, 20)  # PINKY
]

_POSSIBLE_RESOLUTIONS = [
    (320, 240),
    (640, 480),
    (800, 600),
    (1280, 720),
    (1920, 1080),
]

# { SUPPORTED RESOLUTIONS }
def find_supported_resolutions(cap) -> list[tuple[int, int]]:
    """ try common resolutions and return ones the camera actually supports """
    supported = []

    orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    for w, h in _POSSIBLE_RESOLUTIONS:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

        actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # allow some small tolerance cause some cameras slightly adjust values
        if abs(actual_w - w) < 10 and abs(actual_h - h) < 10:
            supported.append((w, h))

    # restore original resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, orig_w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, orig_h)   
    # make sure def resolution included
    default = (orig_w, orig_h)
    if default not in supported:
        supported.append(default)

    return sorted(set(supported), key=lambda r: r[0] * r[1])
 
# { CAMERA FEED }
class CameraFeed:
    def __init__(self, camera_index: int=0):
        self.camera_index = camera_index

        # open camera
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"\n[camera_feed.py] Cannot open camera ID: {camera_index}")
        
        # detect supported resolutions
        self.supported_resolutions = find_supported_resolutions(self.cap)
        print(f"\n[camera_feed.py] Supported: {self.supported_resolutions}")

        # { MEDIAPIPE SETUP }
        model_path = HAND_LANDMARK_PATH.resolve()

        baseOptions = mp.tasks.BaseOptions
        handLandMarker = mp.tasks.vision.HandLandmarker
        handLMOptions = mp.tasks.vision.HandLandmarkerOptions
        runningMode = mp.tasks.vision.RunningMode

        # configure detector - path to hand model, processing a video stream, number of hands
        options = handLMOptions(
            base_options=baseOptions(model_asset_path=str(model_path)),
            running_mode=runningMode.VIDEO,
            num_hands=1
        )

        # create the actual detector
        self.detector = handLandMarker.create_from_options(options)
        # a timestamp detector so detection doesnt silently fail
        self.timestamp = 0;

    # { FRAME CAPTURE }
    def get_frame(self):
        """ captures one frame from webcam, runs hand detection, and returns:
            frame for UI display, and landmarks for business logic """
        # read frame from webcam
        ret, frame = self.cap.read()
        # if frame wasnt captured properly
        if not ret or frame is None:
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
    
    # { RESOLUTION }
    def set_resolution(self, w: int, h: int):
        """ change resolution by restarting camera """
        if (w, h) not in self.supported_resolutions:
            print(f"\n[camera_feed.py] Unsupported resolution: {w}x{h}")
            return False
        print(f"\n[camera_feed.py] Switching resolution to; {w}x{h}")

        # relase current camera
        self.cap.release()

        # recreate capture
        self.cap = cv2.VideoCapture(self.camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

        return True
    
    def get_resultion(self):
        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return w, h

    # { CLEANUP }
    def release(self):
        """ releases resources """
        self.cap.release()
        self.detector.close()
        cv2.destroyAllWindows()