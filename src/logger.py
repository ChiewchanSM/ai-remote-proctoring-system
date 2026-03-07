import os
import time
import cv2
import pyautogui 
from datetime import datetime
import config
import requests  

if not os.path.exists(config.LOG_DIR):
    os.makedirs(config.LOG_DIR)

last_alert_time = 0.0

SERVER_API_URL = "http://127.0.0.1:5000/api/upload"

def log_violation(student_id, violation_type, frame_to_save, capture_screen=False):
    global last_alert_time
    current_time = time.time()
    
    if current_time - last_alert_time > config.ALERT_COOLDOWN:
        dt_string = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_violation_name = "".join([c if c.isalnum() else "_" for c in violation_type])
        photo_name = f"{dt_string}_{safe_violation_name}.jpg"
        
        temp_photo_path = os.path.join(config.LOG_DIR, photo_name)
        if capture_screen:
            pyautogui.screenshot(temp_photo_path) 
        else:
            cv2.imwrite(temp_photo_path, frame_to_save) 
        
        # --- THE API UPLOAD PROCESS ---
        try:
            # Package the text data
            data = {
                'student_id': student_id,
                'violation_type': violation_type,
                'timestamp': dt_string
            }
            # Package the image file
            with open(temp_photo_path, 'rb') as f:
                files = {'photo': (photo_name, f, 'image/jpeg')}
                
                # Send it over the network to the Teacher Server!
                response = requests.post(SERVER_API_URL, data=data, files=files)
                
            if response.status_code == 200:
                print(f"🚨 ALERT SENT TO TEACHER: {violation_type}")
            else:
                print(f"⚠️ Failed to send alert. Server responded with: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Cannot connect to Teacher Server. Is app.py running? Error: {e}")
            
        last_alert_time = current_time