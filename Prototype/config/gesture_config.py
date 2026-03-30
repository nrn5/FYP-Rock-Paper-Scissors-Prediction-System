# { GESTURE DETECTOR CONFIG }

# PUMP DETECTION
PUMP_LEG_RATIO = 0.7  # requreied movement per direction relative to hand size
PUMP_BUF_FRAMES = 30  # history size for detecting pump motion
FIST_THRESHOLD = 1.35 # finger extentino ratio , below = curled

# STILLNESS DETECTION
STILL_FRAMES = 20  # frames required to consider a hand still
STILL_RATIO = 0.03 # max wrist movement to count as still

# VOTING
VOTE_FRAMES = 20      # how many frames to collect votes while still
MIN_VOTE_SHARE = 0.65 # confidence threshold to accept winner

# ROBUSTNESS
MAX_MISSING_FRAMES = 6 # frames hand can disappear before reset

