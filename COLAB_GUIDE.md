# Google Colab Training Guide

## Hızlı Başlangıç

1. **Google Colab'a Git:**
   - https://colab.research.google.com/
   - Yeni notebook oluştur veya `train_on_colab.ipynb` dosyasını yükle

2. **GPU'yu Aktif Et:**
   - `Runtime` → `Change runtime type` → `Hardware accelerator: GPU` → `Save`
   - Ücretsiz: T4 GPU (15GB RAM)
   - Colab Pro: A100 GPU (40GB RAM) - daha hızlı!

3. **Notebook'u Çalıştır:**
   - Her hücreyi sırayla çalıştır (Shift+Enter)
   - Roboflow credentials'ı girmeniz gerekecek

## Adım Adım

### Step 1: Setup
- Paketleri yükle
- GPU kontrolü yap

### Step 2: Google Drive (Opsiyonel)
- Drive'ı mount et
- Modeli kalıcı olarak kaydetmek için

### Step 3: Dataset İndirme
- Roboflow API key'inizi girin
- Dataset otomatik indirilecek

### Step 4: Konfigürasyon
- Model boyutu, epoch sayısı, batch size ayarlayın
- GPU varsa batch size'ı 16-32 yapın

### Step 5: Eğitim
- Model eğitimi başlar
- GPU'da çok daha hızlı olacak (~4 saat vs ~27 saat CPU)

### Step 6-7: Sonuçları Kaydet
- Google Drive'a kaydet
- Veya bilgisayarınıza indir

## Süre Karşılaştırması

| Platform | YOLOv8s + 100 epochs | Süre |
|----------|---------------------|------|
| CPU (Local) | 27 saat | ~1.1 gün |
| **GPU (Colab Free T4)** | **~4 saat** | **Çok hızlı!** |
| GPU (Colab Pro A100) | ~2 saat | En hızlı |

## Önemli Notlar

1. **Colab Free Limitleri:**
   - Günlük GPU kullanımı: ~12 saat
   - Aralıksız çalışma: ~2 saat
   - 100 epoch için yeterli!

2. **Google Drive:**
   - Modeli kaydetmek için Drive mount edin
   - Yoksa session bitince model kaybolur

3. **Roboflow API Key:**
   - `hgqLaPsaj7neykLAQSQy` (sizin key'iniz)
   - Notebook'ta otomatik dolu gelecek

4. **Model İndirme:**
   - Eğitim bitince `best.pt` dosyasını indirin
   - `models/` klasörüne koyun
   - Streamlit uygulaması kullanabilir

## Troubleshooting

### GPU çalışmıyor?
- Runtime → Change runtime type → GPU seçin
- Runtime → Restart runtime

### Out of memory?
- Batch size'ı düşürün (32 → 16 → 8)
- Image size'ı düşürün (640 sabit kalabilir)

### Dataset indirme hatası?
- API key'i kontrol edin
- Workspace ve project isimlerini kontrol edin

## Sonuç

Colab'da GPU ile eğitim çok daha hızlı! 27 saat yerine ~4 saatte bitirirsiniz.

