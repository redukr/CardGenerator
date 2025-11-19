# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_submodules

# Основний файл програми
main_script = 'main.py'

# Збір усіх необхідних PySide6 модулів
hidden_imports = collect_submodules('PySide6')

# Включення ресурсів у збірку
datas = [
    ('app/icons/*.png', 'app/icons'),
    ('app/frames/*.png', 'app/frames'),
    ('app/fonts/*.ttf', 'app/fonts'),
    ('app/decks/*.json', 'app/decks'),
    ('app/editor/*.json', 'app/editor'),
    ('app/template.json', 'app'),
    ('app/config.json', 'app'),
    ('app/ui/styles.qss', 'app/ui'),
]

a = Analysis(
    [main_script],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='CardGenerator',
    debug=False,
    strip=False,
    upx=False,
    console=False,  # Вікна консолі не буде
    icon=None
)

