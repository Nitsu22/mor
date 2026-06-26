from __future__ import annotations

from typing import Protocol

from .constants import OUTPUT_FEATURES, OUTPUT_HEADERS
from .errors import ValidationError
from .mecab_runner import MecabRunner
from .models import MecabToken, ParseRequest, ParseResult, TokenRow
from .normalizer import normalize_to_partial_parse
from .validator import (
    normalize_input_text,
    parse_speaker_line,
    split_mjk_lines,
    validate_request,
)


class Tokenizer(Protocol):
    def parse(self, text: str) -> list[MecabToken]:
        ...


class Parser:
    def __init__(self, tokenizer: Tokenizer | None = None) -> None:
        self.tokenizer = tokenizer or MecabRunner()

    def parse(self, request: ParseRequest) -> ParseResult:
        validate_request(request)

        text = normalize_input_text(request.text)
        mjk_id = f"{request.participant_id}-{request.survey_content}"
        rows: list[TokenRow] = []

        for line_number, line in enumerate(split_mjk_lines(text), start=1):
            speaker_symbol, tagged_text = parse_speaker_line(
                line,
                request.survey_content,
                line_number,
            )
            utterance_id = f"{mjk_id}-{line_number * 10:04d}-{speaker_symbol}"
            normalized = normalize_to_partial_parse(
                line_number,
                tagged_text,
                request.dont_use_tags,
            )
            mecab_tokens = self.tokenizer.parse(normalized.text)
            rows.extend(
                self._tokens_to_rows(
                    utterance_id,
                    mecab_tokens,
                    normalized.tagged_info,
                    normalized.once_deleted,
                )
            )

        if not rows:
            raise ValidationError("文字化テキストを入力してから解析してください。")

        return ParseResult(headers=OUTPUT_HEADERS, rows=rows)

    def _tokens_to_rows(
        self,
        utterance_id: str,
        mecab_tokens: list[MecabToken],
        tagged_info: dict[int, str],
        once_deleted,
    ) -> list[TokenRow]:
        rows: list[TokenRow] = []
        incl_idx = 0
        excl_idx = 0

        for token in mecab_tokens:
            for deleted in once_deleted.get(excl_idx, []):
                rows.append(
                    self._make_row(
                        utterance_id if not rows else "",
                        deleted.surface,
                        deleted.features,
                        "",
                    )
                )
                incl_idx += len(deleted.surface)

            remarks = []
            for index in range(incl_idx, incl_idx + len(token.surface)):
                if index in tagged_info:
                    remarks.append(tagged_info[index])

            rows.append(
                self._make_row(
                    utterance_id if not rows else "",
                    token.surface,
                    token.features,
                    ", ".join(remarks),
                )
            )

            incl_idx += len(token.surface)
            excl_idx += len(token.surface)

        return rows

    def _make_row(
        self,
        utterance_id: str,
        surface: str,
        features: list[str],
        remark: str,
    ) -> TokenRow:
        values = [_feature_at(features, index) for index in OUTPUT_FEATURES]
        return TokenRow(
            utterance_id=utterance_id,
            surface=surface,
            lemma=values[0],
            lform=values[1],
            pos1=values[2],
            pos2=values[3],
            pos3=values[4],
            pos4=values[5],
            ctype=values[6],
            cform=values[7],
            orth=values[8],
            pron=values[9],
            orth_base=values[10],
            pron_base=values[11],
            goshu=values[12],
            remark=remark,
        )


def _feature_at(features: list[str], index: int) -> str:
    if index >= len(features):
        return ""
    return features[index]
