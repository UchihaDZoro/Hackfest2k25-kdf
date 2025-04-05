import yaml
import cv2
import numpy as np
import time

def load_config(config_path="config.yaml"):
    """Loads configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        print("Configuration loaded successfully.")
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}")
        return None
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return None

def draw_detections(frame, detections, class_names):
    """Draws bounding boxes and labels on the frame."""
    for det in detections:
        # Assuming det format: [x1, y1, x2, y2, conf, cls]
        if len(det) >= 6:
            x1, y1, x2, y2 = map(int, det[:4])
            conf = det[4]
            cls = int(det[5])
            label = f"{class_names.get(cls, 'Unknown')} {conf:.2f}"
            color = (0, 255, 0) # Green
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame

def draw_tracks(frame, tracks):
    """Draws bounding boxes and track IDs on the frame."""
    # Assuming tracks format: [x1, y1, x2, y2, track_id, conf, cls, ...] from tracker
    for track in tracks:
         if len(track) >= 5:
            x1, y1, x2, y2 = map(int, track[:4])
            track_id = int(track[4])
            # Optional: Get class/conf if available
            label = f"ID: {track_id}"
            color = (255, 0, 0) # Blue
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame

def draw_fence_zones(frame, zones):
    """Draws fence zones on the frame."""
    if zones:
        for zone in zones:
            pts = np.array(zone, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], isClosed=True, color=(0, 0, 255), thickness=2)
    return frame

# --- Add other utility functions as needed (e.g., coordinate transformations, heatmap generation) ---

class FPSLogger:
    """Calculates and logs FPS."""
    def __init__(self, update_interval=1.0): # Update every second
        self._start_time = None
        self._frame_count = 0
        self._update_interval = update_interval
        self._last_update_time = time.time()
        self._fps = 0.0

    def update(self):
        """Call this once per processed frame."""
        current_time = time.time()
        self._frame_count += 1

        if current_time - self._last_update_time >= self._update_interval:
            self._fps = self._frame_count / (current_time - self._last_update_time)
            self._frame_count = 0
            self._last_update_time = current_time
            # print(f"Current FPS: {self._fps:.2f}") # Optional: print directly

    def get_fps(self):
        """Get the latest calculated FPS."""
        return self._fps