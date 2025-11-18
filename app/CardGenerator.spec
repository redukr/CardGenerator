# -*- mode: python ; coding: utf-8 -*-

import os

project_path = os.getcwd()

datas = []

# Всі папки з ресурсами
for folder in ["ui", "core", "widgets", "frames", "icons", "fonts", "decks"]:
    full_path = os.path.join(project_path, folder)
    if os.path.isdir(full_path):
        datas.append((full_path, folder))

# Файли в корені app/
datas.append((os.path.join(project_path, "template.json"), "."))
datas.append((os.path.join(project_path, "config.json"), "."))

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[project_path],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    cipher=block_cipher
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=False,
    name='CardGenerator',
    debug=False,
    strip=False,
    upx=False,
    console=False
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='CardGenerator'
)
