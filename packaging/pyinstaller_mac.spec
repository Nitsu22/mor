# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

project_root = Path(SPECPATH).parent
mecab_binaries = collect_dynamic_libs("MeCab")
unidic_lite_datas = collect_data_files("unidic_lite")

a = Analysis(
    [str(project_root / "app" / "main.py")],
    pathex=[str(project_root)],
    binaries=mecab_binaries,
    datas=unidic_lite_datas,
    hiddenimports=["MeCab", "unidic_lite"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    name="形態素解析ツール",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    exclude_binaries=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="形態素解析ツール",
)

app = BUNDLE(
    coll,
    name="形態素解析ツール.app",
    icon=str(project_root / "assets" / "icon.icns"),
    bundle_identifier="jp.local.morph-analysis-tool",
)
