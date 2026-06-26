from pathlib import Path
from zipfile import ZipFile

import pytest

from app.core.errors import ValidationError
from app.importers.docx_reader import extract_docx_text, infer_request_values_from_filename


def test_extract_version1_starts_at_first_speaker_line(tmp_path: Path):
    docx_path = tmp_path / "THO04_D_STEP2.docx"
    _write_docx(
        docx_path,
        [
            "THO04_D",
            "[C]はい、IDを教えてください",
            "[K][あー=F] [0:02:00] [死んで=G=死んだ]人がいます",
        ],
    )

    extracted = extract_docx_text(docx_path)

    assert extracted.source_format == "Word version1"
    assert extracted.participant_id == "THO04"
    assert extracted.survey_content == "D"
    assert extracted.text == "[C]はい、IDを教えてください\n[K][あー=F] [死んで=G=死んだ]人がいます"


def test_extract_version2_starts_at_timestamp_and_strips_leading_timestamps(tmp_path: Path):
    docx_path = tmp_path / "VNO04_D.docx"
    _write_docx(
        docx_path,
        [
            "VNO04_D",
            "[00:00:00.00 - 00:00:12.32] [K] 肉屋さんは左側にあります。",
            "[00:00:12.59 - 00:00:25.58] [K] 木が二本あります。",
        ],
    )

    extracted = extract_docx_text(docx_path)

    assert extracted.source_format == "Word version2"
    assert extracted.text == "[K] 肉屋さんは左側にあります。\n[K] 木が二本あります。"


def test_extract_rejects_non_docx(tmp_path: Path):
    path = tmp_path / "sample.doc"
    path.write_text("dummy", encoding="utf-8")

    with pytest.raises(ValidationError):
        extract_docx_text(path)


def test_infer_request_values_from_filename():
    assert infer_request_values_from_filename("THO04_D_STEP2.docx") == ("THO04", "D")
    assert infer_request_values_from_filename("VNO04_ST1.docx") == ("VNO04", "ST1")


def _write_docx(path: Path, paragraphs: list[str]) -> None:
    body = "".join(
        f"<w:p><w:r><w:t>{_escape_xml(paragraph)}</w:t></w:r></w:p>"
        for paragraph in paragraphs
    )
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{body}</w:body>"
        "</w:document>"
    )
    with ZipFile(path, "w") as docx:
        docx.writestr("word/document.xml", document)


def _escape_xml(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
