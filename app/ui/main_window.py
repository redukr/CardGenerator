from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from widgets.card_scene_view import CardSceneView
from widgets.property_panel import PropertyPanel

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1400, 900)

        font_buttons = QFont()
        font_buttons.setPointSize(16)   # великий шрифт

        # --- Центральний віджет ---
        self.centralwidget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)

        self.mainLayout = QHBoxLayout(self.centralwidget)
        self.mainLayout.setContentsMargins(10, 10, 10, 10)

        # === Ліва Панель ===
        self.leftPanel = QVBoxLayout()
        self.leftPanel.setSpacing(15)

        # --- Кнопка завантажити JSON ---
        self.btnLoadJSON = QPushButton("Завантажити JSON")
        self.btnLoadJSON.setFont(font_buttons)
        self.leftPanel.addWidget(self.btnLoadJSON)

        # --- Індикатор JSON ---
        self.labelJsonStatus = QLabel("JSON: [не вибрано]")
        self.labelJsonStatus.setStyleSheet("color: #444; font-size: 14px;")
        self.leftPanel.addWidget(self.labelJsonStatus)

        # --- Вибір Workspace ---
        self.btnSetWorkspace = QPushButton("Директорія Експорту")
        self.btnSetWorkspace.setFont(font_buttons)
        self.leftPanel.addWidget(self.btnSetWorkspace)

        # --- Індикатор папки експорту ---
        self.labelWorkspaceStatus = QLabel("Експорт: [не вибрано]")
        self.labelWorkspaceStatus.setStyleSheet("color: #444; font-size: 14px;")
        self.leftPanel.addWidget(self.labelWorkspaceStatus)

        # --- Вибір рамки ---
        self.btnSelectFrame = QPushButton("Обрати рамку")
        self.btnSelectFrame.setFont(font_buttons)
        self.leftPanel.addWidget(self.btnSelectFrame)

        self.labelFrameStatus = QLabel("Рамка: [не вибрано]")
        self.labelFrameStatus.setStyleSheet("color: #444; font-size: 14px;")
        self.leftPanel.addWidget(self.labelFrameStatus)

        # --- Режим редагування ---
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Режим:"))
        self.comboEditMode = QComboBox()
        self.comboEditMode.addItems(["Template", "Card"])
        mode_layout.addWidget(self.comboEditMode)
        self.leftPanel.addLayout(mode_layout)

        self.chkTemplateLock = QCheckBox("Template Lock")
        self.leftPanel.addWidget(self.chkTemplateLock)

        # --- Генерація ---
        self.btnGeneratePreview = QPushButton("Генерувати прев'ю")
        self.btnGeneratePreview.setFont(font_buttons)
        self.leftPanel.addWidget(self.btnGeneratePreview)

        self.btnGenerateSet = QPushButton("Генерувати набір")
        self.btnGenerateSet.setFont(font_buttons)
        self.leftPanel.addWidget(self.btnGenerateSet)

        self.btnGeneratePDF = QPushButton("Експорт у PDF")
        self.btnGeneratePDF.setFont(font_buttons)
        self.leftPanel.addWidget(self.btnGeneratePDF)

        self.leftPanel.addWidget(QLabel("Список карт"))
        self.cardList = QListWidget()
        self.cardList.setSelectionMode(QAbstractItemView.SingleSelection)
        self.leftPanel.addWidget(self.cardList)

        # Розтягування внизу
        self.leftPanel.addStretch()

        # Додаємо ліву панель
        self.mainLayout.addLayout(self.leftPanel, 0)

        # === Права зона (майбутнє превʼю або шаблон-редактор) ===
        self.rightPanel = QVBoxLayout()

        self.sceneView = CardSceneView()
        self.propertyPanel = PropertyPanel(self.sceneView)

        self.sceneAndPanel = QHBoxLayout()
        self.sceneAndPanel.addWidget(self.sceneView, stretch=3)
        self.sceneAndPanel.addWidget(self.propertyPanel, stretch=1)

        self.rightPanel.addLayout(self.sceneAndPanel)
        self.mainLayout.addLayout(self.rightPanel, 1)

        # ==== Завершення ====
        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("CardGenerator — Editor")
