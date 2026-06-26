from __future__ import annotations

# app/core/models.py

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ParseRequest:
    participant_id: str
    survey_content: str
    text: str
    dont_use_tags: bool = False


@dataclass(frozen=True)
class TokenRow:
    utterance_id: str
    surface: str
    lemma: str
    lform: str
    pos1: str
    pos2: str
    pos3: str
    pos4: str
    ctype: str
    cform: str
    orth: str
    pron: str
    orth_base: str
    pron_base: str
    goshu: str
    remark: str = ""

    def to_list(self) -> list[str]:
        return [
            self.utterance_id,
            self.surface,
            self.lemma,
            self.lform,
            self.pos1,
            self.pos2,
            self.pos3,
            self.pos4,
            self.ctype,
            self.cform,
            self.orth,
            self.pron,
            self.orth_base,
            self.pron_base,
            self.goshu,
            self.remark,
        ]


@dataclass(frozen=True)
class ParseResult:
    headers: tuple[str, ...]
    rows: list[TokenRow]
    warnings: list[str] = field(default_factory=list)

    def to_table(self) -> list[list[str]]:
        return [row.to_list() for row in self.rows]


@dataclass(frozen=True)
class DeletedSpan:
    index: int
    surface: str
    features: list[str]


@dataclass(frozen=True)
class NormalizedText:
    text: str
    tagged_info: dict[int, str]
    once_deleted: dict[int, list[DeletedSpan]]


@dataclass(frozen=True)
class MecabToken:
    surface: str
    features: list[str]
