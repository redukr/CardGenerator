import os
import sys
from pathlib import Path
from math import isclose

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image
from reportlab.lib.units import mm

from app.core.pdf_exporter import PDFExporter
import app.core.pdf_exporter as pdf_exporter


def _create_dummy_card_image(directory: Path, name: str = "card.png") -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    image_path = directory / name
    Image.new("RGB", (100, 100), color=(255, 0, 0)).save(image_path)
    return image_path


def test_export_pdf_handles_large_card_width(tmp_path):
    cards_dir = tmp_path / "cards"
    _create_dummy_card_image(cards_dir)

    exporter = PDFExporter()
    output_pdf = tmp_path / "output.pdf"

    result_path = exporter.export_pdf(
        str(cards_dir),
        str(output_pdf),
        card_width_mm=1000,  # Deliberately wider than the printable area
        card_height_mm=62,
    )

    assert os.path.exists(result_path)

    with open(result_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()

    assert b"/Type /Page" in pdf_bytes
    assert b"/XObject" in pdf_bytes


def test_export_pdf_respects_bleed_dpi_and_order(tmp_path, monkeypatch):
    cards_dir = tmp_path / "cards"
    _create_dummy_card_image(cards_dir, "b.png")
    _create_dummy_card_image(cards_dir, "a.png")

    saved_dpis = []
    original_save = Image.Image.save

    def tracking_save(self, fp, *args, **kwargs):
        if str(fp).endswith("_tmp_for_pdf.png"):
            saved_dpis.append(kwargs.get("dpi"))
        return original_save(self, fp, *args, **kwargs)

    monkeypatch.setattr(Image.Image, "save", tracking_save, raising=False)

    draw_calls = []

    class FakeCanvas:
        def __init__(self, *args, **kwargs):
            self.calls = draw_calls

        def drawImage(self, path, x, y, width, height, preserveAspectRatio=True, mask="auto"):
            self.calls.append({
                "path": path,
                "width": width,
                "height": height,
            })

        def showPage(self):
            self.calls.append({"action": "showPage"})

        def save(self):
            self.calls.append({"action": "save"})

    monkeypatch.setattr(pdf_exporter.canvas, "Canvas", lambda *args, **kwargs: FakeCanvas(*args, **kwargs))

    exporter = PDFExporter(dpi=200)
    exporter.export_pdf(str(cards_dir), str(tmp_path / "output.pdf"), card_width_mm=40, card_height_mm=62, bleed_mm=5)

    draw_paths = [Path(call["path"]).name.replace("_tmp_for_pdf.png", "") for call in draw_calls if "path" in call]
    assert draw_paths == ["a.png", "b.png"]

    first_draw = next(call for call in draw_calls if "width" in call)
    expected_width = (40 + 2 * 5) * mm
    expected_height = (62 + 2 * 5) * mm
    assert isclose(first_draw["width"], expected_width)
    assert isclose(first_draw["height"], expected_height)

    assert saved_dpis == [(200, 200), (200, 200)]
