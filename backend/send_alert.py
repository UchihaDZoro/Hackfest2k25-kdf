from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import cv2
import numpy as np
import time
import socketio
from datetime import datetime
from flask import Flask, Response
from threading import Thread

# === Flask App for Webcam Stream ===
app = Flask(__name__)
output_frame = None

def gen_frames():
    global output_frame
    while True:
        if output_frame is None:
            continue
        _, buffer = cv2.imencode('.jpg', output_frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video1')
def video():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def run_flask():
    app.run(host='0.0.0.0', port=6924, debug=False, use_reloader=False)

# Start Flask in background
flask_thread = Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()
print("🌐 Flask server started at http://localhost:6924/video1")

# === Socket.IO Setup ===
sio = socketio.Client()

@sio.event
def connect():
    print("✅ Connected to alert server")

@sio.event
def disconnect():
    print("🔌 Disconnected from alert server")

@sio.event
def connect_error(data):
    print("❌ Connection failed:", data)

try:
    sio.connect('http://localhost:6969')  # change if hosted elsewhere
except Exception as e:
    print("Error connecting to server:", e)

# === YOLO + DeepSORT Setup ===
model = YOLO("yolov8n.pt")  # Use your trained model if any
tracker = DeepSort(max_age=30, n_init=3)
cap = cv2.VideoCapture(0)
print("🟢 Surveillance system started. Press 'Q' to stop.")

# Loitering Detection
loitering_time_threshold = 5
track_locations = {}

# Alert Function
def send_alert(message, label, confidence):
    alert = {
        "message": message,
        "camera_id": "CAM-001",
        "location": "Main Entrance - North Gate",
        "label": label,
        "confidence": round(confidence, 2),
        "detected_at": datetime.now().isoformat()
    }
    sio.emit('send_alert', alert)
    print("📨 Alert emitted:", alert["message"])

# === Main Loop ===
while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)[0]
    detections = []
    heatmap = np.zeros((frame.shape[0], frame.shape[1]), dtype=np.float32)
    current_time = time.time()

    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        label = model.names[cls]

        detections.append(([x1, y1, x2 - x1, y2 - y1], conf, label))
        heatmap[y1:y2, x1:x2] += conf

    tracks = tracker.update_tracks(detections, frame=frame)

    for track in tracks:
        if not track.is_confirmed():
            continue

        track_id = track.track_id
        ltrb = track.to_ltrb()
        label = track.get_det_class()
        x1, y1, x2, y2 = map(int, ltrb)
        center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2

        # Loitering
        if label == 'person':
            if track_id not in track_locations:
                track_locations[track_id] = {"pos": (center_x, center_y), "start_time": current_time}
            else:
                prev = track_locations[track_id]
                dist = np.linalg.norm(np.array((center_x, center_y)) - np.array(prev["pos"]))
                if dist < 30:
                    duration = current_time - prev["start_time"]
                    if duration > loitering_time_threshold:
                        msg = f"🚨 Loitering detected - ID {track_id}"
                        cv2.putText(frame, msg, (x1, y1 - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
                        send_alert("Loitering Detected", label, 1.0)
                        time.sleep(1)
                else:
                    track_locations[track_id] = {"pos": (center_x, center_y), "start_time": current_time}

        # Suspicious Object
        if label in ['knife', 'gun', 'bag']:
            msg = f"⚠ Suspicious Object: {label}"
            cv2.putText(frame, msg, (x1, y1 - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
            send_alert(f"Suspicious Object Detected: {label}", label, conf)
            time.sleep(1)

        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 100), 2)
        cv2.putText(frame, f"{label} ID:{track_id}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Heatmap overlay
    heatmap = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    heatmap_colored = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    final_frame = cv2.addWeighted(frame, 0.7, heatmap_colored, 0.3, 0)

    # Set frame for Flask streaming
    output_frame = final_frame.copy()

    cv2.imshow("🛡 Real-Time Surveillance", final_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
sio.disconnect()
