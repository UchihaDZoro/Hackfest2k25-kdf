import cv2
import time
import threading

class InputManager:
    def __init__(self, source_config):
        self.source_config = source_config
        self.source_type = source_config.get('type', 'webcam')
        self.uri = source_config.get('uri')
        self.name = source_config.get('name', f"{self.source_type}_{self.uri}")
        self.is_thermal = source_config.get('process_thermal', False)

        self.cap = None
        self.stopped = False
        self.frame = None
        self.lock = threading.Lock()
        self.thread = None
        self._connect()

        if self.cap and self.cap.isOpened():
             self.thread = threading.Thread(target=self._update, args=(), daemon=True)
             self.thread.start()
             print(f"Started video capture thread for: {self.name}")
        else:
             print(f"Failed to start video capture for: {self.name}")
             self.stopped = True


    def _connect(self):
        """Establishes connection to the video source."""
        retry_delay = 5 # seconds
        max_retries = 3
        attempts = 0
        while attempts < max_retries and self.cap is None:
            try:
                print(f"Attempting to connect to {self.name} ({self.uri})...")
                if self.source_type == 'webcam':
                    self.cap = cv2.VideoCapture(int(self.uri), cv2.CAP_V4L2) # Use V4L2 backend for linux often
                elif self.source_type == 'rtsp':
                     # Set environment variable for RTSP TCP transport if needed
                     # os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;tcp'
                     self.cap = cv2.VideoCapture(str(self.uri), cv2.CAP_FFMPEG)
                elif self.source_type == 'file':
                     self.cap = cv2.VideoCapture(str(self.uri))
                else:
                     print(f"Error: Unknown source type '{self.source_type}' for {self.name}")
                     return

                if not self.cap.isOpened():
                     raise IOError(f"Cannot open video source: {self.uri}")

                # Set properties (optional, might not work for all sources)
                # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                print(f"Successfully connected to {self.name}.")
                break # Exit loop on success

            except Exception as e:
                print(f"Error connecting to {self.name}: {e}")
                attempts += 1
                if self.cap:
                     self.cap.release()
                     self.cap = None
                if attempts < max_retries:
                     print(f"Retrying in {retry_delay} seconds...")
                     time.sleep(retry_delay)
                else:
                     print(f"Max retries reached for {self.name}. Connection failed.")
                     break


    def _update(self):
        """Internal method run by the thread to continuously read frames."""
        while not self.stopped:
            if self.cap is None or not self.cap.isOpened():
                 print(f"Connection lost for {self.name}. Attempting to reconnect...")
                 self._connect() # Attempt to reconnect
                 if self.cap is None: # Still failed after reconnect attempt
                      time.sleep(5) # Wait before retrying update loop
                      continue # Skip frame reading


            grabbed, frame = self.cap.read()
            if not grabbed:
                print(f"Warning: Could not grab frame from {self.name}. End of file or stream error?")
                if self.source_type == 'file': # If it's a file, stop when it ends
                     self.stop()
                     break
                else: # For streams, try to reconnect or wait
                     self.cap.release()
                     self.cap = None # Trigger reconnect logic
                     time.sleep(1) # Brief pause before reconnect attempt
                     continue

            with self.lock:
                self.frame = frame
        # Release capture object when stopped
        if self.cap:
            self.cap.release()
        print(f"Stopped video capture thread for: {self.name}")


    def read(self):
        """Returns the latest frame."""
        with self.lock:
            # Return a copy to prevent modification issues if frame is processed elsewhere
            frame_copy = self.frame.copy() if self.frame is not None else None
        return frame_copy


    def stop(self):
        """Signals the thread to stop."""
        print(f"Stopping video capture for: {self.name}")
        self.stopped = True
        if self.thread and self.thread.is_alive():
             self.thread.join(timeout=2) # Wait for thread to finish


    def is_running(self):
         return not self.stopped and self.thread and self.thread.is_alive()