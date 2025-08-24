# Face Recognition Security System 🔒

A real-time face recognition and intruder detection system built for **CODSOFT Internship** using Python and OpenCV.

Detects known faces and alerts on unknown intruders — like a smart security camera.

![Security Camera Screenshot](https://i.imgur.com/your-screenshot-link.jpg)  
*(Replace with your app screenshot)*

---

## 🎯 Features

- ✅ **Face Capture** – Save 60 images per user for training
- 🧠 **LBPH Face Recognition** – Uses OpenCV's Local Binary Patterns Histogram
- 🚨 **Intruder Detection** – Flags unknown faces in real-time
- 📸 **Auto-Save Snapshots** – Saves unknown face images
- 📊 **Confidence Threshold** – Adjustable recognition sensitivity
- 📂 **Clean Folder Structure** – Easy to understand and extend

---

## 🛠️ Tech Stack

- **Python 3.7+**
- **OpenCV** (`cv2`) – Face detection & recognition
- **NumPy** – Image processing
- **Haar Cascade** – Face detection
- **LBPH Recognizer** – Machine Learning model

---

## 📦 How to Run

### 1. Install Dependencies
```bash
pip install opencv-python numpy