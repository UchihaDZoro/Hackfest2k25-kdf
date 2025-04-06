import cv2
import tempfile
import os
from ultralytics import YOLO
from inference_sdk import InferenceHTTPClient

# ---------------- CONFIG ----------------
YOLO_MODEL_PATH = "yolov8n.pt"
ROBOFLOW_API_KEY = "tm3sZ8ebG8ZjGyKa8nZV"
ROBOFLOW_MODEL_ID = "drones_new/3"
FRAME_RESIZE = (640, 480)
VIDEO_PATH = r"D:\codes\python\youtube_vRDvEsKP9iM_1280x720_h264.mp4"
# ----------------------------------------

PERSON_CLASS = 0
VEHICLE_CLASSES = [2, 3, 5, 7]  # Car, Motorcycle, Bus, Truck

# Load YOLOv8 model
yolo_model = YOLO(YOLO_MODEL_PATH)

# Initialize Roboflow client
rf_client = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key=ROBOFLOW_API_KEY
)

# Open video
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print("❌ Unable to open video.")
    exit()

print("🚀 Combined Detection started. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ End of video or failed to grab frame.")
        break

    frame = cv2.resize(frame, FRAME_RESIZE)

    # --- YOLOv8 Detection ---
    results = yolo_model(frame)
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = box.conf[0].item()
            cls = int(box.cls[0].item())
            label = yolo_model.names[cls]

            if cls == PERSON_CLASS and conf > 0.5:
                color = (0, 255, 0)
                text = f"Person {conf:.2f}"
            elif cls in VEHICLE_CLASSES and conf > 0.4:
                color = (255, 165, 0)
                text = f"{label} {conf:.2f}"
            else:
                continue

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, text, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # --- Roboflow Drone Detection via temporary file ---
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmpfile:
            temp_path = tmpfile.name
            cv2.imwrite(temp_path, frame)

        prediction = rf_client.infer(temp_path, model_id=ROBOFLOW_MODEL_ID)

        os.remove(temp_path)  # Clean up
    except Exception as e:
        print("❌ Drone prediction error:", e)
        prediction = {"predictions": []}

    for obj in prediction["predictions"]:
        x, y = int(obj["x"]), int(obj["y"])
        w, h = int(obj["width"]), int(obj["height"])
        conf = float(obj["confidence"])
        x1 = x - w // 2
        y1 = y - h // 2
        x2 = x + w // 2
        y2 = y + h // 2
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(frame, f"Drone {conf:.2f}", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # --- Show Frame ---
    cv2.imshow("🚀 Combined Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("✅ Detection stopped.")
