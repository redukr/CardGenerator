"""Interactive QGraphicsView preview/editor for card templates."""

from __future__ import annotations

import json
import os
from typing import Dict, Optional

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPen, QBrush, QPainter, QPixmap
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
)


class TemplateBlockItem(QGraphicsRectItem):
    """Simple draggable block that represents template areas."""

    def __init__(self, name: str, block: dict, parent: Optional[QGraphicsItem] = None):
        rect = QRectF(0, 0, block.get("w", 50), block.get("h", 20))
        super().__init__(rect, parent)

        self.block_name = name
        self.setPos(block.get("x", 0), block.get("y", 0))
        self.setBrush(QColor(0, 170, 255, 30))
        self.setPen(QPen(QColor(0, 170, 255), 1, Qt.DashLine))
        self.setZValue(10)
        self.setFlags(
            QGraphicsItem.ItemIsMovable
            | QGraphicsItem.ItemIsSelectable
            | QGraphicsItem.ItemSendsGeometryChanges
        )

        label = QGraphicsSimpleTextItem(name, self)
        label.setBrush(QColor(0, 170, 255))
        label.setPos(4, 4)

    # ------------------------------------------------------------------
    def to_payload(self) -> dict:
        rect = self.rect()
        return {
            "x": self.pos().x(),
            "y": self.pos().y(),
            "w": rect.width(),
            "h": rect.height(),
        }


class CardSceneView(QGraphicsView):
    """QGraphicsView-based preview/editor for card templates."""

    def __init__(self, template_path: Optional[str] = None, parent=None):
        super().__init__(parent)

        self._template_path = template_path
        self._template_items: Dict[str, TemplateBlockItem] = {}

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._scene.setSceneRect(-200, -200, 1600, 2200)

        self._background_item: Optional[QGraphicsPixmapItem] = None
        self._preview_item: Optional[QGraphicsPixmapItem] = None

        self._card_rect_item = QGraphicsRectItem(0, 0, 744, 1038)
        self._card_rect_item.setBrush(QBrush(Qt.NoBrush))
        self._card_rect_item.setPen(QPen(QColor(250, 250, 250), 2))
        self._card_rect_item.setZValue(5)
        self._scene.addItem(self._card_rect_item)

        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.setRenderHint(QPainter.TextAntialiasing, True)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setBackgroundBrush(QColor(26, 26, 26))

        self._zoom = 0
        self._fit_in_view_pending = True

        if template_path:
            self.load_template(template_path)

    # ------------------------------------------------------------------
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._fit_in_view_pending:
            self.fit_card_to_view()
            self._fit_in_view_pending = False

    # ------------------------------------------------------------------
    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            angle = event.angleDelta().y()
            factor = 1.1 if angle > 0 else 1 / 1.1
            self.scale(factor, factor)
            event.accept()
            return
        super().wheelEvent(event)

    # ------------------------------------------------------------------
    def drawBackground(self, painter: QPainter, rect: QRectF):
        painter.fillRect(rect, QColor(26, 26, 26))

        grid_size = 50
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)

        pen_minor = QPen(QColor(35, 35, 35))
        for x in range(left, int(rect.right()), grid_size):
            painter.setPen(pen_minor)
            painter.drawLine(x, rect.top(), x, rect.bottom())
        for y in range(top, int(rect.bottom()), grid_size):
            painter.setPen(pen_minor)
            painter.drawLine(rect.left(), y, rect.right(), y)

    # ------------------------------------------------------------------
    def fit_card_to_view(self):
        self.fitInView(self._card_rect_item, Qt.KeepAspectRatio)

    # ------------------------------------------------------------------
    def _sync_scene_rect(self, pixmap: QPixmap):
        rect = QRectF(0, 0, pixmap.width(), pixmap.height())
        self._card_rect_item.setRect(rect)
        self._scene.setSceneRect(rect.adjusted(-200, -200, 200, 200))
        self.fit_card_to_view()

    # ------------------------------------------------------------------
    def display_pixmap(self, pixmap: QPixmap):
        """Displays rendered card preview inside the scene."""
        if pixmap.isNull():
            return

        if not self._preview_item:
            self._preview_item = QGraphicsPixmapItem(pixmap)
            self._preview_item.setTransformationMode(Qt.SmoothTransformation)
            self._preview_item.setZValue(-10)
            self._scene.addItem(self._preview_item)
        else:
            self._preview_item.setPixmap(pixmap)

        self._sync_scene_rect(pixmap)

    # ------------------------------------------------------------------
    def display_background_pixmap(self, pixmap: QPixmap):
        """Displays selected frame/background while no preview exists."""
        if pixmap.isNull():
            return

        if not self._background_item:
            self._background_item = QGraphicsPixmapItem(pixmap)
            self._background_item.setTransformationMode(Qt.SmoothTransformation)
            self._background_item.setZValue(-20)
            self._scene.addItem(self._background_item)
        else:
            self._background_item.setPixmap(pixmap)

        self._sync_scene_rect(pixmap)

    # ------------------------------------------------------------------
    def clear_template(self):
        for item in self._template_items.values():
            self._scene.removeItem(item)
        self._template_items.clear()

    # ------------------------------------------------------------------
    def load_template(self, template_path: str):
        self._template_path = template_path
        self.clear_template()

        if not template_path or not os.path.exists(template_path):
            return

        with open(template_path, "r", encoding="utf-8") as f:
            template_data = json.load(f)

        for name, block in template_data.items():
            self.add_template_block(name, block)

    # ------------------------------------------------------------------
    def add_template_block(self, name: str, block: dict):
        block_item = TemplateBlockItem(name, block)
        self._scene.addItem(block_item)
        self._template_items[name] = block_item

    # ------------------------------------------------------------------
    def export_template(self) -> Dict[str, dict]:
        return {name: item.to_payload() for name, item in self._template_items.items()}

    # ------------------------------------------------------------------
    def save_template(self, output_path: Optional[str] = None):
        path = output_path or self._template_path
        if not path:
            return

        data = self.export_template()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # ------------------------------------------------------------------
    def refresh_from_template_dict(self, template_data: Dict[str, dict]):
        self.clear_template()
        for name, block in template_data.items():
            self.add_template_block(name, block)

