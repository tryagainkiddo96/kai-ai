"""
Animated widgets for engaging, fun user experience.
Provides smooth animations, typing indicators, and visual feedback.
"""

from PyQt5.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout,
                             QGraphicsOpacityEffect, QSizePolicy)
from PyQt5.QtCore import (Qt, QPropertyAnimation, QEasingCurve, QTimer,
                          pyqtSignal, QRect, QPoint)
from PyQt5.QtGui import (QFont, QColor, QPainter, QLinearGradient,
                         QBrush, QPen, QPainterPath)
import math


class AnimatedTypingIndicator(QWidget):
    """Animated typing indicator with bouncing dots and worm animation."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dot_count = 3
        self.dot_size = 8
        self.dot_spacing = 12
        self.animation_offset = 0
        self.timer = None
        self.setup_ui()
        self.setup_animation()
    
    def setup_ui(self):
        """Setup the typing indicator UI."""
        self.setFixedSize(220, 42)
        self.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)
        
        # Label
        self.label = QLabel("Black Worm is thinking")
        self.label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 13px;
                font-weight: 500;
                font-family: 'Segoe UI';
                background: transparent;
            }
        """)
        layout.addWidget(self.label)
        layout.addStretch()
    
    def setup_animation(self):
        """Setup the bouncing dots animation."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(100)  # Update every 100ms
    
    def update_animation(self):
        """Update the animation frame."""
        self.animation_offset = (self.animation_offset + 1) % 20
        self.update()
    
    def paintEvent(self, event):
        """Custom paint for animated dots."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw bouncing dots
        for i in range(self.dot_count):
            x = 170 + i * self.dot_spacing
            # Sine wave for smooth bouncing
            bounce = math.sin((self.animation_offset + i * 5) * 0.3) * 5
            y = 20 + bounce
            
            # Gradient for each dot
            gradient = QLinearGradient(x, y - self.dot_size/2, x, y + self.dot_size/2)
            gradient.setColorAt(0, QColor(0, 198, 255))
            gradient.setColorAt(1, QColor(0, 114, 255))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(x - self.dot_size/2), int(y - self.dot_size/2),
                              self.dot_size, self.dot_size)
        
        painter.end()
    
    def stop_animation(self):
        """Stop the animation."""
        if self.timer:
            self.timer.stop()
    
    def start_animation(self):
        """Start the animation."""
        if self.timer:
            self.timer.start(100)


class AnimatedMessageBubble(QWidget):
    """Message bubble with slide-in and fade animations."""
    
    animation_complete = pyqtSignal()
    
    def __init__(self, content, is_user=True, parent=None):
        super().__init__(parent)
        self.content = content
        self.is_user = is_user
        self.opacity_effect = None
        self.slide_animation = None
        self.opacity_animation = None
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """Setup the message bubble UI."""
        self.setMinimumHeight(50)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 15, 5)
        
        # Bubble container
        bubble = QWidget()
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(15, 12, 15, 12)
        bubble_layout.setSpacing(5)
        
        # Content label
        content_label = QLabel(self.content)
        content_label.setWordWrap(True)
        content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        content_label.setTextFormat(Qt.RichText)
        content_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        content_label.setMaximumWidth(300)
        
        # Timestamp
        from datetime import datetime
        time_label = QLabel(datetime.now().strftime("%H:%M"))
        time_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        bubble_layout.addWidget(content_label)
        bubble_layout.addWidget(time_label)
        
        bubble.setMaximumWidth(330)
        
        # Styling based on sender
        if self.is_user:
            layout.addStretch()
            layout.addWidget(bubble)
            bubble.setStyleSheet("""
                QWidget {
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                        stop:0 #00C6FF, stop:1 #0072FF);
                    border: none;
                    border-radius: 18px;
                    margin: 3px 0px;
                }
            """)
            content_label.setStyleSheet("""
                QLabel {
                    color: #1a1a1a;
                    font-size: 15px;
                    line-height: 1.4;
                    font-weight: 600;
                    font-family: 'Segoe UI';
                    background: transparent;
                    padding: 2px 0px;
                }
            """)
            time_label.setStyleSheet("""
                QLabel {
                    color: rgba(26, 26, 26, 0.7);
                    font-size: 12px;
                    font-weight: 500;
                    background: transparent;
                }
            """)
            time_label.setAlignment(Qt.AlignRight)
        else:
            layout.addWidget(bubble)
            layout.addStretch()
            bubble.setStyleSheet("""
                QWidget {
                    background: rgba(255, 255, 255, 0.15);
                    border: none;
                    border-radius: 18px;
                    margin: 3px 0px;
                }
            """)
            content_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 15px;
                    line-height: 1.4;
                    font-weight: 600;
                    font-family: 'Segoe UI';
                    background: transparent;
                    padding: 2px 0px;
                }
            """)
            time_label.setStyleSheet("""
                QLabel {
                    color: rgba(255, 255, 255, 0.7);
                    font-size: 12px;
                    font-weight: 500;
                    background: transparent;
                }
            """)
            time_label.setAlignment(Qt.AlignLeft)
    
    def setup_animations(self):
        """Setup slide and fade animations."""
        # Opacity effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0)
        self.setGraphicsEffect(self.opacity_effect)
        
        # Opacity animation
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(300)
        self.opacity_animation.setStartValue(0)
        self.opacity_animation.setEndValue(1)
        self.opacity_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Slide animation (for AI messages)
        if not self.is_user:
            self.slide_animation = QPropertyAnimation(self, b"pos")
            self.slide_animation.setDuration(300)
            self.slide_animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def animate_in(self):
        """Animate the message bubble appearing."""
        self.opacity_animation.start()
        if self.slide_animation:
            # Start from left, slide to final position
            start_pos = self.pos() - QPoint(50, 0)
            self.slide_animation.setStartValue(start_pos)
            self.slide_animation.setEndValue(self.pos())
            self.slide_animation.start()
        
        # Connect to completion signal
        self.opacity_animation.finished.connect(self.animation_complete.emit)


class CelebrationEffect(QWidget):
    """Celebration effect for milestones and achievements."""
    
    def __init__(self, message="🎉 Milestone reached!", parent=None):
        super().__init__(parent)
        self.message = message
        self.particles = []
        self.timer = None
        self.setup_ui()
        self.setup_animation()
    
    def setup_ui(self):
        """Setup celebration UI."""
        self.setFixedSize(300, 100)
        self.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        label = QLabel(self.message)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: #00ffff;
                font-size: 18px;
                font-weight: 700;
                font-family: 'Segoe UI';
                background: transparent;
            }
        """)
        layout.addWidget(label)
    
    def setup_animation(self):
        """Setup particle animation."""
        import random
        # Create particles
        for _ in range(20):
            self.particles.append({
                'x': random.randint(0, 300),
                'y': random.randint(0, 100),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-3, -1),
                'size': random.randint(3, 8),
                'color': QColor(random.randint(0, 255),
                              random.randint(0, 255),
                              random.randint(0, 255))
            })
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_particles)
        self.timer.start(50)
    
    def update_particles(self):
        """Update particle positions."""
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.1  # Gravity
            
            # Reset if off screen
            if p['y'] > 100:
                p['y'] = 0
                p['vy'] = random.uniform(-3, -1)
        
        self.update()
    
    def paintEvent(self, event):
        """Paint particles."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        for p in self.particles:
            painter.setBrush(p['color'])
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(p['x']), int(p['y']),
                              p['size'], p['size'])
        
        painter.end()


class SmoothScrollArea(QWidget):
    """Smooth scrolling container with momentum."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.velocity = 0
        self.friction = 0.95
        self.timer = None
        self.setup_animation()
    
    def setup_animation(self):
        """Setup smooth scroll animation."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.apply_friction)
    
    def wheelEvent(self, event):
        """Handle mouse wheel with momentum."""
        self.velocity += event.angleDelta().y() / 120
        if not self.timer.isActive():
            self.timer.start(16)  # ~60fps
    
    def apply_friction(self):
        """Apply friction to velocity."""
        self.velocity *= self.friction
        if abs(self.velocity) < 0.1:
            self.timer.stop()
            self.velocity = 0
        
        # Apply scroll
        # This would need to be connected to actual scroll area
        self.update()


class PulseButton(QWidget):
    """Button with pulse animation on hover."""
    
    clicked = pyqtSignal()
    
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self.is_hovered = False
        self.pulse_scale = 1.0
        self.pulse_direction = 1
        self.timer = None
        self.setup_ui()
        self.setup_animation()
    
    def setup_ui(self):
        """Setup button UI."""
        self.setFixedSize(120, 50)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(self.text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: #1a1a1a;
                font-size: 15px;
                font-weight: 700;
                font-family: 'Segoe UI';
                background: transparent;
            }
        """)
        layout.addWidget(label)
    
    def setup_animation(self):
        """Setup pulse animation."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.pulse)
    
    def enterEvent(self, event):
        """Handle mouse enter."""
        self.is_hovered = True
        self.timer.start(50)
        self.update()
    
    def leaveEvent(self, event):
        """Handle mouse leave."""
        self.is_hovered = False
        self.timer.stop()
        self.pulse_scale = 1.0
        self.update()
    
    def pulse(self):
        """Pulse animation."""
        self.pulse_scale += 0.02 * self.pulse_direction
        if self.pulse_scale >= 1.1:
            self.pulse_direction = -1
        elif self.pulse_scale <= 1.0:
            self.pulse_direction = 1
        self.update()
    
    def mousePressEvent(self, event):
        """Handle click."""
        self.clicked.emit()
    
    def paintEvent(self, event):
        """Custom paint for gradient and pulse."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Scale for pulse effect
        painter.translate(self.width()/2, self.height()/2)
        painter.scale(self.pulse_scale, self.pulse_scale)
        painter.translate(-self.width()/2, -self.height()/2)
        
        # Gradient background
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor(0, 198, 255))
        gradient.setColorAt(1, QColor(0, 114, 255))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 25, 25)
        
        painter.end()


class ProgressIndicator(QWidget):
    """Animated progress indicator for long operations."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 0
        self.timer = None
        self.setup_ui()
        self.setup_animation()
    
    def setup_ui(self):
        """Setup progress indicator UI."""
        self.setFixedSize(200, 6)
        self.setStyleSheet("background: rgba(255, 255, 255, 0.1); border-radius: 3px;")
    
    def setup_animation(self):
        """Setup progress animation."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
    
    def start(self):
        """Start progress animation."""
        self.progress = 0
        self.timer.start(50)
        self.show()
    
    def stop(self):
        """Stop progress animation."""
        self.timer.stop()
        self.hide()
    
    def update_progress(self):
        """Update progress value."""
        self.progress = (self.progress + 2) % 100
        self.update()
    
    def paintEvent(self, event):
        """Paint progress bar."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Progress gradient
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor(0, 198, 255))
        gradient.setColorAt(1, QColor(0, 255, 255))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        
        # Draw progress
        progress_width = int(self.width() * self.progress / 100)
        painter.drawRoundedRect(0, 0, progress_width, self.height(), 3, 3)
        
        painter.end()
