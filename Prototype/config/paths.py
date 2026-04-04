# { PATHS CONFIG }

from pathlib import Path

# { ROOT }
ROOT = Path(__file__).parent.parent

# { MODELS }
MODELS_DIR = ROOT/"business"/"models"
GESTURE_RF_PATH = MODELS_DIR/"rps_model.pkl"
HAND_LANDMARK_PATH = MODELS_DIR/"hand_landmarker.task"

