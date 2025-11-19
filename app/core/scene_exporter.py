"""Helper that reuses CardSceneView to export deck PNGs."""

from __future__ import annotations

import os
from typing import Callable, Optional

from PySide6.QtGui import QPixmap

from widgets.card_scene_view import CardSceneView

from .models import DeckModel


class SceneExporter:
    def __init__(self, scene_view: CardSceneView):
        self.scene_view = scene_view

    def export_deck(
        self,
        deck: DeckModel,
        export_dir: str,
        frame_path: Optional[str] = None,
        progress: Optional[Callable[[int, int, str], None]] = None,
    ) -> str:
        os.makedirs(export_dir, exist_ok=True)
        if frame_path:
            pixmap = QPixmap(frame_path)
            if not pixmap.isNull():
                self.scene_view.set_frame_pixmap(pixmap)
        for idx, card in enumerate(deck.cards):
            self.scene_view.apply_card_data(card.payload, deck.deck_color)
            safe_name = card.name.replace("/", "_").replace(" ", "_")
            out_path = os.path.join(export_dir, f"{safe_name}.png")
            self.scene_view.export_to_png(out_path)
            if progress:
                progress(idx + 1, len(deck), out_path)
        return export_dir
