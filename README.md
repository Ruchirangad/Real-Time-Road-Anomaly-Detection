**Real-Time Road Anomaly Detection using DashCam & Raspberry Pi**

📌 Project Overview
This project presents a real-time Road Anomaly Detection System implemented using a Dash Camera / Raspberry Pi Camera and deployed on Raspberry Pi hardware.

The system detects:

🕳️ Potholes
🛣️ Road Cracks / Rough Surfaces
🚧 Speed Breakers
↩️ Vehicle Turns

⚠️ Collision Risk (via Time-To-Collision estimation)
The implementation operates in real time and has been tested on Delhi roads for over 2 hours of continuous video analysis, demonstrating stable performance in diverse traffic and lighting conditions.

🎯 Key Features
✅ Real-time video processing (30 FPS pipeline)
✅ Works with Pi Camera (libcamera GStreamer pipeline)
✅ Optical Flow–based collision prediction
✅ Variance-based texture analysis for pothole detection
✅ Edge + contour-based anomaly detection
✅ Adaptive Night Mode Enhancement (CLAHE + Hyper Gain)
✅ Temporal filtering to reduce false positives
✅ Lightweight and optimized for Raspberry Pi

🧠 System Architecture
Processing Pipeline
Video Capture (PiCam / DashCam)
Region of Interest Selection (Lower 60% of frame)
Image Enhancement (Optional Night Mode)
Texture Analysis (Variance Mapping)
Edge Detection (Canny)
Contour Analysis
Optical Flow Computation (Farneback)
Time-To-Collision Estimation
Classification & Display

🌙 Night Mode Enhancement
Night Mode applies:
HSV-based Hyper Gain
CLAHE (Contrast Limited Adaptive Histogram Equalization)
Brightness amplification

💻 Software Requirements
Python 3.8+
OpenCV (with GStreamer support)
NumPy
libcamera

Install dependencies:

sudo apt update
sudo apt install python3-opencv
pip3 install numpy

📂 Project Structure
Real-Time-Road-Anomaly-Detection/
│
├── road_anomaly_detection.py   # Main detection system
├── enhancement.py              # Night vision enhancement module
├── README.md                   # Project documentation

▶️ How to Run
Make sure both .py files are in the same directory.
python3 road_anomaly_detection.py
