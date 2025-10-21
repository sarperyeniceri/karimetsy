#!/usr/bin/env python3
"""
PLT dosyasını A4 sayfalarına bölerek PDF'e çevirme programı
Print ekranı mantığıyla 2cm overlap
"""

import re
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
import sys
import os
from glob import glob


class PLTtoPDFA4OverlayConverter:
    def __init__(self, plt_file, pdf_file):
        self.plt_file = plt_file
        self.pdf_file = pdf_file

        # HPGL birimlerini mm'ye çevirme (1016 HPGL units per inch)
        self.unit_to_mm = 25.4 / 1016

        # A4 boyutları
        self.a4_width = 210  # mm
        self.a4_height = 297  # mm
        self.overlap = 20  # 2 cm overlap

    def parse_plt(self):
        """PLT dosyasını oku ve komutları ayrıştır"""
        with open(self.plt_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        content = content.replace('\n', '').replace('\r', '').replace(' ', '')
        pattern = r'([A-Z]{2})([^A-Z]*)'
        commands = re.findall(pattern, content)
        return commands

    def convert(self):
        """PLT'den A4 PDF'lere dönüştür (overlap ile)"""
        print(f"PLT dosyası okunuyor: {self.plt_file}")
        commands = self.parse_plt()

        if not commands:
            print("Hata: PLT dosyasında geçerli komut bulunamadı!")
            return False

        # Tüm çizgileri topla
        lines = []
        x, y = 0, 0
        pen_down = False

        for cmd, params_str in commands:
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

            if cmd == 'PU':
                pen_down = False
                if len(params) >= 2:
                    x, y = params[0], params[1]

            elif cmd == 'PD':
                pen_down = True
                if len(params) >= 2:
                    new_x, new_y = params[0], params[1]
                    lines.append(((x, y), (new_x, new_y)))
                    x, y = new_x, new_y

                    i = 2
                    while i + 1 < len(params):
                        new_x = params[i]
                        new_y = params[i + 1]
                        lines.append(((x, y), (new_x, new_y)))
                        x, y = new_x, new_y
                        i += 2

            elif cmd == 'PA':
                for i in range(0, len(params), 2):
                    if i + 1 < len(params):
                        new_x, new_y = params[i], params[i + 1]
                        if pen_down:
                            lines.append(((x, y), (new_x, new_y)))
                        x, y = new_x, new_y

            elif cmd == 'PR':
                for i in range(0, len(params), 2):
                    if i + 1 < len(params):
                        new_x, new_y = x + params[i], y + params[i + 1]
                        if pen_down:
                            lines.append(((x, y), (new_x, new_y)))
                        x, y = new_x, new_y

            elif cmd == 'IN':
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

        # Normalize et
        normalized_lines = []
        for (x1, y1), (x2, y2) in lines:
            nx1 = (x1 - min_x) * self.unit_to_mm
            nx2 = (x2 - min_x) * self.unit_to_mm
            ny1 = (y1 - min_y) * self.unit_to_mm
            ny2 = (y2 - min_y) * self.unit_to_mm
            normalized_lines.append(((nx1, ny1), (nx2, ny2)))

        width_mm = width_hpgl * self.unit_to_mm
        height_mm = height_hpgl * self.unit_to_mm

        print(f"Çizim boyutu: {width_mm:.1f} mm x {height_mm:.1f} mm")

        # Print ekranı mantığı: Her sayfa overlap kadar daha az ilerler
        # Örnek: A4 210mm, overlap 20mm → her sayfa 190mm ilerler
        step_width = self.a4_width - self.overlap  # 190 mm
        step_height = self.a4_height - self.overlap  # 277 mm

        cols = int((width_mm + step_width - 1) / step_width)
        rows = int((height_mm + step_height - 1) / step_height)

        print(f"A4 grid: {rows} satır x {cols} sütun = {rows * cols} sayfa")
        print(f"2cm overlap ile...")

        # PDF oluştur
        c = canvas.Canvas(self.pdf_file, pagesize=A4)
        page_count = 0

        for row in range(rows):
            for col in range(cols):
                # Her sayfa step kadar ilerler, ama tam A4 gösterir
                page_start_x = col * step_width
                page_start_y = row * step_height
                page_end_x = page_start_x + self.a4_width
                page_end_y = page_start_y + self.a4_height

                # Bu sayfadaki çizgileri filtrele
                page_lines = []
                for (x1, y1), (x2, y2) in normalized_lines:
                    if (min(x1, x2) < page_end_x and max(x1, x2) > page_start_x and
                        min(y1, y2) < page_end_y and max(y1, y2) > page_start_y):
                        page_lines.append(((x1, y1), (x2, y2)))

                if not page_lines:
                    continue

                page_count += 1

                # Çizgileri çiz
                c.setStrokeColorRGB(0, 0, 0)
                c.setLineWidth(0.5)
                c.setLineCap(1)
                c.setLineJoin(1)

                for (x1, y1), (x2, y2) in page_lines:
                    px1 = (x1 - page_start_x) * mm
                    py1 = (y1 - page_start_y) * mm
                    px2 = (x2 - page_start_x) * mm
                    py2 = (y2 - page_start_y) * mm
                    c.line(px1, py1, px2, py2)

                # Overlap sınırlarını kesikli çizgilerle göster
                c.setStrokeColorRGB(0.7, 0.7, 0.7)
                c.setLineWidth(0.3)
                c.setDash([3, 3])

                # Sağda sayfa varsa, sağ kenarda overlap çizgisi
                if col < cols - 1:
                    x_pos = (self.a4_width - self.overlap) * mm
                    c.line(x_pos, 0, x_pos, self.a4_height * mm)

                # Altta sayfa varsa, alt kenarda overlap çizgisi
                if row < rows - 1:
                    y_pos = self.overlap * mm
                    c.line(0, y_pos, self.a4_width * mm, y_pos)

                c.setDash()

                # Sayfa etiketi
                c.setFillColorRGB(0, 0, 0)
                c.setFont("Helvetica-Bold", 12)
                page_label = f"{chr(65 + row)}{col + 1}"
                c.drawString(5 * mm, (self.a4_height - 5) * mm, page_label)

                # Bilgi
                c.setFont("Helvetica", 7)
                info = f"Sayfa {page_count} | 2cm overlap"
                c.drawString(5 * mm, 5 * mm, info)

                c.showPage()

        c.save()
        print(f"{page_count} sayfalık PDF başarıyla oluşturuldu: {self.pdf_file}")
        return True


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, 'input_plt')
    output_dir = os.path.join(script_dir, 'output_pdf')

    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print(f"'{input_dir}' klasörü oluşturuldu.")
        sys.exit(0)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plt_files = glob(os.path.join(input_dir, '*.plt')) + glob(os.path.join(input_dir, '*.PLT'))

    if not plt_files:
        print(f"'{input_dir}' klasöründe PLT dosyası bulunamadı!")
        sys.exit(1)

    print(f"\n{len(plt_files)} adet PLT dosyası bulundu.\n")
    print("=" * 60)

    success_count = 0
    fail_count = 0

    for plt_file in plt_files:
        filename = os.path.basename(plt_file)
        pdf_filename = os.path.splitext(filename)[0] + '_A4_overlap.pdf'
        pdf_file = os.path.join(output_dir, pdf_filename)

        print(f"\n[{plt_files.index(plt_file) + 1}/{len(plt_files)}] İşleniyor: {filename}")
        print("-" * 60)

        converter = PLTtoPDFA4OverlayConverter(plt_file, pdf_file)

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

    print("\n" + "=" * 60)
    print(f"\nDÖNÜŞTÜRME ÖZETİ:")
    print(f"  Toplam dosya: {len(plt_files)}")
    print(f"  Başarılı: {success_count}")
    print(f"  Başarısız: {fail_count}")
    print(f"\nÇıktı klasörü: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
