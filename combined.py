import cv2
from ultralytics import YOLO
from inference_sdk import InferenceHTTPClient

# ---------------- CONFIG ----------------
YOLO_MODEL_PATH = "yolov8n.pt"  # YOLO model for person and vehicle detection
FRAME_RESIZE = (640, 480)

# Roboflow Inference Client
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="tm3sZ8ebG8ZjGyKa8nZV"
)
ROBOFLOW_MODEL_ID = "drones_new/3"
# ----------------------------------------

# Define class IDs (COCO dataset)
PERSON_CLASS = 0
VEHICLE_CLASSES = [2, 3, 5, 7]   # Car, Motorcycle, Bus, Truck

# Load the YOLOv8 model
person_vehicle_model = YOLO(YOLO_MODEL_PATH)

# Setup webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Unable to access webcam.")
    exit()

print("🚀 Real-time Combined Detection started. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Failed to grab frame.")
        break

    frame = cv2.resize(frame, FRAME_RESIZE)

    # --- YOLOv8 Detection for Person and Vehicle ---
    yolo_results = person_vehicle_model(frame)
    for result in yolo_results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = box.conf[0].item()
            cls = int(box.cls[0].item())
            label = person_vehicle_model.names[cls]
            # Person detection
            if cls == PERSON_CLASS and conf > 0.5:
                color = (0, 255, 0)  # Green
                text = f"Person {conf:.2f}"
            # Vehicle detection
            elif cls in VEHICLE_CLASSES and conf > 0.4:
                color = (255, 165, 0)  # Orange
                text = f"{label} {conf:.2f}"
            else:
                continue
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, text, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # --- Roboflow Drone Detection ---
    try:
        response = CLIENT.infer(frame, model_id=ROBOFLOW_MODEL_ID)
        predictions = response["predictions"]
    except Exception as e:
        print("❌ Drone prediction error:", e)
        predictions = []

    for obj in predictions:
        x, y = int(obj["x"]), int(obj["y"])
        w, h = int(obj["width"]), int(obj["height"])
        conf = float(obj["confidence"])
        # Draw drone box in red
        x1 = x - w // 2
        y1 = y - h // 2
        x2 = x + w // 2
        y2 = y + h // 2
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(frame, f"Drone {conf:.2f}", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # --- Display Frame ---
    cv2.imshow("🚀 Combined Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
print("✅ Detection stopped.")
