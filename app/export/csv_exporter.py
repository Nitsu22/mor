from __future__ import annotations

from pathlib import Path
from typing import Iterable

from app.core.models import ParseResult, TokenRow


def export_parse_result(path: str | Path, result: ParseResult) -> None:
    export_csv(path, result.headers, result.rows)


def export_csv(
    path: str | Path,
    headers: Iterable[str],
    rows: Iterable[TokenRow | Iterable[str]],
) -> None:
    output_path = Path(path)
    lines = ["\t".join(headers)]
    for row in rows:
        values = row.to_list() if isinstance(row, TokenRow) else list(row)
        lines.append("\t".join(values))

    text = "\r\n".join(lines) + "\r\n"
    output_path.write_bytes(("\ufeff" + text).encode("utf-16le"))
