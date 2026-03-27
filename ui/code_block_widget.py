import os
import re
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.config import Config


class ToolMetricWidget(QFrame):

    def __init__(self, label, value):
        super().__init__()
        self.label = label
        self.value = value
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(2)

        value_label = QLabel(self.value)
        value_label.setWordWrap(True)
        value_label.setStyleSheet(
            f"""
            QLabel {{
                color: #f5fbff;
                font-size: {Config.FONT_SIZE_MEDIUM + 1}px;
                font-weight: 700;
                font-family: '{Config.FONT_FAMILY}';
                background: transparent;
            }}
            """
        )
        layout.addWidget(value_label)

        label_label = QLabel(self.label.upper())
        label_label.setStyleSheet(
            f"""
            QLabel {{
                color: rgba(190, 225, 255, 0.72);
                font-size: {max(Config.FONT_SIZE_SMALL - 1, 10)}px;
                font-weight: 600;
                letter-spacing: 0.6px;
                font-family: '{Config.FONT_FAMILY}';
                background: transparent;
            }}
            """
        )
        layout.addWidget(label_label)

        self.setStyleSheet(
            """
            QFrame {
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(0, 198, 255, 0.16);
                border-radius: 12px;
            }
            """
        )


class ToolResultCard(QFrame):

    def __init__(self, tool_name, title, subtitle="", metrics=None, sections=None):
        super().__init__()
        self.tool_name = tool_name
        self.title = title
        self.subtitle = subtitle
        self.metrics = metrics or []
        self.sections = sections or []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        eyebrow = QLabel(self.tool_name.upper())
        eyebrow.setStyleSheet(
            f"""
            QLabel {{
                color: #66d9ff;
                font-size: {Config.FONT_SIZE_SMALL}px;
                font-weight: 700;
                letter-spacing: 1px;
                font-family: '{Config.FONT_FAMILY}';
                background: transparent;
            }}
            """
        )
        layout.addWidget(eyebrow)

        title_label = QLabel(self.title)
        title_label.setWordWrap(True)
        title_label.setStyleSheet(
            f"""
            QLabel {{
                color: #ffffff;
                font-size: {Config.FONT_SIZE_MEDIUM + 3}px;
                font-weight: 700;
                font-family: '{Config.FONT_FAMILY}';
                background: transparent;
            }}
            """
        )
        layout.addWidget(title_label)

        if self.subtitle:
            subtitle_label = QLabel(self.subtitle)
            subtitle_label.setWordWrap(True)
            subtitle_label.setStyleSheet(
                f"""
                QLabel {{
                    color: rgba(229, 242, 255, 0.82);
                    font-size: {Config.FONT_SIZE_MEDIUM}px;
                    font-weight: 500;
                    font-family: '{Config.FONT_FAMILY}';
                    background: transparent;
                }}
                """
            )
            layout.addWidget(subtitle_label)

        if self.metrics:
            metrics_grid = QGridLayout()
            metrics_grid.setHorizontalSpacing(10)
            metrics_grid.setVerticalSpacing(10)
            for index, (label, value) in enumerate(self.metrics):
                metrics_grid.addWidget(ToolMetricWidget(label, value), index // 2, index % 2)
            layout.addLayout(metrics_grid)

        for section_title, items in self.sections:
            section_label = QLabel(section_title)
            section_label.setStyleSheet(
                f"""
                QLabel {{
                    color: #7ee7ff;
                    font-size: {Config.FONT_SIZE_MEDIUM}px;
                    font-weight: 700;
                    font-family: '{Config.FONT_FAMILY}';
                    background: transparent;
                    margin-top: 4px;
                }}
                """
            )
            layout.addWidget(section_label)

            for item in items:
                item_label = QLabel(f"- {item}")
                item_label.setWordWrap(True)
                item_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                item_label.setStyleSheet(
                    f"""
                    QLabel {{
                        color: rgba(245, 251, 255, 0.94);
                        font-size: {Config.FONT_SIZE_MEDIUM}px;
                        font-weight: 500;
                        font-family: '{Config.FONT_FAMILY}';
                        background: transparent;
                        padding-left: 2px;
                    }}
                    """
                )
                layout.addWidget(item_label)

        self.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(10, 16, 29, 0.96),
                    stop:0.55 rgba(18, 32, 54, 0.96),
                    stop:1 rgba(8, 18, 31, 0.96));
                border: 1px solid rgba(0, 198, 255, 0.28);
                border-radius: 18px;
                margin: 4px 0px;
            }
            """
        )


class CodeBlockWidget(QFrame):

    def __init__(self, code_content, language=""):
        super().__init__()
        self.code_content = code_content.strip()
        self.language = language
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(12, 8, 12, 8)
        header_layout.setSpacing(8)

        if self.language:
            lang_label = QLabel(self.language.upper())
            lang_label.setStyleSheet(
                f"""
                QLabel {{
                    color: #00f5ff;
                    font-size: {Config.FONT_SIZE_SMALL}px;
                    font-weight: 600;
                    font-family: '{Config.FONT_FAMILY}';
                    background: transparent;
                    padding: 2px 6px;
                    border-radius: 4px;
                    border: 1px solid rgba(0, 245, 255, 0.3);
                }}
                """
            )
            header_layout.addWidget(lang_label)

        header_layout.addStretch()

        self.copy_button = QPushButton("Copy")
        self.copy_button.setStyleSheet(
            f"""
            QPushButton {{
                background: rgba(0, 245, 255, 0.1);
                border: 1px solid rgba(0, 245, 255, 0.3);
                border-radius: 6px;
                padding: 4px 12px;
                font-size: {Config.FONT_SIZE_SMALL}px;
                color: #00f5ff;
                font-weight: 500;
                font-family: '{Config.FONT_FAMILY}';
            }}
            QPushButton:hover {{
                background: rgba(0, 245, 255, 0.2);
                border: 1px solid rgba(0, 245, 255, 0.5);
            }}
            QPushButton:pressed {{
                background: rgba(0, 245, 255, 0.3);
                border: 1px solid rgba(0, 245, 255, 0.7);
            }}
            """
        )
        self.copy_button.clicked.connect(self.copy_code)
        header_layout.addWidget(self.copy_button)

        self.code_label = QLabel(self.code_content)
        self.code_label.setWordWrap(True)
        self.code_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.code_label.setFont(QFont("Consolas", 12))
        self.code_label.setStyleSheet(
            """
            QLabel {
                background: transparent;
                color: #e8f4fd;
                font-family: 'Consolas', 'Fira Code', 'Monaco', monospace;
                font-size: 13px;
                line-height: 1.4;
                padding: 12px 16px;
                white-space: pre-wrap;
            }
            """
        )

        layout.addLayout(header_layout)
        layout.addWidget(self.code_label)
        self.setLayout(layout)

        self.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:0.3 #16213e, stop:0.7 #0f3460, stop:1 #1a1a2e);
                border: 2px solid rgba(0, 245, 255, 0.4);
                border-radius: 12px;
                margin: 8px 0px;
            }
            QFrame:hover {
                border: 2px solid rgba(0, 245, 255, 0.6);
            }
            """
        )

        self.setFrameStyle(QFrame.StyledPanel)
        self.setLineWidth(0)

    def copy_code(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.code_content)

        original_text = self.copy_button.text()
        self.copy_button.setText("Copied")
        self.copy_button.setStyleSheet(
            f"""
            QPushButton {{
                background: rgba(0, 230, 118, 0.2);
                border: 1px solid rgba(0, 230, 118, 0.5);
                border-radius: 6px;
                padding: 4px 12px;
                font-size: {Config.FONT_SIZE_SMALL}px;
                color: #00e676;
                font-weight: 500;
                font-family: '{Config.FONT_FAMILY}';
            }}
            """
        )

        from PyQt5.QtCore import QTimer

        QTimer.singleShot(2000, lambda: self.reset_copy_button(original_text))

    def reset_copy_button(self, original_text):
        self.copy_button.setText(original_text)
        self.copy_button.setStyleSheet(
            f"""
            QPushButton {{
                background: rgba(0, 245, 255, 0.1);
                border: 1px solid rgba(0, 245, 255, 0.3);
                border-radius: 6px;
                padding: 4px 12px;
                font-size: {Config.FONT_SIZE_SMALL}px;
                color: #00f5ff;
                font-weight: 500;
                font-family: '{Config.FONT_FAMILY}';
            }}
            QPushButton:hover {{
                background: rgba(0, 245, 255, 0.2);
                border: 1px solid rgba(0, 245, 255, 0.5);
            }}
            QPushButton:pressed {{
                background: rgba(0, 245, 255, 0.3);
                border: 1px solid rgba(0, 245, 255, 0.7);
            }}
            """
        )


class EnhancedMessageWidget(QWidget):

    def __init__(self, sender, content, timestamp):
        super().__init__()
        self.sender = sender
        self.content = content
        self.timestamp = timestamp
        self.tool_payload = self.extract_tool_payload(content) if sender != "user" else None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(15, 5, 15, 5)
        main_layout.setSpacing(0)

        bubble_container = QWidget()
        bubble_layout = QVBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(15, 12, 15, 12)
        bubble_layout.setSpacing(8)

        self.parse_and_add_content(bubble_layout)

        time_label = QLabel(self.format_timestamp())
        time_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        bubble_layout.addWidget(time_label)

        bubble_container.setMaximumWidth(560 if self.tool_payload else 500)

        if self.sender == "user":
            main_layout.addStretch()
            main_layout.addWidget(bubble_container)
            bubble_container.setStyleSheet(
                f"""
                QWidget {{
                    background: {Config.ACCENT_GRADIENT};
                    border: none;
                    border-radius: 18px;
                    margin: 3px 0px;
                }}
                """
            )
            time_label.setStyleSheet(
                f"""
                QLabel {{
                    color: rgba(26, 26, 26, 0.7);
                    font-size: {Config.FONT_SIZE_SMALL}px;
                    font-weight: 500;
                    background: transparent;
                }}
                """
            )
            time_label.setAlignment(Qt.AlignRight)
        else:
            main_layout.addWidget(bubble_container)
            main_layout.addStretch()
            bubble_container.setStyleSheet(
                """
                QWidget {
                    background: rgba(255, 255, 255, 0.15);
                    border: none;
                    border-radius: 18px;
                    margin: 3px 0px;
                }
                """
            )
            time_label.setStyleSheet(
                f"""
                QLabel {{
                    color: rgba(255, 255, 255, 0.7);
                    font-size: {Config.FONT_SIZE_SMALL}px;
                    font-weight: 500;
                    background: transparent;
                }}
                """
            )
            time_label.setAlignment(Qt.AlignLeft)

        self.setLayout(main_layout)

    def parse_and_add_content(self, layout):
        if self.tool_payload:
            layout.addWidget(
                ToolResultCard(
                    self.tool_payload["tool_name"],
                    self.tool_payload["title"],
                    self.tool_payload["subtitle"],
                    self.tool_payload["metrics"],
                    self.tool_payload["sections"],
                )
            )
            return

        code_block_pattern = r"```(?:(\w+)\s*)?\n?(.*?)```"
        parts = re.split(code_block_pattern, self.content, flags=re.DOTALL)

        i = 0
        while i < len(parts):
            if i % 3 == 0:
                text = parts[i].strip()
                if text:
                    from utils.text_formatter import TextFormatter

                    formatted_text = TextFormatter.format_with_multiple_styles(text, self.sender)
                    text_label = QLabel(formatted_text)
                    text_label.setWordWrap(True)
                    text_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                    text_label.setTextFormat(Qt.RichText)
                    text_label.setMaximumWidth(450)

                    if self.sender == "user":
                        text_label.setStyleSheet(
                            f"""
                            QLabel {{
                                color: #1a1a1a;
                                font-size: {Config.FONT_SIZE_MEDIUM}px;
                                line-height: 1.4;
                                font-weight: 600;
                                font-family: '{Config.FONT_FAMILY}';
                                background: transparent;
                                padding: 2px 0px;
                            }}
                            """
                        )
                    else:
                        text_label.setStyleSheet(
                            f"""
                            QLabel {{
                                color: white;
                                font-size: {Config.FONT_SIZE_MEDIUM}px;
                                line-height: 1.4;
                                font-weight: 600;
                                font-family: '{Config.FONT_FAMILY}';
                                background: transparent;
                                padding: 2px 0px;
                            }}
                            """
                        )

                    layout.addWidget(text_label)

            elif i % 3 == 1:
                language = parts[i] if parts[i] else ""
                code_content = parts[i + 1] if i + 1 < len(parts) else ""

                if code_content.strip():
                    layout.addWidget(CodeBlockWidget(code_content, language))

                i += 1

            i += 1

    @staticmethod
    def extract_tool_payload(content):
        if not isinstance(content, str) or not content.startswith("[[tool:"):
            return None

        lines = [line.strip() for line in content.splitlines() if line.strip()]
        payload = {
            "tool_name": "tool",
            "title": "",
            "subtitle": "",
            "metrics": [],
            "sections": [],
        }
        current_section = None

        for line in lines:
            if line.startswith("[[tool:") and line.endswith("]]"):
                payload["tool_name"] = line[len("[[tool:"):-2].strip() or "tool"
            elif line.startswith("[[title:") and line.endswith("]]"):
                payload["title"] = line[len("[[title:"):-2].strip()
            elif line.startswith("[[subtitle:") and line.endswith("]]"):
                payload["subtitle"] = line[len("[[subtitle:"):-2].strip()
            elif line.startswith("[[metric:") and line.endswith("]]"):
                metric_data = line[len("[[metric:"):-2]
                label, _, value = metric_data.partition("|")
                if label.strip() and value.strip():
                    payload["metrics"].append((label.strip(), value.strip()))
            elif line.startswith("[[section:") and line.endswith("]]"):
                current_section = [line[len("[[section:"):-2].strip(), []]
                payload["sections"].append(current_section)
            elif line.startswith("- ") and current_section:
                current_section[1].append(line[2:].strip())
            elif current_section and line:
                current_section[1].append(line)

        if not payload["title"]:
            return None

        return payload

    def format_timestamp(self):
        try:
            if isinstance(self.timestamp, str):
                from datetime import datetime

                dt = datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
            else:
                dt = self.timestamp

            from datetime import datetime

            now = datetime.now()
            if dt.date() == now.date():
                return dt.strftime("%H:%M")
            return dt.strftime("%m/%d %H:%M")
        except Exception:
            return "Now"
