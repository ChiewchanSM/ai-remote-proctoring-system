<img width="1196" height="703" alt="Examinees view" src="https://github.com/user-attachments/assets/8b47c60a-958c-429e-b363-f7ec7f6b1bee" /><img width="1411" height="699" alt="Evidence Log" src="https://github.com/user-attachments/assets/3c0c116b-53d5-46e1-aad8-5c74b346ea60" /># K-DAI Smart Remote Proctoring System

An end-to-end automated proctoring application designed to secure remote examinations. 

## Overview
This system utilizes computer vision and machine learning for real-time behavioral tracking and digital screen monitoring. Evidence of academic dishonesty is automatically transmitted via REST API to a centralized SQLite database and displayed on a live Flask web dashboard for instructor review.

## Tech Stack
* **Computer Vision:** OpenCV, YOLOv8, MediaPipe, Face_Recognition
* **Backend & API:** Python, Flask, SQLite, Requests
* **Frontend:** HTML, CSS, Bootstrap

## Core Features
1. **AI Behavior Tracking:** D<img width="1919" height="944" alt="Home" src="https://github.com/user-attachments/assets/f97f72c0-9053-4ed4-9fc5-002a26c1c38f" />
<img width="1196" height="703" alt="Examinees view" src="https://github.com/user-attachments/assets/381fa792-849d-4ba1-b169-41b4019688ef" />
etects unauthorized phone usage, identity swapping, and suspicious head/eye movements.
2. **Digital Screen Monitoring:** Actively tracks screen activity, immediately flagging and screenshotting blacklisted applications (e.g., ChatGPT, Discord).
3. **Teacher Dashboard:** A responsive web interface for examiners to monitor multiple students simultaneously and review structured evidence logs.

## Developed By
**Chiewchan Sumalares** - System Architect & Developer

## Examinee View
<img width="1196" height="703" alt="Examinees view" src="https://github.com/user-attachments/assets/986910cd-45ad-4e6b-b564-af012c3ad45b" />

## Examiner View
<img width="1919" height="944" alt="Home" src="https://github.com/user-attachments/assets/bbaae060-c337-4c32-a22b-fe3e4bded136" />
<img width="1411" height="699" alt="Evidence Log" src="https://github.com/user-attachments/assets/64c1685b-ac4e-48d8-8ec7-3a12439e7e66" />
