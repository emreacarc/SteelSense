"""
Inference engine for steel defect detection using trained YOLOv8 model.
"""

import os
import sys
import logging
import numpy as np
from PIL import Image
from .config import BEST_MODEL_PATH

# Try to import cv2 with fallback handling
cv2 = None
try:
    import cv2
except ImportError:
    # If cv2 import fails, try to provide helpful error message
    logging.warning("cv2 (OpenCV) could not be imported. Will retry when ultralytics is imported.")

# Lazy import ultralytics to avoid early cv2 import issues
# YOLO will be imported when needed in load_model method

# Patch for Python 3.13 pathlib compatibility with PyTorch
# This fixes the UnsupportedOperation error when loading models with pathlib objects
# The issue occurs when models trained on Windows contain WindowsPath objects
# that cannot be unpickled on Linux (Streamlit Cloud)
import pickle
import torch

# Store original function
_original_torch_load = torch.load

class PatchedUnpickler(pickle.Unpickler):
    """
    Custom Unpickler that handles pathlib objects in pickled models.
    This prevents UnsupportedOperation errors when loading Windows-trained models on Linux.
    """
    def find_class(self, module, name):
        """
        Patched find_class that converts pathlib classes to str.
        This prevents UnsupportedOperation errors when loading Windows-trained models on Linux.
        """
        # Handle all pathlib Path classes (WindowsPath, PosixPath, PurePath, etc.)
        if 'pathlib' in module.lower():
            if 'Path' in name or 'PurePath' in name:
                # Return str class instead of pathlib class
                return str
        
        # For all other classes, use original behavior
        try:
            return super().find_class(module, name)
        except Exception as e:
            # If we get an UnsupportedOperation error, try to return str
            if 'UnsupportedOperation' in str(type(e).__name__) or 'pathlib' in str(e).lower():
                return str
            raise

# Create a custom pickle module with our PatchedUnpickler
class PatchedPickleModule:
    """Custom pickle module wrapper that uses PatchedUnpickler."""
    Unpickler = PatchedUnpickler
    
    # Forward all other pickle attributes
    def __getattr__(self, name):
        return getattr(pickle, name)

def _patched_torch_load(*args, **kwargs):
    """
    Patched torch.load that handles pathlib objects in pickled models.
    This prevents UnsupportedOperation errors when loading Windows-trained models on Linux.
    """
    # Ensure map_location is set to CPU for Streamlit Cloud compatibility
    if 'map_location' not in kwargs:
        kwargs['map_location'] = 'cpu'
    
    # Use our custom pickle module with PatchedUnpickler
    if 'pickle_module' not in kwargs:
        kwargs['pickle_module'] = PatchedPickleModule()
    
    # Call original torch.load with patched pickle module
    return _original_torch_load(*args, **kwargs)

# Apply the patch
torch.load = _patched_torch_load

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
            ImportError: If required packages are not available.
        """
        # Import YOLO here to avoid early cv2 import issues
        # Try importing with better error handling for Streamlit Cloud
        try:
            # First ensure cv2 is available
            global cv2
            if cv2 is None:
                try:
                    import cv2
                except ImportError:
                    # Try importing opencv-python-headless explicitly
                    try:
                        import sys
                        import subprocess
                        import pkg_resources
                        # Check if opencv is installed
                        try:
                            pkg_resources.get_distribution('opencv-python-headless')
                        except pkg_resources.DistributionNotFound:
                            try:
                                pkg_resources.get_distribution('opencv-python')
                            except pkg_resources.DistributionNotFound:
                                logger.warning("OpenCV not found. Attempting to import ultralytics anyway...")
                    except Exception:
                        pass
            
            # Now try importing ultralytics
            from ultralytics import YOLO
        except ImportError as e:
            error_msg = str(e)
            import sys
            import traceback
            
            # More detailed error message
            logger.error(f"Ultralytics import failed: {error_msg}")
            logger.error(f"Python path: {sys.path}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Check if the error is related to cv2
            if 'cv2' in error_msg.lower() or 'opencv' in error_msg.lower():
                error_msg = (
                    "Failed to import ultralytics due to OpenCV (cv2) import error. "
                    "Please ensure opencv-python-headless is installed: pip install opencv-python-headless"
                )
            else:
                error_msg = (
                    f"Failed to import ultralytics: {error_msg}. "
                    "Please ensure ultralytics is installed: pip install ultralytics"
                )
            logger.error(error_msg)
            raise ImportError(error_msg) from e
        except Exception as e:
            # Catch any other import-related errors
            error_msg = f"Failed to import ultralytics: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise ImportError(error_msg) from e
        
        # Check if cv2 is available (ultralytics might have imported it)
        # Try to import cv2 again in case ultralytics imported it
        if cv2 is None:
            try:
                import cv2
            except ImportError:
                pass
        
        # Final check if cv2 is available
        if cv2 is None:
            error_msg = (
                "OpenCV (cv2) is not available. Please ensure opencv-python-headless is installed: "
                "pip install opencv-python-headless"
            )
            logger.error(error_msg)
            raise ImportError(error_msg)
        
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
        
        Raises:
            ImportError: If required packages are not available.
        """
        # Check if cv2 is available
        global cv2
        if cv2 is None:
            # Try to import cv2 one more time
            try:
                import cv2
            except ImportError:
                error_msg = (
                    "OpenCV (cv2) is not available. Please ensure opencv-python-headless is installed: "
                    "pip install opencv-python-headless"
                )
                logger.error(error_msg)
                raise ImportError(error_msg)
        
        if self.model is None:
            try:
                self.load_model()
            except ImportError as e:
                # Re-raise import errors with better context
                logger.error(f"Failed to load model due to import error: {str(e)}")
                raise
        
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

