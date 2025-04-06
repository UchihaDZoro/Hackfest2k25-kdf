import cv2
import numpy as np
from ultralytics import YOLO

# ---------------- CONFIG ----------------
CAM_INDEX = 0                           # 0 = default webcam, or change for external cam
MODEL_PATH = "yolov8n.pt"               # YOLO model
FRAME_RESIZE = (640, 480)               # Resize for performance
HEAT_DECAY = 0.9                        # Controls how fast heat fades
CONF_THRESHOLD = 0.4                    # YOLO confidence threshold
# ----------------------------------------

# Load YOLO model
model = YOLO(MODEL_PATH)

# Start webcam
cap = cv2.VideoCapture(CAM_INDEX)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_RESIZE[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_RESIZE[1])

if not cap.isOpened():
    print("❌ Failed to access webcam.")
    exit()

# Create heatmap accumulator
heatmap_accumulator = np.zeros(FRAME_RESIZE[::-1], dtype=np.float32)

print("🔥 Live heatmap started... Press 'q' to stop.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize for processing
    frame = cv2.resize(frame, FRAME_RESIZE)

    # Run YOLO detection
    results = model(frame, verbose=False)[0]

    # Apply heat to detected areas
    for box in results.boxes:
        conf = float(box.conf[0])
        if conf < CONF_THRESHOLD:
            continue
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        # Draw a filled white rectangle in the heatmap
        cv2.rectangle(heatmap_accumulator, (x1, y1), (x2, y2), 255, -1)

    # Apply decay to allow fading of older detections
    heatmap_accumulator *= HEAT_DECAY
    heatmap_accumulator = np.clip(heatmap_accumulator, 0, 255)

    # Normalize and convert to 8-bit grayscale
    normalized_heatmap = cv2.normalize(heatmap_accumulator, None, 0, 255, cv2.NORM_MINMAX)
    heatmap_uint8 = normalized_heatmap.astype(np.uint8)

    # Convert to colormap (yellow for hot, greenish for cold)
    colored_heatmap = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)

    # Resize again to ensure match
    colored_heatmap = cv2.resize(colored_heatmap, (frame.shape[1], frame.shape[0]))

    # Blend heatmap on top of original frame
    blended = cv2.addWeighted(frame, 0.5, colored_heatmap, 0.5, 0)

    # Show result
    cv2.imshow("📍 Live Heatmap", blended)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("✅ Done.")
