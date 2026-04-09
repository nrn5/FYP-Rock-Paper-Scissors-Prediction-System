# { COLLECT GESTURE DATA FOR RANDOM FOREST }

import cv2
import csv
from presentation.camera_feed import CameraFeed
from business.feature_extractor import extract_features
from config.paths import RF_DATA_PATH

def init_camera(index=0) -> CameraFeed:
    cam = CameraFeed(camera_index=index)
    if not cam.cap.isOpened():
        raise RuntimeError("\n[collect_rf_data.py] Camera failed to open.")
    return cam

def print_instructions():
    print("\n ***** GESTURE DATA COLLECTION *****")
    print("R = record rock")
    print("P = record paper")
    print("S = record scissors")
    print("ESC = quit\n")

def check_header(writer, path):
    """ write csv header only if file is empty """
    try:
        with open(path, "r") as f:
            has_data = f.read(1)
    except FileNotFoundError:
        has_data = False

    if not has_data:
        writer.writerow(["ext_index", "ext_middle", "ext_ring", "ext_pinky",
                         "avg_gap", "max_gap", "gap_1", "gap_2", "gap_3", "label"])

def run_collection():
    cam = init_camera()
    print_instructions()

    with open(RF_DATA_PATH, mode="a", newline="") as f:
        writer = csv.writer(f)
        check_header(writer, RF_DATA_PATH)

        while True:
            frame, landmarks_list = cam.get_frame()
            if frame is None:
                continue

            cv2.imshow("Data Collection", frame)
            key = cv2.waitKey(1) & 0xFF
            # if esc
            if key == 27:
                break

            # skip if no hand detected
            if not landmarks_list:
                continue

            hand = landmarks_list[0]
            features = extract_features(hand)

            # map keys to labels
            label_map = {ord("r"): "rock",
                         ord("p"): "paper",
                         ord("s"): "scissors",}
            
            if key in label_map:
                label = label_map[key]
                writer.writerow([*features, label])
                print(f"Saved {label.upper()}")

    cam.release()
    cv2.destroyAllWindows()

# { MAIN ENTRY }
if __name__ == "__main__":
    run_collection()