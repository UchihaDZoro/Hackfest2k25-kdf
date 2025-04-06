🛡️ AI-Powered Border Surveillance System
An end-to-end AI-driven prototype for intelligent border surveillance, featuring real-time object detection, behavioral analysis, edge deployment on Raspberry Pi, and live threat alerting via a web dashboard and SMS.

📁 Project Structure
File/Folder	Description
main.py	Main entry point to launch the full pipeline.
alerting.py	Triggers alerts via Twilio when threats are detected.
behavior_analysis.py	Behavioral profiling based on motion patterns.
detection.py	Object detection using YOLOv8/YOLOv11 (NCNN on Pi).
tracking.py	Tracks detected objects across frames.
thermalbehaviour.ipynb	Handles thermal + RGB behavior analysis.
live-model.ipynb	Notebook for real-time object detection demo.
lstm_model.pth	Trained LSTM model for basic behavior prediction.
lstm_behavior_extended.pth	Enhanced version of the LSTM behavior model.
rpi_yolov11_*	Scripts for running YOLOv11 inference on Raspberry Pi.
canvas.py, utils.py	Helper functions and drawing utilities.
segmentation.py	Object/person segmentation module.
input_manager.py	Handles multiple video streams or feeds.
labelimg.py, labeling.sh	Tools for dataset labeling and annotation.
config.yaml, data.txt	Config and data settings.
requirements.txt	Python dependencies.
video-processed.ipynb	Annotated output and demo of processed surveillance video.
🚀 Key Features
✅ Real-time object detection (YOLOv8/YOLOv11)

👣 Motion tracking and behavioral profiling (LSTM)

🔥 Fusion of thermal + RGB analysis

🧠 Risk heat map generation

🌐 Web-based dashboard (Streamlit/Flask)

📲 Instant SMS alerts (Twilio)

🍓 Edge testing on Raspberry Pi 4 (NCNN optimized)

⚙️ How to Run
Clone the repo and install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Run detection + tracking:

bash
Copy
Edit
python main.py
To test on Raspberry Pi using YOLOv11 NCNN:

bash
Copy
Edit
python rpi_yolov11_object_detection_on_custom_dataset.py
📊 Outputs
Live detection stream

Behavior flag logs

Risk heat map

SMS notifications

Dashboard with feed + analytics

🧠 Models Used
YOLOv8 for detection (PC)

YOLOv11 with NCNN for Pi edge deployment

LSTM for behavior analysis
