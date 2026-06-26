from __future__ import annotations

import re
import unicodedata

from .constants import (
    EXPAND_TO_ANALYTIC,
    EXPAND_TO_ORIGINAL,
    EXPAND_TO_STRUCTURED,
    NOD_CLOSE,
    NOD_OPEN,
    NVB_CLOSE,
    NVB_OPEN,
    PII_CLOSE,
    PII_OPEN,
    POS1,
)
from .errors import TagFormatError
from .models import DeletedSpan, NormalizedText
from .tag_expander import (
    expand_mjk_bracket,
    get_partial_parsed_line,
    get_special_part_of_speech,
)


LATIN_LETTER = r"A-Za-z\u00C0-\u024F\u1E00-\u1EFF"
LATIN_WORD_RE = re.compile(rf"([{LATIN_LETTER}]+(?:['’][{LATIN_LETTER}]+)?)")


def normalize_to_partial_parse(
    line_number: int,
    tagged_text: str,
    dont_use_tags: bool = False,
) -> NormalizedText:
    tagged_info: dict[int, str] = {}
    once_deleted: dict[int, list[DeletedSpan]] = {}

    plain_text = tagged_text
    structured = tagged_text
    expand_to_plain_text = EXPAND_TO_ORIGINAL if dont_use_tags else EXPAND_TO_ANALYTIC
    expand_to_structured = EXPAND_TO_ORIGINAL if dont_use_tags else EXPAND_TO_STRUCTURED

    while "[" in plain_text:
        incl_idx = plain_text.find("[")
        close_idx = plain_text.find("]", incl_idx + 1)
        if close_idx < 0:
            raise TagFormatError(f"{line_number}行目で解析エラー: Mismatched parentheses: '['")

        content = plain_text[incl_idx + 1 : close_idx]
        tagged_info[incl_idx] = content
        try:
            expanded_plain = expand_mjk_bracket(content, expand_to_plain_text)
            plain_text = plain_text[:incl_idx] + expanded_plain + plain_text[close_idx + 1 :]

            structured = _replace_next_tag(structured, expand_to_structured)
        except TagFormatError as exc:
            raise TagFormatError(f"{line_number} 行目の [{content}] で解析エラー: {exc}") from exc

    if "]" in structured:
        raise TagFormatError(f"{line_number}行目で解析エラー: Mismatched parentheses: ']'")

    plain_text, structured = _remove_once_deleted_marks(
        line_number,
        plain_text,
        structured,
        once_deleted,
    )

    structured = _replace_special_brackets(line_number, structured, PII_OPEN, PII_CLOSE)
    structured = _partial_parse_latin_words(structured)
    structured = _convert_surface_hankaku_to_zenkaku(structured)
    structured += "\nEOS\n"
    structured = re.sub(r"(?m)^\n", "", structured)

    return NormalizedText(
        text=structured,
        tagged_info=tagged_info,
        once_deleted=once_deleted,
    )


def _replace_next_tag(text: str, expand_to: int) -> str:
    open_idx = text.find("[")
    close_idx = text.find("]", open_idx + 1)
    if open_idx < 0 or close_idx < 0:
        raise TagFormatError("Mismatched parentheses: '['")
    content = text[open_idx + 1 : close_idx]
    replacement = expand_mjk_bracket(content, expand_to)
    return text[:open_idx] + replacement + text[close_idx + 1 :]


def _remove_once_deleted_marks(
    line_number: int,
    plain_text: str,
    structured: str,
    once_deleted: dict[int, list[DeletedSpan]],
) -> tuple[str, str]:
    close_marks = {
        NOD_OPEN: NOD_CLOSE,
        NVB_OPEN: NVB_CLOSE,
    }

    while True:
        candidates = [
            (plain_text.find(open_mark), open_mark)
            for open_mark in close_marks
            if plain_text.find(open_mark) >= 0
        ]
        if not candidates:
            break

        open_idx, open_mark = min(candidates, key=lambda item: item[0])
        close_mark = close_marks[open_mark]
        close_idx = plain_text.find(close_mark, open_idx + 1)
        if close_idx < 0:
            raise TagFormatError(
                f"{line_number}行目で解析エラー: Mismatched parentheses: '{open_mark}'"
            )

        matched_text = plain_text[open_idx : close_idx + len(close_mark)]
        plain_text = plain_text[:open_idx] + plain_text[close_idx + len(close_mark) :]

        structured_open_idx = structured.find(open_mark)
        structured_close_idx = structured.find(close_mark, structured_open_idx + 1)
        if structured_open_idx < 0 or structured_close_idx < 0:
            raise TagFormatError(
                f"{line_number}行目の {matched_text} で解析エラー: "
                f"Mismatched parentheses: '{open_mark}'"
            )
        structured = (
            structured[:structured_open_idx]
            + "\n"
            + structured[structured_close_idx + len(close_mark) :]
        )

        features = [""] * 13
        features[POS1] = get_special_part_of_speech(open_mark)
        once_deleted.setdefault(open_idx, []).append(
            DeletedSpan(index=open_idx, surface=matched_text, features=features)
        )

    return plain_text, structured


def _replace_special_brackets(
    line_number: int,
    text: str,
    open_mark: str,
    close_mark: str,
) -> str:
    parts = []
    cursor = 0

    while True:
        open_idx = text.find(open_mark, cursor)
        if open_idx < 0:
            parts.append(text[cursor:])
            break

        close_idx = text.find(close_mark, open_idx + 1)
        if close_idx < 0:
            raise TagFormatError(
                f"{line_number}行目で解析エラー: Mismatched parentheses: '{open_mark}'"
            )

        surface = text[open_idx : close_idx + len(close_mark)]
        replacement = get_partial_parsed_line(
            surface,
            get_special_part_of_speech(open_mark),
        )
        parts.append(text[cursor:open_idx])
        parts.append(replacement)
        cursor = close_idx + len(close_mark)

    return "".join(parts)


def _partial_parse_latin_words(text: str) -> str:
    structured_lines = []
    for line in text.split("\n"):
        if "\t" not in line:
            line = LATIN_WORD_RE.sub(r"\n\1\t\n", line)
        structured_lines.append(line)
    return "\n".join(structured_lines)


def _convert_surface_hankaku_to_zenkaku(text: str) -> str:
    structured_lines = []
    for line in text.split("\n"):
        if "\t" in line:
            surface, feature = line.split("\t", 1)
            structured_lines.append(f"{_hankaku_to_zenkaku(surface)}\t{feature}")
        else:
            structured_lines.append(_hankaku_to_zenkaku(line))
    return "\n".join(structured_lines)


def _hankaku_to_zenkaku(value: str) -> str:
    chars = []
    index = 0
    while index < len(value):
        char = value[index]
        codepoint = ord(char)
        if char == " ":
            chars.append("　")
            index += 1
        elif 0x21 <= codepoint <= 0x7E:
            chars.append(chr(codepoint + 0xFEE0))
            index += 1
        elif 0xFF61 <= codepoint <= 0xFF9F:
            end = index + 1
            while end < len(value) and 0xFF61 <= ord(value[end]) <= 0xFF9F:
                end += 1
            chars.append(unicodedata.normalize("NFKC", value[index:end]))
            index = end
        else:
            chars.append(char)
            index += 1
    return "".join(chars)
