from ultralytics import YOLO
import time

class Tracker:
    def __init__(self, config):
        self.config = config
        self.tracker_type = config['tracking']['tracker_type']
        # Ultralytics handles tracker initialization within the model object
        # We just need a YOLO model instance to access the track method
        # Using a dummy model load just to get access to the .track() method framework
        # The actual detection model is passed during the update call
        # NOTE: This is a slight workaround. A cleaner way might involve
        # directly using the underlying tracker classes if separated from YOLO.
        try:
            self._yolo_for_tracking = YOLO() # Minimal init
            print(f"Tracker initialized with type: {self.tracker_type}")
        except Exception as e:
             print(f"Error initializing tracker structure: {e}")
             self._yolo_for_tracking = None


    def update(self, frame, detections, detection_model_instance):
        """Updates the tracker with new detections."""
        tracks = []
        latency = 0.0
        if self._yolo_for_tracking is None:
             print("Tracker not initialized properly.")
             return tracks, latency

        if detection_model_instance is None:
             print("Detection model instance not provided to tracker.")
             return tracks, latency

        if len(detections) == 0:
            # Still call track with persist=True to maintain tracks without detections
             try:
                 start_time = time.perf_counter()
                 # Need to call track even with no detections to let the tracker predict next positions
                 # Pass the *original frame* and persist=True
                 results = detection_model_instance.track(frame, tracker=self.config['tracking']['tracker_config'], persist=True, verbose=False)
                 if results and results[0].boxes is not None and results[0].boxes.id is not None:
                    tracks = results[0].boxes.data.cpu().numpy() # xyxy, id, conf, cls
                 else:
                    tracks = [] # No active tracks remain
                 end_time = time.perf_counter()
                 latency = (end_time - start_time) * 1000
             except Exception as e:
                 print(f"Error during empty frame tracking update: {e}")
                 tracks = []
             return tracks, latency


        # When detections are present, pass them to the track method
        try:
            start_time = time.perf_counter()
            # We use the *detection model instance* passed in, as track combines detection+tracking
            # The `detections` are implicitly used by the model's predict cache if called just before.
            # We pass the frame again here. `persist=True` links tracks across calls.
            # Re-running predict inside track isn't ideal for performance if predict was just called.
            # Ideally, ultralytics would allow passing detections directly to track.
            # For now, we rely on the internal mechanism or re-run prediction implicitly.
            # Let's use the model's built-in tracking which re-runs detection if needed.

            # Pass relevant config to track method if possible (check ultralytics docs)
            results = detection_model_instance.track(
                frame,
                conf=self.config['processing']['confidence_threshold'],
                iou=self.config['processing']['iou_threshold'],
                classes=self.config['processing']['detection_classes'],
                tracker=self.config['tracking']['tracker_config'], # Specify tracker type
                persist=True, # Crucial for linking tracks between frames
                verbose=False,
                device=detection_model_instance.device
            )

            end_time = time.perf_counter()
            latency = (end_time - start_time) * 1000 # This includes detection time again

            if results and results[0].boxes is not None and results[0].boxes.id is not None:
                 # Extract boxes with IDs: xyxy, id, conf, cls
                 tracks = results[0].boxes.data.cpu().numpy()
            else:
                 tracks = []

            return tracks, latency

        except Exception as e:
            print(f"Error during tracking update: {e}")
            return [], latency