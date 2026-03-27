"""
Quick actions and slash commands for enhanced user experience.
Provides keyboard shortcuts, commands, and smart suggestions.
"""

import json
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QSizePolicy,
    QGraphicsDropShadowEffect,
    QPushButton,
    QFileDialog,
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QColor


class SlashCommandMenu(QWidget):
    """Dropdown menu for slash commands."""

    command_selected = pyqtSignal(str, list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.commands = self.get_available_commands()
        self.filtered_commands = self.commands
        self.setup_ui()
        self.hide()

    def setup_ui(self):
        self.setFixedWidth(300)
        self.setMaximumHeight(400)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        header = QLabel("Slash Commands")
        header.setStyleSheet(
            """
            QLabel {
                color: #00C6FF;
                font-size: 14px;
                font-weight: 700;
                font-family: 'Segoe UI';
                padding: 5px;
                background: transparent;
            }
            """
        )
        layout.addWidget(header)

        self.commands_list = QListWidget()
        self.commands_list.setStyleSheet(
            """
            QListWidget {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                outline: none;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
            QListWidget::item:selected {
                background: rgba(0, 198, 255, 0.2);
            }
            QListWidget::item:hover {
                background: rgba(255, 255, 255, 0.08);
            }
            """
        )
        self.commands_list.itemClicked.connect(self.on_command_selected)
        layout.addWidget(self.commands_list)

        self.populate_commands()

        self.setStyleSheet(
            """
            QWidget {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #111827, stop:1 #1f2937);
                border: 1px solid rgba(0, 198, 255, 0.3);
                border-radius: 15px;
            }
            """
        )

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

    def get_available_commands(self):
        return [
            {"command": "/help", "description": "Show available commands", "icon": "?", "args": []},
            {"command": "/clear", "description": "Clear current conversation view", "icon": "X", "args": []},
            {"command": "/export", "description": "Export conversation to file", "icon": ">", "args": ["format"]},
            {"command": "/project", "description": "Summarize the current project", "icon": "P", "args": []},
            {"command": "/find", "description": "Find files matching a pattern", "icon": "F", "args": ["pattern"]},
            {"command": "/analyze", "description": "Analyze a project file", "icon": "A", "args": ["path"]},
            {"command": "/related", "description": "Show related files for a path", "icon": "L", "args": ["path"]},
            {"command": "/recent", "description": "Show recently inspected files", "icon": "R", "args": []},
            {"command": "/browse", "description": "Open a URL in the browser", "icon": "W", "args": ["url"]},
            {"command": "/search", "description": "Search the web", "icon": "G", "args": ["query"]},
            {"command": "/task", "description": "Execute a real-world task", "icon": "T", "args": ["description"]},
            {"command": "/portal", "description": "Find a hospital patient portal", "icon": "H", "args": ["hospital_name"]},
            {"command": "/forms", "description": "Find patient forms from a hospital", "icon": "D", "args": ["hospital_name"]},
            {"command": "/settings", "description": "Open settings panel", "icon": "*", "args": []},
            {"command": "/model", "description": "Switch AI model", "icon": "M", "args": ["model_name"]},
            {"command": "/theme", "description": "Change color theme", "icon": "T", "args": ["theme_name"]},
            {"command": "/shortcuts", "description": "Show keyboard shortcuts", "icon": "K", "args": []},
            {"command": "/feedback", "description": "Send feedback", "icon": "B", "args": []},
            {"command": "/stats", "description": "Show usage statistics", "icon": "S", "args": []},
            {"command": "/reset", "description": "Reset to default settings", "icon": "R", "args": []},
        ]

    def populate_commands(self):
        self.commands_list.clear()
        for cmd in self.filtered_commands:
            item = QListWidgetItem()
            item.setText(f"{cmd['icon']}  {cmd['command']}")
            item.setData(Qt.UserRole, cmd)
            item.setToolTip(cmd["description"])
            self.commands_list.addItem(item)

    def filter_commands(self, text):
        if not text.startswith("/"):
            self.hide()
            return

        self.filtered_commands = [cmd for cmd in self.commands if cmd["command"].startswith(text.lower())]
        if self.filtered_commands:
            self.populate_commands()
            self.show()
        else:
            self.hide()

    def on_command_selected(self, item):
        cmd_data = item.data(Qt.UserRole)
        self.command_selected.emit(cmd_data["command"], cmd_data["args"])
        self.hide()

    def show_at(self, position):
        self.move(position)
        self.show()
        self.raise_()


class SmartSuggestions(QWidget):
    """Smart suggestions based on context."""

    suggestion_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.suggestions = []
        self.setup_ui()
        self.hide()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(8)

        self.chip_container = QWidget()
        self.chip_layout = QHBoxLayout(self.chip_container)
        self.chip_layout.setContentsMargins(0, 0, 0, 0)
        self.chip_layout.setSpacing(8)

        layout.addWidget(self.chip_container)
        layout.addStretch()

    def update_suggestions(self, context):
        while self.chip_layout.count():
            child = self.chip_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.suggestions = self.generate_suggestions(context)
        for suggestion in self.suggestions:
            self.chip_layout.addWidget(self.create_chip(suggestion))

        if self.suggestions:
            self.show()
        else:
            self.hide()

    def generate_suggestions(self, context):
        suggestions = []
        lowered = context.lower()

        if "code" in lowered:
            suggestions.extend(["Explain this code", "Find bugs", "Add comments", "Refactor"])
        if "error" in lowered:
            suggestions.extend(["Debug this error", "Show docs", "Suggest fix"])
        if "write" in lowered or "create" in lowered:
            suggestions.extend(["Generate template", "Make it better", "Add style"])
        if not suggestions:
            suggestions = ["Explain more", "Summarize", "Try a different approach", "Show examples"]

        return suggestions[:4]

    def create_chip(self, text):
        chip = QPushButton(text)
        chip.setStyleSheet(
            """
            QPushButton {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 15px;
                padding: 8px 15px;
                color: rgba(255, 255, 255, 0.9);
                font-size: 13px;
                font-weight: 500;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background: rgba(0, 198, 255, 0.2);
                border: 1px solid #00C6FF;
                color: #00C6FF;
            }
            """
        )
        chip.clicked.connect(lambda: self.suggestion_selected.emit(text))
        return chip


class KeyboardShortcuts:
    """Keyboard shortcuts manager."""

    SHORTCUTS = {
        "Ctrl+N": "New chat",
        "Ctrl+Enter": "Send message",
        "Ctrl+L": "Clear conversation",
        "Ctrl+E": "Export conversation",
        "Ctrl+,": "Open settings",
        "Ctrl+/": "Show slash commands",
        "Escape": "Close menu/dialog",
        "Ctrl+1-9": "Switch to chat 1-9",
        "Ctrl+Shift+C": "Copy last response",
        "Ctrl+Shift+S": "Stop generation",
    }

    @classmethod
    def get_shortcuts(cls):
        return cls.SHORTCUTS

    @classmethod
    def format_shortcuts(cls):
        return "<br>".join(f"<b>{key}</b>: {action}" for key, action in cls.SHORTCUTS.items())


class MessageTemplates:
    """Pre-built message templates."""

    TEMPLATES = {
        "code_review": {"name": "Code Review", "icon": "R", "template": "Please review this code and suggest improvements:\n\n```\n{code}\n```"},
        "explain": {"name": "Explain Code", "icon": "E", "template": "Please explain what this code does:\n\n```\n{code}\n```"},
        "debug": {"name": "Debug Error", "icon": "D", "template": "I'm getting this error:\n\n{error}\n\nPlease help me debug it."},
        "optimize": {"name": "Optimize", "icon": "O", "template": "Please optimize this code for better performance:\n\n```\n{code}\n```"},
        "convert": {"name": "Convert", "icon": "C", "template": "Please convert this code to {language}:\n\n```\n{code}\n```"},
        "test": {"name": "Write Tests", "icon": "T", "template": "Please write unit tests for this code:\n\n```\n{code}\n```"},
    }

    @classmethod
    def get_templates(cls):
        return cls.TEMPLATES

    @classmethod
    def format_template(cls, template_key, **kwargs):
        template = cls.TEMPLATES.get(template_key)
        if template:
            return template["template"].format(**kwargs)
        return None


class QuickReply(QWidget):
    """Quick reply suggestions for common responses."""

    reply_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.replies = []
        self.setup_ui()
        self.hide()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(8)

        self.reply_container = QWidget()
        self.reply_layout = QHBoxLayout(self.reply_container)
        self.reply_layout.setContentsMargins(0, 0, 0, 0)
        self.reply_layout.setSpacing(8)

        layout.addWidget(self.reply_container)
        layout.addStretch()

    def update_replies(self, context):
        while self.reply_layout.count():
            child = self.reply_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.replies = self.generate_replies(context)
        for reply in self.replies:
            self.reply_layout.addWidget(self.create_reply_button(reply))

        if self.replies:
            self.show()
        else:
            self.hide()

    def generate_replies(self, context):
        replies = []
        lowered = context.lower()

        if "?" in context:
            replies.extend(["Yes", "No", "Maybe", "Tell me more"])
        if any(word in lowered for word in ["done", "completed", "finished"]):
            replies.extend(["Great", "Thanks", "Perfect", "Next step"])
        if any(word in lowered for word in ["error", "failed", "issue"]):
            replies.extend(["Try again", "Different approach", "Show docs", "Help"])
        if not replies:
            replies = ["Looks good", "Tell me more", "Keep going", "Show examples"]

        return replies[:4]

    def create_reply_button(self, text):
        btn = QPushButton(text)
        btn.setStyleSheet(
            """
            QPushButton {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 18px;
                padding: 10px 20px;
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
                font-weight: 500;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background: rgba(0, 198, 255, 0.2);
                border: 1px solid #00C6FF;
                color: #00C6FF;
            }
            """
        )
        btn.clicked.connect(lambda: self.reply_selected.emit(text))
        return btn


class WorkspaceContextBar(QWidget):
    """Project-aware chips for focused, related, and recent files."""

    chip_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.hide()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(6)

        self.title_label = QLabel("Project radar")
        self.title_label.setStyleSheet(
            """
            QLabel {
                color: rgba(102, 217, 255, 0.9);
                font-size: 12px;
                font-weight: 700;
                font-family: 'Segoe UI';
                letter-spacing: 0.5px;
                padding-left: 2px;
            }
            """
        )
        layout.addWidget(self.title_label)

        self.row_container = QWidget()
        self.row_layout = QHBoxLayout(self.row_container)
        self.row_layout.setContentsMargins(0, 0, 0, 0)
        self.row_layout.setSpacing(8)
        layout.addWidget(self.row_container)

        self.setStyleSheet(
            """
            QWidget {
                background: transparent;
            }
            """
        )

    def update_context(self, focus_file="", related_files=None, recent_files=None):
        while self.row_layout.count():
            child = self.row_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        chip_count = 0

        if focus_file:
            self.row_layout.addWidget(self.create_chip(f"Focus: {self._shorten_path(focus_file, 30)}", f"/related {focus_file}", accent=True))
            chip_count += 1

        for related_file in (related_files or [])[:3]:
            self.row_layout.addWidget(self.create_chip(f"Related: {self._shorten_path(related_file, 24)}", f"/analyze {related_file}"))
            chip_count += 1

        for recent_file in (recent_files or [])[:3]:
            self.row_layout.addWidget(self.create_chip(f"Recent: {self._shorten_path(recent_file, 24)}", f"/analyze {recent_file}"))
            chip_count += 1

        self.row_layout.addStretch()

        if chip_count:
            self.show()
        else:
            self.hide()

    def create_chip(self, text, command, accent=False):
        chip = QPushButton(text)
        border_color = "#00C6FF" if accent else "rgba(255, 255, 255, 0.15)"
        bg_color = "rgba(0, 198, 255, 0.18)" if accent else "rgba(255, 255, 255, 0.08)"
        chip.setStyleSheet(
            f"""
            QPushButton {{
                background: {bg_color};
                border: 1px solid {border_color};
                border-radius: 16px;
                padding: 8px 14px;
                color: rgba(255, 255, 255, 0.94);
                font-size: 12px;
                font-weight: 600;
                font-family: 'Segoe UI';
                text-align: left;
            }}
            QPushButton:hover {{
                background: rgba(0, 198, 255, 0.22);
                border: 1px solid #00C6FF;
                color: #dff8ff;
            }}
            """
        )
        chip.clicked.connect(lambda: self.chip_selected.emit(command))
        return chip

    @staticmethod
    def _shorten_path(path, max_length):
        if len(path) <= max_length:
            return path
        return "..." + path[-(max_length - 3):]


class AsyncLoadingWidget(QWidget):
    """Lightweight loading receipt shown in chat while async commands run."""

    def __init__(self, command="/command", parent=None):
        super().__init__(parent)
        self.command = command
        self.dot_count = 0
        self._destroyed = False
        self.setup_ui()
        self.setup_animation()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 5, 15, 5)
        main_layout.setSpacing(0)

        bubble_container = QWidget()
        bubble_layout = QHBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(15, 12, 15, 12)
        bubble_layout.setSpacing(10)

        # Animated dots label
        self.label = QLabel(self._build_text())
        self.label.setWordWrap(False)
        self.label.setStyleSheet(
            """
            QLabel {
                color: rgba(0, 198, 255, 0.9);
                font-style: italic;
                font-size: 13px;
                font-weight: 600;
                background: transparent;
                font-family: 'Segoe UI';
            }
            """
        )
        bubble_layout.addWidget(self.label)

        bubble_container.setMaximumWidth(400)
        bubble_container.setStyleSheet(
            """
            QWidget {
                background: rgba(0, 198, 255, 0.08);
                border: 1px solid rgba(0, 198, 255, 0.2);
                border-radius: 18px;
                margin: 3px 0px;
            }
            """
        )

        main_layout.addWidget(bubble_container)
        main_layout.addStretch()

    def setup_animation(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(400)

    def _build_text(self):
        dots = "." * (self.dot_count % 4)
        labels = {
            "/project": "Scanning project",
            "/find": "Searching files",
            "/analyze": "Analyzing",
            "/related": "Finding related",
            "/recent": "Checking recent",
        }
        label = labels.get(self.command, "Working")
        return f"  {label}{dots}"

    def _tick(self):
        if self._destroyed:
            return
        try:
            self.dot_count += 1
            self.label.setText(self._build_text())
        except RuntimeError:
            self.stop()

    def update_progress(self, text):
        """Update the loading text with a progress message."""
        if self._destroyed:
            return
        try:
            dots = "." * (self.dot_count % 4)
            self.label.setText(f"  {text}{dots}")
        except RuntimeError:
            self.stop()

    def stop(self):
        self._destroyed = True
        if self._timer and self._timer.isActive():
            self._timer.stop()

    def deleteLater(self):
        self.stop()
        super().deleteLater()


class CapabilityCommandWorker(QThread):
    """Run heavier capability commands off the UI thread."""

    command_completed = pyqtSignal(dict)
    command_failed = pyqtSignal(str, str)
    command_progress = pyqtSignal(str)

    def __init__(self, capabilities, command, args=None):
        super().__init__()
        self.capabilities = capabilities
        self.command = command
        self.args = args or []

    def run(self):
        try:
            self.command_progress.emit("Starting...")
            if self.command == "/project":
                result = self.build_project_summary()
            elif self.command == "/find":
                result = self.build_find_files()
            elif self.command == "/analyze":
                result = self.build_analyze_file()
            elif self.command == "/related":
                result = self.build_related_files()
            elif self.command == "/recent":
                result = self.build_recent_files()
            elif self.command == "/browse":
                result = self.build_browse_web()
            elif self.command == "/search":
                result = self.build_search_web()
            elif self.command == "/task":
                result = self.build_execute_task()
            elif self.command == "/portal":
                result = self.build_find_portal()
            elif self.command == "/forms":
                result = self.build_find_forms()
            else:
                raise ValueError(f"Unsupported async command: {self.command}")

            self.command_completed.emit(result)
        except Exception as exc:
            self.command_failed.emit(self.command, str(exc))

    def build_project_summary(self):
        self.command_progress.emit("Scanning workspace...")
        summary = self.capabilities.scan_project()
        if "error" in summary:
            return {"message_text": f"Project scan failed: {summary['error']}"}

        sorted_languages = sorted(summary["languages"].items(), key=lambda item: (-item[1], item[0]))
        top_languages = ", ".join(f"{lang}: {count}" for lang, count in sorted_languages[:4]) or "Unknown"
        return {
            "tool_name": "project",
            "title": "Project Summary",
            "subtitle": "Quick snapshot of the current workspace.",
            "metrics": [
                ("Files", str(len(summary["files"]))),
                ("Directories", str(len(summary["directories"]))),
                ("Total lines", str(summary["total_lines"])),
                ("Top languages", top_languages),
            ],
            "sections": [
                (
                    "Highlights",
                    [
                        f"Root: {summary['root']}",
                        f"Language mix tracked: {len(summary['languages']) or 0}",
                        f"First files: {', '.join(summary['files'][:3]) or 'No files scanned'}",
                    ],
                )
            ],
        }

    def build_find_files(self):
        pattern = self.args[0] if self.args else "*.py"
        self.command_progress.emit(f"Searching for {pattern}...")
        matches = self.capabilities.find_files(pattern)
        if not matches:
            return {"message_text": f"No files matched `{pattern}`."}

        preview_matches = matches[:8]
        sections = [("Matches", preview_matches)]
        if len(matches) > len(preview_matches):
            sections.append(("More", [f"{len(matches) - len(preview_matches)} additional files not shown."]))

        return {
            "tool_name": "find",
            "title": f"Matches for {pattern}",
            "subtitle": "Project file search results.",
            "metrics": [
                ("Pattern", pattern),
                ("Results", str(len(matches))),
            ],
            "sections": sections,
        }

    def build_analyze_file(self):
        if not self.args:
            return {"message_text": "Use `/analyze path/to/file.py`."}

        file_path = self.args[0]
        self.command_progress.emit(f"Reading {file_path}...")
        self.capabilities.get_file_context(file_path)
        self.command_progress.emit(f"Analyzing structure...")
        analysis = self.capabilities.analyze_file(file_path)
        if analysis.get("language") == "unknown" and analysis.get("lines") == 0 and analysis.get("issues"):
            return {"message_text": f"Analysis failed for `{file_path}`: {analysis['issues'][0]}"}

        sections = []
        if analysis["functions"]:
            sections.append(("Functions", analysis["functions"][:6]))
        if analysis["classes"]:
            sections.append(("Classes", analysis["classes"][:6]))
        if analysis["issues"]:
            sections.append(("Issues", analysis["issues"][:4]))

        return {
            "tool_name": "analyze",
            "title": f"Analysis for {file_path}",
            "subtitle": "File structure and quick complexity readout.",
            "metrics": [
                ("Language", str(analysis["language"])),
                ("Lines", str(analysis["lines"])),
                ("Complexity", str(analysis["complexity"])),
                ("Imports", str(len(analysis["imports"]))),
            ],
            "sections": sections or [("Summary", ["No functions, classes, or issues were detected."])],
            "focus_file": file_path,
        }

    def build_related_files(self):
        if not self.args:
            return {"message_text": "Use `/related path/to/file.py`."}

        file_path = self.args[0]
        self.command_progress.emit(f"Scanning context for {file_path}...")
        context = self.capabilities.get_file_context(file_path)
        if "error" in context:
            return {"message_text": context["error"]}

        self.command_progress.emit("Finding related files...")
        related = self.capabilities.get_related_files(file_path)
        recent_files = self.capabilities.get_recent_files()
        return {
            "tool_name": "related",
            "title": f"Related files for {file_path}",
            "subtitle": "Fast project context around the file in focus.",
            "metrics": [
                ("Language", str(context.get("language", "unknown"))),
                ("Related", str(len(related))),
                ("Recent", str(len(recent_files))),
            ],
            "sections": [
                ("Related files", related[:6] or ["No related files found."]),
                ("Recent files", recent_files[:4] or ["No recent files yet."]),
            ],
            "focus_file": file_path,
        }

    def build_recent_files(self):
        self.command_progress.emit("Gathering recent files...")
        recent_files = self.capabilities.get_recent_files()
        if not recent_files:
            return {"message_text": "No recent project files yet. Analyze a file first."}

        return {
            "tool_name": "recent",
            "title": "Recent project files",
            "subtitle": "The files Kai has touched most recently.",
            "metrics": [("Tracked", str(len(recent_files)))],
            "sections": [("Recent files", recent_files[:8])],
            "focus_file": recent_files[0],
        }

    def build_browse_web(self):
        url = self.args[0] if self.args else ""
        if not url:
            return {"message_text": "Use `/browse https://example.com`"}
        self.command_progress.emit(f"Opening {url}...")
        result = self.capabilities.web_navigate(url)
        if not result["success"]:
            return {"message_text": f"Browse failed: {result.get('error', 'Unknown error')}"}

        # Get page text for context
        self.command_progress.emit("Reading page...")
        page_text = self.capabilities.web_get_text()
        preview = page_text.get("text", "")[:500]

        return {
            "tool_name": "browse",
            "title": f"Browsing: {result.get('title', url)}",
            "subtitle": result.get("url", url),
            "metrics": [
                ("URL", result.get("url", url)),
                ("Title", result.get("title", "Unknown")),
            ],
            "sections": [("Page Preview", [preview] if preview else ["No text content"])],
        }

    def build_search_web(self):
        query = " ".join(self.args) if self.args else ""
        if not query:
            return {"message_text": "Use `/search your query here`"}
        self.command_progress.emit(f"Searching: {query}...")
        result = self.capabilities.web_search(query)
        if not result["success"]:
            return {"message_text": f"Search failed: {result.get('error', 'Unknown error')}"}

        results = result.get("results", [])
        result_lines = []
        for r in results[:5]:
            title = r.get("title", "No title")
            url = r.get("url", "")
            result_lines.append(f"{title}\n{url}")

        return {
            "tool_name": "search",
            "title": f"Web Search: {query}",
            "subtitle": f"{len(results)} results found",
            "metrics": [("Query", query), ("Results", str(len(results)))],
            "sections": [("Top Results", result_lines or ["No results found"])],
        }

    def build_execute_task(self):
        task_desc = " ".join(self.args) if self.args else ""
        if not task_desc:
            return {"message_text": "Use `/task describe what you need done`"}
        self.command_progress.emit(f"Working on: {task_desc[:50]}...")
        result = self.capabilities.execute_task(task_desc)

        steps = result.get("steps", [])
        step_lines = [f"{'✅' if s.get('data', {}).get('success', True) else '❌'} {s.get('action', '')}: {s.get('description', '')}" for s in steps]
        files = result.get("files", [])

        sections = [("Steps", step_lines or ["No steps completed"])]
        if files:
            sections.append(("Downloaded Files", files))

        return {
            "tool_name": "task",
            "title": f"Task: {task_desc[:60]}",
            "subtitle": "Completed" if result.get("success") else "Needs attention",
            "metrics": [
                ("Status", "Done" if result.get("success") else "Partial"),
                ("Steps", str(len(steps))),
                ("Files", str(len(files))),
            ],
            "sections": sections,
        }

    def build_find_portal(self):
        hospital = " ".join(self.args) if self.args else ""
        if not hospital:
            return {"message_text": "Use `/portal Hospital Name`"}
        self.command_progress.emit(f"Finding portal for {hospital}...")
        result = self.capabilities.find_hospital_portal(hospital)

        portal_links = result.get("portal_links", [])
        link_lines = [f"{r.get('title', 'Link')}: {r.get('url', '')}" for r in portal_links[:5]]

        return {
            "tool_name": "portal",
            "title": f"Patient Portal: {hospital}",
            "subtitle": result.get("message", ""),
            "metrics": [("Hospital", hospital), ("Portal Links", str(len(portal_links)))],
            "sections": [("Portal Links", link_lines or ["No portal found - try `/search {hospital} patient portal`"])],
        }

    def build_find_forms(self):
        hospital = " ".join(self.args) if self.args else ""
        if not hospital:
            return {"message_text": "Use `/forms Hospital Name`"}
        self.command_progress.emit(f"Searching for {hospital} forms...")
        result = self.capabilities.find_patient_forms(hospital)

        form_links = result.get("form_links", [])
        link_lines = [f"{r.get('title', 'Form')}: {r.get('url', '')}" for r in form_links[:5]]

        return {
            "tool_name": "forms",
            "title": f"Patient Forms: {hospital}",
            "subtitle": result.get("message", ""),
            "metrics": [("Hospital", hospital), ("Form Links", str(len(form_links)))],
            "sections": [("Available Forms", link_lines or ["No forms found - try `/search {hospital} patient forms download`"])],
        }


class CommandProcessor:
    """Process slash commands and execute actions."""

    def __init__(self, main_window):
        self.main_window = main_window
        self.capability_workers = []
        self.async_commands = {"/project", "/find", "/analyze", "/related", "/recent", "/browse", "/search", "/task", "/portal", "/forms"}
        self._command_cache = {}  # Cache for command results
        self._cache_max_size = 50
        self._active_loading_widget = None  # Currently shown loading receipt
        self._active_command = None  # Track which command is loading
        self._active_args = None
        self.commands = {
            "/help": self.show_help,
            "/clear": self.clear_conversation,
            "/export": self.export_conversation,
            "/project": self.project_summary,
            "/find": self.find_files,
            "/analyze": self.analyze_file,
            "/related": self.related_files,
            "/recent": self.recent_files,
            "/browse": self.browse_web,
            "/search": self.search_web,
            "/task": self.execute_real_task,
            "/portal": self.find_portal,
            "/forms": self.find_forms,
            "/settings": self.open_settings,
            "/model": self.switch_model,
            "/theme": self.change_theme,
            "/shortcuts": self.show_shortcuts,
            "/feedback": self.send_feedback,
            "/stats": self.show_stats,
            "/reset": self.reset_settings,
        }

    def process(self, command, args=None):
        if command in self.async_commands:
            return self.run_capability_command_async(command, args)
        if command in self.commands:
            return self.commands[command](args)
        return False

    def get_capabilities(self):
        if hasattr(self.main_window, "ensure_capabilities"):
            return self.main_window.ensure_capabilities()
        return getattr(self.main_window, "capabilities", None)

    def _get_command_cache_key(self, command, args):
        """Generate a cache key for command results."""
        import hashlib
        args_str = ','.join(str(arg) for arg in (args or []))
        content = f"{command}:{args_str}"
        return hashlib.md5(content.encode()).hexdigest()

    def _manage_cache_size(self):
        """Keep cache size under limit."""
        if len(self._command_cache) > self._cache_max_size:
            # Remove oldest 20% of entries
            remove_count = len(self._command_cache) - int(self._cache_max_size * 0.8)
            keys_to_remove = list(self._command_cache.keys())[:remove_count]
            for key in keys_to_remove:
                del self._command_cache[key]

    def run_capability_command_async(self, command, args=None):
        capabilities = self.get_capabilities()
        if not capabilities:
            self._post_to_chat("Capabilities are not available in this session yet.")
            return False

        # Check cache first
        cache_key = self._get_command_cache_key(command, args)
        if cache_key in self._command_cache:
            self.handle_capability_result(self._command_cache[cache_key])
            return True

        # Remove any existing loading widget
        self._remove_loading_widget()

        # Show loading receipt in chat
        self._active_command = command
        self._active_args = args
        self._show_loading_widget(command)

        worker = CapabilityCommandWorker(capabilities, command, args)
        worker.command_completed.connect(self.handle_capability_result)
        worker.command_failed.connect(self.handle_capability_error)
        worker.command_progress.connect(self._on_command_progress)
        worker.finished.connect(lambda: self.cleanup_capability_worker(worker))
        self.capability_workers.append(worker)

        if hasattr(self.main_window, "status_bar_widget"):
            self.main_window.status_bar_widget.connection_label.setText(f"Working {command}")

        worker.start()
        return True

    def handle_capability_result(self, result):
        # Remove loading receipt
        self._remove_loading_widget()

        if hasattr(self.main_window, "status_bar_widget"):
            self.main_window.status_bar_widget.update_connection(True)

        # Cache the result using the command that produced it
        if self._active_command:
            cache_key = self._get_command_cache_key(self._active_command, self._active_args)
            self._command_cache[cache_key] = result
            self._manage_cache_size()
        self._active_command = None
        self._active_args = None

        if result.get("message_text"):
            self._post_to_chat(result["message_text"])
        else:
            self._post_tool_card(
                result["tool_name"],
                result["title"],
                result.get("subtitle", ""),
                result.get("metrics"),
                result.get("sections"),
            )

        focus_file = result.get("focus_file")
        if focus_file:
            self.main_window.update_workspace_context(focus_file)

    def handle_capability_error(self, command, error_text):
        # Remove loading receipt
        self._remove_loading_widget()
        self._active_command = None
        self._active_args = None

        if hasattr(self.main_window, "status_bar_widget"):
            self.main_window.status_bar_widget.update_connection(False)
        self._post_to_chat(f"{command} failed: {error_text}")

    def cleanup_capability_worker(self, worker):
        try:
            self.capability_workers.remove(worker)
        except ValueError:
            pass

        worker.deleteLater()

        # If no more workers, clear loading state
        if not self.capability_workers:
            self._remove_loading_widget()
            if hasattr(self.main_window, "status_bar_widget"):
                self.main_window.status_bar_widget.update_connection(True)

    def show_help(self, args=None):
        self._post_tool_card(
            "help",
            "Black Worm Command Guide",
            "Everything useful stays in this one chat surface.",
            metrics=[
                ("Commands", str(len(self.commands))),
                ("Mode", "Single window"),
            ],
            sections=[
                (
                    "Project commands",
                    [
                        "/help, /clear, /export",
                        "/project, /find <pattern>, /analyze <path>",
                        "/related <path>, /recent",
                    ],
                ),
                (
                    "Web & real-world tasks",
                    [
                        "/browse <url> - Open a website",
                        "/search <query> - Search the web",
                        "/task <description> - Execute a real-world task",
                        "/portal <hospital> - Find patient portal",
                        "/forms <hospital> - Find patient forms",
                    ],
                ),
                (
                    "Settings",
                    [
                        "/settings, /model <name>, /theme <name>",
                        "/shortcuts, /feedback, /stats, /reset",
                    ],
                ),
            ],
        )
        return True

    def clear_conversation(self, args=None):
        self.main_window.clear_messages()
        self.main_window.add_message_widget(
            "ai",
            "Cleared the current view. Your saved messages are still available from History.",
            datetime.now(),
        )
        return True

    def export_conversation(self, args=None):
        conversation_id = getattr(self.main_window, "current_conversation_id", None)
        if not conversation_id:
            self._post_to_chat("There is no active conversation to export.")
            return False

        messages = self.main_window.db_manager.get_conversation_messages(conversation_id)
        if not messages:
            self._post_to_chat("The current conversation has no messages yet.")
            return False

        payload = [
            {"sender": msg["sender"], "content": msg["content"], "timestamp": msg["timestamp"]}
            for msg in messages
        ]

        target_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Export Conversation",
            f"conversation-{conversation_id}.json",
            "JSON Files (*.json);;Markdown Files (*.md);;Text Files (*.txt)",
        )
        if not target_path:
            return False

        if target_path.endswith(".md"):
            output = "\n\n".join(
                f"## {msg['sender'].title()} - {msg['timestamp']}\n\n{msg['content']}" for msg in payload
            )
        elif target_path.endswith(".txt"):
            output = "\n\n".join(
                f"[{msg['timestamp']}] {msg['sender'].upper()}: {msg['content']}" for msg in payload
            )
        else:
            output = json.dumps(payload, indent=2, ensure_ascii=False)

        with open(target_path, "w", encoding="utf-8") as handle:
            handle.write(output)

        self._post_tool_card(
            "export",
            "Conversation Exported",
            "Your current thread was written to disk.",
            metrics=[
                ("Path", target_path),
                ("Messages", str(len(payload))),
            ],
        )
        return True

    def project_summary(self, args=None):
        capabilities = self.get_capabilities()
        if not capabilities:
            self._post_to_chat("Capabilities are not available in this session yet.")
            return False

        summary = capabilities.scan_project()
        if "error" in summary:
            self._post_to_chat(f"Project scan failed: {summary['error']}")
            return False

        sorted_languages = sorted(summary["languages"].items(), key=lambda item: (-item[1], item[0]))
        top_languages = ", ".join(f"{lang}: {count}" for lang, count in sorted_languages[:4]) or "Unknown"
        self._post_tool_card(
            "project",
            "Project Summary",
            "Quick snapshot of the current workspace.",
            metrics=[
                ("Files", str(len(summary["files"]))),
                ("Directories", str(len(summary["directories"]))),
                ("Total lines", str(summary["total_lines"])),
                ("Top languages", top_languages),
            ],
            sections=[
                (
                    "Highlights",
                    [
                        f"Root: {summary['root']}",
                        f"Language mix tracked: {len(summary['languages']) or 0}",
                        f"First files: {', '.join(summary['files'][:3]) or 'No files scanned'}",
                    ],
                )
            ],
        )
        return True

    def find_files(self, args=None):
        capabilities = self.get_capabilities()
        pattern = args[0] if args else "*.py"
        if not capabilities:
            self._post_to_chat("Capabilities are not available in this session yet.")
            return False

        matches = capabilities.find_files(pattern)
        if not matches:
            self._post_to_chat(f"No files matched `{pattern}`.")
            return True

        preview_matches = matches[:8]
        sections = [("Matches", preview_matches)]
        if len(matches) > len(preview_matches):
            sections.append(("More", [f"{len(matches) - len(preview_matches)} additional files not shown."]))

        self._post_tool_card(
            "find",
            f"Matches for {pattern}",
            "Project file search results.",
            metrics=[
                ("Pattern", pattern),
                ("Results", str(len(matches))),
            ],
            sections=sections,
        )
        return True

    def analyze_file(self, args=None):
        capabilities = self.get_capabilities()
        if not capabilities:
            self._post_to_chat("Capabilities are not available in this session yet.")
            return False
        if not args:
            self._post_to_chat("Use `/analyze path/to/file.py`.")
            return False

        file_path = args[0]
        capabilities.get_file_context(file_path)
        analysis = capabilities.analyze_file(file_path)
        if analysis.get("language") == "unknown" and analysis.get("lines") == 0 and analysis.get("issues"):
            self._post_to_chat(f"Analysis failed for `{file_path}`: {analysis['issues'][0]}")
            return False

        sections = []
        if analysis["functions"]:
            sections.append(("Functions", analysis["functions"][:6]))
        if analysis["classes"]:
            sections.append(("Classes", analysis["classes"][:6]))
        if analysis["issues"]:
            sections.append(("Issues", analysis["issues"][:4]))

        self._post_tool_card(
            "analyze",
            f"Analysis for {file_path}",
            "File structure and quick complexity readout.",
            metrics=[
                ("Language", str(analysis["language"])),
                ("Lines", str(analysis["lines"])),
                ("Complexity", str(analysis["complexity"])),
                ("Imports", str(len(analysis["imports"]))),
            ],
            sections=sections or [("Summary", ["No functions, classes, or issues were detected."])],
        )
        self.main_window.update_workspace_context(file_path)
        return True

    def related_files(self, args=None):
        capabilities = self.get_capabilities()
        if not capabilities:
            self._post_to_chat("Capabilities are not available in this session yet.")
            return False
        if not args:
            self._post_to_chat("Use `/related path/to/file.py`.")
            return False

        file_path = args[0]
        context = capabilities.get_file_context(file_path)
        if "error" in context:
            self._post_to_chat(context["error"])
            return False

        related = capabilities.get_related_files(file_path)
        recent_files = capabilities.get_recent_files()
        self._post_tool_card(
            "related",
            f"Related files for {file_path}",
            "Fast project context around the file in focus.",
            metrics=[
                ("Language", str(context.get("language", "unknown"))),
                ("Related", str(len(related))),
                ("Recent", str(len(recent_files))),
            ],
            sections=[
                ("Related files", related[:6] or ["No related files found."]),
                ("Recent files", recent_files[:4] or ["No recent files yet."]),
            ],
        )
        self.main_window.update_workspace_context(file_path)
        return True

    def recent_files(self, args=None):
        capabilities = self.get_capabilities()
        if not capabilities:
            self._post_to_chat("Capabilities are not available in this session yet.")
            return False

        recent_files = capabilities.get_recent_files()
        if not recent_files:
            self._post_to_chat("No recent project files yet. Analyze a file first.")
            return False

        self._post_tool_card(
            "recent",
            "Recent project files",
            "The files Kai has touched most recently.",
            metrics=[("Tracked", str(len(recent_files)))],
            sections=[("Recent files", recent_files[:8])],
        )
        self.main_window.update_workspace_context(recent_files[0])
        return True

    def browse_web(self, args=None):
        capabilities = self.get_capabilities()
        if not capabilities:
            self._post_to_chat("Capabilities are not available in this session yet.")
            return False
        if not args:
            self._post_to_chat("Use `/browse https://example.com`")
            return False

        result = capabilities.web_navigate(args[0])
        if not result["success"]:
            self._post_to_chat(f"Browse failed: {result.get('error', 'Unknown error')}")
            return True

        page_text = capabilities.web_get_text()
        preview = page_text.get("text", "")[:500]
        self._post_tool_card(
            "browse",
            f"Browsing: {result.get('title', args[0])}",
            result.get("url", args[0]),
            metrics=[("URL", result.get("url", args[0])), ("Title", result.get("title", "Unknown"))],
            sections=[("Page Preview", [preview] if preview else ["No text content"])],
        )
        return True

    def search_web(self, args=None):
        capabilities = self.get_capabilities()
        if not capabilities:
            self._post_to_chat("Capabilities are not available in this session yet.")
            return False

        query = " ".join(args) if args else ""
        if not query:
            self._post_to_chat("Use `/search your query here`")
            return False

        result = capabilities.web_search(query)
        if not result["success"]:
            self._post_to_chat(f"Search failed: {result.get('error', 'Unknown error')}")
            return True

        results = result.get("results", [])
        result_lines = []
        for r in results[:5]:
            title = r.get("title", "No title")
            url = r.get("url", "")
            result_lines.append(f"{title}\n{url}")

        self._post_tool_card(
            "search",
            f"Web Search: {query}",
            f"{len(results)} results found",
            metrics=[("Query", query), ("Results", str(len(results)))],
            sections=[("Top Results", result_lines or ["No results found"])],
        )
        return True

    def execute_real_task(self, args=None):
        capabilities = self.get_capabilities()
        if not capabilities:
            self._post_to_chat("Capabilities are not available in this session yet.")
            return False

        task_desc = " ".join(args) if args else ""
        if not task_desc:
            self._post_to_chat("Use `/task describe what you need done`")
            return False

        result = capabilities.execute_task(task_desc)
        steps = result.get("steps", [])
        step_lines = [f"{'✅' if s.get('data', {}).get('success', True) else '❌'} {s.get('action', '')}: {s.get('description', '')}" for s in steps]
        files = result.get("files", [])

        sections = [("Steps", step_lines or ["No steps completed"])]
        if files:
            sections.append(("Downloaded Files", files))

        self._post_tool_card(
            "task",
            f"Task: {task_desc[:60]}",
            "Completed" if result.get("success") else "Needs attention",
            metrics=[("Status", "Done" if result.get("success") else "Partial"), ("Steps", str(len(steps))), ("Files", str(len(files)))],
            sections=sections,
        )
        return True

    def find_portal(self, args=None):
        capabilities = self.get_capabilities()
        if not capabilities:
            self._post_to_chat("Capabilities are not available in this session yet.")
            return False

        hospital = " ".join(args) if args else ""
        if not hospital:
            self._post_to_chat("Use `/portal Hospital Name`")
            return False

        result = capabilities.find_hospital_portal(hospital)
        portal_links = result.get("portal_links", [])
        link_lines = [f"{r.get('title', 'Link')}: {r.get('url', '')}" for r in portal_links[:5]]

        self._post_tool_card(
            "portal",
            f"Patient Portal: {hospital}",
            result.get("message", ""),
            metrics=[("Hospital", hospital), ("Portal Links", str(len(portal_links)))],
            sections=[("Portal Links", link_lines or ["No portal found - try `/search {hospital} patient portal`"])],
        )
        return True

    def find_forms(self, args=None):
        capabilities = self.get_capabilities()
        if not capabilities:
            self._post_to_chat("Capabilities are not available in this session yet.")
            return False

        hospital = " ".join(args) if args else ""
        if not hospital:
            self._post_to_chat("Use `/forms Hospital Name`")
            return False

        result = capabilities.find_patient_forms(hospital)
        form_links = result.get("form_links", [])
        link_lines = [f"{r.get('title', 'Form')}: {r.get('url', '')}" for r in form_links[:5]]

        self._post_tool_card(
            "forms",
            f"Patient Forms: {hospital}",
            result.get("message", ""),
            metrics=[("Hospital", hospital), ("Form Links", str(len(form_links)))],
            sections=[("Available Forms", link_lines or ["No forms found - try `/search {hospital} patient forms download`"])],
        )
        return True

    def open_settings(self, args=None):
        self.main_window.show_profile_menu()
        return True

    def switch_model(self, args=None):
        selected_model = args[0] if args else "default"
        self._post_tool_card(
            "model",
            "Model Switch Hook Ready",
            "The model control still needs a full picker UI.",
            metrics=[("Requested", selected_model)],
        )
        return True

    def change_theme(self, args=None):
        requested_theme = args[0] if args else "default"
        self._post_tool_card(
            "theme",
            "Theme Hook Ready",
            "Theme switching is queued behind the main layout polish pass.",
            metrics=[("Requested", requested_theme)],
        )
        return True

    def show_shortcuts(self, args=None):
        self._post_tool_card(
            "shortcuts",
            "Keyboard Shortcuts",
            "The fastest way through Kai should always be typing.",
            sections=[("Available shortcuts", [f"{key}: {action}" for key, action in KeyboardShortcuts.get_shortcuts().items()])],
        )
        return True

    def send_feedback(self, args=None):
        self._post_tool_card(
            "feedback",
            "Feedback Hook Ready",
            "Feedback capture is still waiting on a storage target.",
        )
        return True

    def show_stats(self, args=None):
        conversation_id = getattr(self.main_window, "current_conversation_id", None)
        if not conversation_id:
            self._post_to_chat("No active conversation yet.")
            return False

        messages = self.main_window.db_manager.get_conversation_messages(conversation_id)
        user_count = len([msg for msg in messages if msg["sender"] == "user"])
        ai_count = len([msg for msg in messages if msg["sender"] == "ai"])
        self._post_tool_card(
            "stats",
            "Conversation Stats",
            "Live usage numbers for the current thread.",
            metrics=[
                ("Conversation", str(conversation_id)),
                ("User messages", str(user_count)),
                ("AI messages", str(ai_count)),
                ("Total", str(len(messages))),
            ],
        )
        return True

    def reset_settings(self, args=None):
        self._post_tool_card(
            "reset",
            "Reset Reserved",
            "A safe settings reset flow is still queued for a later pass.",
        )
        return True

    def _show_loading_widget(self, command):
        """Insert a loading receipt into the chat area."""
        try:
            self._active_loading_widget = AsyncLoadingWidget(command)
            if hasattr(self.main_window, "messages_layout") and hasattr(self.main_window, "messages_widget"):
                layout = self.main_window.messages_layout
                layout.insertWidget(layout.count() - 1, self._active_loading_widget)
                QTimer.singleShot(50, self.main_window.scroll_to_bottom)
        except Exception as e:
            print(f"⚠️ Could not show loading widget: {e}")
            self._active_loading_widget = None

    def _remove_loading_widget(self):
        """Remove the loading receipt from chat."""
        if self._active_loading_widget:
            try:
                self._active_loading_widget.stop()
                if hasattr(self.main_window, "messages_layout"):
                    self.main_window.messages_layout.removeWidget(self._active_loading_widget)
                self._active_loading_widget.deleteLater()
            except RuntimeError:
                pass
            except Exception as e:
                print(f"⚠️ Error removing loading widget: {e}")
            finally:
                self._active_loading_widget = None

    def _on_command_progress(self, text):
        """Update loading widget and status bar with progress text."""
        # Update loading receipt
        if self._active_loading_widget:
            self._active_loading_widget.update_progress(text)
        # Update status bar
        if hasattr(self.main_window, "status_bar_widget"):
            self.main_window.status_bar_widget.connection_label.setText(f"  {text}")

    def _post_to_chat(self, text):
        self.main_window.add_message_widget("ai", text, datetime.now())

    def _post_tool_card(self, tool_name, title, subtitle="", metrics=None, sections=None):
        lines = [
            f"[[tool:{tool_name}]]",
            f"[[title:{title}]]",
        ]
        if subtitle:
            lines.append(f"[[subtitle:{subtitle}]]")

        for label, value in metrics or []:
            lines.append(f"[[metric:{label}|{value}]]")

        for section_title, items in sections or []:
            if not items:
                continue
            lines.append(f"[[section:{section_title}]]")
            for item in items:
                lines.append(f"- {item}")

        self._post_to_chat("\n".join(lines))
