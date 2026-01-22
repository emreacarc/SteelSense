"""
Source package for SteelSense.
"""

# Only import SteelDefectDetector which is actually used in app.py
# data_manager is not imported here to avoid roboflow/cv2 import issues on Streamlit Cloud
# If data_manager functions are needed, import directly:
# from src.data_manager import download_dataset, list_workspaces

from .inference_engine import SteelDefectDetector

__all__ = ["SteelDefectDetector"]

