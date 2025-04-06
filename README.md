# 🛡️ AI-Powered Border Surveillance System

An end-to-end AI-driven prototype for smart border monitoring using object detection, behavior analysis, and edge deployment. Designed for real-time surveillance, it runs on both standard and constrained hardware like Raspberry Pi.

---

## 📌 Features

- 🔍 **Real-Time Object Detection** using YOLOv8 & YOLOv11 (NCNN)
- 🧠 **Behavioral Analysis** with motion tracking and LSTM profiling
- 🌡️ **Thermal + RGB Fusion** (if available)
- 📍 **Dynamic Risk Heat Map** generation
- 📡 **Edge Inference on Raspberry Pi 4**
- 🌐 **Web Dashboard** (Streamlit/Flask)
- 📲 **SMS Alert System** (Twilio API)
- 🎥 **Multi-Camera Feed Simulation**

---

## 🗂️ Project Structure

| File/Folder                          | Description |
|-------------------------------------|-------------|
| `main.py`                           | Main script to launch the surveillance system |
| `alerting.py`                       | Triggers alerts via Twilio |
| `behavior_analysis.py`              | LSTM-based behavior profiling |
| `detection.py`                      | Runs YOLO detection (PC version) |
| `tracking.py`                       | Tracks detected entities |
| `thermalbehaviour.ipynb`            | Analyzes thermal + RGB behavior |
| `live-model.ipynb`                  | Real-time detection demo notebook |
| `rpi_yolov11_*`                     | Object detection/segmentation scripts optimized for Pi |
| `lstm_model.pth` / `lstm_behavior_extended.pth` | Trained LSTM behavior models |
| `canvas.py`, `utils.py`             | Helper functions for drawing/tracking |
| `segmentation.py`                   | Person/vehicle segmentation logic |
| `labelimg.py`, `labeling.sh`        | Dataset annotation tools |
| `input_manager.py`                  | Feed manager for multiple video streams |
| `config.yaml`, `data.txt`           | Configuration files |
| `requirements.txt`                  | Python dependencies |
| `video-processed.ipynb`             | Annotated demo of detection results |

---

## ⚙️ Setup & Run

1. Clone the repo:

```bash
git clone <your-repo-url>
cd <repo-folder>
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run main detection pipeline:

```bash
python main.py
```

4. For Raspberry Pi edge test (YOLOv11):

```bash
python rpi_yolov11_object_detection_on_custom_dataset.py
```

---

## 🧠 Model Stack

- YOLOv8 for object detection on PC
- YOLOv11 + NCNN module on Raspberry Pi
- LSTM for activity recognition
- OpenCV for tracking and motion detection

---

## 📊 Outputs

- Live annotated video stream
- Real-time behavior alerts
- Risk heat map dashboard
- SMS alerts for high-risk detections
- Detection logs and tracking history

---

## 🏁 Goals

- ✅ Build a lightweight and scalable AI border surveillance prototype
- ✅ Achieve real-time performance on edge hardware
- ✅ Demonstrate multi-modal sensing and alert generation

---

