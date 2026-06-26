from __future__ import annotations

from pathlib import Path
import shlex

from .errors import MecabError
from .models import MecabToken


class MecabRunner:
    def __init__(
        self,
        dic_dir: str | Path | None = None,
        user_dic: str | Path | None = None,
    ) -> None:
        self.dic_dir = Path(dic_dir) if dic_dir else self._default_dic_dir()
        self.user_dic = Path(user_dic) if user_dic else None
        self._tagger = None

    def parse(self, text: str) -> list[MecabToken]:
        tagger = self._get_tagger()
        node = tagger.parseToNode(text)
        if node is None:
            raise MecabError("MeCabの解析結果が空でした。")

        tokens: list[MecabToken] = []
        node = node.next  # skip BOS
        while node:
            surface = node.surface or ""
            feature = node.feature or ""
            tokens.append(MecabToken(surface=surface, features=feature.split(",")))
            node = node.next
        return tokens

    def _get_tagger(self):
        if self._tagger is not None:
            return self._tagger

        try:
            import MeCab
        except ImportError as exc:
            raise MecabError(
                "mecab-python3 が見つかりません。`pip install mecab-python3 unidic-lite` "
                "を実行してください。"
            ) from exc

        args = ["-p"]
        if self.dic_dir:
            args.extend(["-d", str(self.dic_dir)])
        if self.user_dic:
            if not self.user_dic.exists():
                raise MecabError(f"ユーザー辞書が見つかりません: {self.user_dic}")
            args.extend(["-u", str(self.user_dic)])

        try:
            self._tagger = MeCab.Tagger(" ".join(shlex.quote(arg) for arg in args))
        except RuntimeError as exc:
            raise MecabError(f"MeCabの初期化に失敗しました: {exc}") from exc
        return self._tagger

    @staticmethod
    def _default_dic_dir() -> Path | None:
        try:
            import unidic_lite
        except ImportError:
            return None
        return Path(unidic_lite.DICDIR)
