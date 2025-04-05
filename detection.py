from ultralytics import YOLO
import torch
import time
import os

class Detector:
    def __init__(self, model_path_rgb, model_path_thermal, device='cpu', config=None):
        self.device = device
        self.config = config
        self.model_rgb = self._load_model(model_path_rgb)
        # Potentially load a different model optimized for thermal
        self.model_thermal = self._load_model(model_path_thermal)
        if self.model_rgb:
             self.class_names = self.model_rgb.names
        elif self.model_thermal:
             self.class_names = self.model_thermal.names
        else:
             self.class_names = {0: 'object'} # Default fallback

        print(f"Detector initialized on device: {self.device}")
        print(f"Using RGB model: {model_path_rgb}")
        print(f"Using Thermal model: {model_path_thermal}")


    def _load_model(self, model_path):
        if not model_path or not os.path.exists(model_path):
             print(f"Warning: Model file not found at {model_path}. Detection will be skipped for this type.")
             return None
        try:
            # TODO: Add logic here to load ONNX or TensorRT models if path ends with .onnx or .engine
            # Example for ONNX (requires onnxruntime):
            # if model_path.endswith('.onnx'):
            #     import onnxruntime
            #     sess_options = onnxruntime.SessionOptions()
            #     # Add TensorRT provider options if applicable
            #     providers = ['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider']
            #     model = onnxruntime.InferenceSession(model_path, sess_options=sess_options, providers=providers)
            #     print(f"Loaded ONNX model: {model_path} with providers: {model.get_providers()}")
            #     return model # Need to adapt predict method for ONNX

            # Example for PyTorch (.pt) using Ultralytics
            model = YOLO(model_path)
            model.to(self.device)
            print(f"Loaded PyTorch YOLO model: {model_path}")
            return model
        except Exception as e:
            print(f"Error loading model {model_path}: {e}")
            return None

    def predict(self, frame, is_thermal=False):
        """Runs detection on a single frame."""
        model = self.model_thermal if is_thermal else self.model_rgb
        if model is None:
            return [], 0.0 # No detections if model isn't loaded

        conf = self.config['processing']['confidence_threshold']
        iou = self.config['processing']['iou_threshold']
        classes = self.config['processing']['detection_classes']
        latency = 0.0

        try:
            start_time = time.perf_counter()

            # --- Perform Inference ---
            # Adapt based on model type (PyTorch/ONNX/TensorRT)
            if isinstance(model, YOLO): # Ultralytics YOLO
                results = model.predict(frame, conf=conf, iou=iou, classes=classes, verbose=False, device=self.device)
                # Process results: ultralytics returns a list, take first element
                detections = results[0].boxes.data.cpu().numpy() # xyxy, conf, cls
            # elif isinstance(model, onnxruntime.InferenceSession):
                # Preprocess frame for ONNX
                # input_name = model.get_inputs()[0].name
                # output_names = [output.name for output in model.get_outputs()]
                # preprocessed_frame = preprocess_for_onnx(frame) # Implement this function
                # onnx_detections_raw = model.run(output_names, {input_name: preprocessed_frame})
                # detections = postprocess_onnx_output(onnx_detections_raw) # Implement this function
            else:
                 print("Warning: Unsupported model type for prediction.")
                 detections = []


            end_time = time.perf_counter()
            latency = (end_time - start_time) * 1000 # Latency in ms

            return detections, latency

        except Exception as e:
            print(f"Error during detection: {e}")
            return [], latency # Return empty list on error