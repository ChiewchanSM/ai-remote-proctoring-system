# Smart Remote Exam Proctoring System

> An AI-powered, **privacy-preserving** online exam proctoring system that runs entirely on the student's local device — no video is ever streamed to external servers.

Built as a Special Project for the Bachelor of Science in Digital Technology and Integrated Innovation,
**King Mongkut's Institute of Technology Ladkrabang (KMITL)**, Academic Year 2025.

**Developer:** Chiewchan Sumalares (Student ID: 66051177)
**Advisor:** Asst. Prof. Dr. Akadej Udomchaiporn
**Co-Advisor:** Mr. Yuttapichai Kerdcharoen

---

## Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Detection Modules](#-detection-modules)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [Evaluation](#-evaluation)
- [Results](#-results)
- [Future Work](#-future-work)

---

## Overview

The widespread adoption of online education has made remote examinations a permanent fixture of academic life. However, ensuring academic integrity in unproctored environments remains a critical challenge. Existing commercial solutions are expensive and raise serious student privacy concerns by streaming live video to third-party servers.

This system offers a **lightweight, zero-cost alternative** that:

- Runs all AI inference **locally on the student's CPU** — no video ever leaves the device
- Transmits only **text-based alert logs and snapshot images** when a violation is detected
- Enables instructors to review evidence through a **Flask web dashboard**
- Keeps the **human in the loop** — the AI flags, the instructor decides

---

## Key Features

| Feature | Description | Threshold |
|---|---|---|
| Phone Detection | Detects unauthorized mobile phones via YOLOv8 | Confidence > 70% |
| Head Pose Estimation | Detects sustained looking away from screen | Pitch or Yaw > ±20° for > 3s |
| Eye Gaze Tracking | Detects gaze deviation off-screen | Off-screen > 3 consecutive seconds |
| Face Recognition | Verifies examinee identity each frame | Match confidence > 80% |
| People Counting | Detects absence or unauthorized assistance | Count = 0 or Count > 1 |
| App Blacklist | Detects forbidden apps (ChatGPT, Google, etc.) | Within 2 seconds of opening |

---

## System Architecture

```
┌─────────────────────────────┐        HTTP POST         ┌──────────────────────────────┐
│      STUDENT DEVICE          │   (alert payload only)   │     INSTRUCTOR SERVER         │
│                             │ ────────────────────────▶ │                              │
│  Webcam → Detection Pipeline│                           │  Flask REST API              │
│  ├── YOLOv8 (phone)         │   timestamp + flag +      │       ↓                      │
│  ├── MediaPipe (head/eyes)  │   snapshot image          │  SQLite Database             │
│  ├── face_recognition       │                           │       ↓                      │
│  └── PyGetWindow (apps)     │   ✗ NO video stream       │  Flask Web Dashboard         │
│                             │                           │       ↓                      │
│  All inference runs locally │                           │  Instructor Review           │
└─────────────────────────────┘                           └──────────────────────────────┘
```

The system uses a **Human-in-the-Loop** architecture — the AI detects and logs suspicious events, but the instructor makes all final decisions. This prevents students from being automatically penalized due to false positives.

---

## Detection Modules

### 1. Phone Detection (YOLOv8 Nano)
Uses the YOLOv8 Nano model pre-trained on COCO to detect `cell phone` class objects in real time. Only triggers an alert when the model confidence exceeds **70%**, reducing false positives from similar-looking objects (books, remotes, etc.).

### 2. Head Pose Estimation (MediaPipe Face Mesh)
Extracts 468 3D facial landmarks per frame and solves a PnP problem to compute Euler angles (Yaw, Pitch, Roll). An alert is triggered if the student's head is rotated beyond **±20 degrees** for more than **3 consecutive seconds**.

### 3. Eye Gaze Tracking (MediaPipe Face Mesh)
Uses iris landmark positions relative to eye contour landmarks to estimate gaze direction. Triggers an alert if the gaze is continuously off-screen for more than **3 seconds**.

### 4. Face Recognition (face_recognition / dlib)
Encodes the student's face as a 128-dimensional vector at enrollment. During the exam, each detected face is compared against the registered encoding. A confidence score below **80%** triggers an identity alert.

### 5. People Counting (YOLOv8)
Counts detected persons in the frame. A count of **0** triggers a "Left Seat" alert; a count **> 1** triggers a "Multiple People Detected" alert.

### 6. App Blacklist (PyGetWindow / PyAutoGUI)
Polls the active desktop window title. If a blacklisted application (e.g. ChatGPT, Google, Discord) is detected, a screenshot is captured and transmitted within **2 seconds**.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Object Detection | YOLOv8 Nano (Ultralytics) |
| Face Analysis | MediaPipe Face Mesh |
| Identity Verification | face_recognition (dlib) |
| OS Monitoring | PyGetWindow / PyAutoGUI |
| Backend API | Flask (Python) |
| Database | SQLite |
| Frontend Dashboard | HTML / Bootstrap / Flask |
| Language | Python 77% · HTML 23% |

---

## 📁 Project Structure

```
ai-remote-proctoring-system/
│
├── src/                        # AI client (runs on student's device)
│   ├── main.py                 # Entry point — student-side proctoring client
│   ├── config.py               # All thresholds and configuration constants
│   ├── vision_tools.py         # MediaPipe, eye ratio, face mesh helpers
│   └── Videos_Testing/         # Place test videos here for evaluation
│
├── server/                     # Backend server (runs on instructor's device)
│   ├── app.py                  # Flask REST API + web dashboard
│   ├── database.py             # SQLite schema and query helpers
│   └── templates/              # HTML dashboard templates
│       ├── index.html          # Classroom overview page
│       └── evidence.html       # Per-student evidence log page
│
├── evaluate_video.py           # Offline batch evaluation script (with FPS graph)
├── requirements.txt            # Python dependencies
└── README.md
```

---

## ⚙️ Installation

### Prerequisites
- Python 3.9+
- Windows OS (required for PyGetWindow app monitoring)
- Webcam

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/ChiewchanSM/ai-remote-proctoring-system.git
cd ai-remote-proctoring-system
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

> ⚠️ `face_recognition` requires `cmake` and `dlib` to build. On Windows, install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) first, then run `pip install dlib face_recognition`.

**3. Download YOLOv8 model** (auto-downloads on first run, or manually place in `src/`)
```bash
# The model downloads automatically when you first run the client.
# To pre-download:
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

---

## Usage

### Step 1 — Start the instructor server
```bash
cd server
python app.py
```
The dashboard will be available at `http://localhost:5000`

### Step 2 — Enroll the student (first-time setup)
Place a clear front-facing photo of the student as `reference.jpg` in the `src/` folder.

### Step 3 — Start the student client
```bash
cd src
python main.py
```
Enter your Student ID in the login dialog. The proctoring session begins immediately.

### Step 4 — Monitor via dashboard
Open `http://localhost:5000` on the instructor's machine to view the Classroom Overview and Evidence Logs in real time.

---

## Evaluation

To run offline batch evaluation against a folder of test videos:

```bash
# Edit VIDEO_FOLDER and REFERENCE_IMAGE_PATH at the top of evaluate_video.py first
python evaluate_video.py
```

**Outputs generated per video:**
- `evaluation_evidence/<video_name>/` — snapshot images for each detected violation
- `evaluation_evidence/<video_name>/fps_graph.png` — FPS performance graph
- `evaluation_evidence/evaluation_report.csv` — full alert log (video, time, type, evidence path)
- `evaluation_evidence/fps_summary.csv` — FPS stats per video with Grade A pass/fail

---

## Results

Evaluated on 20 self-recorded mock exam videos (10 normal, 10 suspicious) on an **Intel Core i5-12500H** laptop (CPU-only inference):

| Metric | Target (Grade A) | Achieved |
|---|---|---|
| Detection Accuracy | > 90% | **90% (18/20)** ✅ |
| Processing Speed | > 15 FPS | **~17 FPS** ✅ |
| App Alert Response | < 2 seconds | **< 2 seconds** ✅ |
| False Alarms (normal videos) | 0 | **0 / 10** ✅ |

**Per-feature detection summary (suspicious videos):**

| Feature | Tested | Detected | FN |
|---|---|---|---|
| Phone Detection | 5 | 4 | 1 |
| Looking Left/Right | 5 | 5 | 0 |
| Head Left/Right | 5 | 4 | 1 |
| Head Down/Up | 5 | 4 | 0 |
| Left Seat | 5 | 5 | 0 |
| Multiple People | 3 | 5* | 1 |
| Face Recognition | 3 | 5* | 1 |

---

## Future Work

- **Live camera deployment** — validate in real multi-student exam sessions
- **User authentication** — registration and login system for students and instructors
- **Cloud deployment** — Dockerized server for institutional hosting
- **Adaptive thresholds** — personalized calibration per student to reduce false positives
- **Larger evaluation dataset** — diverse subjects, lighting conditions, and camera qualities

---

## License

This project was developed as an academic special project at KMITL. Source code is open for reference and educational use.

---

*Special Project — Bachelor of Science, Digital Technology and Integrated Innovation*
*King Mongkut's Institute of Technology Ladkrabang · Academic Year 2025*

**Chiewchan Sumalares** - System Architect & Developer

## Examinee View
<img width="1196" height="703" alt="Examinees view" src="https://github.com/user-attachments/assets/986910cd-45ad-4e6b-b564-af012c3ad45b" />

## Examiner View
<img width="1919" height="944" alt="Home" src="https://github.com/user-attachments/assets/bbaae060-c337-4c32-a22b-fe3e4bded136" />
<img width="1411" height="699" alt="Evidence Log" src="https://github.com/user-attachments/assets/64c1685b-ac4e-48d8-8ec7-3a12439e7e66" />
