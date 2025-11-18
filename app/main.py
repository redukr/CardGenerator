import sys
import json
import os

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice

# ──────────────────────────────────────────────────────────────
# Завантаження CONFIG
# ──────────────────────────────────────────────────────────────

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if not os.path.exists(config_path):
        return {"workspace": "", "last_deck": "", "use_json_color": True}

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg):
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)


# ──────────────────────────────────────────────────────────────
# Головне вікно
# ──────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Завантаження UI
        ui_path = os.path.join(os.path.dirname(__file__), "ui", "main_window.ui")
        loader = QUiLoader()
        ui_file = QFile(ui_path)

        if not ui_file.open(QIODevice.ReadOnly):
            raise FileNotFoundError(f"UI файл не знайдено: {ui_path}")

        self.ui = loader.load(ui_file, self)
        ui_file.close()

        self.setCentralWidget(self.ui)

        # Конфіг
        self.config = load_config()

        # Прив’язуємо кнопки
        self.connect_buttons()

        # Статус інтерфейсу
        self.current_deck = None
        self.current_deck_path = None

        self.setWindowTitle("CardGenerator — Alpha Build")
        self.resize(1400, 900)

    # ────────────────────────────────────────────────────────
    # ПРИВ’ЯЗКА КНОПОК
    # ────────────────────────────────────────────────────────
    def connect_buttons(self):
        try:
            self.ui.btnLoadJSON.clicked.connect(self.load_json_deck)
            self.ui.btnSetWorkspace.clicked.connect(self.set_workspace)
            self.ui.btnGeneratePreview.clicked.connect(self.generate_preview)
            self.ui.btnGenerateSet.clicked.connect(self.generate_set)
            self.ui.btnGeneratePDF.clicked.connect(self.generate_pdf)

        except Exception as e:
            print("⚠ UI кнопки не знайдено — переконайся, що назви збігаються у main_window.ui")
            print(e)

    # ────────────────────────────────────────────────────────
    # ВИБІР ДИРЕКТОРІЇ WORKSPACE
    # ────────────────────────────────────────────────────────
    def set_workspace(self):
        folder = QFileDialog.getExistingDirectory(self, "Обрати директорію workspace")
        if folder:
            self.config["workspace"] = folder
            save_config(self.config)
            QMessageBox.information(self, "OK", f"Workspace встановлено:\n{folder}")

    # ────────────────────────────────────────────────────────
    # ЗАВАНТАЖЕННЯ JSON КОЛОДИ
    # ────────────────────────────────────────────────────────
    def load_json_deck(self):
        path, _ = QFileDialog.getOpenFileName(self, "Обрати JSON колоду", "", "JSON Files (*.json)")
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                self.current_deck = json.load(f)
                self.current_deck_path = path

            self.config["last_deck"] = path
            save_config(self.config)

            QMessageBox.information(self, "OK", f"Колодa завантажена:\n{os.path.basename(path)}")

        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"JSON не вдалося прочитати:\n{str(e)}")

    # ────────────────────────────────────────────────────────
    # ГЕНЕРАЦІЯ ПРЕВ'Ю (заглушка)
    # ────────────────────────────────────────────────────────
    def generate_preview(self):
        QMessageBox.information(self, "Preview", "Генерація прев’ю буде реалізована в renderer.py")

    # ────────────────────────────────────────────────────────
    # ГЕНЕРАЦІЯ ПОВНОГО НАБОРУ (заглушка)
    # ────────────────────────────────────────────────────────
    def generate_set(self):
        QMessageBox.information(self, "Generate Set", "Генерація PNG буде реалізована в renderer.py")

    # ────────────────────────────────────────────────────────
    # ГЕНЕРАЦІЯ PDF (заглушка)
    # ────────────────────────────────────────────────────────
    def generate_pdf(self):
        QMessageBox.information(self, "PDF", "Експорт у PDF буде реалізовано у pdf_exporter.py")


# ──────────────────────────────────────────────────────────────
# Головний запуск
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
