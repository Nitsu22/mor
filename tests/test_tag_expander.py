import pytest

from app.core.constants import (
    EXPAND_TO_ANALYTIC,
    EXPAND_TO_ORIGINAL,
    EXPAND_TO_STRUCTURED,
)
from app.core.errors import TagFormatError
from app.core.tag_expander import expand_mjk_bracket, get_prime_surface


def test_expand_filler_to_structured_line():
    assert expand_mjk_bracket("えーと=F", EXPAND_TO_STRUCTURED) == "\nえーと\t感動詞\n"


def test_expand_correction_uses_analytic_surface():
    assert expand_mjk_bracket("ーと=T=と", EXPAND_TO_ANALYTIC) == "と"


def test_expand_correction_can_use_original_surface():
    assert expand_mjk_bracket("ーと=T=と", EXPAND_TO_ORIGINAL) == "ーと"


def test_expand_comment_only_tag():
    assert expand_mjk_bracket("な+過剰使用", EXPAND_TO_STRUCTURED) == (
        "\nな\t助動詞,*,*,*,助動詞-ダ,連体形-一般\n"
    )


def test_get_prime_surface_uses_first_candidate_and_removes_reading():
    assert get_prime_surface("行く（イク）/ゆく") == "行く"


def test_plain_bracket_content_is_illegal():
    with pytest.raises(TagFormatError):
        expand_mjk_bracket("えーと", EXPAND_TO_ANALYTIC)
