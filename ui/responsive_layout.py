"""
Responsive layout manager for adaptive single-window design.
Handles different screen sizes and provides smooth transitions.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
                             QFrame, QLabel, QPushButton, QSizePolicy,
                             QGraphicsOpacityEffect, QScrollArea)
from PyQt5.QtCore import (Qt, QPropertyAnimation, QEasingCurve, QTimer,
                          pyqtSignal, QSize, QPoint)
from PyQt5.QtGui import QFont, QColor


class ResponsiveContainer(QWidget):
    """Container that adapts to window size with smooth transitions."""
    
    size_changed = pyqtSignal(str)  # Emits 'large', 'medium', or 'small'
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_size = 'large'
        self.minimum_width = 1200
        self.medium_threshold = 800
        self.setup_ui()
    
    def setup_ui(self):
        """Setup responsive container."""
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def resizeEvent(self, event):
        """Handle resize and emit size category."""
        super().resizeEvent(event)
        width = event.size().width()
        
        if width >= self.minimum_width:
            new_size = 'large'
        elif width >= self.medium_threshold:
            new_size = 'medium'
        else:
            new_size = 'small'
        
        if new_size != self.current_size:
            self.current_size = new_size
            self.size_changed.emit(new_size)


class CollapsiblePanel(QWidget):
    """Panel that can collapse/expand with smooth animation."""
    
    toggled = pyqtSignal(bool)
    
    def __init__(self, title, content_widget, parent=None):
        super().__init__(parent)
        self.title = title
        self.content_widget = content_widget
        self.is_expanded = True
        self.animation = None
        self.setup_ui()
        self.setup_animation()
    
    def setup_ui(self):
        """Setup collapsible panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setFixedHeight(50)
        header.setCursor(Qt.PointingHandCursor)
        header.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border: none;
                border-bottom: 1px solid rgba(0, 198, 255, 0.3);
            }
            QFrame:hover {
                background: rgba(255, 255, 255, 0.08);
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 15px;
                font-weight: 600;
                font-family: 'Segoe UI';
                background: transparent;
            }
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Toggle button
        self.toggle_btn = QPushButton("▼")
        self.toggle_btn.setFixedSize(30, 30)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: rgba(255, 255, 255, 0.7);
                font-size: 12px;
            }
            QPushButton:hover {
                color: #00C6FF;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle)
        header_layout.addWidget(self.toggle_btn)
        
        layout.addWidget(header)
        
        # Content container
        self.content_container = QWidget()
        self.content_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.content_widget)
        
        layout.addWidget(self.content_container)
    
    def setup_animation(self):
        """Setup collapse/expand animation."""
        self.animation = QPropertyAnimation(self.content_container, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
    
    def toggle(self):
        """Toggle panel expansion."""
        self.is_expanded = not self.is_expanded
        
        if self.is_expanded:
            self.animation.setStartValue(0)
            self.animation.setEndValue(self.content_widget.sizeHint().height())
            self.toggle_btn.setText("▼")
        else:
            self.animation.setStartValue(self.content_container.height())
            self.animation.setEndValue(0)
            self.toggle_btn.setText("▶")
        
        self.animation.start()
        self.toggled.emit(self.is_expanded)


class AdaptiveStackedWidget(QStackedWidget):
    """Stacked widget with fade transitions."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fade_duration = 200
        self.current_opacity = 1.0
        self.setup_animations()
    
    def setup_animations(self):
        """Setup fade animations."""
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(self.fade_duration)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(self.fade_duration)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
    
    def setCurrentIndex(self, index):
        """Switch widget with fade animation."""
        if index == self.currentIndex():
            return
        
        # Fade out current
        self.fade_out.start()
        
        # Switch after fade out
        QTimer.singleShot(self.fade_duration, lambda: self._switch_widget(index))
    
    def _switch_widget(self, index):
        """Actually switch the widget."""
        super().setCurrentIndex(index)
        self.fade_in.start()


class FloatingInput(QWidget):
    """Floating input area that stays at bottom."""
    
    send_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup floating input UI."""
        self.setFixedHeight(80)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)
        
        # Input field
        from PyQt5.QtWidgets import QLineEdit
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.input_field.setFixedHeight(50)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.08);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 25px;
                padding: 12px 20px;
                font-size: 15px;
                color: white;
                font-weight: 500;
                font-family: 'Segoe UI';
                selection-background-color: #00C6FF;
            }
            QLineEdit:focus {
                border: 2px solid #00C6FF;
                background: rgba(255, 255, 255, 0.12);
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        layout.addWidget(self.input_field)
        
        # Send button
        from ui.animated_widgets import PulseButton
        send_btn = PulseButton("Send")
        send_btn.clicked.connect(self.send_message)
        layout.addWidget(send_btn)
    
    def send_message(self):
        """Send the message."""
        text = self.input_field.text().strip()
        if text:
            self.send_requested.emit(text)
            self.input_field.clear()


class ResponsiveSidebar(QWidget):
    """Sidebar that adapts to screen size."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_collapsed = False
        self.expanded_width = 300
        self.collapsed_width = 60
        self.animation = None
        self.setup_ui()
        self.setup_animation()
    
    def setup_ui(self):
        """Setup responsive sidebar."""
        self.setFixedWidth(self.expanded_width)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # New chat button
        from ui.animated_widgets import PulseButton
        new_chat_btn = PulseButton("+ New Chat")
        new_chat_btn.clicked.connect(self.new_chat)
        layout.addWidget(new_chat_btn)
        
        # Recent chats label
        recent_label = QLabel("Recent Chats")
        recent_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: 700;
                font-family: 'Segoe UI';
                margin: 15px 0px 10px 0px;
                padding: 8px 0px;
                background: transparent;
            }
        """)
        layout.addWidget(recent_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("""
            QFrame {
                background-color: #00C6FF;
                border: none;
                height: 2px;
                margin: 5px 0px 15px 0px;
            }
        """)
        layout.addWidget(separator)
        
        # Chats scroll area
        self.chats_scroll = QScrollArea()
        self.chats_scroll.setWidgetResizable(True)
        self.chats_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chats_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chats_scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
                outline: none;
            }
        """)
        
        self.chats_container = QWidget()
        self.chats_layout = QVBoxLayout(self.chats_container)
        self.chats_layout.setContentsMargins(5, 5, 5, 5)
        self.chats_layout.setSpacing(5)
        self.chats_layout.addStretch()
        
        self.chats_scroll.setWidget(self.chats_container)
        layout.addWidget(self.chats_scroll)
        
        # Styling
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #111827, stop:1 #1f2937);
                border: 1px solid rgba(0, 245, 255, 0.3);
                border-right: 2px solid #00C6FF;
                border-radius: 15px 0px 0px 15px;
                margin: 5px 0px 5px 5px;
            }
        """)
    
    def setup_animation(self):
        """Setup collapse/expand animation."""
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
    
    def toggle_collapse(self):
        """Toggle sidebar collapse."""
        self.is_collapsed = not self.is_collapsed
        
        if self.is_collapsed:
            self.animation.setStartValue(self.expanded_width)
            self.animation.setEndValue(self.collapsed_width)
        else:
            self.animation.setStartValue(self.collapsed_width)
            self.animation.setEndValue(self.expanded_width)
        
        self.animation.start()
    
    def new_chat(self):
        """Create new chat."""
        # Emit signal or call parent method
        pass


class GlassmorphismFrame(QFrame):
    """Frame with glassmorphism effect."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_style()
    
    def setup_style(self):
        """Apply glassmorphism style."""
        self.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }
        """)


class QuickActionBar(QWidget):
    """Quick action bar with slash commands and reactions."""
    
    action_triggered = pyqtSignal(str, str)  # action_type, value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup quick action bar."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(8)
        
        # Slash commands
        commands = ["/help", "/clear", "/export", "/settings"]
        for cmd in commands:
            btn = QPushButton(cmd)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.08);
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    border-radius: 12px;
                    padding: 6px 12px;
                    color: rgba(255, 255, 255, 0.8);
                    font-size: 12px;
                    font-weight: 500;
                    font-family: 'Segoe UI';
                }
                QPushButton:hover {
                    background: rgba(0, 198, 255, 0.2);
                    border: 1px solid #00C6FF;
                    color: #00C6FF;
                }
            """)
            btn.clicked.connect(lambda checked, c=cmd: self.action_triggered.emit("command", c))
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # Reactions
        reactions = ["👍", "❤️", "🎉", "💡"]
        for reaction in reactions:
            btn = QPushButton(reaction)
            btn.setFixedSize(30, 30)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                }
            """)
            btn.clicked.connect(lambda checked, r=reaction: self.action_triggered.emit("reaction", r))
            layout.addWidget(btn)


class StatusBar(QWidget):
    """Status bar showing connection, credits, and other info."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup status bar."""
        self.setFixedHeight(30)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(20)
        
        # Connection status
        self.connection_label = QLabel("🟢 Connected")
        self.connection_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 12px;
                font-family: 'Segoe UI';
                background: transparent;
            }
        """)
        layout.addWidget(self.connection_label)
        
        layout.addStretch()
        
        # Credits
        self.credits_label = QLabel("💳 Credits: 15")
        self.credits_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 12px;
                font-family: 'Segoe UI';
                background: transparent;
            }
        """)
        layout.addWidget(self.credits_label)
        
        # Model info
        self.model_label = QLabel("🤖 GPT-4o")
        self.model_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 12px;
                font-family: 'Segoe UI';
                background: transparent;
            }
        """)
        layout.addWidget(self.model_label)
    
    def update_credits(self, credits):
        """Update credits display."""
        self.credits_label.setText(f"💳 Credits: {credits}")
    
    def update_connection(self, connected):
        """Update connection status."""
        if connected:
            self.connection_label.setText("🟢 Connected")
        else:
            self.connection_label.setText("🔴 Disconnected")
