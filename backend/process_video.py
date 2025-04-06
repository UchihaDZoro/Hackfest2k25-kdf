import cv2
import numpy as np
import gc
import sys
import os
import time

# ---- Utility ----
def log(msg, level="INFO"):
    print(f"[{level}] {msg}")

# ---- Argument Parsing ----
if len(sys.argv) < 3:
    log("Usage: python process_video.py <input_path> <output_path>", "ERROR")
    sys.exit(1)

input_path = sys.argv[1]
output_path = sys.argv[2]
print(input_path)
print(output_path)
# ---- Validate Paths ----
if not os.path.isfile(input_path):
    log(f"Input file does not exist: {input_path}", "ERROR")
    sys.exit(1)

os.makedirs(os.path.dirname(output_path), exist_ok=True)

log(f"Input video: {input_path}")
log(f"Output will be saved to: {output_path}")

# ---- Open Input Video ----
cap = cv2.VideoCapture(input_path)
if not cap.isOpened():
    log("Cannot open input video", "ERROR")
    sys.exit(1)

# ---- Video Processing Config ----
resize_width, resize_height = 640, 360
fgbg = cv2.createBackgroundSubtractorMOG2(history=200, varThreshold=25, detectShadows=True)
heatmap_accum = np.zeros((resize_height, resize_width), dtype=np.float32)

fps = cap.get(cv2.CAP_PROP_FPS)
fps = fps if fps and fps > 0 else 20  # fallback
log(f"FPS detected: {fps}")

# ---- Setup Output Video Writer ----
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (resize_width, resize_height))

if not out.isOpened():
    log("Cannot open output VideoWriter", "ERROR")
    cap.release()
    sys.exit(1)

# ---- Frame Processing Loop ----
frame_count = 0
max_frames = 300

log("Processing video frames...")
while cap.isOpened() and frame_count < max_frames:
    ret, frame = cap.read()
    if not ret:
        log("Stream ended or failed to read frame", "WARN")
        break

    # Resize and apply background subtraction
    frame = cv2.resize(frame, (resize_width, resize_height))
    fgmask = fgbg.apply(frame)
    heatmap_accum += (fgmask > 0).astype(np.float32)

    # Create heatmap overlay
    normalized_heatmap = cv2.normalize(heatmap_accum, None, 0, 255, cv2.NORM_MINMAX)
    colored_heatmap = cv2.applyColorMap(normalized_heatmap.astype(np.uint8), cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(frame, 0.7, colored_heatmap, 0.3, 0)

    out.write(overlay)
    frame_count += 1

    # Memory cleanup
    del frame, fgmask, normalized_heatmap, colored_heatmap, overlay
    gc.collect()

# ---- Finalization ----
cap.release()
out.release()
gc.collect()

# ---- Output Validation ----
if os.path.exists(output_path):
    size = os.path.getsize(output_path)
    if size < 1000:
        log("Output video seems too small — possibly corrupted.", "WARN")
    log(f"DONE: Video processed successfully. File size: {size} bytes")
    sys.exit(0)
else:
    log("Output video not created!", "ERROR")
    sys.exit(1)
