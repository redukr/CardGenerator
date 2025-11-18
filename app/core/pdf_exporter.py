import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

class PDFExporter:
    def __init__(self, dpi=300, margin_mm=20):
        self.dpi = dpi
        self.margin_mm = margin_mm

    def mm_to_px(self, mm_value):
        return int((mm_value / 25.4) * self.dpi)

    def export_pdf(self, image_paths, output_path, card_width_mm=40, card_height_mm=62, bleed_mm=0):
        if not image_paths:
            raise ValueError("Немає зображень для експорту у PDF.")

        page_width, page_height = A4  # у пунктах reportlab
        margin = self.margin_mm * mm

        card_w_px = self.mm_to_px(card_width_mm + bleed_mm * 2)
        card_h_px = self.mm_to_px(card_height_mm + bleed_mm * 2)

        card_w_pt = card_width_mm * mm
        card_h_pt = card_height_mm * mm

        c = canvas.Canvas(output_path, pagesize=A4)

        x = margin
        y = page_height - margin - card_h_pt

        cards_per_row = int((page_width - margin * 2) // card_w_pt)
        cards_per_col = int((page_height - margin * 2) // card_h_pt)

        counter = 0

        for img_path in image_paths:
            if not os.path.exists(img_path):
                continue

            temp_img = Image.open(img_path)
            temp_img_path = img_path + "_tmp_for_pdf.png"
            temp_img.save(temp_img_path, dpi=(300,300))

            c.drawImage(
                temp_img_path,
                x, y,
                width=card_w_pt,
                height=card_h_pt,
                preserveAspectRatio=True,
                mask='auto'
            )

            os.remove(temp_img_path)

            x += card_w_pt
            counter += 1

            if counter % cards_per_row == 0:
                x = margin
                y -= card_h_pt

                if y < margin:
                    c.showPage()
                    y = page_height - margin - card_h_pt

        c.save()

        return output_path
