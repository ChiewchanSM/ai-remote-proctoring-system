import cv2
import numpy as np
import math
import mediapipe as mp

# MediaPipe Setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Points & 3D Model
RIGHT_EYE_POINTS = [362, 263, 473] 
LEFT_EYE_POINTS = [133, 33, 468]

face_3d_model = np.array([
    [0.0, 0.0, 0.0],          # Nose
    [0.0, 330.0, -65.0],      # Chin
    [-225.0, -170.0, -135.0], # Left Eye
    [225.0, -170.0, -135.0],  # Right Eye
    [-150.0, 150.0, -125.0],  # Left Mouth
    [150.0, 150.0, -125.0]    # Right Mouth
], dtype=np.float64)

# Helper Functions
def euclidean_distance(point1, point2):
    x1, y1 = point1.ravel()
    x2, y2 = point2.ravel()
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def get_h_eye_ratio(img, landmarks, indices):
    h, w, _ = img.shape
    p_inner = np.array([landmarks[indices[0]].x * w, landmarks[indices[0]].y * h])
    p_outer = np.array([landmarks[indices[1]].x * w, landmarks[indices[1]].y * h])
    p_iris  = np.array([landmarks[indices[2]].x * w, landmarks[indices[2]].y * h])

    eye_width = euclidean_distance(p_inner, p_outer)
    dist_to_inner = euclidean_distance(p_inner, p_iris)
    if eye_width == 0: return 0.5
    return dist_to_inner / eye_width, p_iris