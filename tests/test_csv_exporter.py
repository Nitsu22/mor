from pathlib import Path

from app.core.constants import OUTPUT_HEADERS
from app.core.models import ParseResult, TokenRow
from app.export.csv_exporter import export_parse_result


def test_export_parse_result_writes_utf16le_bom(tmp_path: Path):
    result = ParseResult(
        headers=OUTPUT_HEADERS,
        rows=[
            TokenRow(
                utterance_id="ABC01-SW1-0010-K",
                surface="これ",
                lemma="此れ",
                lform="コレ",
                pos1="代名詞",
                pos2="*",
                pos3="*",
                pos4="*",
                ctype="*",
                cform="*",
                orth="これ",
                pron="コレ",
                orth_base="これ",
                pron_base="コレ",
                goshu="和",
            )
        ],
    )
    output = tmp_path / "result.csv"

    export_parse_result(output, result)

    data = output.read_bytes()
    assert data.startswith(b"\xff\xfe")
    assert "ABC01-SW1-0010-K" in data.decode("utf-16le")
