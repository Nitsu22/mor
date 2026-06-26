# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

project_root = Path(SPECPATH).parent
mecab_binaries = collect_dynamic_libs("MeCab")
unidic_lite_datas = collect_data_files("unidic_lite")
user_dic_path = project_root / "resources" / "mjk-cwj.dic"
user_dic_datas = [(str(user_dic_path), "resources")] if user_dic_path.exists() else []

a = Analysis(
    [str(project_root / "app" / "main.py")],
    pathex=[str(project_root)],
    binaries=mecab_binaries,
    datas=unidic_lite_datas + user_dic_datas,
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
    name="形態素解析ツール Word入力版",
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
    name="形態素解析ツール Word入力版",
)

app = BUNDLE(
    coll,
    name="形態素解析ツール Word入力版.app",
    icon=str(project_root / "assets" / "icon.icns"),
    bundle_identifier="jp.local.morph-analysis-tool-word",
)
