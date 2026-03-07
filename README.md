# K-DAI Smart Remote Proctoring System

An end-to-end automated proctoring application designed to secure remote examinations. 

## Overview
This system utilizes computer vision and machine learning for real-time behavioral tracking and digital screen monitoring. Evidence of academic dishonesty is automatically transmitted via REST API to a centralized SQLite database and displayed on a live Flask web dashboard for instructor review.

## Tech Stack
* **Computer Vision:** OpenCV, YOLOv8, MediaPipe, Face_Recognition
* **Backend & API:** Python, Flask, SQLite, Requests
* **Frontend:** HTML, CSS, Bootstrap

## Core Features
1. **AI Behavior Tracking:** Detects unauthorized phone usage, identity swapping, and suspicious head/eye movements.
2. **Digital Screen Monitoring:** Actively tracks screen activity, immediately flagging and screenshotting blacklisted applications (e.g., ChatGPT, Discord).
3. **Teacher Dashboard:** A responsive web interface for examiners to monitor multiple students simultaneously and review structured evidence logs.

## Developed By
**Chiewchan Sumalares** - System Architect & Developer
