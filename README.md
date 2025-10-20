# PLT to PDF Dönüştürücü

PLT (HPGL) dosyalarını gerçek ölçeğinde PDF'e çeviren basit bir Python programı.

## Klasör Yapısı

```
sarpapp/
├── plt_to_pdf.py        # Ana program
├── input_plt/           # PLT dosyalarını buraya koyun
└── output_pdf/          # PDF dosyaları buraya kaydedilir
```

## Kurulum

Önce gerekli kütüphaneyi yükleyin:

```bash
pip install reportlab
```

## Kullanım

### Adım 1: PLT Dosyalarını Yerleştirin

PLT dosyalarınızı `input_plt` klasörüne kopyalayın.

### Adım 2: Programı Çalıştırın

```bash
python plt_to_pdf.py
```

Program otomatik olarak:
- `input_plt` klasöründeki tüm PLT dosyalarını bulur
- Her birini PDF'e çevirir
- PDF'leri `output_pdf` klasörüne kaydeder

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
- ✓ Gerçek ölçekte PDF oluşturur
- ✓ Toplu dönüştürme (birden fazla dosya)
- ✓ Otomatik sayfa boyutu hesaplama
- ✓ Klasör tabanlı kolay kullanım
- ✓ Detaylı ilerleme raporu

## Teknik Detaylar

- HPGL birimlerini mm'ye çevirir (1 HPGL birimi = 0.025 mm)
- PU (Pen Up), PD (Pen Down), PA (Plot Absolute) komutlarını destekler
- ReportLab kütüphanesi kullanarak PDF oluşturur
- Hem .plt hem de .PLT uzantılarını destekler
