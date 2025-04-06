import cv2
import numpy as np
from ultralytics import YOLO

# ---------------- CONFIG ----------------
YOLO_MODEL_PATH = "yolov8n.pt"
VIDEO_PATH = "D:\codes\python\youtube_WvhYuDvH17I_1280x720_h264.mp4"  # Change to your video path
FRAME_RESIZE = (640, 480)
# ----------------------------------------

# Load YOLO model
model = YOLO(YOLO_MODEL_PATH)

# Define object classes of interest
INTEREST_CLASSES = [0, 1, 2, 3, 5, 7]  # person, bicycle, car, motorcycle, bus, truck

# Open video
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print("❌ Couldn't open video.")
    exit()

print("🔥 Generating heatmap. Press 'q' to stop preview...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, FRAME_RESIZE)

    # Run detection
    results = model(frame)[0]

    # Create mask
    heatmap_mask = np.zeros_like(frame, dtype=np.uint8)

    # Draw yellow boxes (for detections)
    for box in results.boxes:
        cls = int(box.cls[0].item())
        if cls in INTEREST_CLASSES:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(heatmap_mask, (x1, y1), (x2, y2), (0, 255, 255), -1)  # Yellow

    # Assign green to background (non-detected regions)
    green_background = np.full_like(frame, (0, 255, 0))  # Green
    heatmap = np.where(heatmap_mask.any(axis=2, keepdims=True), heatmap_mask, green_background)

    # Overlay heatmap on frame
    blended = cv2.addWeighted(frame, 0.4, heatmap, 0.6, 0)

    cv2.imshow("Heatmap View", blended)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("✅ Heatmap generation complete.")
