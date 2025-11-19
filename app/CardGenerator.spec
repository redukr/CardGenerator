# -*- mode: python ; coding: utf-8 -*-

import os

# Папка проєкту — там, де лежить main.py
project_path = os.path.dirname(os.path.abspath('main.py'))

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[project_path],
    binaries=[],
    datas=[
        (os.path.join(project_path, 'ui'), 'ui'),
        (os.path.join(project_path, 'frames'), 'frames'),
        (os.path.join(project_path, 'icons'), 'icons'),
        (os.path.join(project_path, 'fonts'), 'fonts'),
        (os.path.join(project_path, 'template.json'), '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CardGenerator',
    debug=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='CardGenerator'
)
