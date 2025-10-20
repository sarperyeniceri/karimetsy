#!/usr/bin/env python3
"""
PLT dosyasını gerçek ölçeğinde PDF'e çevirme programı
input_plt klasöründen dosyaları okur, output_pdf klasörüne kaydeder
"""

import re
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import sys
import os
from glob import glob


class PLTtoPDFConverter:
    def __init__(self, plt_file, pdf_file):
        self.plt_file = plt_file
        self.pdf_file = pdf_file
        self.commands = []
        self.current_x = 0
        self.current_y = 0
        self.pen_down = False

        # HPGL birimlerini mm'ye çevirme (1016 HPGL units per inch)
        self.unit_to_mm = 25.4 / 1016  # ≈ 0.025

    def parse_plt(self):
        """PLT dosyasını oku ve komutları ayrıştır"""
        with open(self.plt_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Boşlukları ve satır sonlarını temizle
        content = content.replace('\n', '').replace('\r', '').replace(' ', '')

        # HPGL komutlarını bul - 2 harfli komut + parametreler
        pattern = r'([A-Z]{2})([^A-Z]*)'
        commands = re.findall(pattern, content)
        return commands

    def get_bounds(self, commands):
        """Çizim sınırlarını bul"""
        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = float('-inf'), float('-inf')
        x, y = 0, 0

        for cmd, params in commands:
            if cmd in ['PA', 'PD', 'PU']:
                coords = [int(p) for p in re.findall(r'-?\d+', params)]
                for i in range(0, len(coords), 2):
                    if i + 1 < len(coords):
                        x, y = coords[i], coords[i + 1]
                        min_x = min(min_x, x)
                        min_y = min(min_y, y)
                        max_x = max(max_x, x)
                        max_y = max(max_y, y)

        return min_x, min_y, max_x, max_y

    def convert(self):
        """PLT'den PDF'e dönüştür"""
        print(f"PLT dosyası okunuyor: {self.plt_file}")
        commands = self.parse_plt()

        if not commands:
            print("Hata: PLT dosyasında geçerli komut bulunamadı!")
            return False

        # İlk geçiş: Tüm çizgileri topla ve HPGL birimlerinde sakla
        lines = []
        x, y = 0, 0
        pen_down = False

        for cmd, params_str in commands:
            # Parametreleri parse et
            params_str = params_str.replace(';', '').strip()
            params = []
            if params_str:
                param_parts = params_str.split(',')
                for part in param_parts:
                    part = part.strip()
                    if part:
                        try:
                            params.append(float(part))
                        except ValueError:
                            pass

            if cmd == 'PU':  # Pen Up
                pen_down = False
                if len(params) >= 2:
                    x, y = params[0], params[1]

            elif cmd == 'PD':  # Pen Down
                pen_down = True  # ÖNCE kalemi indir
                if len(params) >= 2:
                    # İlk nokta - mevcut pozisyondan yeni pozisyona çiz
                    new_x, new_y = params[0], params[1]
                    lines.append(((x, y), (new_x, new_y)))
                    x, y = new_x, new_y

                    # Sonraki noktalar (PD komutunda birden fazla nokta olabilir)
                    i = 2
                    while i + 1 < len(params):
                        new_x = params[i]
                        new_y = params[i + 1]
                        lines.append(((x, y), (new_x, new_y)))
                        x, y = new_x, new_y
                        i += 2

            elif cmd == 'PA':  # Plot Absolute
                # PA komutunda birden fazla nokta olabilir
                for i in range(0, len(params), 2):
                    if i + 1 < len(params):
                        new_x, new_y = params[i], params[i + 1]
                        if pen_down:
                            lines.append(((x, y), (new_x, new_y)))
                        x, y = new_x, new_y

            elif cmd == 'PR':  # Plot Relative
                for i in range(0, len(params), 2):
                    if i + 1 < len(params):
                        new_x, new_y = x + params[i], y + params[i + 1]
                        if pen_down:
                            lines.append(((x, y), (new_x, new_y)))
                        x, y = new_x, new_y

            elif cmd == 'IN':  # Initialize
                x, y = 0, 0
                pen_down = False

        if not lines:
            print("Hata: Çizim verisi bulunamadı!")
            return False

        print(f"{len(lines)} çizgi segmenti bulundu")

        # Sınırları hesapla
        all_x = []
        all_y = []
        for (x1, y1), (x2, y2) in lines:
            all_x.extend([x1, x2])
            all_y.extend([y1, y2])

        min_x = min(all_x)
        max_x = max(all_x)
        min_y = min(all_y)
        max_y = max(all_y)

        width_hpgl = max_x - min_x
        height_hpgl = max_y - min_y

        # Normalize et (Y ekseni çevirme YOK - düz kullan)
        normalized_lines = []
        for (x1, y1), (x2, y2) in lines:
            # X'i normalize et
            nx1 = (x1 - min_x) * self.unit_to_mm
            nx2 = (x2 - min_x) * self.unit_to_mm
            # Y'yi normalize et (çevirmeden)
            ny1 = (y1 - min_y) * self.unit_to_mm
            ny2 = (y2 - min_y) * self.unit_to_mm
            normalized_lines.append(((nx1, ny1), (nx2, ny2)))

        width_mm = width_hpgl * self.unit_to_mm
        height_mm = height_hpgl * self.unit_to_mm

        print(f"Çizim boyutu: {width_mm:.1f} mm x {height_mm:.1f} mm")

        # 2 cm güvenli alan (margin) ekle
        margin_mm = 20  # 2 cm = 20 mm
        page_width_mm = width_mm + (2 * margin_mm)
        page_height_mm = height_mm + (2 * margin_mm)

        print(f"PDF boyutu (2cm margin ile): {page_width_mm:.1f} mm x {page_height_mm:.1f} mm")

        # PDF oluştur
        c = canvas.Canvas(self.pdf_file, pagesize=(page_width_mm * mm, page_height_mm * mm))

        # Çizim parametreleri
        c.setStrokeColorRGB(0, 0, 0)  # Siyah
        c.setLineWidth(0.5)
        c.setLineCap(1)  # Round cap
        c.setLineJoin(1)  # Round join

        # Tüm çizgileri çiz
        for (x1, y1), (x2, y2) in normalized_lines:
            # Margin ekle
            px1 = (x1 + margin_mm) * mm
            py1 = (y1 + margin_mm) * mm
            px2 = (x2 + margin_mm) * mm
            py2 = (y2 + margin_mm) * mm
            c.line(px1, py1, px2, py2)

        c.save()
        print(f"PDF başarıyla oluşturuldu: {self.pdf_file}")
        return True


def main():
    # Çalışma dizinini al
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, 'input_plt')
    output_dir = os.path.join(script_dir, 'output_pdf')

    # Klasörlerin varlığını kontrol et
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print(f"'{input_dir}' klasörü oluşturuldu.")
        print("Lütfen PLT dosyalarınızı bu klasöre koyun.")
        sys.exit(0)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"'{output_dir}' klasörü oluşturuldu.")

    # input_plt klasöründeki tüm PLT dosyalarını bul
    plt_files = glob(os.path.join(input_dir, '*.plt')) + glob(os.path.join(input_dir, '*.PLT'))

    if not plt_files:
        print(f"'{input_dir}' klasöründe PLT dosyası bulunamadı!")
        print("Lütfen .plt uzantılı dosyalarınızı bu klasöre koyun.")
        sys.exit(1)

    print(f"\n{len(plt_files)} adet PLT dosyası bulundu.\n")
    print("=" * 60)

    # Her dosyayı dönüştür
    success_count = 0
    fail_count = 0

    for plt_file in plt_files:
        # Sadece dosya adını al
        filename = os.path.basename(plt_file)
        pdf_filename = os.path.splitext(filename)[0] + '.pdf'
        pdf_file = os.path.join(output_dir, pdf_filename)

        print(f"\n[{plt_files.index(plt_file) + 1}/{len(plt_files)}] İşleniyor: {filename}")
        print("-" * 60)

        # Dönüştürme işlemini başlat
        converter = PLTtoPDFConverter(plt_file, pdf_file)

        try:
            if converter.convert():
                print(f"✓ Başarılı: {pdf_filename}")
                success_count += 1
            else:
                print(f"✗ Başarısız: {filename}")
                fail_count += 1
        except Exception as e:
            print(f"✗ Hata: {filename} - {str(e)}")
            fail_count += 1

    # Özet
    print("\n" + "=" * 60)
    print(f"\nDÖNÜŞTÜRME ÖZETİ:")
    print(f"  Toplam dosya: {len(plt_files)}")
    print(f"  Başarılı: {success_count}")
    print(f"  Başarısız: {fail_count}")
    print(f"\nÇıktı klasörü: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
