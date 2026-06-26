# 形態素解析ツール Word入力版

Perl CGI版 `maweb.pl` を、Windows/Macで動かせるデスクトップアプリへ移植するためのPythonプロジェクトです。

現段階では、解析コアとCLIに加えて、Word `.docx` 読み込み、解析、結果確認、CSV保存ができる簡易GUIを用意しています。

## セットアップ

```bash
cd /Users/daichi/Work/RA_work/形態素解析/morph_app
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
```

実際にMeCab解析まで動かす場合は、追加で以下も入れます。

```bash
pip install -e ".[mecab]"
```

## CLI

```bash
python -m app.main parse sample.txt \
  --participant-id ABC01 \
  --survey-content SW1 \
  --output result.csv
```

`resources/mjk-cwj.dic` をMeCabユーザー辞書として自動利用します。
任意のユーザー辞書を指定する場合は `--user-dic` を使います。

```bash
python -m app.main parse sample.txt \
  --participant-id ABC01 \
  --survey-content D \
  --output result.csv \
  --user-dic /path/to/mjk-cwj.dic
```

対話データの場合は、各行を `C ` / `K ` または `[C]` / `[K]` で始めます。

```text
C これは何ですか。
[K]これはペンです。
```

`SW1` / `SW2` はストーリーライティング扱いなので、行頭の話者記号なしでも `K` として扱います。
行頭に `K ` や `[K]` が付いている場合は、話者記号として取り除いて解析します。

## GUI

簡易GUIを起動するには、追加でGUI依存関係を入れます。

```bash
pip install -e ".[gui,mecab]"
python -m app.main gui
```

画面では、協力者ID、調査内容、文字化テキストを指定できます。
Word入力では `.docx` ファイルのみ対応します。Wordファイルを選択すると、自動で文字化テキスト入力欄へ読み込みます。Word version1は最初の `[C]` / `[K]` 行から、Word version2は最初のタイムスタンプ行から読み込み、version2の行頭タイムスタンプは解析対象から除外します。
解析後は表で結果を確認し、CSV保存できます。

配布版アプリは `unidic-lite` を同梱して動作します。
`mjk-cwj.dic` も同梱し、MeCabユーザー辞書として自動で使用します。

## テスト

```bash
python -m pytest
```

## Mac版アプリのビルド

```bash
pip install -e ".[build]"
QT_QPA_PLATFORM=offscreen python scripts/generate_icon.py
PYINSTALLER_CONFIG_DIR=.pyinstaller-cache pyinstaller --noconfirm packaging/pyinstaller_mac.spec
```

成果物は以下に作成されます。

```text
dist/形態素解析ツール Word入力版.app
```

## Windows版アプリのビルド

GitHubにこのプロジェクトをpushすると、GitHub ActionsでWindows版を自動ビルドできます。
Actions画面の `Build Windows App` を開き、完了した実行の `Artifacts` から `形態素解析ツール-Word入力版-windows` をダウンロードします。

手元のWindows環境で直接ビルドする場合は、以下を実行します。

```powershell
python -m pip install -e ".[gui,mecab,build,test]"
python scripts/generate_icon.py
python -m pytest
pyinstaller --noconfirm packaging/pyinstaller_windows.spec
Compress-Archive -Path "dist/形態素解析ツール Word入力版" -DestinationPath "dist/形態素解析ツール-Word入力版-windows.zip" -Force
```

Windows版も `unidic-lite` を同梱して動作します。
配布先のWindows PCにPythonやvenvを入れてもらう必要はありません。

## 主要ファイル

```text
app/core/constants.py         定数
app/core/models.py            データ構造
app/core/validator.py         入力検証
app/core/tag_expander.py      [...] タグ展開
app/core/normalizer.py        MeCab部分解析済み形式への正規化
app/core/mecab_runner.py      mecab-python3 呼び出し
app/core/user_dictionary.py   mjk-cwj.dic の自動検出
app/core/parser.py            解析全体の組み立て
app/importers/docx_reader.py  Word .docx 読み込み
app/export/csv_exporter.py    UTF-16LE BOM付きCSV保存
app/main.py                   CLI入口
```
