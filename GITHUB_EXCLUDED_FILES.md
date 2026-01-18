# GitHub'a Yüklenmeyecek Dosyalar

Bu dosya, `.gitignore` kurallarına göre GitHub'a yüklenmeyecek tüm dosya ve klasörleri listeler.

---

## YÜKLENMEYECEK DOSYALAR

### 1. MODEL DOSYALARI (21+ MB)

**Neden?** Model dosyaları çok büyük ve kullanıcılar kendi modellerini eğitecek.

```
models/*.pt
models/*.onnx
models/*.pth
models/steel_defect_detection*/
models/base/*.pt
yolov8*.pt
yolov8*.pt.broken
```

**Projedeki gerçek dosyalar:**
- `models/best.pt` (~21 MB)
- `models/best_yolov8n_backup.pt`
- `models/hf_model.pt`
- `models/yolov8s.pt`
- `models/steel_defect_detection/weights/best.pt`
- `models/steel_defect_detection/weights/last.pt`
- `models/steel_defect_detection5/weights/best.pt`
- `models/steel_defect_detection5/weights/last.pt`
- `models/steel_defect_detection5/weights/epoch0.pt`
- `models/steel_defect_detection5/weights/epoch5.pt`
- `yolov8n.pt`
- `yolov8s.pt.broken`

---

### 2. DATASET (283 MB)

**Neden?** Dataset çok büyük. Kullanıcılar Roboflow'dan indirecek (README'de talimatlar var).

```
data/
*.csv
*.jpg
*.jpeg
*.png
*.bmp
```

**Projedeki gerçek dosyalar:**
- `data/steel-defect-dataset/` (tüm klasör - 283 MB)
  - `train/images/` (~1800+ görsel)
  - `train/labels/` (annotation dosyaları)
  - `valid/images/` (~400+ görsel)
  - `valid/labels/` (annotation dosyaları)
  - `test/images/` (~200+ görsel)
  - `test/labels/` (annotation dosyaları)
  - `data.yaml`
  - `dataset_export.csv`
  - `dataset_summary.csv`

---

### 3. GEÇİCİ VE YARDIMCI SCRIPTLER

**Neden?** Bunlar geliştirme/yardımcı scriptler, ana uygulama için gerekli değil.

```
check_*.py
train_model_local.py
create_backup.py
estimate_*.py
monitor_*.py
start_training_*.py
cross_validation.py
compare_*.py
download_hf_model.py
list_workspaces.py
export_dataset_to_csv.py
colab_training.py
```

**Projedeki gerçek dosyalar:**
- `check_current_training.py`
- `check_hf_download.py`
- `check_training_progress.py`
- `check_training_status.py`
- `train_model_local.py`
- `create_backup.py`
- `estimate_training_time_s.py`
- `estimate_training_time.py`
- `monitor_training.py`
- `start_training_final.py`
- `cross_validation.py`
- `compare_detailed.py`
- `compare_models.py`
- `download_hf_model.py`
- `list_workspaces.py`
- `export_dataset_to_csv.py`
- `colab_training.py`

---

### 4. CACHE VE LOG DOSYALARI

**Neden?** Geçici dosyalar, her kullanıcının kendi sisteminde oluşacak.

```
__pycache__/
*.pyc
*.pyo
*.cache
*.log
training_log*.txt
runs/
wandb/
temp_*/
```

**Projedeki gerçek dosyalar:**
- `__pycache__/` (Python cache)
- `src/__pycache__/`
- `training_log.txt`
- `training_log_live.txt`
- `runs/` (YOLOv8 eğitim çıktıları)
- `wandb/` (Weights & Biases logları - varsa)
- `temp_check/` (HuggingFace cache)
- `temp_hf_check/` (HuggingFace cache)
- `data/steel-defect-dataset/train/labels.cache`
- `data/steel-defect-dataset/valid/labels.cache`
- `*.cache` dosyaları

---

### 5. IDE VE OS DOSYALARI

**Neden?** Kullanıcıya özel ayarlar, herkesin kendi IDE'sini kullanacak.

```
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
Thumbs.db
desktop.ini
```

**Projedeki gerçek dosyalar:**
- `.vscode/` (VS Code ayarları - varsa)
- `.idea/` (PyCharm ayarları - varsa)
- `.DS_Store` (macOS - varsa)
- `Thumbs.db` (Windows - varsa)
- `desktop.ini` (Windows - varsa)

---

### 6. STREAMLIT CACHE

**Neden?** Streamlit'in kendi cache'i, her kullanıcıda otomatik oluşur.

```
.streamlit/
```

**Projedeki gerçek dosyalar:**
- `.streamlit/` (Streamlit cache ve ayarlar)

---

### 7. JUPYTER NOTEBOOKS

**Neden?** Notebook dosyaları proje için gerekli değil.

```
*.ipynb
.ipynb_checkpoints/
```

**Projedeki gerçek dosyalar:**
- `*.ipynb` (varsa)
- `.ipynb_checkpoints/` (varsa)

---

### 8. GEÇİCİ VE BACKUP DOSYALARI

**Neden?** Geçici dosyalar, proje için gerekli değil.

```
*.tmp
*.temp
*.bak
*.broken
```

**Projedeki gerçek dosyalar:**
- `yolov8s.pt.broken` (bozuk model dosyası)
- `*.tmp`, `*.temp`, `*.bak` (varsa)

---

### 9. SAMPLE IMAGES (Opsiyonel)

**Not:** Şu an `.gitignore`'da yorum satırı olarak var. İsterseniz dahil edebilirsiniz.

```
# sample_images/  (şu an yorum satırı)
```

**Projedeki gerçek dosyalar:**
- `sample_images/` klasörü (şu an yüklenir, ama isteğe bağlı hariç tutulabilir)

---

## TOPLAM BOYUT

**Yüklenmeyecek dosyalar:**
- Model dosyaları: ~21 MB
- Dataset: ~283 MB
- Cache/Log: ~50-100 MB (tahmini)
- Scriptler: ~1-2 MB
- **TOPLAM: ~350+ MB**

**Yüklenecek dosyalar:**
- Kod + Dokümantasyon: ~0.11 MB

**Sonuç:** Repo çok küçük ve hızlı olacak!

---

## KONTROL

GitHub'a push yapmadan önce kontrol edin:

```bash
# Git durumunu kontrol et
git status

# Yüklenmeyecek dosyaları gör
git status --ignored

# Sadece yüklenecek dosyaları gör
git ls-files
```

---

## ÖZEL DURUMLAR

### Sample Images Klasörü

`sample_images/` klasörü şu an `.gitignore`'da değil, yani yüklenecek. Eğer hariç tutmak isterseniz:

```gitignore
# .gitignore'a ekleyin
sample_images/
```

### Colab Guide Dosyaları

`COLAB_GUIDE.md` ve `COLAB_QUICK_START.md` dosyaları yüklenecek (dokümantasyon olarak). Eğer hariç tutmak isterseniz `.gitignore`'a ekleyin.

---

## NOTLAR

1. **Model dosyaları:** Kullanıcılar `setup.py` çalıştırarak kendi modellerini eğitecek
2. **Dataset:** Kullanıcılar Roboflow'dan indirecek (README'de talimatlar var)
3. **Geçici scriptler:** Sadece geliştirme için kullanıldı, ana uygulama için gerekli değil
4. **Cache dosyaları:** Her kullanıcının sisteminde otomatik oluşacak

