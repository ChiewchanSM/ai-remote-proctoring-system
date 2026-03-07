import os

# ==========================================
# THRESHOLDS & SETTINGS
# ==========================================
# Head Pose Limits 
HEAD_YAW_LIMIT = 30    
HEAD_PITCH_LIMIT = 20
PITCH_OFFSET = 0       

# Eye Tracking Limits
EYE_THRESH_LEFT = 0.38
EYE_THRESH_RIGHT = 0.62

# YOLO Targets (COCO Dataset)
CLASS_PERSON = 0
CLASS_PHONE = 67

# Evidence Logging Settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "data")
CSV_FILE = os.path.join(LOG_DIR, "proctor_report.csv")
ALERT_COOLDOWN = 5.0  # Wait 5 seconds before taking another photo