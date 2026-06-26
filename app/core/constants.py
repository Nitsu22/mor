from __future__ import annotations

# app/core/constants.py

from typing import Final

# UniDic feature indexes
POS1: Final = 0
POS2: Final = 1
POS3: Final = 2
POS4: Final = 3
CTYPE: Final = 4
CFORM: Final = 5
LFORM: Final = 6
LEMMA: Final = 7
ORTH: Final = 8
PRON: Final = 9
ORTH_BASE: Final = 10
PRON_BASE: Final = 11
GOSHU: Final = 12

FEATURE_NAMES: Final[dict[int, str]] = {
    POS1: "品詞大分類",
    POS2: "品詞中分類",
    POS3: "品詞小分類",
    POS4: "品詞細分類",
    CTYPE: "活用型",
    CFORM: "活用形",
    LFORM: "語彙素読み",
    LEMMA: "語彙素",
    ORTH: "書字形出現形",
    PRON: "発音形出現形",
    ORTH_BASE: "書字形基本形",
    PRON_BASE: "発音形基本形",
    GOSHU: "語種",
}

# Perl版と同じ出力順
OUTPUT_FEATURES: Final[tuple[int, ...]] = (
    LEMMA,
    LFORM,
    POS1,
    POS2,
    POS3,
    POS4,
    CTYPE,
    CFORM,
    ORTH,
    PRON,
    ORTH_BASE,
    PRON_BASE,
    GOSHU,
)

OUTPUT_HEADERS: Final[tuple[str, ...]] = (
    "発話 ID",
    "表層形",
) + tuple(FEATURE_NAMES[i] for i in OUTPUT_FEATURES) + (
    "備考",
)

# 調査内容
SURVEY_CONTENTS: Final[tuple[str, ...]] = (
    "ST1",
    "ST2",
    "D",
    "I",
    "RP1",
    "RP2",
    "SW1",
    "SW2",
)

SURVEY_LABELS: Final[dict[str, str]] = {
    "ST1": "ストーリーテリング 1",
    "ST2": "ストーリーテリング 2",
    "D": "ディスクリプション",
    "I": "インタビュー",
    "RP1": "ロールプレイ 1",
    "RP2": "ロールプレイ 2",
    "SW1": "ストーリーライティング 1",
    "SW2": "ストーリーライティング 2",
}

STORY_WRITING_SURVEYS: Final[tuple[str, ...]] = ("SW1", "SW2")

# 話者記号
SPEAKER_RESEARCHER: Final = "C"
SPEAKER_PARTICIPANT: Final = "K"
SPEAKER_SYMBOLS: Final[tuple[str, ...]] = (
    SPEAKER_RESEARCHER,
    SPEAKER_PARTICIPANT,
)

# 文字化タグ
TAG_FILLER: Final = "F"
TAG_PRENOUN_ADJ: Final = "R"
TAG_PROPER_NOUN: Final = "N"
TAG_NOT_PARSED: Final = "X"
TAG_CORRECTION: Final = "T"
TAG_MISUSE: Final = "G"
TAG_CORRECTION_K: Final = "K"
TAG_READING: Final = "Y"
TAG_AMBIG_PRON: Final = "H"

SPECIAL_POS_TAGS: Final[frozenset[str]] = frozenset({
    TAG_FILLER,
    TAG_PRENOUN_ADJ,
    TAG_PROPER_NOUN,
    TAG_NOT_PARSED,
})

CORRECTION_TAGS: Final[frozenset[str]] = frozenset({
    TAG_CORRECTION,
    TAG_MISUSE,
    TAG_CORRECTION_K,
})

# 特殊括弧
PII_OPEN: Final = "【"
PII_CLOSE: Final = "】"

NOD_OPEN: Final = "〈"
NOD_CLOSE: Final = "〉"

NVB_OPEN: Final = "｛"
NVB_CLOSE: Final = "｝"

# タグ展開モード
EXPAND_TO_ORIGINAL: Final = 1
EXPAND_TO_ANALYTIC: Final = 2
EXPAND_TO_STRUCTURED: Final = 3

# 特殊品詞名
SPECIAL_POS_NAMES: Final[dict[str, str]] = {
    TAG_FILLER: "感動詞",
    TAG_PRENOUN_ADJ: "連体詞",
    TAG_PROPER_NOUN: "",
    TAG_NOT_PARSED: "解析困難箇所",
    PII_OPEN: "個人情報",
    NOD_OPEN: "あいづち",
    NVB_OPEN: "非言語行動",
}

# 補足情報だけが付いた「過剰使用」タグの互換処理
OVERUSE_FEATURES: Final[dict[str, list[str]]] = {
    "な": ["助動詞", "*", "*", "*", "助動詞-ダ", "連体形-一般"],
    "の": ["助詞", "格助詞"],
    "だ": ["助動詞", "*", "*", "*", "助動詞-ダ", "終止形-一般"],
}

FULLWIDTH_OPEN_BRACKET: Final = "［"
FULLWIDTH_CLOSE_BRACKET: Final = "］"
