import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image

from app.core.pdf_exporter import PDFExporter


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
