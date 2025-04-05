import cv2
import time
import threading
from collections import deque

# Import project modules
from utils import load_config, draw_detections, draw_tracks, draw_fence_zones, FPSLogger
from detection import Detector
from tracking import Tracker
from segmentation import Segmenter # Placeholder
from behavior_analysis import BehaviorAnalyzer
from alerting import Alerter
from input_manager import InputManager


def process_stream(source_config, config):
    """Processes a single video stream."""
    stream_name = source_config.get('name', 'Unknown Stream')
    print(f"Initializing processing pipeline for: {stream_name}")

    # --- Initialize Components ---
    input_mgr = InputManager(source_config)
    if not input_mgr.is_running():
         print(f"Failed to initialize input for {stream_name}. Exiting thread.")
         return

    # Shared detector instance (consider if separate instances needed per stream type)
    # Ensure detector is initialized outside this function or passed carefully if shared
    # For simplicity here, assume detector handles model loading correctly based on config
    detector = Detector(
         config['model']['detection_model_rgb'],
         config['model']['detection_model_thermal'],
         config['model']['device'],
         config # Pass full config
     )
    tracker = Tracker(config)
    segmenter = Segmenter(config['model']['segmentation_model_path'], device=config['model']['device']) # Placeholder
    behavior_analyzer = BehaviorAnalyzer(config)
    alerter = Alerter(config)
    fps_logger = FPSLogger()

    # Frame skipping counter
    frame_counter = 0
    frame_skip = config['processing']['frame_skip']

    # Latency tracking
    latency_tracker = deque(maxlen=50) # Track latency over last 50 frames

    # Output video writer (optional)
    video_writer = None
    if config['visualization']['output_video_path']:
         # Define codec and create VideoWriter object
         # Get frame dimensions from first read frame (robust way)
         time.sleep(1) # Wait a bit for first frame
         first_frame = input_mgr.read()
         if first_frame is not None:
             h, w = first_frame.shape[:2]
             fourcc = cv2.VideoWriter_fourcc(*'mp4v') # or 'XVID'
             output_path = f"{config['visualization']['output_video_path']}_{stream_name}.mp4"
             video_writer = cv2.VideoWriter(output_path, fourcc, 15.0, (w, h)) # Adjust FPS as needed
             print(f"Initialized video writer for {stream_name} to {output_path}")
         else:
             print(f"Warning: Could not get frame dimensions for {stream_name}. Output video disabled.")


    print(f"Starting processing loop for: {stream_name}")
    while input_mgr.is_running():
        start_cycle_time = time.perf_counter()

        frame = input_mgr.read()
        if frame is None:
            # print(f"No frame received from {stream_name}, waiting...")
            time.sleep(0.05) # Wait briefly if no frame
            continue

        # --- Frame Skipping ---
        if frame_counter % (frame_skip + 1) != 0:
            frame_counter += 1
            continue # Skip processing this frame
        frame_counter += 1


        # --- 1. Detection ---
        is_thermal = input_mgr.is_thermal
        detections, detect_latency = detector.predict(frame, is_thermal=is_thermal)


        # --- 2. Tracking ---
        # Use appropriate model instance for tracking (RGB or Thermal)
        # Ultralytics track method might implicitly re-run detection. See tracking.py notes.
        # Pass the detector's model instance that was used for prediction.
        active_model = detector.model_thermal if is_thermal else detector.model_rgb
        tracks, track_latency = tracker.update(frame, detections, active_model) # Pass detections and frame


        # --- 3. Segmentation (Optional & Expensive) ---
        seg_masks = None
        seg_latency = 0.0
        # Example: Segment only tracked persons (class 0)
        boxes_to_segment = [t[:4] for t in tracks if len(t) >= 7 and int(t[6]) == 0] # Check class ID
        if config['visualization']['draw_segmentation'] and boxes_to_segment:
             # TODO: Implement efficient SAM call (load model once!)
             # seg_masks, seg_latency = segmenter.segment_objects(frame, boxes_to_segment)
             pass # Placeholder call


        # --- 4. Behavior Analysis ---
        behavior_alerts = behavior_analyzer.update(tracks)


        # --- 5. Alerting ---
        if behavior_alerts:
             # TODO: Get GPS coords if available (requires camera calibration/mapping)
             gps_coords = None # Placeholder
             for alert in behavior_alerts:
                 alerter.send_alert(alert, source_name=stream_name, gps_coords=gps_coords)


        # --- Performance Monitoring ---
        fps_logger.update()
        total_latency = (time.perf_counter() - start_cycle_time) * 1000
        latency_tracker.append(total_latency)
        avg_latency = sum(latency_tracker) / len(latency_tracker)


        # --- Visualization ---
        display_frame = frame.copy() # Work on a copy for display
        if config['visualization']['draw_detections'] and len(detections) > 0:
            display_frame = draw_detections(display_frame, detections, detector.class_names)
        if config['visualization']['draw_tracks'] and len(tracks) > 0:
            display_frame = draw_tracks(display_frame, tracks)
        if config['visualization']['draw_segmentation'] and seg_masks is not None:
             # Need to align masks with the boxes they were generated from if drawing per box
             # display_frame = segmenter.draw_masks(display_frame, seg_masks, boxes_to_segment)
             pass # Placeholder draw call
        if config['visualization']['draw_fence_zones']:
            display_frame = draw_fence_zones(display_frame, config['behavior_analysis']['fence_zones'])

        # Display FPS and Latency
        fps_text = f"FPS: {fps_logger.get_fps():.2f}"
        lat_text = f"Latency: {total_latency:.1f}ms (Avg: {avg_latency:.1f}ms)"
        cv2.putText(display_frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(display_frame, lat_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Check latency against requirement
        if avg_latency > config['processing']['max_latency_ms']:
             cv2.putText(display_frame, "LATENCY WARNING!", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


        # Save frame to output video
        if video_writer is not None:
             video_writer.write(display_frame)


        # Show video window
        if config['visualization']['show_video']:
            try:
                # Resize for display if needed
                # display_frame_resized = cv2.resize(display_frame, (960, 540))
                cv2.imshow(stream_name, display_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                     print(f"Quit signal received for {stream_name}. Stopping.")
                     input_mgr.stop() # Signal the input manager to stop
                     break # Exit processing loop
            except cv2.error as e:
                 print(f"OpenCV display error for {stream_name}: {e}. Maybe window closed?")
                 input_mgr.stop() # Stop if window is closed
                 break


        # Small delay to prevent pure CPU spin if processing is very fast
        # time.sleep(0.001)


    # --- Cleanup ---
    print(f"Exiting processing loop for: {stream_name}")
    if config['visualization']['show_video']:
        cv2.destroyWindow(stream_name)
    if video_writer is not None:
        video_writer.release()
        print(f"Closed video writer for {stream_name}")
    input_mgr.stop() # Ensure input manager is stopped
    print(f"Processing finished for: {stream_name}")


if __name__ == "__main__":
    print("Starting AI Border Surveillance System...")
    config = load_config("config.yaml")

    if config is None:
        print("Exiting due to configuration error.")
        exit(1)

    if not config.get('sources'):
        print("No input sources defined in config.yaml. Exiting.")
        exit(1)

    threads = []
    for source_cfg in config['sources']:
        thread = threading.Thread(target=process_stream, args=(source_cfg, config), daemon=True)
        threads.append(thread)
        thread.start()
        time.sleep(1) # Stagger thread starts slightly

    # Keep main thread alive while processing threads run
    try:
        while any(t.is_alive() for t in threads):
            time.sleep(1) # Check every second
    except KeyboardInterrupt:
        print("\nCtrl+C received. Stopping all streams...")
        # Signal all input managers to stop (handled within process_stream on exit/error)
        # We just need to wait for threads to join
    finally:
         print("Waiting for processing threads to finish...")
         for t in threads:
             # No explicit stop signal here, rely on input_mgr.stop() called inside thread
             t.join(timeout=5) # Wait for each thread to complete
         print("All processing threads finished.")
         cv2.destroyAllWindows()
         print("System shutdown complete.")