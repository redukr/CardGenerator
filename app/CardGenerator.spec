# -*- mode: python ; coding: utf-8 -*-

import os

# Поточна директорія (app/)
project_path = os.getcwd()

datas = []

# ВСІ ПАПКИ, ЯКІ ПОТРІБНО ВКЛЮЧИТИ У EXE
for folder in ["ui", "core", "widgets", "frames", "icons", "fonts", "decks"]:
    full_dir = os.path.join(project_path, folder)
    if os.path.isdir(full_dir):
        datas.append((full_dir, folder))

# Окремі файли
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
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CardGenerator',
    debug=False,
    bootloader_ignore_signals=False,
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
