"""
Setup script for SteelSense project.
This script downloads the dataset and trains the model.
Run this script once before using the Streamlit app.

Usage:
    python setup.py
    python setup.py --api-key YOUR_KEY --workspace SteelSense --project SteelSense --version 1
"""

import os
import sys
import argparse
from src import download_dataset, train_model, download_base_model
from src.config import BEST_MODEL_PATH

def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Setup script for SteelSense")
    parser.add_argument("--api-key", type=str, help="Roboflow API Key")
    parser.add_argument("--workspace", type=str, default="SteelSense", help="Roboflow workspace name")
    parser.add_argument("--project", type=str, default="SteelSense", help="Roboflow project name")
    parser.add_argument("--version", type=int, default=1, help="Dataset version number")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("SteelSense - Setup Script")
    print("=" * 60)
    print()
    
    # Step 1: Download dataset
    print("Step 1: Downloading dataset from Roboflow...")
    print("-" * 60)
    
    # Get API key from args or prompt
    if args.api_key:
        api_key = args.api_key.strip()
    else:
        api_key = input("Enter your Roboflow API Key: ").strip()
    
    if not api_key:
        print("Error: API key is required.")
        sys.exit(1)
    
    # Get workspace, project, version from args or prompt
    if args.workspace:
        workspace = args.workspace
    else:
        workspace = input("Enter workspace name (default: SteelSense): ").strip() or "SteelSense"
    
    if args.project:
        project = args.project
    else:
        project = input("Enter project name (default: SteelSense): ").strip() or "SteelSense"
    
    if args.version:
        version = args.version
    else:
        version_input = input("Enter dataset version (default: 1): ").strip() or "1"
    
        try:
            version = int(version_input)
        except ValueError:
            print("Invalid version number. Using version 1.")
            version = 1
    
    try:
        dataset_path = download_dataset(
            api_key=api_key,
            workspace=workspace,
            project=project,
            version=version
        )
        print(f"Dataset downloaded successfully to: {dataset_path}")
        print()
    except Exception as e:
        print(f"Error downloading dataset: {str(e)}")
        sys.exit(1)
    
    # Step 2: Download base model
    print("Step 2: Downloading base YOLOv8 model...")
    print("-" * 60)
    
    try:
        base_model_path = download_base_model()
        print(f"Base model ready: {base_model_path}")
        print()
    except Exception as e:
        print(f"Warning: Could not download base model explicitly: {str(e)}")
        print("Base model will be downloaded automatically during training.")
        print()
    
    # Step 3: Train model
    print("Step 3: Training the model...")
    print("-" * 60)
    print("This may take a while depending on your hardware.")
    print()
    
    try:
        model_path = train_model()
        print(f"Training completed successfully!")
        print(f"Model saved to: {model_path}")
        print()
    except Exception as e:
        print(f"Error during training: {str(e)}")
        sys.exit(1)
    
    # Final check
    if os.path.exists(BEST_MODEL_PATH):
        print("=" * 60)
        print("Setup completed successfully!")
        print("=" * 60)
        print()
        print("You can now run the Streamlit app:")
        print("  streamlit run app.py")
        print()
    else:
        print("Warning: Model file not found at expected location.")
        print("Please check the training output above.")

if __name__ == "__main__":
    main()

