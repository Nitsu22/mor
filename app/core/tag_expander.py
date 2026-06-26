from __future__ import annotations

import re

from .constants import (
    CORRECTION_TAGS,
    EXPAND_TO_ORIGINAL,
    EXPAND_TO_STRUCTURED,
    OVERUSE_FEATURES,
    SPECIAL_POS_NAMES,
    SPECIAL_POS_TAGS,
    TAG_AMBIG_PRON,
    TAG_READING,
)
from .errors import TagFormatError


COMMENT_MARKS = {
    "r": "?",
    "e": "+",
    "i": "#",
}


def get_special_part_of_speech(key: str | None) -> str:
    if key is None:
        raise TagFormatError("Part of speech key is undefined")
    try:
        return SPECIAL_POS_NAMES[key]
    except KeyError as exc:
        raise TagFormatError(f"Unknown part of speech key: '{key}'") from exc


def get_partial_parsed_line(surface: str, *features: str) -> str:
    if features:
        return f"\n{surface}\t{','.join(features)}\n"
    return f"\n{surface}\n"


def get_prime_surface(value: str) -> str:
    surface = value.split("/")[0]
    return re.sub(r"（.+?）", "", surface)


def split_comments(content: str) -> tuple[str, dict[str, str]]:
    comments: dict[str, str] = {}
    indexes = {
        comment_type: content.rfind(mark)
        for comment_type, mark in COMMENT_MARKS.items()
    }

    for comment_type, index in sorted(indexes.items(), key=lambda item: item[1], reverse=True):
        if index >= 0:
            comments[comment_type] = content[index:]
            content = content[:index]

    return content, comments


def expand_mjk_bracket(content: str, expand_to: int) -> str:
    original_content = content
    content, comments = split_comments(content)

    parts = content.split("=")
    original = parts[0]
    tag = parts[1] if len(parts) >= 2 else None
    analytic = parts[2] if len(parts) >= 3 else None

    features: list[str] = []

    if tag is None:
        surface = original
        if surface == original_content:
            raise TagFormatError("Illegal tag format")
        if comments.get("e") == "+過剰使用":
            features = OVERUSE_FEATURES.get(surface, [])
    elif tag in SPECIAL_POS_TAGS:
        if analytic is not None:
            raise TagFormatError("Illegal tag format")
        surface = original
        features = [get_special_part_of_speech(tag)]
    elif tag in CORRECTION_TAGS:
        if not analytic:
            raise TagFormatError("Illegal tag format")
        source = original if expand_to == EXPAND_TO_ORIGINAL else analytic
        surface = get_prime_surface(source)
    elif tag in {TAG_READING, TAG_AMBIG_PRON}:
        surface = get_prime_surface(original)
    else:
        raise TagFormatError(f"Unknown tag: '{tag}'")

    if "（" in surface or "）" in surface:
        raise TagFormatError("Illegal tag format")

    if expand_to == EXPAND_TO_STRUCTURED:
        return get_partial_parsed_line(surface, *features)
    return surface
