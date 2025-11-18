# -*- mode: python ; coding: utf-8 -*-

import os

# Поточна робоча директорія (app/)
project_path = os.getcwd()

# Ресурси
datas = [
    (os.path.join(project_path, "template.json"), "app"),
    (os.path.join(project_path, "config.json"), "app"),
]

resource_dirs = [
    "ui",
    "core",
    "widgets",
    "../frames",
    "../icons",
    "../fonts",
    "../decks"
]

for folder in resource_dirs:
    full_path = os.path.join(project_path, folder)
    if os.path.isdir(full_path):
        datas.append((full_path, folder))

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
