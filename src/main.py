import cv2
import numpy as np
import torch
from ultralytics import YOLO
import face_recognition
import tkinter as tk
from tkinter import simpledialog, messagebox

import config
import logger
import vision_tools
import screen_tools

# ==========================================
# 0. STUDENT LOGIN SCREEN
# ==========================================
# Hide the main tkinter background window
ROOT = tk.Tk()
ROOT.withdraw()

# Show the popup dialogs
student_id_input = simpledialog.askstring(title="Smart Proctor Login", prompt="Enter your Student ID:")
student_name_input = simpledialog.askstring(title="Smart Proctor Login", prompt="Enter your Full Name:")

# Check if they hit "Cancel" or left it blank
if not student_id_input or not student_name_input:
    messagebox.showerror("Login Failed", "You must enter your ID and Name to take the exam.")
    exit() # Closes the program completely

# Combine them so the dashboard knows exactly who it is!
EXAMINEE_ID = f"{student_name_input} ({student_id_input})"
print(f"✅ Logged in successfully as: {EXAMINEE_ID}")

# ==========================================
# 1. SETUP
# ==========================================
if torch.cuda.is_available():
    print(f"SUCCESS: Running on {torch.cuda.get_device_name(0)}")
    device_target, use_half_precision = 0, True
else:
    print("WARNING: Running on CPU.")
    device_target, use_half_precision = 'cpu', False

print("Loading YOLOv8s Model...")
model = YOLO("yolov8s.pt")

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

registered_face_encoding = None  
current_trusted_yolo_id = None  

print("\n*** MASTER PROCTOR INITIALIZED. Press 'q' to quit, 'r' to reset identity. ***")

# ==========================================
# 2. MAIN LOOP
# ==========================================
while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.flip(frame, 1) 
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Save a clean copy for evidence photos BEFORE we draw boxes on it
    clean_evidence_frame = frame.copy() 

    # --- PHASE 1: YOLO SWEEP ---
    results = model.track(frame, persist=True, conf=0.5, classes=[config.CLASS_PERSON, config.CLASS_PHONE], 
                          device=device_target, half=use_half_precision, verbose=False)
    annotated_frame = results[0].plot(labels=False) 
    
    room_status, room_color = "WAITING FOR EXAMINEE...", (200, 200, 200) 
    head_status1, head_color1 = "HEAD: FOCUSED", (0, 255, 0)
    head_status2, head_color2 = "HEAD: FOCUSED", (0, 255, 0)
    eye_status, eye_color = "EYES: FOCUSED", (0, 255, 0)
    
    phone_detected, is_identity_secure, people_data = False, False, [] 

    if results[0].boxes is not None:
        coords = results[0].boxes.xywh.cpu()
        classes = results[0].boxes.cls.int().cpu().tolist()
        ids = results[0].boxes.id.int().cpu().tolist() if results[0].boxes.id is not None else [-1] * len(classes)

        for box, clss, t_id in zip(coords, classes, ids):
            x_tl, y_tl = int(box[0] - box[2]/2), int(box[1] - box[3]/2)

            if clss == config.CLASS_PHONE:
                phone_detected = True
                cv2.rectangle(annotated_frame, (x_tl, y_tl), (x_tl + int(box[2]), y_tl + int(box[3])), (0, 0, 255), 4)
                cv2.putText(annotated_frame, "CONTRABAND: PHONE", (x_tl, y_tl - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                logger.log_violation(EXAMINEE_ID, "Cell Phone Detected", clean_evidence_frame)
            
            elif clss == config.CLASS_PERSON: 
                people_data.append((box, t_id))

        # --- PHASE 2: IDENTITY ---
        current_people = len(people_data)
        if current_people == 1:
            current_id = people_data[0][1]
            if registered_face_encoding is None:
                face_locations = face_recognition.face_locations(rgb_frame)
                if face_locations:
                    registered_face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
                    current_trusted_yolo_id = current_id
                    print("*** EXAMINEE FACE REGISTERED! ***")
                else:
                    room_status, room_color = "PLEASE LOOK AT CAMERA TO REGISTER", (0, 165, 255)
            elif registered_face_encoding is not None:
                if current_id == current_trusted_yolo_id:
                    room_status, room_color, is_identity_secure = "ROOM: SECURE", (0, 255, 0), True
                else:
                    room_status, room_color = "VERIFYING IDENTITY...", (0, 165, 255)
                    face_locations = face_recognition.face_locations(rgb_frame)
                    if face_locations:
                        current_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
                        if face_recognition.compare_faces([registered_face_encoding], current_encoding, tolerance=0.5)[0]:
                            current_trusted_yolo_id, is_identity_secure = current_id, True
                        else:
                            room_status, room_color = "ALERT: IDENTITY SWAP DETECTED!", (0, 0, 255)
                            logger.log_violation(EXAMINEE_ID, "Identity Swap", clean_evidence_frame)

        elif current_people > 1:
            room_status, room_color = "ALERT: MULTIPLE PEOPLE DETECTED!", (0, 0, 255) 
            logger.log_violation(EXAMINEE_ID, "Multiple People Detected", clean_evidence_frame)
        elif current_people == 0 and registered_face_encoding is not None:
            room_status, room_color = "WARNING: EXAMINEE LEFT SEAT!", (0, 165, 255)
            logger.log_violation(EXAMINEE_ID, "Left Seat", clean_evidence_frame)

        for box, t_id in people_data:
            x_tl, y_tl = int(box[0] - box[2]/2), int(box[1] - box[3]/2)
            if registered_face_encoding is not None and t_id == current_trusted_yolo_id:
                cv2.putText(annotated_frame, f"SECURE: {EXAMINEE_ID}", (x_tl, y_tl - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                cv2.putText(annotated_frame, f"UNKNOWN PERSON DETECTED", (x_tl, y_tl - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # --- PHASE 3: BEHAVIOR TRACKING ---
    if is_identity_secure and not phone_detected:
        mp_results = vision_tools.face_mesh.process(rgb_frame)
        
        if mp_results.multi_face_landmarks:
            landmarks = mp_results.multi_face_landmarks[0].landmark
            img_h, img_w, _ = annotated_frame.shape

            face_2d = np.array([[int(landmarks[idx].x * img_w), int(landmarks[idx].y * img_h)] for idx in [1, 199, 33, 263, 61, 291]], dtype=np.float64)
            cam_matrix = np.array([[1 * img_w, 0, img_w/2], [0, 1 * img_w, img_h/2], [0, 0, 1]])
            dist_matrix = np.zeros((4, 1), dtype=np.float64)

            success, rot_vec, trans_vec = cv2.solvePnP(vision_tools.face_3d_model, face_2d, cam_matrix, dist_matrix)
            rmat, _ = cv2.Rodrigues(rot_vec)
            angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

            raw_pitch = angles[0] 
            pitch = raw_pitch - config.PITCH_OFFSET 
            yaw = angles[1]  

            # User Logic preserved
            if yaw < -config.HEAD_YAW_LIMIT:
                head_status1, head_color1 = "HEAD: TURNED LEFT", (0, 0, 255)
                logger.log_violation(EXAMINEE_ID, "Looking Left", clean_evidence_frame)
            elif yaw > config.HEAD_YAW_LIMIT:
                head_status1, head_color1 = "HEAD: TURNED RIGHT", (0, 0, 255)
                logger.log_violation(EXAMINEE_ID, "Looking Right", clean_evidence_frame)
            
            if pitch < -config.HEAD_PITCH_LIMIT:
                head_status2, head_color2 = "HEAD: TILTED DOWN", (0, 0, 255)
                logger.log_violation(EXAMINEE_ID, "Looking Down", clean_evidence_frame)
            elif pitch > config.HEAD_PITCH_LIMIT:
                head_status2, head_color2 = "HEAD: TILTED UP", (0, 0, 255)
                logger.log_violation(EXAMINEE_ID, "Looking Up", clean_evidence_frame)

            r_ratio, r_iris = vision_tools.get_h_eye_ratio(annotated_frame, landmarks, vision_tools.RIGHT_EYE_POINTS)
            l_ratio, l_iris = vision_tools.get_h_eye_ratio(annotated_frame, landmarks, vision_tools.LEFT_EYE_POINTS)
            avg_h_eye = (r_ratio + (1.0 - l_ratio)) / 2

            if avg_h_eye < config.EYE_THRESH_LEFT:
                eye_status, eye_color = "EYES: LOOKING RIGHT", (0, 165, 255)
                logger.log_violation(EXAMINEE_ID, "Eyes Right", clean_evidence_frame)
            elif avg_h_eye > config.EYE_THRESH_RIGHT:
                eye_status, eye_color = "EYES: LOOKING LEFT", (0, 165, 255) 
                logger.log_violation(EXAMINEE_ID, "Eyes Left", clean_evidence_frame)
            
            screen_violation = screen_tools.check_active_window()
            if screen_violation:
                logger.log_violation(EXAMINEE_ID, screen_violation, clean_evidence_frame, capture_screen=True)
                
                room_status = f"CRITICAL: {screen_violation.upper()}!"
                room_color = (0, 0, 255)
                
            # Draw visual tracking guides
            nose_point = (int(face_2d[0][0]), int(face_2d[0][1]))
            p2_2d, _ = cv2.projectPoints(np.array([(0.0, 0.0, 1000.0)]), rot_vec, trans_vec, cam_matrix, dist_matrix)
            cv2.line(annotated_frame, nose_point, (int(p2_2d[0][0][0]), int(p2_2d[0][0][1])), (255, 255, 0), 3)
            cv2.circle(annotated_frame, (int(r_iris[0]), int(r_iris[1])), 3, (0, 255, 255), -1)
            cv2.circle(annotated_frame, (int(l_iris[0]), int(l_iris[1])), 3, (0, 255, 255), -1)

            cv2.putText(annotated_frame, f"RAW PITCH: {int(raw_pitch)}", (30, img_h - 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
            cv2.putText(annotated_frame, f"OFFSET PITCH: {int(pitch)}", (30, img_h - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
            cv2.putText(annotated_frame, f"YAW: {int(yaw)}", (30, img_h - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
            cv2.putText(annotated_frame, f"EYE RATIO: {avg_h_eye:.2f}", (30, img_h - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

    # --- UI DASHBOARD ---
    cv2.putText(annotated_frame, room_status, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, room_color, 2)
    
    if phone_detected:
        cv2.putText(annotated_frame, "CRITICAL ALERT: PHONE DETECTED!", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    elif is_identity_secure:
        cv2.putText(annotated_frame, head_status1, (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, head_color1, 3)
        cv2.putText(annotated_frame, head_status2, (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, head_color2, 3)
        cv2.putText(annotated_frame, eye_status, (30, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, eye_color, 3)

    # Draw a simple red "Recording" dot on the clean frame
    cv2.circle(clean_evidence_frame, (30, 30), 10, (0, 0, 255), -1)
    cv2.putText(clean_evidence_frame, "PROCTORING ACTIVE", (50, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    # Show the clean frame to the student, keeping the AI invisible!
    cv2.imshow("Smart Proctor - Exam View", clean_evidence_frame)
  
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"): break
    elif key == ord("r"):
        print("Resetting Memory...")
        current_trusted_yolo_id = None
        registered_face_encoding = None

cap.release()
cv2.destroyAllWindows()