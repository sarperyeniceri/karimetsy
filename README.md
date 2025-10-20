# PLT to PDF Dönüştürücü

PLT (HPGL) dosyalarını gerçek ölçeğinde PDF'e çeviren basit bir Python programı.

## Klasör Yapısı

```
sarpapp/
├── plt_to_pdf.py              # Tek sayfa gerçek ölçek
├── plt_to_pdf_a4.py           # A4 sayfalarına bölünmüş
├── plt_to_pdf_a4_overlay.py   # A4 + 2cm yapıştırma alanları
├── input_plt/                 # PLT dosyalarını buraya koyun
└── output_pdf/                # PDF dosyaları buraya kaydedilir
```

## Kurulum

Önce gerekli kütüphaneyi yükleyin:

```bash
pip install reportlab
```

## Kullanım

### Adım 1: PLT Dosyalarını Yerleştirin

PLT dosyalarınızı `input_plt` klasörüne kopyalayın.

### Adım 2: Programı Seçin ve Çalıştırın

**Seçenek 1: Tek Sayfa Gerçek Ölçek**
```bash
python plt_to_pdf.py
```
- Tüm çizim tek sayfada
- Gerçek ölçekte (örn: 114 cm x 89 cm)
- 2 cm margin

**Seçenek 2: A4 Sayfalarına Bölünmüş**
```bash
python plt_to_pdf_a4.py
```
- Çizim A4 sayfalarına bölünür
- Her sayfada 2 cm margin
- Sayfa etiketleri (A1, A2, B1, vb.)

**Seçenek 3: A4 + Yapıştırma Alanları (ÖNERİLEN)**
```bash
python plt_to_pdf_a4_overlay.py
```
- Çizim A4 sayfalarına bölünür
- **2 cm overlap (bindirme) alanları**
- Komşu sayfalar birbirine tam oturur
- Kesikli çizgiler yapıştırma sınırlarını gösterir
- Yazdırıp yapıştırarak gerçek ölçekli kalıp elde edilir

### Örnek Çıktı

```
3 adet PLT dosyası bulundu.

============================================================

[1/3] İşleniyor: cizim1.plt
------------------------------------------------------------
PLT dosyası okunuyor: input_plt/cizim1.plt
Çizim sınırları bulundu: (100, 100) - (8000, 6000)
PDF boyutu: 197.5 mm x 147.5 mm
PDF başarıyla oluşturuldu: output_pdf/cizim1.pdf
✓ Başarılı: cizim1.pdf

[2/3] İşleniyor: cizim2.plt
------------------------------------------------------------
...

============================================================

DÖNÜŞTÜRME ÖZETİ:
  Toplam dosya: 3
  Başarılı: 3
  Başarısız: 0

Çıktı klasörü: /Users/.../sarpapp/output_pdf
============================================================
```

## Özellikler

- ✓ HPGL (PLT) formatını okur
- ✓ Gerçek ölçekte PDF oluşturur (yazıcıda test edildi)
- ✓ Üç farklı çıktı modu (tek sayfa / A4 / A4+overlap)
- ✓ Yapıştırma için 2cm overlap alanları
- ✓ Toplu dönüştürme (birden fazla dosya)
- ✓ Otomatik sayfa boyutu hesaplama
- ✓ Klasör tabanlı kolay kullanım
- ✓ Detaylı ilerleme raporu

## Teknik Detaylar

- HPGL birimlerini mm'ye çevirir (1 HPGL birimi = 0.025 mm)
- PU (Pen Up), PD (Pen Down), PA (Plot Absolute) komutlarını destekler
- ReportLab kütüphanesi kullanarak PDF oluşturur
- Hem .plt hem de .PLT uzantılarını destekler
