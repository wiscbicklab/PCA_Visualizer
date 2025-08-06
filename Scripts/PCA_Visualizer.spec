# -*- mode: python ; coding: utf-8 -*-

datas = [
    ("C:/Users/Scarl/OneDrive/Documents/Environments/PCA/Lib/site-packages/plotly/validators", "plotly/validators"),
    ("C:/Users/Scarl/OneDrive/Documents/Environments/PCA/Lib/site-packages/matplotlib", "matplotlib"),
]

a = Analysis(
    ['..\\source\\gui\\app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PCA_Visualizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
