"""Property panel for editing card template elements."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFontComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .card_scene_view import CardSceneView


class PropertyPanel(QWidget):
    """Right side property inspector linked to CardSceneView."""

    def __init__(self, scene_view: CardSceneView, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.scene_view = scene_view
        self.current_item_id: Optional[str] = None
        self._updating = False

        self.setMinimumWidth(320)
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)

        self.layout_header = QLabel("Template Layout")
        self.layout_header.setStyleSheet("font-weight: 600; font-size: 16px;")
        self.layout.addWidget(self.layout_header)

        self.layout_path_label = QLineEdit(self.scene_view.get_layout_path())
        self.layout_path_label.setReadOnly(True)
        self.layout_path_label.setStyleSheet("font-size: 11px; color: #999;")
        self.layout.addWidget(self.layout_path_label)

        layout_btn_row = QHBoxLayout()
        self.btn_save_layout = QPushButton("💾 Зберегти")
        self.btn_save_layout.clicked.connect(self.scene_view.save_layout)
        layout_btn_row.addWidget(self.btn_save_layout)
        self.btn_save_as = QPushButton("Зберегти як…")
        self.btn_save_as.clicked.connect(self._save_layout_as)
        layout_btn_row.addWidget(self.btn_save_as)
        self.btn_load_layout = QPushButton("Завантажити")
        self.btn_load_layout.clicked.connect(self._load_layout_dialog)
        layout_btn_row.addWidget(self.btn_load_layout)
        self.layout.addLayout(layout_btn_row)

        self.btn_background = QPushButton("Колір фону сцени")
        self.btn_background.clicked.connect(self._change_background)
        self.layout.addWidget(self.btn_background)

        self.item_title = QLabel("Елемент: —")
        self.item_title.setStyleSheet("font-weight: 600; margin-top: 12px;")
        self.layout.addWidget(self.item_title)

        form = QFormLayout()
        self.layout.addLayout(form)

        self.pos_x = QDoubleSpinBox()
        self.pos_x.setRange(-5000, 5000)
        self.pos_y = QDoubleSpinBox()
        self.pos_y.setRange(-5000, 5000)
        self.pos_x.valueChanged.connect(self._update_position)
        self.pos_y.valueChanged.connect(self._update_position)
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(self.pos_x)
        pos_layout.addWidget(self.pos_y)
        form.addRow("X / Y", pos_layout)

        self.size_w = QDoubleSpinBox()
        self.size_h = QDoubleSpinBox()
        for spin in (self.size_w, self.size_h):
            spin.setRange(0, 5000)
            spin.valueChanged.connect(self._update_size)
        size_layout = QHBoxLayout()
        size_layout.addWidget(self.size_w)
        size_layout.addWidget(self.size_h)
        form.addRow("W / H", size_layout)

        self.text_width_spin = QDoubleSpinBox()
        self.text_width_spin.setRange(0, 2000)
        self.text_width_spin.valueChanged.connect(self._update_text_width)
        form.addRow("Text width", self.text_width_spin)

        self.font_family = QFontComboBox()
        self.font_family.currentFontChanged.connect(self._update_font)
        form.addRow("Шрифт", self.font_family)

        self.font_size = QSpinBox()
        self.font_size.setRange(6, 120)
        self.font_size.valueChanged.connect(self._update_font)
        form.addRow("Розмір", self.font_size)

        font_flags = QHBoxLayout()
        self.chk_bold = QCheckBox("B")
        self.chk_bold.setStyleSheet("font-weight: 800;")
        self.chk_bold.toggled.connect(self._update_font)
        self.chk_italic = QCheckBox("I")
        self.chk_italic.setStyleSheet("font-style: italic;")
        self.chk_italic.toggled.connect(self._update_font)
        self.chk_underline = QCheckBox("U")
        self.chk_underline.setStyleSheet("text-decoration: underline;")
        self.chk_underline.toggled.connect(self._update_font)
        font_flags.addWidget(self.chk_bold)
        font_flags.addWidget(self.chk_italic)
        font_flags.addWidget(self.chk_underline)
        form.addRow("Стиль", font_flags)

        self.btn_font_color = QPushButton("Колір тексту")
        self.btn_font_color.clicked.connect(self._change_text_color)
        form.addRow("Колір", self.btn_font_color)

        self.outline_width = QDoubleSpinBox()
        self.outline_width.setRange(0, 20)
        self.outline_width.setSingleStep(0.5)
        self.outline_width.valueChanged.connect(self._update_outline)
        self.btn_outline_color = QPushButton("Колір обводки")
        self.btn_outline_color.clicked.connect(self._change_outline_color)
        outline_layout = QHBoxLayout()
        outline_layout.addWidget(self.outline_width)
        outline_layout.addWidget(self.btn_outline_color)
        form.addRow("Обводка", outline_layout)

        opacity_row = QHBoxLayout()
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.valueChanged.connect(self._update_opacity)
        self.opacity_value = QLabel("100%")
        opacity_row.addWidget(self.opacity_slider)
        opacity_row.addWidget(self.opacity_value)
        form.addRow("Прозорість", opacity_row)

        lock_row = QHBoxLayout()
        self.chk_lock_item = QCheckBox("Lock move")
        self.chk_lock_item.toggled.connect(self._toggle_item_lock)
        self.chk_lock_x = QCheckBox("Lock X")
        self.chk_lock_x.toggled.connect(self._toggle_axis_lock)
        self.chk_lock_y = QCheckBox("Lock Y")
        self.chk_lock_y.toggled.connect(self._toggle_axis_lock)
        lock_row.addWidget(self.chk_lock_item)
        lock_row.addWidget(self.chk_lock_x)
        lock_row.addWidget(self.chk_lock_y)
        form.addRow("Блокування", lock_row)

        self.btn_change_icon = QPushButton("Змінити іконку / PNG")
        self.btn_change_icon.clicked.connect(self._change_pixmap)
        form.addRow("Зображення", self.btn_change_icon)

        z_row = QHBoxLayout()
        self.z_spin = QDoubleSpinBox()
        self.z_spin.setRange(-50, 50)
        self.z_spin.valueChanged.connect(self._update_z_value)
        z_row.addWidget(self.z_spin)
        form.addRow("Z-index", z_row)

        shadow_group = QGroupBox("Drop shadow")
        shadow_layout = QFormLayout(shadow_group)
        self.shadow_color_btn = QPushButton("Колір")
        self.shadow_color_btn.clicked.connect(self._change_shadow_color)
        self.shadow_offset_x = QDoubleSpinBox()
        self.shadow_offset_y = QDoubleSpinBox()
        self.shadow_offset_x.setRange(-100, 100)
        self.shadow_offset_y.setRange(-100, 100)
        self.shadow_offset_x.valueChanged.connect(self._update_shadow)
        self.shadow_offset_y.valueChanged.connect(self._update_shadow)
        self.shadow_blur = QDoubleSpinBox()
        self.shadow_blur.setRange(0, 100)
        self.shadow_blur.valueChanged.connect(self._update_shadow)
        shadow_layout.addRow("Колір", self.shadow_color_btn)
        offset_row = QHBoxLayout()
        offset_row.addWidget(self.shadow_offset_x)
        offset_row.addWidget(self.shadow_offset_y)
        shadow_layout.addRow("Зміщення", offset_row)
        shadow_layout.addRow("Blur", self.shadow_blur)
        self.layout.addWidget(shadow_group)

        self.scene_view.selectionChanged.connect(self._on_item_selected)
        self.scene_view.itemUpdated.connect(self._on_item_updated)
        self.scene_view.layoutLoaded.connect(self._on_layout_loaded)

        self._current_outline_color = QColor("#FFFFFF")
        self._current_font_color = QColor("#FFFFFF")
        self._current_shadow_color = QColor("#000000")

    # ------------------------------------------------------------------
    def _on_layout_loaded(self, layout_dict: dict):
        self.layout_path_label.setText(self.scene_view.get_layout_path())

    # ------------------------------------------------------------------
    def _on_item_selected(self, item_id: str):
        self.current_item_id = item_id
        self._populate_from_config(self.scene_view.get_item_config(item_id))

    # ------------------------------------------------------------------
    def _on_item_updated(self, item_id: str, cfg: dict):
        if self.current_item_id != item_id:
            return
        self._populate_from_config(cfg)

    # ------------------------------------------------------------------
    def _populate_from_config(self, cfg: dict):
        self._updating = True
        try:
            self.item_title.setText(f"Елемент: {self.current_item_id}")
            pos = cfg.get("pos", {})
            self.pos_x.setValue(pos.get("x", 0))
            self.pos_y.setValue(pos.get("y", 0))
            size = cfg.get("size", {})
            self.size_w.setValue(size.get("w", 0))
            self.size_h.setValue(size.get("h", 0))
            self.text_width_spin.setValue(cfg.get("text_width", 0))
            font_cfg = cfg.get("font", {})
            self.font_family.setCurrentFont(QFont(font_cfg.get("family", "Arial")))
            if font_cfg.get("size"):
                self.font_size.setValue(int(font_cfg.get("size", 12)))
            self.chk_bold.setChecked(font_cfg.get("bold", False))
            self.chk_italic.setChecked(font_cfg.get("italic", False))
            self.chk_underline.setChecked(font_cfg.get("underline", False))
            self._current_font_color = QColor(cfg.get("color", "#FFFFFF"))
            self.btn_font_color.setStyleSheet(f"background:{self._current_font_color.name()};")
            self.outline_width.setValue(cfg.get("shadow", {}).get("blur", 0) / 2)
            self._current_outline_color = QColor(cfg.get("shadow", {}).get("color", "#000000"))
            self.btn_outline_color.setStyleSheet(f"background:{self._current_outline_color.name()};")
            opacity = int(cfg.get("opacity", 1.0) * 100)
            self.opacity_slider.setValue(opacity)
            self.opacity_value.setText(f"{opacity}%")
            bindings = cfg.get("bindings", {})
            self.chk_lock_x.setChecked(bindings.get("lock_x", False))
            self.chk_lock_y.setChecked(bindings.get("lock_y", False))
            self.chk_lock_item.setChecked(cfg.get("locked", False))
            self.z_spin.setValue(cfg.get("z", 0))
            shadow = cfg.get("shadow", {})
            self._current_shadow_color = QColor(shadow.get("color", "#000000"))
            self.shadow_color_btn.setStyleSheet(f"background:{self._current_shadow_color.name()};")
            offset = shadow.get("offset", [0, 0])
            self.shadow_offset_x.setValue(offset[0])
            self.shadow_offset_y.setValue(offset[1])
            self.shadow_blur.setValue(shadow.get("blur", 0))
            item_type = cfg.get("type", "text")
            self._toggle_controls_for_type(item_type)
        finally:
            self._updating = False

    # ------------------------------------------------------------------
    def _toggle_controls_for_type(self, item_type: str):
        is_text = item_type == "text"
        self.text_width_spin.setEnabled(is_text)
        self.font_family.setEnabled(is_text)
        self.font_size.setEnabled(is_text)
        self.chk_bold.setEnabled(is_text)
        self.chk_italic.setEnabled(is_text)
        self.chk_underline.setEnabled(is_text)
        self.btn_font_color.setEnabled(is_text)
        self.outline_width.setEnabled(is_text)
        self.btn_outline_color.setEnabled(is_text)
        self.shadow_color_btn.setEnabled(is_text)
        self.shadow_offset_x.setEnabled(is_text)
        self.shadow_offset_y.setEnabled(is_text)
        self.shadow_blur.setEnabled(is_text)
        self.btn_change_icon.setEnabled(item_type in {"image", "pixmap", "icon"})
        self.size_w.setEnabled(item_type != "text")
        self.size_h.setEnabled(item_type != "text")

    # ------------------------------------------------------------------
    def _update_position(self):
        if self._updating or not self.current_item_id:
            return
        self.scene_view.update_item_position(
            self.current_item_id, (self.pos_x.value(), self.pos_y.value())
        )

    # ------------------------------------------------------------------
    def _update_size(self):
        if self._updating or not self.current_item_id:
            return
        self.scene_view.update_item_size(
            self.current_item_id, (self.size_w.value(), self.size_h.value())
        )

    # ------------------------------------------------------------------
    def _update_text_width(self, value: float):
        if self._updating or not self.current_item_id:
            return
        self.scene_view.update_text_width(self.current_item_id, value)

    # ------------------------------------------------------------------
    def _update_font(self, *_):
        if self._updating or not self.current_item_id:
            return
        font = QFont(self.font_family.currentFont())
        font.setPointSize(self.font_size.value())
        font.setBold(self.chk_bold.isChecked())
        font.setItalic(self.chk_italic.isChecked())
        font.setUnderline(self.chk_underline.isChecked())
        self.scene_view.update_font(self.current_item_id, font)

    # ------------------------------------------------------------------
    def _change_text_color(self):
        color = QColorDialog.getColor(self._current_font_color, self)
        if not color.isValid() or not self.current_item_id:
            return
        self._current_font_color = color
        self.btn_font_color.setStyleSheet(f"background:{color.name()};")
        self.scene_view.update_text_color(self.current_item_id, color)

    # ------------------------------------------------------------------
    def _change_outline_color(self):
        color = QColorDialog.getColor(self._current_outline_color, self)
        if not color.isValid():
            return
        self._current_outline_color = color
        self.btn_outline_color.setStyleSheet(f"background:{color.name()};")
        self._update_outline()

    # ------------------------------------------------------------------
    def _update_outline(self):
        if self._updating or not self.current_item_id:
            return
        self.scene_view.apply_outline(
            self.current_item_id, self._current_outline_color, self.outline_width.value()
        )

    # ------------------------------------------------------------------
    def _update_opacity(self, value: int):
        if self._updating or not self.current_item_id:
            return
        self.opacity_value.setText(f"{value}%")
        self.scene_view.update_item_opacity(self.current_item_id, value / 100)

    # ------------------------------------------------------------------
    def _toggle_item_lock(self, checked: bool):
        if self._updating or not self.current_item_id:
            return
        self.scene_view.set_item_locked(self.current_item_id, checked)

    # ------------------------------------------------------------------
    def _toggle_axis_lock(self, _):
        if self._updating or not self.current_item_id:
            return
        self.scene_view.set_axis_lock(
            self.current_item_id,
            lock_x=self.chk_lock_x.isChecked(),
            lock_y=self.chk_lock_y.isChecked(),
        )

    # ------------------------------------------------------------------
    def _change_pixmap(self):
        if not self.current_item_id:
            return
        path, _ = QFileDialog.getOpenFileName(self, "Обрати PNG", "", "Images (*.png *.jpg *.webp)")
        if not path:
            return
        self.scene_view.change_icon_source(self.current_item_id, path)

    # ------------------------------------------------------------------
    def _update_z_value(self):
        if self._updating or not self.current_item_id:
            return
        self.scene_view.update_item_zvalue(self.current_item_id, self.z_spin.value())

    # ------------------------------------------------------------------
    def _change_shadow_color(self):
        color = QColorDialog.getColor(self._current_shadow_color, self)
        if not color.isValid():
            return
        self._current_shadow_color = color
        self.shadow_color_btn.setStyleSheet(f"background:{color.name()};")
        self._update_shadow()

    # ------------------------------------------------------------------
    def _update_shadow(self):
        if self._updating or not self.current_item_id:
            return
        self.scene_view.apply_shadow(
            self.current_item_id,
            self._current_shadow_color,
            (self.shadow_offset_x.value(), self.shadow_offset_y.value()),
            self.shadow_blur.value(),
        )

    # ------------------------------------------------------------------
    def _change_background(self):
        color = QColorDialog.getColor(parent=self)
        if not color.isValid():
            return
        self.scene_view.set_background_color(color)

    # ------------------------------------------------------------------
    def _save_layout_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Зберегти layout", "template_layout.json", "JSON (*.json)")
        if not path:
            return
        self.scene_view.save_layout(path)
        self.layout_path_label.setText(path)

    # ------------------------------------------------------------------
    def _load_layout_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Обрати layout", "", "JSON (*.json)")
        if not path:
            return
        self.scene_view.load_template(path)
        self.layout_path_label.setText(path)
