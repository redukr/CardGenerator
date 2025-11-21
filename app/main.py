import json
import logging
import os
import sys
import traceback

from PySide6.QtGui import QPixmap


from core.paths import application_base_dir

BASE_DIR = application_base_dir()
ERROR_LOG_PATH = BASE_DIR / "error.txt"
APP_LOG_PATH = BASE_DIR / "application.log"


def _setup_logger() -> logging.Logger:
    logger = logging.getLogger("card_generator")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler(APP_LOG_PATH, encoding="utf-8")
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.propagate = False
    return logger


logger = _setup_logger()


def exception_handler(exc_type, exc_value, exc_traceback):
    """Записує всі помилки у error.txt поруч із EXE."""
    with open(ERROR_LOG_PATH, "a", encoding="utf-8") as f:
        f.write("=== ERROR ===\n")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
        f.write("\n")
    logger.exception("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))


# Перехопити всі uncaught exceptions
sys.excepthook = exception_handler


def resource_path(*paths):
    """
    Повертає шлях до ресурсів у режимі розробки і в PyInstaller (onefile).
    У onefile PyInstaller розпаковує все безпосередньо в _MEIPASS.
    """
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS   # без _internal!
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, *paths)


from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QListWidgetItem,
    QMessageBox,
    QMainWindow,
)

from core.json_loader import JSONLoader
from core.pdf_exporter import PDFExporter
from core.scene_exporter import SceneExporter


def load_config():
    config_path = resource_path("config.json")
    if not os.path.exists(config_path):
        return {"workspace": "", "last_deck": "", "use_json_color": True}

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg):
    config_path = resource_path("config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        from ui.main_window import Ui_MainWindow

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.btnSetWorkspace.setText("Директорія Експорту")

        self.config = load_config()
        self.base_dir = BASE_DIR
        self.logger = logger
        self.template_path = resource_path("editor", "template_layout.json")
        self.frame_path = self.config.get(
            "frame_path", resource_path("frames", "base_frame.png")
        )

        self.ui.sceneView.load_template(self.template_path)
        self._apply_frame_to_scene(self.frame_path)
        self.ui.labelFrameStatus.setText(
            f"Рамка: {os.path.basename(self.frame_path)}"
        )

        self.connect_buttons()

        self.current_deck = None
        self.current_deck_path = None
        self.scene_exporter = SceneExporter(self.ui.sceneView)

        self.setWindowTitle("CardGenerator — Alpha Build")
        self.resize(1400, 900)
      
    def select_frame(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Обрати рамку",
            "",
            "PNG Files (*.png)"
        )

        if not path:
            return

        self.config["frame_path"] = path
        save_config(self.config)
        self.frame_path = path

        self.ui.labelFrameStatus.setText(f"Рамка: {os.path.basename(path)}")

        self._apply_frame_to_scene(path)

        QMessageBox.information(self, "OK", f"Рамка вибрана:\n{path}")
        self._log(f"Frame selected: {path}")

    def _apply_frame_to_scene(self, path: str):
        pixmap = QPixmap(path)
        if pixmap.isNull():
            return
        self.ui.sceneView.set_frame_pixmap(pixmap)

    def connect_buttons(self):
        try:
            self.ui.btnLoadJSON.clicked.connect(self.load_json_deck)
            self.ui.btnSetWorkspace.clicked.connect(self.set_workspace)
            self.ui.btnSelectFrame.clicked.connect(self.select_frame)
            self.ui.btnGeneratePreview.clicked.connect(self.generate_preview)
            self.ui.btnGenerateSet.clicked.connect(self.generate_set)
            self.ui.btnGeneratePDF.clicked.connect(self.generate_pdf)
            self.ui.cardList.currentRowChanged.connect(self.update_preview_for_selection)
            self.ui.comboEditMode.currentTextChanged.connect(self._on_edit_mode_changed)
            self.ui.chkTemplateLock.toggled.connect(self.ui.sceneView.set_template_locked)
        except Exception as e:
            print("⚠ UI кнопки не знайдено:")
            print(e)

    def _log(self, message: str):
        self.logger.info(message)

    def set_workspace(self):
        folder = QFileDialog.getExistingDirectory(self, "Обрати директорію workspace")
        if folder:
            self.config["workspace"] = folder
            save_config(self.config)
            QMessageBox.information(self, "OK", f"Workspace встановлено:\n{folder}")
            self.ui.labelWorkspaceStatus.setText(f"Експорт: {folder}")
            self._log(f"Workspace set to: {folder}")


    def load_json_deck(self):
        path, _ = QFileDialog.getOpenFileName(self, "Обрати JSON колоду", "", "JSON Files (*.json)")
        if not path:
            return

        try:
            loader = JSONLoader(path)
            deck = loader.load()
            self.current_deck = deck
            self.current_deck_path = path

            self.config["last_deck"] = path
            save_config(self.config)

            QMessageBox.information(self, "OK", f"Колодa завантажена:\n{os.path.basename(path)}")
            self.ui.labelJsonStatus.setText(f"JSON: {os.path.basename(path)}")
            self._populate_card_list(deck)
            self.update_preview_for_selection()
            self._log(f"Deck loaded: {path}")

        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"JSON не вдалося прочитати:\n{str(e)}")
            self._log(f"Failed to load deck {path}: {e}")

    def _populate_card_list(self, deck, *, selected_index: int = 0):
        self.ui.cardList.blockSignals(True)
        self.ui.cardList.clear()
        for card in deck.cards:
            item = QListWidgetItem(card.name)
            self.ui.cardList.addItem(item)
        self.ui.cardList.blockSignals(False)
        if deck.cards:
            index = min(max(selected_index, 0), len(deck.cards) - 1)
            self.ui.cardList.setCurrentRow(index)

    def _current_card(self):
        if not self.current_deck or not self.current_deck.cards:
            return None
        row = self.ui.cardList.currentRow()
        if row < 0:
            row = 0
        return self.current_deck.card_at(row) or self.current_deck.cards[0]

    # ---------------------------
    # Generate Preview
    # ---------------------------
    def generate_preview(self):
        if not self.current_deck_path:
            QMessageBox.warning(self, "Помилка", "Завантаж JSON колоди.")
            return

        loader = JSONLoader(self.current_deck_path)
        deck = loader.load()
        current_row = self.ui.cardList.currentRow()
        self.current_deck = deck
        self._populate_card_list(deck, selected_index=current_row)

        if not deck.cards:
            QMessageBox.warning(self, "Помилка", "У колоді немає карт.")
            return

        card = self._current_card()
        if not card:
            QMessageBox.warning(self, "Помилка", "Не вдалося знайти картку для прев'ю.")
            return

        self.ui.sceneView.apply_card_data(card.payload, deck.deck_color)

        QMessageBox.information(self, "OK", "Превʼю оновлено у редакторі.")
        self._log("Preview generated from current deck")

    def update_preview_for_selection(self):
        """Оновлює сцену для вибраної картки у списку."""
        if not self.current_deck:
            return
        try:
            card = self._current_card()
            if not card:
                return
            self.ui.sceneView.apply_card_data(card.payload, self.current_deck.deck_color)
        except Exception as e:
            with open(ERROR_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"=== ERROR UPDATE PREVIEW ===\n{e}\n\n")
            self._log(f"Preview update failed: {e}")

    def generate_set(self):
        if not self.current_deck_path:
            QMessageBox.warning(self, "Помилка", "Завантаж JSON колоди.")
            return

        loader = JSONLoader(self.current_deck_path)
        deck = loader.load()
        self.current_deck = deck

        export_root = self.config.get("workspace") or os.path.join(self.base_dir, "export")

        deck_export_dir = os.path.join(export_root, deck.name)
        self.scene_exporter.export_deck(deck, deck_export_dir, frame_path=self.frame_path)

        QMessageBox.information(self, "OK", f"Набір карт згенеровано:\n{deck_export_dir}")
        self._log(f"Card set generated to: {deck_export_dir}")

    def _on_edit_mode_changed(self, mode_name: str):
        self.ui.sceneView.set_edit_mode(mode_name.lower())

    # ---------------------------
    # Generate PDF
    # ---------------------------
    def generate_pdf(self):
        if not self.current_deck_path:
            QMessageBox.warning(self, "Помилка", "Завантаж JSON колоди.")
            return

        export_root = self.config.get("workspace") or os.path.join(self.base_dir, "export")

        deck_name = os.path.splitext(os.path.basename(self.current_deck_path))[0]
        deck_export_dir = os.path.join(export_root, deck_name)

        if not os.path.isdir(deck_export_dir):
            QMessageBox.warning(self, "Помилка", f"Не знайдено директорію:\n{deck_export_dir}")
            return

        pdf_path = os.path.join(deck_export_dir, f"{deck_name}.pdf")

        exporter = PDFExporter()
        exporter.export_pdf(deck_export_dir, pdf_path)

        QMessageBox.information(self, "OK", f"PDF створено:\n{pdf_path}")
        self._log(f"PDF exported: {pdf_path}")


if __name__ == "__main__":
    try:
        with open(ERROR_LOG_PATH, "a", encoding="utf-8") as f:
            f.write("\n=== APP STARTED ===\n")
    except Exception:
        pass

    logger.info("Application started")

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
