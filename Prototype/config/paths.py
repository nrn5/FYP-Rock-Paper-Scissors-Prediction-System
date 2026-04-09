# { PATHS CONFIG }

from pathlib import Path

# { ROOT }
ROOT = Path(__file__).parent.parent

# { MODELS }
MODELS_DIR = ROOT/"business"/"models"
GESTURE_RF_PATH = MODELS_DIR/"rps_model.pkl"
LSTM_PATH = MODELS_DIR/"lstm_model.h5"
HAND_LANDMARK_PATH = MODELS_DIR/"hand_landmarker.task"

# { TRAINING DATA }
TRAINING_DIR = ROOT/"training"
DATA_DIR = TRAINING_DIR/"data"
RF_DATA_PATH = DATA_DIR/"rf_training_data.csv"