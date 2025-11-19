import os
import sys
import tempfile
import unittest
from types import ModuleType


if "widgets.card_scene_view" not in sys.modules:
    widgets_pkg = ModuleType("widgets")
    card_scene_module = ModuleType("widgets.card_scene_view")

    class _StubCardSceneView:
        def __init__(self, *args, **kwargs):
            pass

        def apply_card_data(self, payload, deck_color):
            pass

        def set_frame_pixmap(self, pixmap):
            pass

        def export_to_png(self, path):
            pass

    card_scene_module.CardSceneView = _StubCardSceneView
    widgets_pkg.card_scene_view = card_scene_module
    sys.modules["widgets"] = widgets_pkg
    sys.modules["widgets.card_scene_view"] = card_scene_module

if "PySide6" not in sys.modules:
    pyside6 = ModuleType("PySide6")
    qtgui = ModuleType("PySide6.QtGui")

    class _StubQPixmap:
        def __init__(self, *_args, **_kwargs):
            self._null = True

        def isNull(self):
            return self._null

    qtgui.QPixmap = _StubQPixmap
    pyside6.QtGui = qtgui
    sys.modules["PySide6"] = pyside6
    sys.modules["PySide6.QtGui"] = qtgui

from app.core.models import CardModel, DeckModel
from app.core.scene_exporter import SceneExporter


class DummySceneView:
    def __init__(self):
        self.exported = []

    def apply_card_data(self, payload, deck_color):
        pass

    def set_frame_pixmap(self, pixmap):
        pass

    def export_to_png(self, path):
        self.exported.append(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(b"PNG")


class SceneExporterTests(unittest.TestCase):
    def test_duplicate_names_export_unique_pngs(self):
        deck = DeckModel(
            name="Test Deck",
            path="",
            deck_color="#FFFFFF",
            cards=[
                CardModel(index=0, payload={"name": "Duplicate/Name"}),
                CardModel(index=1, payload={"name": "Duplicate/Name"}),
            ],
        )
        exporter = SceneExporter(DummySceneView())
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter.export_deck(deck, tmpdir)
            files = sorted(os.listdir(tmpdir))
            self.assertEqual(2, len(files))
            self.assertNotEqual(files[0], files[1])
            for filename in files:
                self.assertTrue(filename.startswith("duplicate_name-"))
                self.assertTrue(filename.endswith(".png"))


if __name__ == "__main__":
    unittest.main()
