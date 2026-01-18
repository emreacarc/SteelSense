"""
Data management module for downloading and managing the steel defect dataset.
"""

import os
import logging
from roboflow import Roboflow
from config import DATASET_DIR, DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def list_workspaces(api_key: str):
    """
    List available workspaces for the given API key.
    Note: This feature may not be available in all Roboflow API versions.
    
    Args:
        api_key: Roboflow API key
    
    Returns:
        list: List of workspace names, or empty list if not available
    """
    try:
        rf = Roboflow(api_key=api_key)
        # Try to list workspaces if the method exists
        if hasattr(rf, 'list_workspaces'):
            workspaces = rf.list_workspaces()
            return workspaces if workspaces else []
        else:
            logger.info("list_workspaces method not available in this Roboflow version.")
            return []
    except AttributeError:
        logger.info("list_workspaces method not available.")
        return []
    except Exception as e:
        logger.warning(f"Could not list workspaces: {str(e)}")
        return []


def download_dataset(api_key: str, workspace: str, project: str, version: int = 1):
    """
    Download the steel defect detection dataset from Roboflow.
    
    Args:
        api_key: Roboflow API key
        workspace: Roboflow workspace name (required)
        project: Roboflow project name (required)
        version: Dataset version number (default: 1)
    
    Returns:
        str: Path to the downloaded dataset directory
    
    Raises:
        ValueError: If workspace or project is not provided
        FileNotFoundError: If workspace or project doesn't exist
    """
    if not workspace or not workspace.strip():
        raise ValueError("Workspace name is required.")
    if not project or not project.strip():
        raise ValueError("Project name is required.")
    
    try:
        # Check if dataset already exists
        if os.path.exists(DATASET_DIR) and os.listdir(DATASET_DIR):
            logger.info("Dataset already exists. Skipping download.")
            return DATASET_DIR
        
        # Create data directory if it doesn't exist
        os.makedirs(DATA_DIR, exist_ok=True)
        
        logger.info("Initializing Roboflow connection...")
        rf = Roboflow(api_key=api_key)
        
        logger.info(f"Accessing workspace: {workspace}")
        workspace_obj = rf.workspace(workspace)
        
        logger.info(f"Accessing project: {project}")
        project_obj = workspace_obj.project(project)
        
        logger.info(f"Downloading dataset version {version}...")
        # Try both numeric version and "v{version}" format
        try:
            dataset = project_obj.version(version).download("yolov8", location=DATASET_DIR)
        except Exception as e:
            # If numeric version fails, try "v{version}" format
            logger.info(f"Trying version format 'v{version}'...")
            try:
                dataset = project_obj.version(f"v{version}").download("yolov8", location=DATASET_DIR)
            except Exception as e2:
                # If both fail, try to list available versions
                logger.error(f"Failed with version {version} and v{version}")
                logger.info("Attempting to find available versions...")
                raise e
        
        logger.info("Dataset downloaded successfully.")
        return DATASET_DIR
        
    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg or "404" in error_msg:
            raise FileNotFoundError(
                f"Workspace '{workspace}' or project '{project}' not found. "
                f"Please verify the workspace and project names are correct. "
                f"Error: {error_msg}"
            )
        logger.error(f"Error downloading dataset: {error_msg}")
        raise

