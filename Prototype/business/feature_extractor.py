# { FEATURE EXTRACTOR }

import math
import numpy as np

def calculate_distance(a, b):
    """ 2d euclidean distance between two landmarks """
    return math.dist((a.x, a.y), (b.x, b.y))

def calculate_hand_size(landmarks):
    """ estimate hand size using wrist to pinky mcp """
    return calculate_distance(landmarks[0], landmarks[17]) + 1e-6

def extract_features(landmarks):
    """ convert hand landmarks into feature vector for ML
        features:  
         - finger extension ratios 
         - finger gaps
         - average gap stats (mean + max) """
    wrist = landmarks[0]
    fingers = [(8, 5), (12, 9), (16, 13), (20, 17)]
    # finger extention ratios
    extensions = []
    for tip_idx, base_idx in fingers:
        tip_dist = calculate_distance(landmarks[tip_idx], wrist)
        base_dist = calculate_distance(landmarks[base_idx], wrist) + 1e-6
        extensions.append(tip_dist / base_dist)

    # gaps between finger tips
    gaps = [calculate_distance(landmarks[8],  landmarks[12]),
            calculate_distance(landmarks[12], landmarks[16]),
            calculate_distance(landmarks[16], landmarks[20]),]

    # combine into single feature vector
    features = extensions + [np.mean(gaps), np.max(gaps)] + gaps
    return np.array(features, dtype=np.float32)