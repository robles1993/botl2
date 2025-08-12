# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['index.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('settings', 'settings') # Solo necesitamos la carpeta de datos
    ],
    # --- AÑADE TUS SCRIPTS AQUÍ ---
    hiddenimports=['leveling', 'detectLife', 'launcher', 'utils'],
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
    [],
    exclude_binaries=True,
    name='MiBot', # <--- Ponle un nombre personalizado
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
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MiBot'
)