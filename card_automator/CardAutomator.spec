# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('cardtrader', 'cardtrader'), ('cardmarket', 'cardmarket'), ('shared', 'shared')],
    hiddenimports=['cardtrader.cardtrader_automation', 'cardtrader.cardtrader_selector', 'cardtrader.cardtrader_finder', 'cardmarket.cardmarket_automation', 'cardmarket.cardmarket_selector', 'cardmarket.cardmarket_finder', 'shared.base_automation', 'shared.multi_card_automator', 'shared.base_platform', 'config_manager', 'login_dialog', 'utils'],
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
    name='CardAutomator',
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
