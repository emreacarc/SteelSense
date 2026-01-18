# Streamlit Deployment Guide

## Dataset Boyutu ve Kullanımı

### Dataset Detayları
- **Boyut**: 283.24 MB (~0.28 GB)
- **Kullanım**: 
  - "Get Random Surface" butonu için random resim seçimi
  - PDF raporunda resimleri göstermek için
  - Batch Inspection'da resim gösterimi için

### Platform Limitleri

#### Streamlit Cloud (Önerilen)
- **Free tier**: ~1 GB repo limiti (283 MB yeterli)
- Dataset dahil edilebilir
- İlk deployment zaman alabilir (283 MB yükleme)
- Çalışır, ancak yavaş olabilir

#### Heroku
- **Slug size limiti**: 500 MB
- Dataset (283 MB) + Model (21 MB) + Dependencies ≈ 350+ MB
- Limit aşılmayabilir ama risk var
- Heroku ücretsiz planı kaldırıldı (ücretli)

#### PythonAnywhere
- **Free tier**: 512 MB disk
- Sadece dosyalar için yeterli, deployment için ücretli plan gerekebilir

### Öneriler

#### Seçenek 1: Dataset ile Deploy (Önerilen)
```bash
# .gitignore'dan data/ klasörünü çıkar
# Veya repository'ye dataset'i dahil et
```

**Artıları:**
- Tüm özellikler çalışır
- "Get Random Surface" butonu çalışır
- PDF raporunda resimler gösterilir

**Eksileri:**
- Deployment zamanı uzar (~283 MB yükleme)
- Repo boyutu büyür

#### Seçenek 2: Dataset Olmadan Deploy (Alternatif)
Dataset'i `.gitignore`'da tut, kullanıcılar sadece upload yapsın.

**Artıları:**
- Hızlı deployment
- Küçük repo boyutu

**Eksileri:**
- "Get Random Surface" butonu çalışmaz (dataset yok)
- PDF raporunda sadece uploaded resimler gösterilir

### Deployment Adımları

#### Streamlit Cloud (Önerilen)

1. **GitHub'a Push**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Streamlit Cloud'a Deploy**
   - https://share.streamlit.io adresine git
   - GitHub repository'yi bağla
   - `app.py` dosyasını seç
   - Deploy!

3. **Not**: Dataset 283 MB olduğu için ilk deployment 5-10 dakika sürebilir.

#### Dataset Boyutu Optimizasyonu (İsteğe Bağlı)

Eğer deployment yavaşsa, dataset'i optimize edebilirsiniz:

```python
# app.py'de sadece validation setini kullan
# veya daha az resim kullan
```

### Şu Anki Durum

- **Streamlit Cloud'da ÇALIŞIR** - 283 MB yeterli (1 GB limit içinde)
- İlk deployment uzun sürebilir
- Tüm özellikler çalışır (Random Surface, PDF, vb.)

### Kontrol Listesi

- [x] Dataset boyutu: 283 MB (Streamlit Cloud için uygun)
- [x] Model boyutu: 21 MB (dahil edilmeyecek - kullanıcılar train edecek)
- [x] Requirements.txt: Güncel ve tam
- [x] README.md: Deployment talimatları (gerekirse ekle)
- [ ] GitHub'a push
- [ ] Streamlit Cloud'da deploy

## Sonuç

**283 MB dataset ile Streamlit Cloud'da çalışır!** 

Deployment zamanı biraz uzayabilir ama tüm özellikler çalışacaktır.

