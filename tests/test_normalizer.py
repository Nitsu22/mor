from app.core.normalizer import normalize_to_partial_parse


def test_normalize_adds_eos():
    normalized = normalize_to_partial_parse(1, "これはペンです。")
    assert normalized.text.endswith("EOS\n")


def test_normalize_records_tagged_info():
    normalized = normalize_to_partial_parse(1, "[えーと=F]これは")
    assert normalized.tagged_info == {0: "えーと=F"}


def test_normalize_deletes_nod_temporarily():
    normalized = normalize_to_partial_parse(1, "それ〈はい〉です")
    assert normalized.once_deleted[2][0].surface == "〈はい〉"
    assert "〈はい〉" not in normalized.text


def test_normalize_deletes_nod_and_nonverbal_in_text_order():
    normalized = normalize_to_partial_parse(1, "あ｛笑い｝い〈はい〉う")
    assert normalized.once_deleted[1][0].surface == "｛笑い｝"
    assert normalized.once_deleted[2][0].surface == "〈はい〉"


def test_normalize_partial_parses_personal_information():
    normalized = normalize_to_partial_parse(1, "それは【山田】です")

    assert "【山田】\t個人情報" in normalized.text
    assert normalized.text.count("【山田】") == 1


def test_normalize_converts_halfwidth_katakana_to_fullwidth():
    normalized = normalize_to_partial_parse(1, "ｶﾞ ABC ﾃｽﾄ")

    assert "ガ" in normalized.text
    assert "ＡＢＣ\t" in normalized.text
    assert "テスト" in normalized.text


def test_normalize_partial_parses_non_ascii_latin_letters():
    normalized = normalize_to_partial_parse(1, "caféです")

    assert "ｃａｆé\t" in normalized.text
