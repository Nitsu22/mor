from __future__ import annotations

from pathlib import Path
import sys

from app.core.constants import SURVEY_CONTENTS, SURVEY_LABELS
from app.core.errors import MorphAppError
from app.core.mecab_runner import MecabRunner
from app.core.models import ParseRequest, ParseResult
from app.core.parser import Parser
from app.export.csv_exporter import export_parse_result


LEGEND_ROWS: tuple[tuple[str, str], ...] = (
    ("[発音通り=F]", "感動詞 (フィラーを含む)"),
    ("[発音通り=R]", "連体詞"),
    ("[発音通り=N]", "固有名詞"),
    ("[発音通り=X]", "解析困難箇所"),
    ("[発音通り=T=解析用]", "訂正 (長音やポーズ)"),
    ("[発音通り=G=解析用]", "誤用 (発音や活用)"),
    ("[発音通り=K=解析用]", "?"),
    ("[発音通り（読み）=Y]", "読み指定"),
    ("[発音 1/発音 2...=H]", "発音が曖昧"),
    ("[...?補足情報]", "判断待ち補足情報"),
    ("[...+補足情報]", "外部向け補足情報"),
    ("[...#補足情報]", "内部向け補足情報"),
    ("【...】", "個人情報"),
    ("〈...〉", "あいづち"),
    ("｛...｝", "非言語行動"),
)


def run_gui() -> int:
    try:
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QFont
        from PySide6.QtWidgets import (
            QApplication,
            QCheckBox,
            QComboBox,
            QFileDialog,
            QGridLayout,
            QHBoxLayout,
            QHeaderView,
            QLabel,
            QLineEdit,
            QMainWindow,
            QMessageBox,
            QPushButton,
            QPlainTextEdit,
            QSizePolicy,
            QStatusBar,
            QTableWidget,
            QTableWidgetItem,
            QVBoxLayout,
            QWidget,
        )
    except ImportError as exc:
        raise RuntimeError("GUIを起動するには PySide6 が必要です。") from exc

    class MainWindow(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            self._result: ParseResult | None = None

            self.setWindowTitle("形態素解析ツール")
            self.resize(1320, 820)

            self.participant_id_edit = QLineEdit()
            self.participant_id_edit.setPlaceholderText("協力者 ID を入力してください。")
            self.participant_id_edit.setMaxLength(5)
            self.participant_id_edit.setMinimumWidth(250)

            self.survey_combo = QComboBox()
            for survey in SURVEY_CONTENTS:
                self.survey_combo.addItem(SURVEY_LABELS[survey], survey)
            self.survey_combo.setCurrentIndex(SURVEY_CONTENTS.index("SW1"))
            self.survey_combo.setMinimumWidth(250)

            self.dont_use_tags_check = QCheckBox("解析にタグを使用しない")

            self.input_edit = QPlainTextEdit()
            self.input_edit.setPlaceholderText("文字化テキストを入力してください。")
            self.input_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
            self.input_edit.setMinimumHeight(240)

            self.parse_button = QPushButton("解析する")
            self.parse_button.setObjectName("primaryButton")
            self.parse_button.clicked.connect(self._parse_text)

            self.save_button = QPushButton("解析結果をダウンロードする")
            self.save_button.setObjectName("primaryButton")
            self.save_button.clicked.connect(self._save_csv)

            self.clear_button = QPushButton("クリアする")
            self.clear_button.clicked.connect(self._clear)

            self.legend_table = QTableWidget()
            self._setup_legend_table()

            self.result_table = QTableWidget()
            self.result_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.result_table.setAlternatingRowColors(True)
            self.result_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            self.result_table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
            self.result_table.horizontalHeader().setStretchLastSection(True)
            self.result_table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Interactive
            )

            self.status_label = QLabel("未解析")

            self._apply_styles(app)
            self.setCentralWidget(self._build_body())
            self.setStatusBar(QStatusBar())
            self.statusBar().addWidget(self.status_label, 1)

        def _build_body(self) -> QWidget:
            root = QWidget()
            root_layout = QVBoxLayout(root)
            root_layout.setContentsMargins(20, 18, 20, 16)
            root_layout.setSpacing(14)

            title_label = QLabel("形態素解析ツール")
            title_label.setObjectName("titleLabel")

            top_layout = QHBoxLayout()
            top_layout.setSpacing(34)
            top_layout.addWidget(self._build_input_panel(), 1)
            top_layout.addWidget(self._build_legend_panel())

            result_label = QLabel("解析結果")
            result_label.setObjectName("sectionLabel")

            root_layout.addWidget(title_label)
            root_layout.addLayout(top_layout, 0)
            root_layout.addWidget(result_label)
            root_layout.addWidget(self.result_table, 1)
            return root

        def _build_input_panel(self) -> QWidget:
            panel = QWidget()
            layout = QVBoxLayout(panel)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(14)

            fields_layout = QGridLayout()
            fields_layout.setHorizontalSpacing(34)
            fields_layout.setVerticalSpacing(8)

            participant_label = QLabel("協力者 ID")
            participant_label.setObjectName("fieldLabel")
            survey_label = QLabel("調査内容")
            survey_label.setObjectName("fieldLabel")

            fields_layout.addWidget(participant_label, 0, 0)
            fields_layout.addWidget(survey_label, 0, 1)
            fields_layout.addWidget(self.participant_id_edit, 1, 0)
            fields_layout.addWidget(self.survey_combo, 1, 1)
            fields_layout.setColumnStretch(0, 1)
            fields_layout.setColumnStretch(1, 1)

            text_label = QLabel("文字化テキスト入力欄")
            text_label.setObjectName("fieldLabel")

            note_label = QLabel(
                "文字化テキスト内で使用する特殊なタグや括弧についての詳細は、"
                "別途、文字化ルールを記載したドキュメントにしたがってください。"
            )
            note_label.setObjectName("noteLabel")
            note_label.setWordWrap(True)

            button_row = QHBoxLayout()
            button_row.setSpacing(0)
            button_row.addWidget(self.parse_button)
            button_row.addWidget(self.save_button)
            button_row.addWidget(self.clear_button)
            button_row.addStretch(1)
            button_row.addWidget(self.dont_use_tags_check)

            layout.addLayout(fields_layout)
            layout.addWidget(text_label)
            layout.addWidget(self.input_edit)
            layout.addWidget(note_label)
            layout.addLayout(button_row)
            layout.addStretch(1)
            return panel

        def _build_legend_panel(self) -> QWidget:
            panel = QWidget()
            panel.setFixedWidth(430)
            layout = QVBoxLayout(panel)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(8)

            legend_label = QLabel("凡例")
            legend_label.setObjectName("fieldLabel")
            layout.addWidget(legend_label)
            layout.addWidget(self.legend_table)
            return panel

        def _setup_legend_table(self) -> None:
            self.legend_table.setColumnCount(2)
            self.legend_table.setRowCount(len(LEGEND_ROWS))
            self.legend_table.horizontalHeader().hide()
            self.legend_table.verticalHeader().hide()
            self.legend_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.legend_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.legend_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
            self.legend_table.setAlternatingRowColors(True)
            self.legend_table.setShowGrid(False)
            self.legend_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            self.legend_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            self.legend_table.verticalHeader().setDefaultSectionSize(32)
            self.legend_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.legend_table.setFixedHeight(32 * len(LEGEND_ROWS) + 2)

            for row_index, (tag, description) in enumerate(LEGEND_ROWS):
                for column_index, value in enumerate((tag, description)):
                    item = QTableWidgetItem(value)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.legend_table.setItem(row_index, column_index, item)

        def _parse_text(self) -> None:
            self.parse_button.setEnabled(False)
            self.save_button.setEnabled(False)
            self.status_label.setText("解析中...")
            try:
                result = self._parse_current_input()
            except MorphAppError as exc:
                self._result = None
                self.status_label.setText("解析エラー")
                QMessageBox.warning(self, "解析エラー", str(exc))
            except OSError as exc:
                self._result = None
                self.status_label.setText("ファイルエラー")
                QMessageBox.warning(self, "ファイルエラー", str(exc))
            except Exception as exc:  # noqa: BLE001 - GUI should report unexpected failures.
                self._result = None
                self.status_label.setText("予期しないエラー")
                QMessageBox.critical(self, "予期しないエラー", str(exc))
            else:
                self._set_result(result)
            finally:
                self.parse_button.setEnabled(True)
                self.save_button.setEnabled(True)

        def _save_csv(self) -> None:
            self.parse_button.setEnabled(False)
            self.save_button.setEnabled(False)
            self.status_label.setText("解析中...")
            try:
                result = self._parse_current_input()
            except MorphAppError as exc:
                self._result = None
                self.status_label.setText("解析エラー")
                QMessageBox.warning(self, "解析エラー", str(exc))
                self.parse_button.setEnabled(True)
                self.save_button.setEnabled(True)
                return
            except OSError as exc:
                self._result = None
                self.status_label.setText("ファイルエラー")
                QMessageBox.warning(self, "ファイルエラー", str(exc))
                self.parse_button.setEnabled(True)
                self.save_button.setEnabled(True)
                return
            except Exception as exc:  # noqa: BLE001 - GUI should report unexpected failures.
                self._result = None
                self.status_label.setText("予期しないエラー")
                QMessageBox.critical(self, "予期しないエラー", str(exc))
                self.parse_button.setEnabled(True)
                self.save_button.setEnabled(True)
                return
            else:
                self._set_result(result)
                self.parse_button.setEnabled(True)
                self.save_button.setEnabled(True)

            default_name = self._default_output_name()
            selected, _ = QFileDialog.getSaveFileName(
                self,
                "解析結果をダウンロードする",
                str(Path.home() / default_name),
                "CSV files (*.csv);;All files (*)",
            )
            if not selected:
                return

            try:
                export_parse_result(selected, self._result)
            except OSError as exc:
                self.status_label.setText("保存エラー")
                QMessageBox.warning(self, "保存エラー", str(exc))
                return

            self.status_label.setText(f"保存しました: {selected}")

        def _clear(self) -> None:
            self.participant_id_edit.clear()
            self.survey_combo.setCurrentIndex(SURVEY_CONTENTS.index("SW1"))
            self.dont_use_tags_check.setChecked(False)
            self.input_edit.clear()
            self.result_table.clear()
            self.result_table.setRowCount(0)
            self.result_table.setColumnCount(0)
            self._result = None
            self.status_label.setText("未解析")

        def _parse_current_input(self) -> ParseResult:
            request = ParseRequest(
                participant_id=self.participant_id_edit.text().strip().upper(),
                survey_content=self.survey_combo.currentData(),
                text=self.input_edit.toPlainText(),
                dont_use_tags=self.dont_use_tags_check.isChecked(),
            )
            return Parser(MecabRunner()).parse(request)

        def _set_result(self, result: ParseResult) -> None:
            self._result = result
            self._show_result(result)
            self.status_label.setText(f"{len(result.rows)} トークン")

        def _show_result(self, result: ParseResult) -> None:
            rows = result.to_table()
            self.result_table.clear()
            self.result_table.setRowCount(len(rows))
            self.result_table.setColumnCount(len(result.headers))
            self.result_table.setHorizontalHeaderLabels(list(result.headers))

            for row_index, values in enumerate(rows):
                for column_index, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.result_table.setItem(row_index, column_index, item)

            self.result_table.resizeColumnsToContents()

        def _default_output_name(self) -> str:
            participant_id = self.participant_id_edit.text().strip().upper() or "result"
            survey_content = self.survey_combo.currentData() or "parse"
            return f"{participant_id}_{survey_content}.csv"

        @staticmethod
        def _apply_styles(app: QApplication) -> None:
            font = QFont()
            font.setPointSize(14)
            app.setFont(font)
            app.setStyleSheet(
                """
                QMainWindow, QWidget {
                    background: #ffffff;
                    color: #333333;
                }
                QLabel#titleLabel {
                    font-size: 28px;
                    font-weight: 700;
                    margin-bottom: 8px;
                }
                QLabel#fieldLabel, QLabel#sectionLabel {
                    font-size: 16px;
                    font-weight: 700;
                    margin-top: 2px;
                }
                QLabel#noteLabel {
                    color: #777777;
                    font-size: 14px;
                }
                QLineEdit, QComboBox, QPlainTextEdit {
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 8px 10px;
                    background: #ffffff;
                    selection-background-color: #337ab7;
                }
                QLineEdit, QComboBox {
                    min-height: 36px;
                }
                QPlainTextEdit {
                    font-size: 15px;
                }
                QPushButton {
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 8px 16px;
                    min-height: 34px;
                    background: #ffffff;
                }
                QPushButton#primaryButton {
                    color: #ffffff;
                    background: #337ab7;
                    border-color: #2e6da4;
                    font-weight: 700;
                }
                QPushButton#primaryButton:disabled {
                    color: #e8eef5;
                    background: #75a7cf;
                    border-color: #6f9ec4;
                }
                QCheckBox {
                    spacing: 8px;
                    font-size: 15px;
                }
                QTableWidget {
                    border: 1px solid #dddddd;
                    background: #ffffff;
                    alternate-background-color: #f7f7f7;
                    gridline-color: #dddddd;
                }
                QTableWidget::item {
                    padding: 6px 10px;
                }
                QHeaderView::section {
                    background: #f7f7f7;
                    border: 1px solid #dddddd;
                    padding: 6px 10px;
                    font-weight: 700;
                }
                """
            )

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    return app.exec()
