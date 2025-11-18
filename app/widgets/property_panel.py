import json
import os
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QSpinBox, QPushButton, QColorDialog, QComboBox
)
from PySide6.QtGui import QColor


class PropertyPanel(QWidget):
    def __init__(self, template_path, canvas):
        super().__init__()

        self.template_path = template_path
        self.canvas = canvas
        self.current_key = None

        self.template = self.load_template()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.lblTitle = QLabel("Властивості елемента")
        self.layout.addWidget(self.lblTitle)

        # X/Y
        self.x_spin = QSpinBox()
        self.y_spin = QSpinBox()

        self.x_spin.setMaximum(2000)
        self.y_spin.setMaximum(2000)

        xy_row = QHBoxLayout()
        xy_row.addWidget(QLabel("X:"))
        xy_row.addWidget(self.x_spin)
        xy_row.addWidget(QLabel("Y:"))
        xy_row.addWidget(self.y_spin)
        self.layout.addLayout(xy_row)

        # FONT SIZE
        self.font_size = QSpinBox()
        self.font_size.setMaximum(200)
        font_row = QHBoxLayout()
        font_row.addWidget(QLabel("Розмір шрифту:"))
        font_row.addWidget(self.font_size)
        self.layout.addLayout(font_row)

        # COLOR
        self.btnColor = QPushButton("Колір тексту")
        self.btnColor.clicked.connect(self.select_color)
        self.layout.addWidget(self.btnColor)

        # SAVE BUTTON
        self.btnSave = QPushButton("Зберегти шаблон")
        self.btnSave.clicked.connect(self.save_template)
        self.layout.addWidget(self.btnSave)

        # EVENTS
        self.x_spin.valueChanged.connect(self.update_item)
        self.y_spin.valueChanged.connect(self.update_item)
        self.font_size.valueChanged.connect(self.update_item)

        self.selected_color = "#FFFFFF"

    # ─────────────────────────────────────────────
    def load_template(self):
        if not os.path.exists(self.template_path):
            return {}
        with open(self.template_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ─────────────────────────────────────────────
    def select_color(self):
        c = QColorDialog.getColor()
        if c.isValid():
            self.selected_color = c.name()
            self.update_item()

    # ─────────────────────────────────────────────
    def set_item(self, key):
        """Отримує назву елемента із Canvas."""
        self.current_key = key

        if key not in self.template:
            return

        data = self.template[key]

        self.x_spin.setValue(data.get("x_px", 50))
        self.y_spin.setValue(data.get("y_px", 50))
        self.font_size.setValue(data.get("size", 24))
        self.selected_color = data.get("color", "#FFFFFF")

    # ─────────────────────────────────────────────
    def update_item(self):
        if self.current_key is None:
            return

        self.template[self.current_key]["x_px"] = self.x_spin.value()
        self.template[self.current_key]["y_px"] = self.y_spin.value()
        self.template[self.current_key]["size"] = self.font_size.value()
        self.template[self.current_key]["color"] = self.selected_color

        if self.current_key in self.canvas.items:
            self.canvas.items[self.current_key].move(
                self.x_spin.value(), self.y_spin.value()
            )

    # ─────────────────────────────────────────────
    def save_template(self):
        for key, item in self.canvas.items.items():
            if key not in self.template:
                self.template[key] = {}

            self.template[key]["x_px"] = item.x()
            self.template[key]["y_px"] = item.y()

        with open(self.template_path, "w", encoding="utf-8") as f:
            json.dump(self.template, f, indent=4, ensure_ascii=False)
