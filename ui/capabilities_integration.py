"""
Kai Capabilities Integration Module
Integrates core capabilities with the PyQt5 UI.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFileDialog, QMessageBox, QTabWidget, QSplitter,
    QTreeWidget, QTreeWidgetItem, QHeaderView, QMenu, QAction
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QSyntaxHighlighter, QTextCharFormat

# Import capabilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kai_capabilities import KaiCapabilities


class CodeHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for code display."""

    def __init__(self, parent=None, language='python'):
        super().__init__(parent)
        self.language = language
        self.highlighting_rules = []

        # Common formats
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor('#569CD6'))
        keyword_format.setFontWeight(QFont.Bold)

        string_format = QTextCharFormat()
        string_format.setForeground(QColor('#CE9178'))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor('#6A9955'))
        comment_format.setFontItalic(True)

        function_format = QTextCharFormat()
        function_format.setForeground(QColor('#DCDCAA'))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor('#B5CEA8'))

        # Python keywords
        if language == 'python':
            keywords = [
                'def', 'class', 'import', 'from', 'return', 'if', 'else', 'elif',
                'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'pass',
                'break', 'continue', 'and', 'or', 'not', 'in', 'is', 'lambda',
                'yield', 'async', 'await', 'True', 'False', 'None'
            ]
            for word in keywords:
                self.highlighting_rules.append((rf'\b{word}\b', keyword_format))

        # JavaScript/TypeScript keywords
        elif language in ['javascript', 'typescript']:
            keywords = [
                'function', 'const', 'let', 'var', 'if', 'else', 'for', 'while',
                'return', 'class', 'extends', 'import', 'export', 'default',
                'try', 'catch', 'finally', 'throw', 'new', 'this', 'super',
                'async', 'await', 'true', 'false', 'null', 'undefined'
            ]
            for word in keywords:
                self.highlighting_rules.append((rf'\b{word}\b', keyword_format))

        # Common patterns
        self.highlighting_rules.append((r'"[^"]*"', string_format))
        self.highlighting_rules.append((r"'[^']*'", string_format))
        self.highlighting_rules.append((r'#[^\n]*', comment_format))
        self.highlighting_rules.append((r'//[^\n]*', comment_format))
        self.highlighting_rules.append((r'/\*.*?\*/', comment_format))
        self.highlighting_rules.append((r'\b\d+\.?\d*\b', number_format))
        self.highlighting_rules.append((r'\b\w+(?=\()', function_format))

    def highlightBlock(self, text):
        """Apply highlighting rules to a block of text."""
        for pattern, format in self.highlighting_rules:
            import re
            for match in re.finditer(pattern, text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format)


class CodeEditorWidget(QWidget):
    """Widget for editing and analyzing code."""

    code_analyzed = pyqtSignal(dict)
    code_executed = pyqtSignal(dict)

    def __init__(self, capabilities: KaiCapabilities, parent=None):
        super().__init__(parent)
        self.capabilities = capabilities
        self.current_file = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        toolbar = QHBoxLayout()
        
        self.file_label = QLabel("No file loaded")
        self.file_label.setStyleSheet("color: rgba(255, 255, 255, 0.7); font-size: 12px;")
        toolbar.addWidget(self.file_label)
        toolbar.addStretch()

        # Buttons
        open_btn = QPushButton("📂 Open")
        open_btn.clicked.connect(self.open_file)
        open_btn.setStyleSheet(self._button_style())
        toolbar.addWidget(open_btn)

        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save_file)
        save_btn.setStyleSheet(self._button_style())
        toolbar.addWidget(save_btn)

        analyze_btn = QPushButton("🔍 Analyze")
        analyze_btn.clicked.connect(self.analyze_code)
        analyze_btn.setStyleSheet(self._button_style())
        toolbar.addWidget(analyze_btn)

        run_btn = QPushButton("▶️ Run")
        run_btn.clicked.connect(self.run_code)
        run_btn.setStyleSheet(self._button_style())
        toolbar.addWidget(run_btn)

        layout.addLayout(toolbar)

        # Splitter for editor and output
        splitter = QSplitter(Qt.Vertical)

        # Code editor
        self.editor = QTextEdit()
        self.editor.setStyleSheet("""
            QTextEdit {
                background: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                padding: 10px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
        """)
        self.editor.textChanged.connect(self.on_text_changed)
        splitter.addWidget(self.editor)

        # Output panel
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("""
            QTextEdit {
                background: #0d1117;
                color: #c9d1d9;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                padding: 10px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
        """)
        splitter.addWidget(self.output)

        splitter.setSizes([400, 200])
        layout.addWidget(splitter)

    def _button_style(self):
        return """
            QPushButton {
                background: rgba(0, 198, 255, 0.12);
                border: 1px solid rgba(0, 198, 255, 0.35);
                border-radius: 8px;
                padding: 6px 12px;
                color: white;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(0, 198, 255, 0.2);
                border: 1px solid #00C6FF;
            }
        """

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "",
            "Python Files (*.py);;JavaScript Files (*.js);;All Files (*)"
        )
        if file_path:
            result = self.capabilities.read_file(file_path)
            if result['success']:
                self.editor.setPlainText(result['content'])
                self.current_file = file_path
                self.file_label.setText(f"📄 {Path(file_path).name}")
                
                # Detect language and apply highlighter
                language = self.capabilities.code_analyzer.detect_language(file_path)
                self.highlighter = CodeHighlighter(self.editor.document(), language)
            else:
                self.output.append(f"❌ Error: {result['message']}")

    def save_file(self):
        if not self.current_file:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save File", "",
                "Python Files (*.py);;JavaScript Files (*.js);;All Files (*)"
            )
            if file_path:
                self.current_file = file_path
            else:
                return

        content = self.editor.toPlainText()
        result = self.capabilities.write_file(self.current_file, content)
        
        if result['success']:
            self.output.append(f"✅ File saved: {self.current_file}")
        else:
            self.output.append(f"❌ Error: {result['message']}")

    def analyze_code(self):
        code = self.editor.toPlainText()
        if not code.strip():
            self.output.append("⚠️ No code to analyze")
            return

        language = 'python'
        if self.current_file:
            language = self.capabilities.code_analyzer.detect_language(self.current_file)

        analysis = self.capabilities.analyze_code(code, language)
        
        self.output.append("\n" + "=" * 50)
        self.output.append("📊 Code Analysis Results")
        self.output.append("=" * 50)
        self.output.append(f"Language: {analysis['language']}")
        self.output.append(f"Lines: {analysis['lines']}")
        self.output.append(f"Complexity: {analysis['complexity']}")
        
        if analysis['functions']:
            self.output.append(f"\nFunctions ({len(analysis['functions'])}):")
            for func in analysis['functions']:
                self.output.append(f"  • {func}")
        
        if analysis['classes']:
            self.output.append(f"\nClasses ({len(analysis['classes'])}):")
            for cls in analysis['classes']:
                self.output.append(f"  • {cls}")
        
        if analysis['imports']:
            self.output.append(f"\nImports ({len(analysis['imports'])}):")
            for imp in analysis['imports']:
                self.output.append(f"  • {imp}")
        
        if analysis['issues']:
            self.output.append(f"\n⚠️ Issues ({len(analysis['issues'])}):")
            for issue in analysis['issues']:
                self.output.append(f"  • {issue}")
        
        self.code_analyzed.emit(analysis)

    def run_code(self):
        code = self.editor.toPlainText()
        if not code.strip():
            self.output.append("⚠️ No code to run")
            return

        self.output.append("\n" + "=" * 50)
        self.output.append("▶️ Running code...")
        self.output.append("=" * 50)

        result = self.capabilities.execute_python(code)
        
        if result['stdout']:
            self.output.append(result['stdout'])
        
        if result['stderr']:
            self.output.append(f"❌ Error:\n{result['stderr']}")
        
        self.output.append(f"\n⏱️ Execution time: {result['execution_time']:.3f}s")
        self.output.append(f"Return code: {result['return_code']}")
        
        self.code_executed.emit(result)

    def on_text_changed(self):
        """Handle text changes."""
        pass  # Could add auto-save or live analysis here


class FileExplorerWidget(QWidget):
    """Widget for exploring project files."""

    file_selected = pyqtSignal(str)
    file_opened = pyqtSignal(str)

    def __init__(self, capabilities: KaiCapabilities, parent=None):
        super().__init__(parent)
        self.capabilities = capabilities
        self._scan_cache = None
        self._scan_cache_time = None
        self._cache_ttl = 5.0  # Cache for 5 seconds
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QHBoxLayout()
        title = QLabel("📁 Project Files")
        title.setStyleSheet("color: white; font-size: 14px; font-weight: 700;")
        header.addWidget(title)
        header.addStretch()

        refresh_btn = QPushButton("🔄")
        refresh_btn.clicked.connect(self.refresh)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: white;
                font-size: 16px;
                padding: 5px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
            }
        """)
        header.addWidget(refresh_btn)

        layout.addLayout(header)

        # File tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Type", "Size"])
        self.tree.setStyleSheet("""
            QTreeWidget {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                color: white;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:selected {
                background: rgba(0, 198, 255, 0.2);
            }
            QTreeWidget::item:hover {
                background: rgba(255, 255, 255, 0.08);
            }
        """)
        self.tree.header().setStyleSheet("""
            QHeaderView::section {
                background: rgba(255, 255, 255, 0.08);
                color: white;
                padding: 5px;
                border: none;
            }
        """)
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.tree)

        # Info label
        self.info_label = QLabel("Click refresh to scan project")
        self.info_label.setStyleSheet("color: rgba(255, 255, 255, 0.5); font-size: 11px;")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

    def refresh(self):
        """Refresh the file tree with caching."""
        import time
        
        # Check cache first
        current_time = time.time()
        if (self._scan_cache is not None and 
            self._scan_cache_time is not None and 
            current_time - self._scan_cache_time < self._cache_ttl):
            structure = self._scan_cache
        else:
            self.tree.clear()
            self.info_label.setText("Scanning project...")
            
            structure = self.capabilities.scan_project()
            
            # Cache the result
            self._scan_cache = structure
            self._scan_cache_time = current_time
        
        if 'error' in structure:
            self.info_label.setText(f"Error: {structure['error']}")
            return

        # Create root item
        root = QTreeWidgetItem(self.tree)
        root.setText(0, Path(structure['root']).name)
        root.setText(1, "Project")
        root.setText(2, f"{structure['total_lines']} lines")
        root.setExpanded(True)

        # Add directories
        dir_items = {}
        for dir_path in sorted(structure['directories']):
            parts = Path(dir_path).parts
            parent = root
            current_path = ""
            
            for part in parts:
                current_path = os.path.join(current_path, part) if current_path else part
                if current_path not in dir_items:
                    item = QTreeWidgetItem(parent)
                    item.setText(0, part)
                    item.setText(1, "Directory")
                    item.setData(0, Qt.UserRole, current_path)
                    dir_items[current_path] = item
                parent = dir_items[current_path]

        # Add files
        for file_path in sorted(structure['files']):
            parts = Path(file_path).parts
            parent = root
            
            # Navigate to parent directory
            for part in parts[:-1]:
                dir_path = os.path.join(*parts[:parts.index(part) + 1])
                if dir_path in dir_items:
                    parent = dir_items[dir_path]
            
            # Add file item
            item = QTreeWidgetItem(parent)
            item.setText(0, parts[-1])
            item.setText(1, Path(file_path).suffix or "File")
            item.setData(0, Qt.UserRole, file_path)

        # Update info
        lang_summary = ", ".join([f"{lang}: {count}" for lang, count in structure['languages'].items()])
        self.info_label.setText(f"{len(structure['files'])} files | {lang_summary}")

    def on_item_double_clicked(self, item, column):
        """Handle double-click on item."""
        file_path = item.data(0, Qt.UserRole)
        if file_path:
            self.file_opened.emit(file_path)

    def show_context_menu(self, position):
        """Show context menu."""
        item = self.tree.itemAt(position)
        if not item:
            return

        file_path = item.data(0, Qt.UserRole)
        if not file_path:
            return

        menu = QMenu()
        
        open_action = QAction("📂 Open", self)
        open_action.triggered.connect(lambda: self.file_opened.emit(file_path))
        menu.addAction(open_action)

        analyze_action = QAction("🔍 Analyze", self)
        analyze_action.triggered.connect(lambda: self.analyze_file(file_path))
        menu.addAction(analyze_action)

        menu.exec_(self.tree.viewport().mapToGlobal(position))

    def analyze_file(self, file_path):
        """Analyze a file."""
        analysis = self.capabilities.analyze_file(file_path)
        
        msg = QMessageBox()
        msg.setWindowTitle(f"Analysis: {Path(file_path).name}")
        msg.setTextFormat(Qt.RichText)
        
        text = f"""
        <h3>File Analysis</h3>
        <p><b>Language:</b> {analysis['language']}</p>
        <p><b>Lines:</b> {analysis['lines']}</p>
        <p><b>Complexity:</b> {analysis['complexity']}</p>
        """
        
        if analysis['functions']:
            text += f"<p><b>Functions:</b> {', '.join(analysis['functions'])}</p>"
        
        if analysis['classes']:
            text += f"<p><b>Classes:</b> {', '.join(analysis['classes'])}</p>"
        
        if analysis['issues']:
            text += f"<p><b>Issues:</b></p><ul>"
            for issue in analysis['issues']:
                text += f"<li>{issue}</li>"
            text += "</ul>"
        
        msg.setText(text)
        msg.exec_()


class TerminalWidget(QWidget):
    """Widget for executing commands."""

    command_executed = pyqtSignal(dict)

    def __init__(self, capabilities: KaiCapabilities, parent=None):
        super().__init__(parent)
        self.capabilities = capabilities
        self.command_history = []
        self.history_index = -1
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QHBoxLayout()
        title = QLabel("💻 Terminal")
        title.setStyleSheet("color: white; font-size: 14px; font-weight: 700;")
        header.addWidget(title)
        header.addStretch()

        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.clicked.connect(self.clear_output)
        clear_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 5px;
                color: white;
                font-size: 11px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
        """)
        header.addWidget(clear_btn)

        layout.addLayout(header)

        # Output area
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("""
            QTextEdit {
                background: #0d1117;
                color: #c9d1d9;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                padding: 10px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.output)

        # Input area
        input_layout = QHBoxLayout()
        
        self.prompt_label = QLabel("$")
        self.prompt_label.setStyleSheet("""
            QLabel {
                color: #00C6FF;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                font-weight: bold;
            }
        """)
        input_layout.addWidget(self.prompt_label)

        self.input = QTextEdit()
        self.input.setMaximumHeight(40)
        self.input.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 0.05);
                color: white;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                padding: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
        """)
        self.input.installEventFilter(self)
        input_layout.addWidget(self.input)

        run_btn = QPushButton("▶️")
        run_btn.clicked.connect(self.execute_command)
        run_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 198, 255, 0.2);
                border: 1px solid #00C6FF;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background: rgba(0, 198, 255, 0.3);
            }
        """)
        input_layout.addWidget(run_btn)

        layout.addLayout(input_layout)

        # Welcome message
        self.output.append("Welcome to Kai Terminal")
        self.output.append("Type a command and press Enter or click Run")
        self.output.append("=" * 50)

    def eventFilter(self, obj, event):
        """Handle key events."""
        if obj == self.input and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Return and not event.modifiers():
                self.execute_command()
                return True
            elif event.key() == Qt.Key_Up:
                self.navigate_history(-1)
                return True
            elif event.key() == Qt.Key_Down:
                self.navigate_history(1)
                return True
        return super().eventFilter(obj, event)

    def execute_command(self):
        """Execute a command."""
        command = self.input.toPlainText().strip()
        if not command:
            return

        # Add to history
        self.command_history.append(command)
        self.history_index = len(self.command_history)

        # Display command
        self.output.append(f"\n$ {command}")
        self.output.append("-" * 50)

        # Execute
        result = self.capabilities.execute_command(command)

        # Display result
        if result['stdout']:
            self.output.append(result['stdout'])
        
        if result['stderr']:
            self.output.append(f"Error: {result['stderr']}")

        self.output.append(f"\n[Return code: {result['return_code']}, Time: {result['execution_time']:.3f}s]")

        # Clear input
        self.input.clear()

        # Emit signal
        self.command_executed.emit(result)

    def navigate_history(self, direction):
        """Navigate command history."""
        if not self.command_history:
            return

        self.history_index += direction
        self.history_index = max(0, min(self.history_index, len(self.command_history) - 1))
        
        self.input.setPlainText(self.command_history[self.history_index])

    def clear_output(self):
        """Clear the output."""
        self.output.clear()
        self.output.append("Terminal cleared")
        self.output.append("=" * 50)


class ToolBrowserWidget(QWidget):
    """Widget for browsing and executing tools."""

    tool_executed = pyqtSignal(str, dict)

    def __init__(self, capabilities: KaiCapabilities, parent=None):
        super().__init__(parent)
        self.capabilities = capabilities
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QHBoxLayout()
        title = QLabel("🔧 Tools")
        title.setStyleSheet("color: white; font-size: 14px; font-weight: 700;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Tool tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Tool", "Category", "Description"])
        self.tree.setStyleSheet("""
            QTreeWidget {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                color: white;
            }
            QTreeWidget::item {
                padding: 8px;
            }
            QTreeWidget::item:selected {
                background: rgba(0, 198, 255, 0.2);
            }
            QTreeWidget::item:hover {
                background: rgba(255, 255, 255, 0.08);
            }
        """)
        self.tree.header().setStyleSheet("""
            QHeaderView::section {
                background: rgba(255, 255, 255, 0.08);
                color: white;
                padding: 5px;
                border: none;
            }
        """)
        self.tree.itemDoubleClicked.connect(self.on_tool_double_clicked)
        layout.addWidget(self.tree)

        # Populate tools
        self.populate_tools()

    def populate_tools(self):
        """Populate the tool tree."""
        self.tree.clear()
        
        tools = self.capabilities.list_tools()
        
        # Group by category
        categories = {}
        for tool in tools:
            cat = tool['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(tool)

        # Add to tree
        for category, tools in sorted(categories.items()):
            cat_item = QTreeWidgetItem(self.tree)
            cat_item.setText(0, category.upper())
            cat_item.setText(1, "")
            cat_item.setText(2, f"{len(tools)} tools")
            cat_item.setExpanded(True)

            for tool in sorted(tools, key=lambda t: t['name']):
                tool_item = QTreeWidgetItem(cat_item)
                tool_item.setText(0, tool['name'])
                tool_item.setText(1, tool['category'])
                tool_item.setText(2, tool['description'])
                tool_item.setData(0, Qt.UserRole, tool['name'])

    def on_tool_double_clicked(self, item, column):
        """Handle tool double-click."""
        tool_name = item.data(0, Qt.UserRole)
        if tool_name:
            self.execute_tool(tool_name)

    def execute_tool(self, tool_name):
        """Execute a tool."""
        # For now, just show a message
        # In a full implementation, this would open a dialog to collect parameters
        msg = QMessageBox()
        msg.setWindowTitle(f"Execute Tool: {tool_name}")
        msg.setText(f"Tool: {tool_name}\n\nThis would open a parameter dialog in a full implementation.")
        msg.exec_()
        
        self.tool_executed.emit(tool_name, {})


class CapabilitiesPanel(QWidget):
    """Main panel that integrates all capability widgets."""

    def __init__(self, capabilities: KaiCapabilities, parent=None):
        super().__init__(parent)
        self.capabilities = capabilities
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header
        header = QLabel("🚀 Kai Capabilities")
        header.setStyleSheet("""
            QLabel {
                color: #00C6FF;
                font-size: 18px;
                font-weight: 800;
                padding: 10px;
            }
        """)
        layout.addWidget(header)

        # Tab widget
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.05);
            }
            QTabBar::tab {
                background: rgba(255, 255, 255, 0.08);
                color: white;
                padding: 10px 20px;
                border: none;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: rgba(0, 198, 255, 0.2);
                border-bottom: 2px solid #00C6FF;
            }
            QTabBar::tab:hover {
                background: rgba(255, 255, 255, 0.12);
            }
        """)

        # Code Editor tab
        self.code_editor = CodeEditorWidget(self.capabilities)
        tabs.addTab(self.code_editor, "📝 Code Editor")

        # File Explorer tab
        self.file_explorer = FileExplorerWidget(self.capabilities)
        tabs.addTab(self.file_explorer, "📁 Files")

        # Terminal tab
        self.terminal = TerminalWidget(self.capabilities)
        tabs.addTab(self.terminal, "💻 Terminal")

        # Tools tab
        self.tool_browser = ToolBrowserWidget(self.capabilities)
        tabs.addTab(self.tool_browser, "🔧 Tools")

        layout.addWidget(tabs)

        # Status bar
        status = QLabel("Ready | All capabilities loaded")
        status.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.5);
                font-size: 11px;
                padding: 5px;
            }
        """)
        layout.addWidget(status)
