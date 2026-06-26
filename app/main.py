from __future__ import annotations

import argparse
from pathlib import Path
import sys

from app.core.errors import MorphAppError
from app.core.mecab_runner import MecabRunner
from app.core.models import ParseRequest
from app.core.parser import Parser
from app.core.user_dictionary import find_bundled_user_dic
from app.export.csv_exporter import export_parse_result


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    effective_argv = sys.argv[1:] if argv is None else argv
    if not effective_argv and getattr(sys, "frozen", False):
        effective_argv = ["gui"]
    args = parser.parse_args(effective_argv)

    if args.command == "parse":
        return run_parse(args)
    if args.command == "gui":
        try:
            from app.gui.main_window import run_gui

            return run_gui()
        except RuntimeError as exc:
            print(f"エラー: {exc}", file=sys.stderr)
            return 2

    parser.print_help()
    return 1


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="morph-app")
    subparsers = parser.add_subparsers(dest="command")

    parse_parser = subparsers.add_parser("parse", help="文字化テキストを解析してCSVに保存する")
    parse_parser.add_argument("input", type=Path, help="入力テキストファイル")
    parse_parser.add_argument("--participant-id", required=True, help="例: ABC01")
    parse_parser.add_argument("--survey-content", required=True, help="例: SW1, RP1")
    parse_parser.add_argument("--output", type=Path, required=True, help="保存先CSV")
    parse_parser.add_argument("--encoding", default="utf-8", help="入力ファイルの文字コード")
    parse_parser.add_argument("--dic-dir", type=Path, help="UniDic辞書ディレクトリ")
    parse_parser.add_argument("--user-dic", type=Path, help="ユーザー辞書 .dic")
    parse_parser.add_argument(
        "--dont-use-tags",
        action="store_true",
        help="解析にタグを使用しない",
    )

    subparsers.add_parser("gui", help="GUIを起動する")
    return parser


def run_parse(args: argparse.Namespace) -> int:
    try:
        text = args.input.read_text(encoding=args.encoding)
        request = ParseRequest(
            participant_id=args.participant_id,
            survey_content=args.survey_content,
            text=text,
            dont_use_tags=args.dont_use_tags,
        )
        tokenizer = MecabRunner(
            dic_dir=args.dic_dir,
            user_dic=args.user_dic or find_bundled_user_dic(),
        )
        result = Parser(tokenizer).parse(request)
        export_parse_result(args.output, result)
    except MorphAppError as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"ファイルエラー: {exc}", file=sys.stderr)
        return 2

    print(f"{len(result.rows)}行を保存しました: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
