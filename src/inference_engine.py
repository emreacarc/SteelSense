"""
Inference engine for steel defect detection using trained YOLOv8 model.
"""

import os
import logging
import numpy as np
import cv2
from PIL import Image
from ultralytics import YOLO
from config import BEST_MODEL_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SteelDefectDetector:
    """
    Steel defect detection class using YOLOv8 model.
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize the detector.
        
        Args:
            model_path: Path to the trained model. If None, uses default path from config.
        """
        self.model_path = model_path or BEST_MODEL_PATH
        self.model = None
    
    def load_model(self):
        """
        Load the trained YOLOv8 model.
        
        Raises:
            FileNotFoundError: If model file does not exist.
        """
        # Convert to string explicitly to avoid pathlib issues on Python 3.13
        model_path_str = str(self.model_path)
        
        if not os.path.exists(model_path_str):
            error_msg = f"Model file not found at: {model_path_str}. Please train the model first."
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            logger.info(f"Loading model from: {model_path_str}")
            self.model = YOLO(model_path_str)
            
            logger.info("Model loaded successfully.")
        except Exception as e:
            error_msg = f"Error loading model: {str(e)}"
            logger.error(error_msg)
            raise
    
    def predict(self, image, conf_threshold: float = 0.25):
        """
        Perform defect detection on an image.
        
        Args:
            image: Input image (PIL Image, numpy array, or file path)
            conf_threshold: Confidence threshold for detections (default: 0.25)
        
        Returns:
            tuple: (processed_image, detection_data)
                - processed_image: PIL Image with bounding boxes drawn
                - detection_data: List of dictionaries with detection information
        """
        if self.model is None:
            self.load_model()
        
        # Run inference
        results = self.model.predict(
            image,
            conf=conf_threshold,
            imgsz=640,
            verbose=False
        )
        
        # Correct class names mapping (NEU-DET dataset standard names)
        correct_class_names = {
            0: "Crazing",
            1: "Inclusion",
            2: "Patches",
            3: "Pitted Surface",
            4: "Rolled in Scale",
            5: "Scratches"
        }
        
        # Extract detection data and prepare for manual annotation
        detection_data = []
        result = results[0]
        
        # Convert image to numpy array for OpenCV operations
        if isinstance(image, Image.Image):
            img_array = np.array(image)
        elif isinstance(image, np.ndarray):
            img_array = image.copy()
        else:
            img_array = np.array(Image.open(image))
        
        # Convert RGB to BGR for OpenCV
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        else:
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
        
        # Colors for different classes (BGR format for OpenCV)
        colors = [
            (0, 255, 0),      # Crazing - Green
            (255, 0, 0),      # Inclusion - Blue
            (0, 0, 255),      # Patches - Red
            (255, 255, 0),    # Pitted Surface - Cyan
            (255, 0, 255),    # Rolled in Scale - Magenta
            (0, 255, 255),    # Scratches - Yellow
        ]
        
        if result.boxes is not None and len(result.boxes) > 0:
            boxes = result.boxes
            for i in range(len(boxes)):
                box = boxes[i]
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                bbox = box.xyxy[0].cpu().numpy()
                
                # Get correct class name for display
                if cls in correct_class_names:
                    class_name = correct_class_names[cls]
                else:
                    class_name = f"Class_{cls}"
                
                detection_data.append({
                    "class_name": class_name,
                    "confidence": conf,
                    "bbox": bbox.tolist()
                })
                
                # Draw bounding box
                x1, y1, x2, y2 = map(int, bbox)
                color = colors[cls % len(colors)]
                cv2.rectangle(img_bgr, (x1, y1), (x2, y2), color, 2)
                
                # Draw label with class name and confidence
                label = f"{class_name} {conf:.2f}"
                (text_width, text_height), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                )
                cv2.rectangle(
                    img_bgr,
                    (x1, y1 - text_height - baseline - 5),
                    (x1 + text_width, y1),
                    color,
                    -1
                )
                cv2.putText(
                    img_bgr,
                    label,
                    (x1, y1 - baseline - 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )
        
        # Convert back to RGB for PIL
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        processed_image = Image.fromarray(img_rgb)
        
        return processed_image, detection_data

