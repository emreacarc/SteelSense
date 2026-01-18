# SteelSense

A professional Computer Vision application for automated defect detection on steel surfaces using YOLOv8 deep learning model and Streamlit web interface.

## 🎯 Features

- **Single Inspection**: Analyze individual steel surface images with real-time defect detection
- **Batch Inspection**: Process multiple images simultaneously with comprehensive analysis
- **Random Image Selection**: Test the system with random images from the dataset (3, 5, or 10 images)
- **Confidence Threshold Control**: Adjustable detection sensitivity (default: 0.20)
- **Image & Defect ID System**: Unique identification for each image and defect (e.g., Image ID: 1, Defect ID: 1-A, 1-B)
- **Detailed Results View**: View all detected defects with confidence scores and defect types
- **Summary Statistics**: Comprehensive statistics including defect distribution, percentages, and analysis threshold
- **PDF Report Generation**: Export complete inspection reports in PDF format (A4) with all images, tables, and statistics
- **Visual Analysis**: Side-by-side comparison of original and processed images with defect annotations

## 🔍 Defect Classes

The system can detect the following 6 types of steel surface defects:

1. **Crazing**: Fine network of cracks on the surface
2. **Inclusion**: Non-metallic particles embedded in steel
3. **Patches**: Localized surface irregularities
4. **Pitted Surface**: Small holes or depressions
5. **Rolled-in Scale**: Oxide scale pressed into the surface during rolling
6. **Scratches**: Linear surface damage marks

## 📦 Installation

### Prerequisites

- Python 3.8+
- Roboflow API key (for dataset download)
- See `requirements.txt` for full list of dependencies

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd SteelSense
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download dataset and train model:**
   ```bash
   python setup.py --api-key YOUR_ROBOFLOW_API_KEY --workspace steelsense --project steel-surface-defects-5cztc --version 1
   ```
   
   Or run interactively:
   ```bash
   python setup.py
   ```
   
   **Note:** This process may take 30-60 minutes depending on your hardware. The dataset will be downloaded and the model will be trained automatically.

4. **Run the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

## 🚀 Usage

### Single Inspection

1. Navigate to **Single Inspection** page
2. Upload a steel surface image or click **Get Random Surface** to test with a random image
3. Adjust confidence threshold if needed (default: 0.20)
4. View detection results with bounding boxes, confidence scores, and defect classifications

### Batch Inspection

1. Navigate to **Batch Inspection** page
2. Upload multiple images or use **Get Random Surface** button (select 3, 5, or 10 images)
3. Click **Analyze All Images** to process all uploaded/selected images
4. View **Batch Inspection Results** table with Image ID, Image Name, Total Defects, and Defect Types
5. Use **Show Detailed Results** to see all defects with Image & Defect IDs
6. Use **Show Images** to view original and processed images side-by-side with defect tables
7. Review **Summary Statistics** including:
   - Total Images, Total Defects
   - Images with/without Defects (with percentages)
   - Defect Distribution table (count and percentage for each defect type)
   - Analysis Threshold used
8. Click **Generate PDF Report** to export a comprehensive PDF report

### PDF Report Features

- Current date and time
- Batch Inspection Results table
- Detailed Results table with Image & Defect IDs
- All images (original and processed side-by-side)
- Defect tables under each image
- Summary Statistics section
- Professional footer on each page

## 🏗️ Project Structure

```
SteelSense/
├── app.py                 # Main Streamlit application
├── config.py              # Configuration settings
├── setup.py               # Setup script for dataset and model
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
├── src/
│   ├── data_manager.py   # Dataset download from Roboflow
│   ├── model_trainer.py   # YOLOv8 model training
│   └── inference_engine.py # Defect detection inference
├── models/                # Trained YOLOv8 models (created after training)
└── data/                  # Dataset (downloaded from Roboflow)
```

## ⚙️ Configuration

Edit `config.py` to customize:

- `EPOCHS`: Number of training epochs (default: 10)
- `BATCH_SIZE`: Training batch size (default: 32)
- `IMAGE_SIZE`: Input image size (default: 640)
- `MODEL_SIZE`: YOLOv8 model size - "n", "s", "m", "l", "x" (default: "s")
- `DEFAULT_CONF_THRESHOLD`: Default confidence threshold (default: 0.20)

## 📊 Model Information

- **Model**: YOLOv8s (Small)
- **Training**: 10 epochs
- **Performance Metrics**:
  - Precision: 68.40%
  - Recall: 68.54%
  - mAP50: 73.02%
- **Model Size**: ~21.48 MB

## 📚 Dataset

The project uses the **NEU-DET (Northeastern University Steel Surface Defects Database)** dataset, which is a publicly available dataset for steel surface defect detection. The dataset contains images of steel surfaces with 6 different types of defects.

- **Dataset Name**: NEU-DET (Northeastern University Steel Surface Defects Database)
- **Source**: Roboflow (processed and formatted for YOLOv8)
- **Defect Classes**: 6 classes (Crazing, Inclusion, Patches, Pitted Surface, Rolled-in Scale, Scratches)
- **Image Format**: RGB images with annotations in YOLO format
- **Dataset Split**: Train/Validation splits for model training

## 🛠️ Technology Stack

- **YOLOv8**: State-of-the-art object detection model (Ultralytics)
- **Streamlit**: Web application framework for interactive UI
- **PyTorch**: Deep learning framework
- **ReportLab**: PDF generation library
- **PIL/Pillow**: Image processing
- **Pandas**: Data manipulation and table display
- **OpenCV**: Computer vision operations
- **Roboflow**: Dataset management and download

## 📝 Notes

- The trained model (`models/best.pt`) is not included in the repository due to size limitations
- Users must train the model using `setup.py` before using the application
- The dataset is downloaded from Roboflow and requires an API key
- Model training can be done on CPU or GPU (GPU recommended for faster training)

## 📄 License

[Your License Here]

## 👤 Contact

**Developer**: Emre AÇAR

- **LinkedIn**: [Your LinkedIn Profile]
- **Email**: [Your Email Address]

## 🙏 Acknowledgments

- NEU-DET Dataset for providing the steel surface defect dataset
- Ultralytics for YOLOv8 implementation
- Roboflow for dataset management tools
