from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QPixmap
from PySide6.QtWidgets import (
    QColorDialog,
    QFileDialog,
    QFontComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtWidgets import QGraphicsItem, QGraphicsPixmapItem, QGraphicsTextItem


class PropertyPanel(QWidget):
    """Side panel with controls for the currently selected scene item."""

    selected_item_changed = Signal(object)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._current_item: Optional[QGraphicsItem] = None
        self._updating = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        self.labelType = QLabel("Елемент: [не вибрано]")
        layout.addWidget(self.labelType)

        # font controls ---------------------------------------------------
        layout.addWidget(QLabel("Шрифт"))
        self.fontCombo = QFontComboBox()
        layout.addWidget(self.fontCombo)

        layout.addWidget(QLabel("Розмір"))
        self.fontSize = QSpinBox()
        self.fontSize.setRange(6, 120)
        layout.addWidget(self.fontSize)

        self.colorButton = QPushButton("Колір тексту")
        layout.addWidget(self.colorButton)

        # coordinates -----------------------------------------------------
        coords_layout = QGridLayout()
        coords_layout.addWidget(QLabel("X"), 0, 0)
        self.posX = QSpinBox()
        self.posX.setRange(-2000, 4000)
        coords_layout.addWidget(self.posX, 0, 1)
        coords_layout.addWidget(QLabel("Y"), 1, 0)
        self.posY = QSpinBox()
        self.posY.setRange(-2000, 4000)
        coords_layout.addWidget(self.posY, 1, 1)
        layout.addLayout(coords_layout)

        # opacity ---------------------------------------------------------
        self.opacityLabel = QLabel("Прозорість: 100%")
        layout.addWidget(self.opacityLabel)
        self.opacitySlider = QSlider(Qt.Horizontal)
        self.opacitySlider.setRange(0, 100)
        self.opacitySlider.setValue(100)
        layout.addWidget(self.opacitySlider)

        # z-order ---------------------------------------------------------
        layer_row = QHBoxLayout()
        self.btnLayerUp = QPushButton("На верх")
        self.btnLayerDown = QPushButton("На низ")
        layer_row.addWidget(self.btnLayerUp)
        layer_row.addWidget(self.btnLayerDown)
        layout.addLayout(layer_row)

        # icon + locking --------------------------------------------------
        self.btnReplaceIcon = QPushButton("Замінити іконку")
        layout.addWidget(self.btnReplaceIcon)

        self.lockButton = QPushButton("🔓 Рухомий")
        self.lockButton.setCheckable(True)
        layout.addWidget(self.lockButton)

        layout.addStretch()

        # register slots --------------------------------------------------
        self.fontCombo.currentFontChanged.connect(self._on_font_changed)
        self.fontSize.valueChanged.connect(self._on_font_size_changed)
        self.colorButton.clicked.connect(self._choose_color)
        self.posX.valueChanged.connect(self._on_position_changed)
        self.posY.valueChanged.connect(self._on_position_changed)
        self.opacitySlider.valueChanged.connect(self._on_opacity_changed)
        self.btnLayerUp.clicked.connect(lambda: self._adjust_layer(1))
        self.btnLayerDown.clicked.connect(lambda: self._adjust_layer(-1))
        self.btnReplaceIcon.clicked.connect(self._replace_pixmap)
        self.lockButton.toggled.connect(self._toggle_lock)

        self._set_all_controls_enabled(False)

    # ------------------------------------------------------------------
    def bind_item(self, item: Optional[QGraphicsItem]) -> None:
        """Attach scene item to the panel controls."""
        self._current_item = item
        self._updating = True

        if not item:
            self.labelType.setText("Елемент: [не вибрано]")
            self._set_all_controls_enabled(False)
            self.selected_item_changed.emit(None)
            self._updating = False
            return

        self.labelType.setText(f"Елемент: {type(item).__name__}")
        self._set_all_controls_enabled(True)
        self._update_type_specific_states(item)

        pos = item.pos()
        self.posX.setValue(int(pos.x()))
        self.posY.setValue(int(pos.y()))

        self.opacitySlider.setValue(int(item.opacity() * 100))
        self._update_opacity_label()

        if isinstance(item, QGraphicsTextItem):
            font = item.font()
            self.fontCombo.setCurrentFont(font)
            self.fontSize.setValue(max(font.pointSize(), 6))
            self._update_color_button(item.defaultTextColor())
        else:
            self.fontCombo.setCurrentFont(QFont())
            self.fontSize.setValue(12)
            self._update_color_button(QColor("#999"))

        locked = bool(item.data(Qt.UserRole))
        self.lockButton.blockSignals(True)
        self.lockButton.setChecked(locked)
        self._update_lock_button_text(locked)
        self.lockButton.blockSignals(False)

        self.selected_item_changed.emit(item)
        self._updating = False

    # ------------------------------------------------------------------
    def _set_all_controls_enabled(self, enabled: bool) -> None:
        widgets = [
            self.fontCombo,
            self.fontSize,
            self.colorButton,
            self.posX,
            self.posY,
            self.opacitySlider,
            self.btnLayerUp,
            self.btnLayerDown,
            self.btnReplaceIcon,
            self.lockButton,
        ]
        for widget in widgets:
            widget.setEnabled(enabled)
        if not enabled:
            self.opacityLabel.setText("Прозорість: 100%")

    # ------------------------------------------------------------------
    def _update_type_specific_states(self, item: QGraphicsItem) -> None:
        is_text = isinstance(item, QGraphicsTextItem)
        self.fontCombo.setEnabled(is_text)
        self.fontSize.setEnabled(is_text)
        self.colorButton.setEnabled(is_text)

        is_pixmap = isinstance(item, QGraphicsPixmapItem)
        self.btnReplaceIcon.setEnabled(is_pixmap)

    # ------------------------------------------------------------------
    def _on_font_changed(self, font: QFont) -> None:
        if self._updating:
            return
        text_item = self._get_text_item()
        if not text_item:
            return
        current_font = text_item.font()
        current_font.setFamily(font.family())
        text_item.setFont(current_font)

    # ------------------------------------------------------------------
    def _on_font_size_changed(self, size: int) -> None:
        if self._updating:
            return
        text_item = self._get_text_item()
        if not text_item:
            return
        font = text_item.font()
        font.setPointSize(size)
        text_item.setFont(font)

    # ------------------------------------------------------------------
    def _choose_color(self) -> None:
        text_item = self._get_text_item()
        if not text_item:
            return
        color = QColorDialog.getColor(text_item.defaultTextColor(), self)
        if color.isValid():
            text_item.setDefaultTextColor(color)
            self._update_color_button(color)

    # ------------------------------------------------------------------
    def _update_color_button(self, color: QColor) -> None:
        self.colorButton.setStyleSheet(
            f"background-color: {color.name()}; color: {'black' if color.lightness() > 128 else 'white'}"
        )

    # ------------------------------------------------------------------
    def _on_position_changed(self) -> None:
        if self._updating or not self._current_item:
            return
        self._current_item.setPos(self.posX.value(), self.posY.value())

    # ------------------------------------------------------------------
    def _on_opacity_changed(self, value: int) -> None:
        if self._updating or not self._current_item:
            return
        self._current_item.setOpacity(value / 100.0)
        self._update_opacity_label()

    # ------------------------------------------------------------------
    def _update_opacity_label(self) -> None:
        self.opacityLabel.setText(f"Прозорість: {self.opacitySlider.value()}%")

    # ------------------------------------------------------------------
    def _adjust_layer(self, delta: int) -> None:
        if not self._current_item:
            return
        self._current_item.setZValue(self._current_item.zValue() + delta)

    # ------------------------------------------------------------------
    def _replace_pixmap(self) -> None:
        pixmap_item = self._get_pixmap_item()
        if not pixmap_item:
            return
        start_dir = str(Path.home())
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Обрати іконку",
            start_dir,
            "Зображення (*.png *.jpg *.jpeg *.webp)"
        )
        if not path:
            return
        pixmap = QPixmap(path)
        if pixmap.isNull():
            return
        pixmap_item.setPixmap(pixmap)

    # ------------------------------------------------------------------
    def _toggle_lock(self, checked: bool) -> None:
        if not self._current_item:
            return
        self._current_item.setFlag(QGraphicsItem.ItemIsMovable, not checked)
        self._current_item.setFlag(QGraphicsItem.ItemIsSelectable, not checked)
        self._current_item.setData(Qt.UserRole, int(checked))
        self._update_lock_button_text(checked)

    # ------------------------------------------------------------------
    def _update_lock_button_text(self, locked: bool) -> None:
        self.lockButton.setText("🔒 Заблоковано" if locked else "🔓 Рухомий")

    # ------------------------------------------------------------------
    def _get_text_item(self) -> Optional[QGraphicsTextItem]:
        if isinstance(self._current_item, QGraphicsTextItem):
            return self._current_item
        return None

    # ------------------------------------------------------------------
    def _get_pixmap_item(self) -> Optional[QGraphicsPixmapItem]:
        if isinstance(self._current_item, QGraphicsPixmapItem):
            return self._current_item
        return None
