# EduSync AI

## Intelligent Attendance Verification and Academic Resource Distribution System

EduSync AI is an AI-powered attendance verification platform designed for educational institutions. The system automates attendance marking using classroom camera feeds, face recognition, timetable integration, and intelligent scheduling.

Instead of continuously processing video streams, EduSync AI performs scheduled attendance scans during a class session, significantly reducing computational requirements while maintaining attendance accuracy.

The project is being developed as a scalable SaaS solution that can integrate with existing college databases and ERP systems.

---

# Project Overview

Traditional attendance systems suffer from several limitations:

* Manual attendance consumes classroom time.
* QR-code systems can be exploited through sharing.
* Biometric systems require dedicated hardware.
* Attendance records are often disconnected from existing academic systems.
* Institutions lack centralized attendance automation.

EduSync AI addresses these challenges by integrating:

* Classroom RTSP camera streams
* Face recognition
* Timetable management
* Student database integration
* Automated attendance scheduling

---

# Core Concept

Attendance is **not calculated continuously**.

For every scheduled class:

1. Active timetable entry is identified.
2. Corresponding classroom RTSP stream is selected.
3. Student embeddings for that class are loaded.
4. Four randomized attendance scans are executed.
5. Students detected in at least three scans are marked present.
6. Attendance records are stored and exposed through the web portal.

This approach dramatically reduces GPU usage compared to continuously processing video feeds.

---

# Current Development Status

## Completed

### AI Pipeline

* Webcam integration using OpenCV
* YOLOv8 Pose Detection
* InsightFace integration
* CUDA GPU acceleration
* ONNX model testing
* Face detection experiments
* Face recognition experiments
* Student registration workflow
* Embedding generation and storage

### Testing Utilities

Implemented prototype scripts:

```text
test_camera.py
test_detection.py
test_scan.py
test_scheduler.py
register_test.py
pose_detection.py
pose_ironman.py
```

### Infrastructure

* Python virtual environment setup
* Project folder structure
* Environment variable management
* Embedding storage system
* Temporary crop storage
* Scheduler prototype

---

# Current Project Structure

```text
edusync_ai/
│
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   └── models/
│
├── data/
│   ├── embeddings/
│   ├── student_photos/
│   └── temp_crops/
│
├── scripts/
│   ├── export_yolo_onnx.py
│   └── test_insightface_onnx.py
│
├── pose_detection.py
├── pose_ironman.py
├── register_test.py
├── test_camera.py
├── test_detection.py
├── test_scan.py
├── test_scheduler.py
│
├── gpu.py
├── requirements.txt
├── .env
│
├── yolov8n-pose.pt
└── yolov8n-pose.onnx
```

---

# System Architecture

```text
┌─────────────────────────────────────────────────────┐
│                     EDUSYNC AI                      │
│      Intelligent Attendance Verification System    │
└─────────────────────────────────────────────────────┘

                     ┌─────────────┐
                     │  College DB │
                     └──────┬──────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼

┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Student Data │   │ Timetables   │   │ Room Mapping │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                          ▼

            ┌─────────────────────────┐
            │   Attendance Engine     │
            │                         │
            │ • Active Class Lookup   │
            │ • Scan Scheduling       │
            │ • Batch Loading         │
            │ • Session Management    │
            └───────────┬─────────────┘
                        │
        ┌───────────────┼───────────────┐
        │                               │
        ▼                               ▼

┌─────────────────┐          ┌─────────────────┐
│ RTSP Classroom  │          │ Student         │
│ Camera Stream   │          │ Embeddings      │
└────────┬────────┘          └────────┬────────┘
         │                            │
         └────────────┬───────────────┘
                      ▼

           ┌──────────────────────┐
           │ Face Recognition AI  │
           │     (InsightFace)    │
           └──────────┬───────────┘
                      │
                      ▼

           ┌──────────────────────┐
           │ Attendance Decision  │
           └──────────┬───────────┘
                      │
                      ▼

           ┌──────────────────────┐
           │ Attendance Database  │
           └──────────────────────┘
```

---

# Attendance Workflow

## Example Scenario

Class:

```text
B.Tech CSE FSD Section A
Subject: Data Structures
Room: A109
Time: 09:00 AM - 10:00 AM
```

The system automatically:

* Identifies the active timetable entry.
* Loads the student list for the class.
* Loads face embeddings for those students.
* Retrieves the RTSP stream associated with the classroom.
* Schedules four randomized scans.
* Processes attendance.
* Saves results to the database.

---

# Attendance Processing Workflow

```text
┌─────────────────────────────┐
│ Class Starts (9:00 AM)      │
└──────────────┬──────────────┘
               │
               ▼

┌─────────────────────────────┐
│ Find Active Timetable Entry │
└──────────────┬──────────────┘
               │
               ▼

┌─────────────────────────────┐
│ Identify Classroom          │
│ Example: A109              │
└──────────────┬──────────────┘
               │
               ▼

┌─────────────────────────────┐
│ Load Student List           │
│ B.Tech CSE FSD Sec-A        │
└──────────────┬──────────────┘
               │
               ▼

┌─────────────────────────────┐
│ Load Face Embeddings        │
└──────────────┬──────────────┘
               │
               ▼

┌─────────────────────────────┐
│ Generate 4 Random Scans     │
│ Within Class Duration       │
└──────────────┬──────────────┘
               │
               ▼

     ┌─────────────────────┐
     │ Scan #1             │
     └─────────┬───────────┘
               ▼

     ┌─────────────────────┐
     │ Scan #2             │
     └─────────┬───────────┘
               ▼

     ┌─────────────────────┐
     │ Scan #3             │
     └─────────┬───────────┘
               ▼

     ┌─────────────────────┐
     │ Scan #4             │
     └─────────┬───────────┘
               ▼

┌─────────────────────────────┐
│ Count Student Detections    │
└──────────────┬──────────────┘
               │
               ▼

┌─────────────────────────────┐
│ Detected >= 3 Times ?       │
└───────┬─────────────┬───────┘
        │ YES         │ NO
        ▼             ▼

┌──────────────┐   ┌──────────────┐
│ PRESENT      │   │ ABSENT       │
└──────┬───────┘   └──────┬───────┘
       │                  │
       └────────┬─────────┘
                ▼

      ┌──────────────────┐
      │ Save Attendance  │
      └──────────────────┘
```

---

# Scan Scheduling Logic

Attendance scans are randomized within the lecture duration.

Example:

```text
Class Duration

09:00 AM ───────────────────────► 10:00 AM

Possible Scan Schedule

09:07 AM
09:18 AM
09:36 AM
09:54 AM
```

Rules:

* First scan occurs after class begins.
* Last scan occurs before class ends.
* Scan times are randomized.
* Students cannot predict attendance checks.

Default attendance rule:

```text
Detected in 3 or more scans
          ↓
     PRESENT

Detected in fewer than 3 scans
          ↓
      ABSENT
```

---

# Student Registration Workflow

Before attendance can be processed, every student must be registered.

The registration system generates a unique face embedding for each student.

```text
┌──────────────────────────────┐
│ Student Records Imported     │
│ From College Database        │
└──────────────┬───────────────┘
               │
               ▼

┌──────────────────────────────┐
│ Student Photograph Available │
└──────────────┬───────────────┘
               │
               ▼

┌──────────────────────────────┐
│ register_test.py             │
└──────────────┬───────────────┘
               │
               ▼

┌──────────────────────────────┐
│ Detect Face                  │
└──────────────┬───────────────┘
               │
               ▼

┌──────────────────────────────┐
│ Generate Embedding Vector    │
│ (InsightFace)                │
└──────────────┬───────────────┘
               │
               ▼

┌──────────────────────────────┐
│ Store Embedding              │
│ data/embeddings/             │
└──────────────┬───────────────┘
               │
               ▼

┌──────────────────────────────┐
│ Student Ready For Attendance │
└──────────────────────────────┘
```

---

# Database Integration Workflow

Institutions can connect their existing databases or ERP systems.

```text
┌────────────────────┐
│ College Database   │
└─────────┬──────────┘
          │
          ▼

┌────────────────────┐
│ EduSync AI         │
└─────────┬──────────┘
          │
          ├── Student Data
          ├── Timetable Data
          ├── Faculty Data
          ├── Classroom Data
          └── Batch Data
```

The imported data is used to:

* Identify active classes.
* Identify enrolled students.
* Load attendance sessions.
* Map rooms to RTSP streams.
* Generate attendance records.

---

# Planned Web Portal Modules

## Super Admin

* Institution management
* Database connection management
* Tenant onboarding
* Global analytics

## College Admin

* Student management
* Room management
* RTSP configuration
* Timetable management

## Faculty

* Attendance viewing
* Attendance overrides
* Attendance reports
* Session monitoring

---

# Future Roadmap

* Multi-tenant SaaS architecture
* PostgreSQL integration
* FastAPI production APIs
* RTSP camera management
* Attendance dashboard
* Analytics engine
* Attendance reports
* Docker deployment
* Dedicated AI server deployment
* Academic Resource Distribution Module
* ERP integration support

---

# Technology Stack

## AI & Computer Vision

* OpenCV
* InsightFace
* ONNX Runtime
* YOLOv8 Pose

## Backend

* Python
* FastAPI (planned)

## Database

* PostgreSQL (planned)

## Frontend

* React (in development)

## Deployment

* Docker (planned)

---

# Current Status

**Prototype Development Phase**

Completed:

✅ Face Detection
✅ Face Registration
✅ Embedding Generation
✅ GPU Acceleration
✅ Scheduler Prototype
✅ ONNX Testing
✅ Recognition Pipeline Experiments

In Progress:

🚧 Attendance Automation
🚧 Database Integration
🚧 RTSP Integration
🚧 Backend API Development
🚧 Web Portal Development

---

Developed by:

* Anant Kumar
* Rohan Vashisht
* Yug Verma
* Vasu Aggarwal

K.R. Mangalam University
B.Tech CSE (AI/ML, FSD)
