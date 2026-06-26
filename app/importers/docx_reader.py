from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

from app.core.constants import SURVEY_CONTENTS
from app.core.errors import ValidationError


WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": WORD_NS}

SPEAKER_LINE_RE = re.compile(r"^\s*(?:[CK]\s+|\[[CK]\])")
LEADING_TIMESTAMP_RE = re.compile(
    r"^\s*\["
    r"(?:\d{1,2}:)?\d{1,2}:\d{2}(?:[.:]\d{1,3})?"
    r"(?:\s*[-–〜~]\s*(?:\d{1,2}:)?\d{1,2}:\d{2}(?:[.:]\d{1,3})?)?"
    r"\]\s*"
)
TIMESTAMP_RE = re.compile(
    r"\s*\["
    r"(?:\d{1,2}:)?\d{1,2}:\d{2}(?:[.:]\d{1,3})?"
    r"(?:\s*[-–〜~]\s*(?:\d{1,2}:)?\d{1,2}:\d{2}(?:[.:]\d{1,3})?)?"
    r"\]\s*"
)
FILENAME_RE = re.compile(r"^(?P<participant>[A-Za-z]{3}\d{2})_(?P<survey>[A-Za-z0-9]+)")


@dataclass(frozen=True)
class DocxExtractResult:
    text: str
    source_format: str
    line_count: int
    participant_id: str | None = None
    survey_content: str | None = None


def extract_docx_text(path: str | Path) -> DocxExtractResult:
    docx_path = Path(path)
    if docx_path.suffix.lower() != ".docx":
        raise ValidationError("Word入力は .docx ファイルのみ対応しています。")
    if not docx_path.exists():
        raise ValidationError(f"Wordファイルが見つかりません: {docx_path}")

    raw_lines = _read_document_lines(docx_path)
    if not raw_lines:
        raise ValidationError("Wordファイルから文字化テキストを読み取れませんでした。")

    timestamp_index = _first_timestamp_line_index(raw_lines)
    if timestamp_index is not None:
        source_format = "Word version2"
        lines = [_strip_leading_timestamps(line) for line in raw_lines[timestamp_index:]]
    else:
        source_format = "Word version1"
        lines = _drop_version1_heading(raw_lines)

    lines = [_strip_timestamps(line) for line in lines]
    lines = [line.strip() for line in lines if line.strip()]
    if not lines:
        raise ValidationError("Wordファイルから解析対象の文字化テキストを読み取れませんでした。")

    participant_id, survey_content = infer_request_values_from_filename(docx_path)
    return DocxExtractResult(
        text="\n".join(lines),
        source_format=source_format,
        line_count=len(lines),
        participant_id=participant_id,
        survey_content=survey_content,
    )


def infer_request_values_from_filename(path: str | Path) -> tuple[str | None, str | None]:
    match = FILENAME_RE.match(Path(path).stem)
    if not match:
        return None, None

    participant_id = match.group("participant").upper()
    survey_content = match.group("survey").upper()
    if survey_content not in SURVEY_CONTENTS:
        survey_content = None
    return participant_id, survey_content


def _read_document_lines(path: Path) -> list[str]:
    try:
        with ZipFile(path) as docx:
            document_xml = docx.read("word/document.xml")
    except KeyError as exc:
        raise ValidationError("Wordファイルの本文を読み取れませんでした。") from exc
    except BadZipFile as exc:
        raise ValidationError("有効な .docx ファイルではありません。") from exc

    root = ET.fromstring(document_xml)
    body = root.find("w:body", NS)
    if body is None:
        return []

    lines: list[str] = []
    for child in list(body):
        tag = _local_name(child.tag)
        if tag == "p":
            text = _paragraph_text(child).strip()
            if text:
                lines.append(text)
        elif tag == "tbl":
            lines.extend(_table_lines(child))
    return lines


def _table_lines(table: ET.Element) -> list[str]:
    lines: list[str] = []
    for row in table.findall(".//w:tr", NS):
        cells = []
        for cell in row.findall("./w:tc", NS):
            paragraphs = [
                _paragraph_text(paragraph).strip()
                for paragraph in cell.findall("./w:p", NS)
            ]
            cell_text = " ".join(paragraph for paragraph in paragraphs if paragraph)
            if cell_text:
                cells.append(cell_text)
        if cells:
            lines.append(" ".join(cells))
    return lines


def _paragraph_text(paragraph: ET.Element) -> str:
    return "".join(_text_parts(paragraph, in_deleted_text=False))


def _text_parts(element: ET.Element, in_deleted_text: bool) -> list[str]:
    tag = _local_name(element.tag)
    if tag == "del":
        in_deleted_text = True
    if in_deleted_text:
        return []
    if tag == "t" and element.text:
        return [element.text]
    if tag == "tab":
        return ["\t"]
    if tag in {"br", "cr"}:
        return ["\n"]

    parts: list[str] = []
    for child in list(element):
        parts.extend(_text_parts(child, in_deleted_text))
    return parts


def _first_timestamp_line_index(lines: list[str]) -> int | None:
    for index, line in enumerate(lines):
        if LEADING_TIMESTAMP_RE.match(line):
            return index
    return None


def _strip_leading_timestamps(line: str) -> str:
    previous = None
    stripped = line
    while previous != stripped:
        previous = stripped
        stripped = LEADING_TIMESTAMP_RE.sub("", stripped, count=1)
    return stripped


def _strip_timestamps(line: str) -> str:
    return TIMESTAMP_RE.sub(" ", line).strip()


def _drop_version1_heading(lines: list[str]) -> list[str]:
    for index, line in enumerate(lines):
        if SPEAKER_LINE_RE.match(line):
            return lines[index:]
    return lines[1:] if len(lines) > 1 else lines


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]
