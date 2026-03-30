# { GESTURE DETECTOR }

import time
import warnings
from enum import Enum
from pathlib import Path
from collections import deque

import numpy as np
import joblib

from config.gesture_config import *
from business.feature_extractor import (
    extract_features,
    calculate_distance,
    calculate_hand_size,
)

# { STATE ENUM }
class RPSState(Enum):
    WAITING = "WAITING"
    PLAYING = "PLAYING"
    LOCKED  = "LOCKED" 

# { LANDMARK WRAPPER }
class _LM:
    """ wrap raw (x, y, z) tuples into mediapipe structuer to support lists and mediappe output """
    __slots__ = ("landmark",)

    class _Point:
        __slots__ = ("x", "y", "z")

        def __init__(self, x, y, z):
            self.x = x; self.y = y; self.z = z

    def __init__(self, pts):
        # convert list of tuples to list of objects w .x/.y/.z
        self.landmark = [self._Point(x, y, z) for x, y, z in pts]

# { GESTURE DETECTOR}
class GestureDetector:
    """ core gesture detection state machine
        flow:
            - WAITING > detect pump > PLAYING
            - PLAYING > detect still > LOCKED
            - LOCKED > remains until reset called """
    
    def __init__(self, model_path=None):
        # get model path, default or custom
        model_file = Path(model_path) if model_path else (
            Path(__file__).parent / "models" / "rps_model.pkl"
        )
        # load ML model and suppress sklearn warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.model = joblib.load(model_file)
        warnings.filterwarnings("ignore", message="z does not have valid feature names")

        # state and output
        self.state = RPSState.WAITING
        self.locked_move = None

        # tracks  how many frames had no hand detected
        self._missing_frames = 0

        # initialise buffers (movement and voting)
        self._vote_frames = 20
        self._init_buffers()

    # { CONFIG SETTINGS }
    def set_vote_frames(self, n: int):
        """ dynamically update how many frames we use for voting """
        self._vote_frames = max(1, n) # prevent invalid values
        # rebuild buffer w new size
        self.vote_history = deque(self.vote_history, maxlen=self._vote_frames)
    
    # { PUBLIC API }
    def update(self, landmarks):
        """ process one frame of landmarks, returns gesture only on the frame it locks """
        # handle missing frames , like if hand leaves camera
        if not landmarks:
            self._missing_frames += 1
            # only reset if hand has been gone long enough
            if self._missing_frames > MAX_MISSING_FRAMES:
                if self.state != RPSState.LOCKED:
                    self.reset()
            return None
        # reset missing frame counter once we see hand again
        self._missing_frames = 0
        # normalise input format, raw list to wrapped lm object
        lm = _LM(landmarks) if isinstance(landmarks, list) else landmarks

        # WAITING: look for pump motion
        if self.state == RPSState.WAITING:
            if self._detect_pump(lm):
                print("\n[gesture_detector.py] Pump detected >> STATE: PLAYING")
                # reset buffers so previs motion doesnt affect detection
                self._init_buffers()
                self.state = RPSState.PLAYING
            return None
        
        # PLAYING: detect gesture
        if self.state == RPSState.PLAYING:
            return self._process_playing(lm)

        # LOCKED: do nothing, gesture already returned once
        return None

    def reset(self):
        """ reset detector back to WAITING state """
        self._init_buffers()
        self.state = RPSState.WAITING
        self.locked_move = None
        self._missing_frames = 0

    # { PLAYING STATE LOGIC }
    def _process_playing(self, lm):
        """ handles detection after pump:
            - wait until hands become still
            - collect classification votes
            - lock when consensus is strong enoghu """
        # track wrist y (used to detect stillness)
        self.still_history.append(lm.landmark[0].y)

        if not self._is_still():
            self.vote_history.clear()
            self._still_start_time = None
            return None
        # start timing when hands become still, for my debug and research mostly
        if self._still_start_time is None:
            self._still_start_time = time.perf_counter()
        
        # classify current frame
        gesture, confidence = self._classify(lm)
        # store vote
        self.vote_history.append((gesture, confidence))
        print(f"[gesture_detector.py] gesture:{gesture} vote:{len(self.vote_history)}/{self.vote_history.maxlen}")
        # wait until enough votes collected
        if len(self.vote_history) < self.vote_history.maxlen:
            return None
        
        # try to resove winner
        winner = self._resolve_vote()
        if winner:
            # measure time from still to lock
            elapsed = (time.perf_counter() - self._still_start_time) * 1000
            self.last_detection_ms = round(elapsed, 1)
            self.locked_move = winner
            self.state = RPSState.LOCKED

            print(f"\n[gesture_detector.py] Locked move: {winner} ({self.last_detection_ms} ms)") 
            return winner
        # if no clear winner, reset and keep collecting
        self.vote_history.clear()
        return None

    def _is_still(self):
        """ check if hand movement is still """
        # wait until buffer fills before making decisins
        if len(self.still_history) < self.still_history.maxlen:
            return False
        # calculate how much hand moves revently
        movement_range = max(self.still_history) - min(self.still_history)

        return movement_range < STILL_RATIO

    # { PUMP DETECTION }
    def _detect_pump(self, lm):
        """ detect pump gesture, up-down motion while fist
            for it to be a pump:
                - hand has to be a fist
                - movement has to reverse direction
                - both movement legs need ot exceed threshold (so no small jitter) """
        # track wrist y movement over time
        self.pump_history.append(lm.landmark[0].y)

        # only allow pump when hand is closed (a fist)
        if not self._is_fist(lm):
            return False
        # need enough frames to detect motion pattern
        if len(self.pump_history) < 6:
            return False
    
        hand_size = calculate_hand_size(lm.landmark)
        min_movement = PUMP_LEG_RATIO * hand_size
        values = list(self.pump_history)

        # track highest and lowest points
        highest = lowest = values[0]
        direction = None # up or down

        for y in values[1:]:
            # moving downward
            if y < lowest:
                # if we were moving up before, check if full motion done
                if direction == "up" and (highest - lowest) >= min_movement:
                    self.pump_history.clear()
                    return True
                lowest = y
                direction = "down"
            
            # moving upward
            elif y > highest:
                if direction == "down" and (highest - lowest) >= min_movement:
                    self.pump_history.clear()
                    return True
                highest = y
                direction = "up"
        return False

    # { FIST DETECTION }
    def _is_fist(self, lm):
        """ determine is hand is closed; uses ratio - tip distance / base distance,
            smaller ratio = finger curled """
        wrist = lm.landmark[0]
        
        for tip_idx, base_idx in ((8,5), (12,9), (16,13), (20,17)):
            tip_dist = calculate_distance(lm.landmark[tip_idx], wrist)
            base_dist = calculate_distance(lm.landmark[base_idx], wrist) + 1e-6
            # if any finger is extended, not a fist
            if (tip_dist/base_dist) >= FIST_THRESHOLD:
                return False
        return True

    # { CLASSIFICATION }
    def _classify(self, lm):
        """ run ML model on extracted features """
        import pandas as pd
        features = extract_features(lm.landmark)
        columns = ["ext_index","ext_middle","ext_ring","ext_pinky",
                   "avg_gap","max_gap","gap_1","gap_2","gap_3"]
        df = pd.DataFrame([features], columns=columns)

        probabilities = self.model.predict_proba(df)[0]
        best_idx = int(np.argmax(probabilities))

        return self.model.classes_[best_idx], float(probabilities[best_idx])

    def _resolve_vote(self):
        """ combines votes using confidence weighting, returns winner only if confidence is high enough """
        scores = {}
        total_confidence = 0.0
        # get weighted votes
        for gesture, conf in self.vote_history:
            scores[gesture] = scores.get(gesture, 0.0) + conf
            total_confidence += conf
        
        winner = max(scores, key=scores.get)
        share = scores[winner] / (total_confidence + 1e-9) # 1e-9 to avoid zero divide
        
        return winner if share >= MIN_VOTE_SHARE else None

    # { BUFFERS }
    def _init_buffers(self):
        """ initialise or reset all buffers, currently used for:
            - pump detection
            - stillness tracking
            - voting """
        self.pump_history = deque(maxlen=PUMP_BUF_FRAMES)
        self.still_history = deque(maxlen=STILL_FRAMES)
        self.vote_history = deque(maxlen=self._vote_frames)
        
        self._still_start_time = None
        self.last_detection_ms = None