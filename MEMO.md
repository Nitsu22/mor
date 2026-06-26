app/core/constants.py
UniDicの列番号、列名、調査内容、タグ名を定義する。

app/core/models.py
ParseRequest, TokenRow, ParseResult などのデータ構造を作る。

app/core/validator.py
協力者ID、調査内容、本文、話者記号をチェックする。

app/core/tag_expander.py
[えーと=F], [ーと=T=と], [よみ（ヨミ）=Y] などを処理する。

app/core/normalizer.py
Perl版の normalize_to_partial_parse 相当を書く。

app/core/mecab_runner.py
mecab-python3 でMeCabを呼び出す部分を書く。

app/core/parser.py
入力全体を受け取り、発話IDを作り、トークン行に変換する。

app/export/csv_exporter.py
UTF-16LE BOM付き、タブ区切り、CRLFで保存する。

app/main.py
まずはCLIで動かす。GUIは後回し。