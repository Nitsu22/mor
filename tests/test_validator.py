import pytest

from app.core.errors import ValidationError
from app.core.validator import parse_speaker_line, split_mjk_lines, validate_participant_id


def test_validate_participant_id_accepts_expected_format():
    validate_participant_id("ABC01")


def test_validate_participant_id_rejects_lowercase():
    with pytest.raises(ValidationError):
        validate_participant_id("abc01")


def test_parse_speaker_line_for_dialogue():
    assert parse_speaker_line("K こんにちは", "RP1", 1) == ("K", "こんにちは")


def test_parse_speaker_line_accepts_bracketed_dialogue_marker():
    assert parse_speaker_line("[K]こんにちは", "RP1", 1) == ("K", "こんにちは")
    assert parse_speaker_line("[C] こんにちは", "RP1", 1) == ("C", "こんにちは")


def test_parse_speaker_line_for_story_writing():
    assert parse_speaker_line("こんにちは", "SW1", 1) == ("K", "こんにちは")


def test_parse_speaker_line_strips_optional_story_writing_marker():
    assert parse_speaker_line("K こんにちは", "SW1", 1) == ("K", "こんにちは")
    assert parse_speaker_line("[K]こんにちは", "SW1", 1) == ("K", "こんにちは")


def test_split_mjk_lines_roughly_matches_perl_split():
    assert split_mjk_lines("A\r\nB\n\nC\n") == ["A", "B", "C"]
