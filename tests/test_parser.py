from app.core.models import MecabToken, ParseRequest
from app.core.parser import Parser


class FakeTokenizer:
    def parse(self, text: str) -> list[MecabToken]:
        assert text.endswith("EOS\n")
        return [
            MecabToken(
                surface="これは",
                features=[
                    "代名詞",
                    "*",
                    "*",
                    "*",
                    "*",
                    "*",
                    "コレ",
                    "此れ",
                    "これ",
                    "コレ",
                    "これ",
                    "コレ",
                    "和",
                ],
            )
        ]


def test_parser_generates_utterance_id_for_story_writing():
    request = ParseRequest(
        participant_id="ABC01",
        survey_content="SW1",
        text="これは",
    )
    result = Parser(FakeTokenizer()).parse(request)

    assert result.rows[0].utterance_id == "ABC01-SW1-0010-K"
    assert result.rows[0].surface == "これは"
    assert result.rows[0].lemma == "此れ"
