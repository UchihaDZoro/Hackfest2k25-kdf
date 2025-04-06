import cv2
import numpy as np
import gc
import sys
import os

# Read input and output path from CLI args
input_path = sys.argv[1]
output_path = sys.argv[2]

# Ensure output directory exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

print(f"Processing video: {input_path}")
print(f"Output will be saved to: {output_path}")

# Open the video
cap = cv2.VideoCapture(input_path)

if not cap.isOpened():
    print("Error: Cannot open input video")
    sys.exit(1)

# Resize and preprocessing settings
resize_width, resize_height = 640, 360
fgbg = cv2.createBackgroundSubtractorMOG2(history=200, varThreshold=25, detectShadows=True)
heatmap_accum = np.zeros((resize_height, resize_width), dtype=np.float32)

fps = cap.get(cv2.CAP_PROP_FPS)
if not fps or fps <= 0:
    fps = 20  # fallback
print(f"FPS: {fps}")

frame_count = 0
max_frames = 300

# Prepare output writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (resize_width, resize_height))

if not out.isOpened():
    print("Error: Cannot open VideoWriter")
    cap.release()
    sys.exit(1)

while cap.isOpened() and frame_count < max_frames:
    ret, frame = cap.read()
    if not ret:
        print("End of stream or read error")
        break

    frame = cv2.resize(frame, (resize_width, resize_height))
    fgmask = fgbg.apply(frame)
    heatmap_accum += (fgmask > 0).astype(np.float32)

    normalized_heatmap = cv2.normalize(heatmap_accum, None, 0, 255, cv2.NORM_MINMAX)
    colored_heatmap = cv2.applyColorMap(normalized_heatmap.astype(np.uint8), cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(frame, 0.7, colored_heatmap, 0.3, 0)

    out.write(overlay)
    frame_count += 1

    del frame, fgmask, normalized_heatmap, colored_heatmap, overlay
    gc.collect()

cap.release()
out.release()
gc.collect()

# Final check
if os.path.exists(output_path):
    size = os.path.getsize(output_path)
    print(f"DONE: Video saved. Size: {size} bytes")
    if size < 1000:
        print("Warning: Output file is too small — may be corrupted.")
else:
    print("Output video not created!")
