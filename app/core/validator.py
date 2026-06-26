from __future__ import annotations

import re

from .constants import (
    FULLWIDTH_CLOSE_BRACKET,
    FULLWIDTH_OPEN_BRACKET,
    SPEAKER_PARTICIPANT,
    SPEAKER_SYMBOLS,
    STORY_WRITING_SURVEYS,
    SURVEY_CONTENTS,
)
from .errors import ValidationError
from .models import ParseRequest


PARTICIPANT_ID_RE = re.compile(r"^[A-Z]{3}[0-9]{2}$")
SPEAKER_LINE_RE = re.compile(r"^\s*(?:([CK])\s+|\[([CK])\]\s*)(.+)")


def normalize_input_text(text: str) -> str:
    return text.replace(FULLWIDTH_OPEN_BRACKET, "[").replace(FULLWIDTH_CLOSE_BRACKET, "]")


def validate_participant_id(participant_id: str) -> None:
    if not participant_id:
        raise ValidationError("協力者 ID を入力してください。")
    if not PARTICIPANT_ID_RE.fullmatch(participant_id):
        raise ValidationError(
            "協力者 ID は、アルファベットの大文字 3 文字、数字 2 文字を半角で入力してください。"
        )


def validate_survey_content(survey_content: str) -> None:
    if not survey_content:
        raise ValidationError("調査内容を選択してください。")
    if survey_content not in SURVEY_CONTENTS:
        allowed = ", ".join(SURVEY_CONTENTS)
        raise ValidationError(f"調査内容は次のいずれかを指定してください: {allowed}")


def validate_text(text: str) -> None:
    if not text or not text.strip():
        raise ValidationError("文字化テキストを入力してから解析してください。")


def validate_request(request: ParseRequest) -> None:
    validate_participant_id(request.participant_id)
    validate_survey_content(request.survey_content)
    validate_text(request.text)


def split_mjk_lines(text: str) -> list[str]:
    lines = re.split(r"[\r\n]+", text)
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def parse_speaker_line(line: str, survey_content: str, line_number: int) -> tuple[str, str]:
    match = SPEAKER_LINE_RE.match(line)

    if survey_content in STORY_WRITING_SURVEYS:
        if match:
            speaker_symbol = match.group(1) or match.group(2)
            return speaker_symbol, match.group(3)
        return SPEAKER_PARTICIPANT, line

    if not match:
        allowed = "/".join(SPEAKER_SYMBOLS)
        raise ValidationError(
            f"{line_number}行目: 各行は、話者記号 ({allowed}) または [C]/[K] の後に、"
            "その後ろにテキストを入力してください。"
        )
    speaker_symbol = match.group(1) or match.group(2)
    return speaker_symbol, match.group(3)
