"""
Model training module for YOLOv8 steel defect detection.
"""

import os
import logging
import shutil
from .config import MODELS_DIR, BASE_MODELS_DIR, EPOCHS, IMAGE_SIZE, MODEL_SIZE, DATA_YAML_NAME, PROJECT_ROOT, BATCH_SIZE

# Lazy import ultralytics to avoid early cv2 import issues
# YOLO will be imported when needed in functions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_data_yaml():
    """
    Automatically locate data.yaml within project subdirectories.
    
    Returns:
        str: Path to data.yaml file
    """
    # Common locations to search
    search_paths = [
        os.path.join(PROJECT_ROOT, "data", "steel-defect-dataset", DATA_YAML_NAME),
        os.path.join(PROJECT_ROOT, "data", DATA_YAML_NAME),
        os.path.join(PROJECT_ROOT, DATA_YAML_NAME),
    ]
    
    # Recursive search in data directory
    for root, dirs, files in os.walk(os.path.join(PROJECT_ROOT, "data")):
        if DATA_YAML_NAME in files:
            found_path = os.path.join(root, DATA_YAML_NAME)
            logger.info(f"Found data.yaml at: {found_path}")
            return found_path
    
    # Check predefined paths
    for path in search_paths:
        if os.path.exists(path):
            logger.info(f"Found data.yaml at: {path}")
            return path
    
    raise FileNotFoundError(f"Could not locate {DATA_YAML_NAME}. Please ensure the dataset is downloaded.")


def download_base_model():
    """
    Download the base YOLOv8 model to local directory.
    This triggers the automatic download of the pre-trained model.
    
    Returns:
        str: Path to the downloaded base model file
    """
    try:
        # Create base models directory if it doesn't exist
        os.makedirs(BASE_MODELS_DIR, exist_ok=True)
        
        model_name = f"yolov8{MODEL_SIZE}.pt"
        local_model_path = os.path.join(BASE_MODELS_DIR, model_name)
        
        # Check if model already exists locally
        if os.path.exists(local_model_path):
            logger.info(f"Base model already exists at: {local_model_path}")
            return local_model_path
        
        # Download the base model by initializing it
        # This triggers automatic download to ultralytics cache
        logger.info(f"Downloading base model {model_name}...")
        try:
            from ultralytics import YOLO
        except ImportError as e:
            error_msg = (
                "Failed to import ultralytics. Please ensure ultralytics is installed: "
                "pip install ultralytics"
            )
            logger.error(error_msg)
            raise ImportError(error_msg) from e
        model = YOLO(model_name)
        
        # Try to find and copy from ultralytics cache
        import pathlib
        home_dir = pathlib.Path.home()
        ultralytics_cache = home_dir / ".ultralytics" / "weights" / model_name
        
        if ultralytics_cache.exists():
            # Copy from cache to our local directory
            shutil.copy2(str(ultralytics_cache), local_model_path)
            logger.info(f"Base model saved to local directory: {local_model_path}")
            return local_model_path
        else:
            # Model was downloaded to cache but path might be different
            # The model is ready to use, just return the name
            logger.info(f"Base model downloaded to ultralytics cache. Will be used during training.")
            return model_name
        
    except Exception as e:
        logger.warning(f"Could not save base model locally: {str(e)}")
        logger.info("Base model will be downloaded automatically during training.")
        return f"yolov8{MODEL_SIZE}.pt"


def train_model(data_yaml_path: str = None):
    """
    Train YOLOv8n model for steel defect detection.
    
    Args:
        data_yaml_path: Optional path to data.yaml. If None, will search automatically.
    
    Returns:
        str: Path to the trained model (best.pt)
    """
    try:
        # Locate data.yaml if not provided
        if data_yaml_path is None:
            data_yaml_path = find_data_yaml()
        
        if not os.path.exists(data_yaml_path):
            raise FileNotFoundError(f"data.yaml not found at: {data_yaml_path}")
        
        # Create models directory if it doesn't exist
        os.makedirs(MODELS_DIR, exist_ok=True)
        
        # Always use model name to let Ultralytics handle download and caching
        # This avoids issues with corrupted local files
        # Use 'yolov8s' instead of 'yolov8s.pt' to force download from source
        model_identifier = f"yolov8{MODEL_SIZE}"  # Without .pt extension to avoid local file conflicts
        logger.info(f"Initializing {model_identifier} (will be downloaded automatically if needed)...")
        
        # Import YOLO here to avoid early cv2 import issues
        try:
            from ultralytics import YOLO
        except ImportError as e:
            error_msg = (
                "Failed to import ultralytics. Please ensure ultralytics is installed: "
                "pip install ultralytics"
            )
            logger.error(error_msg)
            raise ImportError(error_msg) from e
        
        # Change to models directory to avoid loading corrupted files in current directory
        original_dir = os.getcwd()
        try:
            os.chdir(MODELS_DIR)
            model = YOLO(model_identifier)  # YOLO will download fresh copy
        finally:
            os.chdir(original_dir)
        
        # Train the model
        logger.info("Training started...")
        logger.info(f"Configuration: epochs={EPOCHS}, imgsz={IMAGE_SIZE}, batch={BATCH_SIZE}")
        
        results = model.train(
            data=data_yaml_path,
            epochs=EPOCHS,
            imgsz=IMAGE_SIZE,
            batch=BATCH_SIZE,
            project=MODELS_DIR,
            name="steel_defect_detection",
            patience=50,  # Early stopping patience (stops if no improvement for 50 epochs)
            save=True,  # Save checkpoints
            save_period=5,  # Save checkpoint every 5 epochs (for 10 epoch training)
            device='cpu',  # Use CPU (change to 0 for GPU if available)
            resume=False,  # Don't resume from previous training (ensures fresh start)
            workers=8,  # Number of worker threads for data loading
            augment=True,  # Enable data augmentation
            lr0=0.01,  # Initial learning rate
            lrf=0.1,  # Final learning rate (lr0 * lrf)
            momentum=0.937,  # SGD momentum
            weight_decay=0.0005,  # Weight decay
            warmup_epochs=3.0,  # Warmup epochs
            warmup_momentum=0.8,  # Warmup initial momentum
            box=7.5,  # Box loss gain
            cls=0.5,  # Class loss gain
            dfl=1.5,  # DFL loss gain
        )
        
        # Get the path to the best model
        best_model_path = os.path.join(MODELS_DIR, "steel_defect_detection", "weights", "best.pt")
        
        # Copy to main models directory for easier access
        if os.path.exists(best_model_path):
            final_model_path = os.path.join(MODELS_DIR, "best.pt")
            shutil.copy2(best_model_path, final_model_path)
            logger.info(f"Training completed. Model saved to: {final_model_path}")
            return final_model_path
        else:
            logger.warning("Training completed but best.pt not found in expected location.")
            return best_model_path
        
    except Exception as e:
        logger.error(f"Error during training: {str(e)}")
        raise

