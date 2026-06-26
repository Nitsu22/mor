from __future__ import annotations

import shutil
import struct
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QGuiApplication,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ICONSET = ASSETS / "icon.iconset"
PNG_1024 = ASSETS / "icon.png"
ICNS = ASSETS / "icon.icns"
ICO = ASSETS / "icon.ico"


def main() -> int:
    app = QGuiApplication.instance() or QGuiApplication([])
    ASSETS.mkdir(exist_ok=True)

    base = _draw_icon(1024)
    base.save(str(PNG_1024))

    if ICONSET.exists():
        shutil.rmtree(ICONSET)
    ICONSET.mkdir()

    sizes = (16, 32, 128, 256, 512)
    for size in sizes:
        _save_icon_variant(base, size, ICONSET / f"icon_{size}x{size}.png")
        _save_icon_variant(base, size * 2, ICONSET / f"icon_{size}x{size}@2x.png")
    _save_icon_variant(base, 48, ICONSET / "icon_48x48.png")

    _write_icns(
        ICNS,
        (
            ("icp4", ICONSET / "icon_16x16.png"),
            ("icp5", ICONSET / "icon_32x32.png"),
            ("icp6", ICONSET / "icon_32x32@2x.png"),
            ("ic07", ICONSET / "icon_128x128.png"),
            ("ic08", ICONSET / "icon_256x256.png"),
            ("ic09", ICONSET / "icon_512x512.png"),
            ("ic10", ICONSET / "icon_512x512@2x.png"),
        ),
    )
    _write_ico(
        ICO,
        (
            (16, ICONSET / "icon_16x16.png"),
            (32, ICONSET / "icon_32x32.png"),
            (48, ICONSET / "icon_48x48.png"),
            (256, ICONSET / "icon_256x256.png"),
        ),
    )
    app.quit()
    print(ICNS)
    print(ICO)
    return 0


def _draw_icon(size: int) -> QImage:
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)

    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

    margin = size * 0.07
    rect = QRectF(margin, margin, size - margin * 2, size - margin * 2)
    radius = size * 0.18

    shadow_path = QPainterPath()
    shadow_path.addRoundedRect(rect.translated(0, size * 0.025), radius, radius)
    painter.fillPath(shadow_path, QColor(0, 0, 0, 42))

    background = QLinearGradient(rect.topLeft(), rect.bottomRight())
    background.setColorAt(0.0, QColor("#1f6fb2"))
    background.setColorAt(0.55, QColor("#2a9d8f"))
    background.setColorAt(1.0, QColor("#1b4965"))

    tile_path = QPainterPath()
    tile_path.addRoundedRect(rect, radius, radius)
    painter.fillPath(tile_path, background)

    painter.setPen(QPen(QColor(255, 255, 255, 70), size * 0.015))
    painter.drawRoundedRect(rect.adjusted(size * 0.02, size * 0.02, -size * 0.02, -size * 0.02), radius * 0.85, radius * 0.85)

    _draw_token_bar(painter, size)
    _draw_main_glyph(painter, size)
    _draw_nodes(painter, size)

    painter.end()
    return image


def _draw_main_glyph(painter: QPainter, size: int) -> None:
    painter.setPen(QColor("#ffffff"))
    font = QFont("Hiragino Sans")
    font.setPixelSize(int(size * 0.42))
    font.setWeight(QFont.Weight.Black)
    painter.setFont(font)
    painter.drawText(QRectF(0, size * 0.17, size, size * 0.5), Qt.AlignmentFlag.AlignCenter, "形")


def _draw_token_bar(painter: QPainter, size: int) -> None:
    labels = ("名", "動", "助")
    token_w = size * 0.19
    token_h = size * 0.105
    gap = size * 0.025
    total_w = token_w * len(labels) + gap * (len(labels) - 1)
    x = (size - total_w) / 2
    y = size * 0.69

    font = QFont("Hiragino Sans")
    font.setPixelSize(int(size * 0.052))
    font.setWeight(QFont.Weight.Bold)
    painter.setFont(font)

    for index, label in enumerate(labels):
        token_rect = QRectF(x + index * (token_w + gap), y, token_w, token_h)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, 230))
        painter.drawRoundedRect(token_rect, size * 0.028, size * 0.028)
        painter.setPen(QColor("#1b4965"))
        painter.drawText(token_rect, Qt.AlignmentFlag.AlignCenter, label)


def _draw_nodes(painter: QPainter, size: int) -> None:
    pen = QPen(QColor(255, 255, 255, 135), size * 0.012)
    painter.setPen(pen)
    painter.setBrush(QColor(255, 255, 255, 210))

    points = [
        (size * 0.29, size * 0.58),
        (size * 0.43, size * 0.61),
        (size * 0.57, size * 0.58),
        (size * 0.71, size * 0.61),
    ]

    for start, end in zip(points, points[1:]):
        painter.drawLine(int(start[0]), int(start[1]), int(end[0]), int(end[1]))

    painter.setPen(Qt.PenStyle.NoPen)
    for x, y in points:
        painter.drawEllipse(QRectF(x - size * 0.025, y - size * 0.025, size * 0.05, size * 0.05))


def _save_icon_variant(base: QImage, size: int, path: Path) -> None:
    scaled = base.scaled(
        size,
        size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    scaled.save(str(path))


def _write_icns(path: Path, chunks: tuple[tuple[str, Path], ...]) -> None:
    parts = []
    total_size = 8
    for chunk_type, png_path in chunks:
        data = png_path.read_bytes()
        chunk = chunk_type.encode("ascii") + struct.pack(">I", len(data) + 8) + data
        parts.append(chunk)
        total_size += len(chunk)

    path.write_bytes(b"icns" + struct.pack(">I", total_size) + b"".join(parts))


def _write_ico(path: Path, images: tuple[tuple[int, Path], ...]) -> None:
    png_images = [(size, png_path.read_bytes()) for size, png_path in images]
    header_size = 6 + 16 * len(png_images)
    offset = header_size
    entries = []
    payloads = []

    for size, data in png_images:
        icon_size = 0 if size >= 256 else size
        entries.append(
            struct.pack(
                "<BBBBHHII",
                icon_size,
                icon_size,
                0,
                0,
                1,
                32,
                len(data),
                offset,
            )
        )
        payloads.append(data)
        offset += len(data)

    path.write_bytes(
        struct.pack("<HHH", 0, 1, len(png_images)) + b"".join(entries) + b"".join(payloads)
    )


if __name__ == "__main__":
    raise SystemExit(main())
