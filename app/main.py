import sys
import json
import os
import traceback
from PySide6.QtGui import QPixmap


def exception_handler(exc_type, exc_value, exc_traceback):
    """Записує всі помилки у error.txt поруч із EXE."""
    # Шлях до error.txt поруч з exe
    if hasattr(sys, '_MEIPASS'):
        # Onefile: реальний exe лежить у sys.argv[0]
        base = os.path.dirname(sys.argv[0])
    else:
        # IDE: поруч з main.py
        base = os.path.dirname(os.path.abspath(__file__))

    log_path = os.path.join(base, "error.txt")

    with open(log_path, "a", encoding="utf-8") as f:
        f.write("=== ERROR ===\n")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
        f.write("\n")

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
    QApplication, QMainWindow, QFileDialog, QMessageBox
)

from core.json_loader import JSONLoader
from core.renderer import CardRenderer
from core.pdf_exporter import PDFExporter


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
        self.template_path = resource_path("template.json")
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

    def _apply_frame_to_scene(self, path: str):
        pixmap = QPixmap(path)
        if pixmap.isNull():
            return
        self.ui.sceneView.display_background_pixmap(pixmap)

    def connect_buttons(self):
        try:
            self.ui.btnLoadJSON.clicked.connect(self.load_json_deck)
            self.ui.btnSetWorkspace.clicked.connect(self.set_workspace)
            self.ui.btnSelectFrame.clicked.connect(self.select_frame)
            self.ui.btnGeneratePreview.clicked.connect(self.generate_preview)
            self.ui.btnGenerateSet.clicked.connect(self.generate_set)
            self.ui.btnGeneratePDF.clicked.connect(self.generate_pdf)
        except Exception as e:
            print("⚠ UI кнопки не знайдено:")
            print(e)

    def set_workspace(self):
        folder = QFileDialog.getExistingDirectory(self, "Обрати директорію workspace")
        if folder:
            self.config["workspace"] = folder
            save_config(self.config)
            QMessageBox.information(self, "OK", f"Workspace встановлено:\n{folder}")
            self.ui.labelWorkspaceStatus.setText(f"Експорт: {folder}")


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
            self.ui.labelJsonStatus.setText(f"JSON: {os.path.basename(path)}")


        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"JSON не вдалося прочитати:\n{str(e)}")

    # ---------------------------
    # Generate Preview
    # ---------------------------
    def generate_preview(self):
        if not self.current_deck_path:
            QMessageBox.warning(self, "Помилка", "Завантаж JSON колоди.")
            return

        loader = JSONLoader(self.current_deck_path)
        deck = loader.load()

        if not deck["cards"]:
            QMessageBox.warning(self, "Помилка", "У колоді немає карт.")
            return

        # Папка з EXE
        base_dir = os.path.dirname(sys.argv[0])

        # export/
        export_root = os.path.join(base_dir, "export")
        os.makedirs(export_root, exist_ok=True)

        # export/<deck_name>/
        deck_name = os.path.splitext(os.path.basename(self.current_deck_path))[0]
        deck_export_dir = os.path.join(export_root, deck_name)
        os.makedirs(deck_export_dir, exist_ok=True)

        # Генерація
        card = deck["cards"][0]
        deck_color = deck["deck_color"]

        renderer = CardRenderer(
            template_path=self.template_path,
            frame_path=self.frame_path,
            fonts_folder=resource_path("fonts")
        )

        img = renderer.render_card(card, deck_color)

        # preview.png
        preview_path = os.path.join(deck_export_dir, "preview.png")
        renderer.save_png(img, preview_path)

        preview_path = os.path.abspath(preview_path)
        preview_path = os.path.normpath(preview_path)

        pixmap = QPixmap(preview_path)
        if pixmap.isNull():
            QMessageBox.warning(self, "Помилка", f"Не вдалося завантажити превʼю:\n{preview_path}")
            return

        self.ui.sceneView.display_pixmap(pixmap)

        QMessageBox.information(self, "OK", f"Превʼю створено:\n{preview_path}")

    def update_preview(self):
        """
        Оновлює превʼю картки при будь-якій зміні параметрів UI.
        """
        try:
            if not self.current_deck_path:
                return

            loader = JSONLoader(self.current_deck_path)
            deck = loader.load()

            if not deck["cards"]:
                return

            card = deck["cards"][0]
            deck_color = deck["deck_color"]

            renderer = CardRenderer(
                template_path=self.template_path,
                frame_path=self.frame_path,
                fonts_folder=resource_path("fonts")
            )

            img = renderer.render_card(card, deck_color)

            preview_path = os.path.join(
                os.path.dirname(sys.argv[0]),
                "export",
                "_preview_temp.png"
            )
            renderer.save_png(img, preview_path)

            pixmap = QPixmap(os.path.normpath(preview_path))
            if not pixmap.isNull():
                self.ui.sceneView.display_pixmap(pixmap)

        except Exception as e:
            with open("error.txt", "a", encoding="utf-8") as f:
                f.write(f"=== ERROR UPDATE PREVIEW ===\n{e}\n\n")

    def generate_set(self):
        if not self.current_deck_path:
            QMessageBox.warning(self, "Помилка", "Завантаж JSON колоди.")
            return

        loader = JSONLoader(self.current_deck_path)
        deck = loader.load()

        base_dir = os.path.dirname(sys.argv[0])
        export_root = os.path.join(base_dir, "export")

        deck_name = os.path.splitext(os.path.basename(self.current_deck_path))[0]
        deck_export_dir = os.path.join(export_root, deck_name)
        os.makedirs(deck_export_dir, exist_ok=True)

        renderer = CardRenderer(
            template_path=self.template_path,
            frame_path=self.frame_path,
            fonts_folder=resource_path("fonts")
        )

        deck_color = deck["deck_color"]

        for card in deck["cards"]:
            img = renderer.render_card(card, deck_color)
            out_path = os.path.join(
                deck_export_dir,
                f"{card['name'].replace(' ', '_')}.png"
            )
            renderer.save_png(img, out_path)

        QMessageBox.information(self, "OK", f"Набір карт згенеровано:\n{deck_export_dir}")

    # ---------------------------
    # Generate PDF
    # ---------------------------
    def generate_pdf(self):
        if not self.current_deck_path:
            QMessageBox.warning(self, "Помилка", "Завантаж JSON колоди.")
            return

        base_dir = os.path.dirname(sys.argv[0])
        export_root = os.path.join(base_dir, "export")

        deck_name = os.path.splitext(os.path.basename(self.current_deck_path))[0]
        deck_export_dir = os.path.join(export_root, deck_name)

        if not os.path.isdir(deck_export_dir):
            QMessageBox.warning(self, "Помилка", f"Не знайдено директорію:\n{deck_export_dir}")
            return

        pdf_path = os.path.join(deck_export_dir, f"{deck_name}.pdf")

        exporter = PDFExporter()
        exporter.export_pdf(deck_export_dir, pdf_path)

        QMessageBox.information(self, "OK", f"PDF створено:\n{pdf_path}")


if __name__ == "__main__":
    
        # Лог старту
    try:
        if hasattr(sys, '_MEIPASS'):
            base = os.path.dirname(sys.argv[0])
        else:
            base = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(base, "error.txt"), "a", encoding="utf-8") as f:
            f.write("\n=== APP STARTED ===\n")
    except:
        pass

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
