"""
Configuration file for SteelSense project.
All paths are Windows-compatible using os.path.
"""

import os

# Project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Data directories
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
DATASET_DIR = os.path.join(DATA_DIR, "steel-defect-dataset")

# Base model directory (for pre-trained YOLOv8 models)
BASE_MODELS_DIR = os.path.join(MODELS_DIR, "base")

# Model paths
BEST_MODEL_PATH = os.path.join(MODELS_DIR, "best.pt")

# Training hyperparameters
EPOCHS = 10  # Number of training epochs (can be increased later if needed)
IMAGE_SIZE = 640  # Can increase to 1280 for better accuracy (slower training)
MODEL_SIZE = "s"  # YOLOv8s (small). Options: "n", "s", "m", "l", "x" (larger = better accuracy, slower)
BATCH_SIZE = 32  # Batch size for training (higher = faster but more memory)
# Note: For better performance, consider:
# - MODEL_SIZE = "s" or "m" for higher accuracy
# - IMAGE_SIZE = 1280 for better detection of small defects
# - EPOCHS = 100-200 for full convergence

# Data configuration
DATA_YAML_NAME = "data.yaml"

# Default confidence threshold for inference
DEFAULT_CONF_THRESHOLD = 0.20

