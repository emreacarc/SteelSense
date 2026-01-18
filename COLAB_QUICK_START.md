# Colab Quick Start - GPU Activation

## GPU ERROR TROUBLESHOOTING

### Step 1: Activate GPU
1. Go to **Runtime** menu in Colab
2. Select **Change runtime type**
3. Set **Hardware accelerator:** → **GPU**
4. Click **Save**

### Step 2: Restart Runtime
1. Go to **Runtime** menu
2. Click **Restart runtime**
3. Or use **Runtime** → **Restart and run all**

### Step 3: GPU Check
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
```

### Step 4: Start Training
Now `colab_training.py` will work, or use the code below:

---

## QUICK START CODE

Paste into Colab notebook and run:

```python
# ========================================
# STEP 1: GPU CHECK
# ========================================
import torch
print("="*70)
print("GPU CHECK")
print("="*70)
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")

if not torch.cuda.is_available():
    print("\nGPU NOT FOUND!")
    print("  → Runtime → Change runtime type → Select GPU")
    print("  → Runtime → Restart runtime")
    print("  → Then run this code again")
else:
    print(f"GPU found: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

# ========================================
# STEP 2: INSTALL PACKAGES
# ========================================
print("\n" + "="*70)
print("INSTALLING PACKAGES")
print("="*70)
!pip install -q ultralytics roboflow pandas numpy pillow opencv-python scikit-learn PyYAML

# ========================================
# STEP 3: DOWNLOAD DATASET
# ========================================
print("\n" + "="*70)
print("DOWNLOADING DATASET")
print("="*70)
from roboflow import Roboflow

ROBOFLOW_API_KEY = "hgqLaPsaj7neykLAQSQy"
ROBOFLOW_WORKSPACE = "steelsense"
ROBOFLOW_PROJECT = "steel-surface-defects-5cztc"
ROBOFLOW_VERSION = 1

rf = Roboflow(api_key=ROBOFLOW_API_KEY)
project = rf.workspace(ROBOFLOW_WORKSPACE).project(ROBOFLOW_PROJECT)

try:
    dataset = project.version(ROBOFLOW_VERSION).download("yolov8")
except:
    dataset = project.version(f"v{ROBOFLOW_VERSION}").download("yolov8")

DATA_YAML = f"{dataset.location}/data.yaml"
print(f"Dataset downloaded: {DATA_YAML}")

# ========================================
# STEP 4: CONFIGURATION
# ========================================
print("\n" + "="*70)
print("TRAINING CONFIGURATION")
print("="*70)

MODEL_SIZE = "s"  # "n", "s", "m", "l", "x"
EPOCHS = 100
IMAGE_SIZE = 640
BATCH_SIZE = 16 if torch.cuda.is_available() else 8
PATIENCE = 50
DEVICE = 0 if torch.cuda.is_available() else 'cpu'

print(f"  Model: YOLOv8{MODEL_SIZE}")
print(f"  Epochs: {EPOCHS}")
print(f"  Image Size: {IMAGE_SIZE}")
print(f"  Batch Size: {BATCH_SIZE}")
print(f"  Device: {DEVICE} ({'GPU' if torch.cuda.is_available() else 'CPU'})")

if not torch.cuda.is_available():
    print("\nWARNING: Training on CPU will take ~27 hours!")
    print("  Enable GPU for faster training (~4 hours)")

# ========================================
# STEP 5: START TRAINING
# ========================================
print("\n" + "="*70)
print("STARTING TRAINING")
print("="*70)

from ultralytics import YOLO

model = YOLO(f"yolov8{MODEL_SIZE}.pt")

results = model.train(
    data=DATA_YAML,
    epochs=EPOCHS,
    imgsz=IMAGE_SIZE,
    batch=BATCH_SIZE,
    patience=PATIENCE,
    save=True,
    save_period=10,
    device=DEVICE,  # Use 'cpu' if GPU not available
    workers=8,
    augment=True,
    project="/content/runs/detect",
    name="steel_defect_detection",
    lr0=0.01,
    lrf=0.1,
    momentum=0.937,
    weight_decay=0.0005,
    warmup_epochs=3.0,
    warmup_momentum=0.8,
    box=7.5,
    cls=0.5,
    dfl=1.5,
)

# ========================================
# STEP 6: SHOW RESULTS
# ========================================
print("\n" + "="*70)
print("TRAINING COMPLETED")
print("="*70)

best_model_path = "/content/runs/detect/steel_defect_detection/weights/best.pt"

if results:
    metrics = results.results_dict
    print(f"\nFinal Metrics:")
    print(f"  Precision:  {metrics.get('metrics/precision(B)', 0)*100:.2f}%")
    print(f"  Recall:     {metrics.get('metrics/recall(B)', 0)*100:.2f}%")
    print(f"  mAP50:      {metrics.get('metrics/mAP50(B)', 0)*100:.2f}%")
    print(f"  mAP50-95:   {metrics.get('metrics/mAP50-95(B)', 0)*100:.2f}%")

print(f"\nModel saved to: {best_model_path}")

# ========================================
# STEP 7: DOWNLOAD MODEL
# ========================================
print("\n" + "="*70)
print("DOWNLOAD MODEL")
print("="*70)

from google.colab import files
files.download(best_model_path)
print("Model downloaded to your computer!")
print(f"\nNow copy best.pt to: models/best.pt in your local project")
```

---

## CHECK IF GPU IS ACTIVE

Run this code before training:

```python
import torch
print(f"CUDA: {torch.cuda.is_available()}")
print(f"GPU Count: {torch.cuda.device_count()}")
```

Should see **True** and **> 0**! If not, repeat the steps above.

---

## TROUBLESHOOTING

### "CUDA not available" error
1. Runtime → Change runtime type → Select GPU
2. Runtime → Restart runtime
3. Run GPU check code again

### "Out of memory" error
- Reduce batch size: `BATCH_SIZE = 8` or `4`
- Reduce image size: `IMAGE_SIZE = 512` (instead of 640)

### Colab session timeout
- Mount Google Drive and save model there
- Download from Drive after session ends
