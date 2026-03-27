"""
Kai 3D Desktop Renderer
Renders Kai's 3D model on the desktop with Shiba-like behaviors
"""

import sys
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List
from enum import Enum
import math
import time

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QComboBox
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QPoint, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPixmap, QImage
from PyQt5.QtOpenGL import QGLWidget, QGLFormat

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    from OpenGL.GLUT import *
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("Warning: PyOpenGL not installed. Install with: pip install PyOpenGL PyOpenGL_accelerate")

try:
    import pygltflib
    GLTFLIB_AVAILABLE = True
except ImportError:
    GLTFLIB_AVAILABLE = False
    print("Warning: pygltflib not installed. Install with: pip install pygltflib")


class KaiState(Enum):
    """Kai's behavioral states"""
    IDLE = "idle"
    SITTING = "sitting"
    TAIL_WAG = "tail_wag"
    HEAD_TILT = "head_tilt"
    WALKING = "walking"
    SLEEPING = "sleeping"
    EXCITED = "excited"


class Kai3DRenderer(QGLWidget):
    """OpenGL widget for rendering Kai's 3D model"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.mesh_data = []
        self.animation_time = 0.0
        self.current_state = KaiState.IDLE
        self.state_timer = 0.0
        self.state_duration = 5.0  # seconds per state
        
        # Camera settings
        self.camera_distance = 3.0
        self.camera_rotation_x = 20.0
        self.camera_rotation_y = 0.0
        self.last_mouse_pos = QPoint()
        self.mouse_dragging = False
        
        # Animation parameters
        self.breathing_amplitude = 0.02
        self.breathing_speed = 1.0
        self.tail_wag_speed = 3.0
        self.tail_wag_amplitude = 0.3
        self.ear_twitch_amplitude = 0.15
        
        # Colors (Shiba Inu colors)
        self.primary_color = (0.9, 0.7, 0.4, 1.0)  # Orange/cream
        self.secondary_color = (1.0, 1.0, 1.0, 1.0)  # White
        self.accent_color = (0.2, 0.2, 0.2, 1.0)  # Black (nose, eyes)
        
        # Initialize timer for animations
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(16)  # ~60 FPS
        
        # State change timer
        self.state_change_timer = QTimer(self)
        self.state_change_timer.timeout.connect(self.change_state)
        self.state_change_timer.start(5000)  # Change state every 5 seconds
        
    def initializeGL(self):
        """Initialize OpenGL settings"""
        if not OPENGL_AVAILABLE:
            return
            
        glClearColor(0.0, 0.0, 0.0, 0.0)  # Transparent background
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_NORMALIZE)
        
        # Set up lighting
        light_pos = [2.0, 2.0, 2.0, 1.0]
        light_ambient = [0.3, 0.3, 0.3, 1.0]
        light_diffuse = [0.8, 0.8, 0.8, 1.0]
        light_specular = [1.0, 1.0, 1.0, 1.0]
        
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
        
        # Set up material
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
    def resizeGL(self, width, height):
        """Handle window resize"""
        if not OPENGL_AVAILABLE:
            return
            
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        
    def paintGL(self):
        """Render the 3D scene"""
        if not OPENGL_AVAILABLE:
            return
            
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Set camera position
        glTranslatef(0.0, -0.5, -self.camera_distance)
        glRotatef(self.camera_rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.camera_rotation_y, 0.0, 1.0, 0.0)
        
        # Draw Kai
        self.draw_kai()
        
    def draw_kai(self):
        """Draw Kai's 3D model with current animation"""
        # Calculate animation values based on current state
        breathing_offset = self.calculate_breathing()
        tail_wag_angle = self.calculate_tail_wag()
        ear_twitch = self.calculate_ear_twitch()
        head_tilt = self.calculate_head_tilt()
        leg_bend = self.calculate_leg_bend()
        
        # Draw body (simplified Shiba Inu shape)
        glPushMatrix()
        
        # Apply breathing animation
        glTranslatef(0.0, breathing_offset, 0.0)
        
        # Draw main body (torso)
        glColor4f(*self.primary_color)
        self.draw_ellipsoid(0.4, 0.3, 0.5, 16, 16)
        
        # Draw white chest
        glPushMatrix()
        glTranslatef(0.0, -0.1, 0.2)
        glColor4f(*self.secondary_color)
        self.draw_ellipsoid(0.25, 0.2, 0.3, 12, 12)
        glPopMatrix()
        
        # Draw head
        glPushMatrix()
        glTranslatef(0.0, 0.4, 0.3)
        glRotatef(head_tilt, 0.0, 0.0, 1.0)  # Head tilt animation
        
        # Head
        glColor4f(*self.primary_color)
        self.draw_sphere(0.25, 16, 16)
        
        # Snout
        glPushMatrix()
        glTranslatef(0.0, -0.05, 0.2)
        glColor4f(*self.secondary_color)
        self.draw_ellipsoid(0.12, 0.1, 0.15, 12, 12)
        
        # Nose
        glTranslatef(0.0, 0.0, 0.12)
        glColor4f(*self.accent_color)
        self.draw_sphere(0.04, 8, 8)
        glPopMatrix()
        
        # Eyes
        glPushMatrix()
        glTranslatef(-0.1, 0.05, 0.15)
        glColor4f(*self.accent_color)
        self.draw_sphere(0.03, 8, 8)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0.1, 0.05, 0.15)
        glColor4f(*self.accent_color)
        self.draw_sphere(0.03, 8, 8)
        glPopMatrix()
        
        # Ears
        glPushMatrix()
        glTranslatef(-0.15, 0.2, 0.0)
        glRotatef(-30 + ear_twitch, 0.0, 0.0, 1.0)
        glColor4f(*self.primary_color)
        self.draw_cone(0.08, 0.2, 12)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0.15, 0.2, 0.0)
        glRotatef(30 - ear_twitch, 0.0, 0.0, 1.0)
        glColor4f(*self.primary_color)
        self.draw_cone(0.08, 0.2, 12)
        glPopMatrix()
        
        glPopMatrix()  # End head
        
        # Draw legs
        # Front left leg
        glPushMatrix()
        glTranslatef(-0.2, -0.2, 0.2)
        glRotatef(leg_bend, 1.0, 0.0, 0.0)
        glColor4f(*self.primary_color)
        self.draw_cylinder(0.06, 0.25, 12)
        
        # Paw
        glTranslatef(0.0, -0.15, 0.0)
        glColor4f(*self.secondary_color)
        self.draw_sphere(0.06, 8, 8)
        glPopMatrix()
        
        # Front right leg
        glPushMatrix()
        glTranslatef(0.2, -0.2, 0.2)
        glRotatef(leg_bend, 1.0, 0.0, 0.0)
        glColor4f(*self.primary_color)
        self.draw_cylinder(0.06, 0.25, 12)
        
        # Paw
        glTranslatef(0.0, -0.15, 0.0)
        glColor4f(*self.secondary_color)
        self.draw_sphere(0.06, 8, 8)
        glPopMatrix()
        
        # Back left leg
        glPushMatrix()
        glTranslatef(-0.2, -0.2, -0.2)
        glRotatef(-leg_bend, 1.0, 0.0, 0.0)
        glColor4f(*self.primary_color)
        self.draw_cylinder(0.06, 0.25, 12)
        
        # Paw
        glTranslatef(0.0, -0.15, 0.0)
        glColor4f(*self.secondary_color)
        self.draw_sphere(0.06, 8, 8)
        glPopMatrix()
        
        # Back right leg
        glPushMatrix()
        glTranslatef(0.2, -0.2, -0.2)
        glRotatef(-leg_bend, 1.0, 0.0, 0.0)
        glColor4f(*self.primary_color)
        self.draw_cylinder(0.06, 0.25, 12)
        
        # Paw
        glTranslatef(0.0, -0.15, 0.0)
        glColor4f(*self.secondary_color)
        self.draw_sphere(0.06, 8, 8)
        glPopMatrix()
        
        # Draw tail
        glPushMatrix()
        glTranslatef(0.0, 0.1, -0.4)
        glRotatef(tail_wag_angle, 0.0, 1.0, 0.0)  # Tail wag animation
        
        # Tail base
        glColor4f(*self.primary_color)
        self.draw_cylinder(0.05, 0.15, 12)
        
        # Tail mid
        glTranslatef(0.0, 0.1, -0.1)
        glRotatef(tail_wag_angle * 1.2, 0.0, 1.0, 0.0)
        self.draw_cylinder(0.04, 0.12, 12)
        
        # Tail tip (curled up like Shiba)
        glTranslatef(0.0, 0.08, -0.08)
        glRotatef(-45, 1.0, 0.0, 0.0)
        glColor4f(*self.secondary_color)
        self.draw_cylinder(0.03, 0.1, 12)
        
        glPopMatrix()  # End tail
        
        glPopMatrix()  # End body
        
    def draw_sphere(self, radius, slices, stacks):
        """Draw a sphere"""
        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluSphere(quad, radius, slices, stacks)
        gluDeleteQuadric(quad)
        
    def draw_ellipsoid(self, radius_x, radius_y, radius_z, slices, stacks):
        """Draw an ellipsoid"""
        glPushMatrix()
        glScalef(radius_x, radius_y, radius_z)
        self.draw_sphere(1.0, slices, stacks)
        glPopMatrix()
        
    def draw_cylinder(self, radius, height, slices):
        """Draw a cylinder"""
        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluCylinder(quad, radius, radius, height, slices, 1)
        gluDeleteQuadric(quad)
        
    def draw_cone(self, radius, height, slices):
        """Draw a cone"""
        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluCylinder(quad, radius, 0.0, height, slices, 1)
        gluDeleteQuadric(quad)
        
    def calculate_breathing(self) -> float:
        """Calculate breathing animation offset"""
        return self.breathing_amplitude * math.sin(self.animation_time * self.breathing_speed)
        
    def calculate_tail_wag(self) -> float:
        """Calculate tail wag animation angle"""
        if self.current_state == KaiState.TAIL_WAG:
            return self.tail_wag_amplitude * math.sin(self.animation_time * self.tail_wag_speed)
        elif self.current_state == KaiState.EXCITED:
            return self.tail_wag_amplitude * 1.5 * math.sin(self.animation_time * self.tail_wag_speed * 2)
        else:
            # Subtle tail movement when idle
            return 0.05 * math.sin(self.animation_time * 0.5)
            
    def calculate_ear_twitch(self) -> float:
        """Calculate ear twitch animation"""
        if self.current_state == KaiState.IDLE:
            # Occasional ear twitch
            if int(self.animation_time) % 3 == 0:
                return self.ear_twitch_amplitude * math.sin(self.animation_time * 10)
        return 0.0
        
    def calculate_head_tilt(self) -> float:
        """Calculate head tilt animation"""
        if self.current_state == KaiState.HEAD_TILT:
            return 15.0 * math.sin(self.animation_time * 0.5)
        return 0.0
        
    def calculate_leg_bend(self) -> float:
        """Calculate leg bend animation"""
        if self.current_state == KaiState.SITTING:
            return 30.0  # Bend legs when sitting
        elif self.current_state == KaiState.WALKING:
            return 15.0 * math.sin(self.animation_time * 3.0)
        return 0.0
        
    def update_animation(self):
        """Update animation time and trigger redraw"""
        self.animation_time += 0.016  # ~60 FPS
        self.update()
        
    def change_state(self):
        """Change Kai's behavioral state"""
        states = list(KaiState)
        current_index = states.index(self.current_state)
        next_index = (current_index + 1) % len(states)
        self.current_state = states[next_index]
        print(f"Kai state changed to: {self.current_state.value}")
        
    def set_state(self, state: KaiState):
        """Manually set Kai's state"""
        self.current_state = state
        print(f"Kai state set to: {self.current_state.value}")
        
    def mousePressEvent(self, event):
        """Handle mouse press for camera rotation"""
        if event.button() == Qt.LeftButton:
            self.mouse_dragging = True
            self.last_mouse_pos = event.pos()
            
    def mouseMoveEvent(self, event):
        """Handle mouse move for camera rotation"""
        if self.mouse_dragging:
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()
            
            self.camera_rotation_y += dx * 0.5
            self.camera_rotation_x += dy * 0.5
            
            # Clamp vertical rotation
            self.camera_rotation_x = max(-30.0, min(30.0, self.camera_rotation_x))
            
            self.last_mouse_pos = event.pos()
            self.update()
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            self.mouse_dragging = False
            
    def wheelEvent(self, event):
        """Handle mouse wheel for zoom"""
        delta = event.angleDelta().y()
        self.camera_distance -= delta * 0.001
        self.camera_distance = max(1.0, min(10.0, self.camera_distance))
        self.update()


class KaiDesktopWindow(QMainWindow):
    """Main window for Kai's 3D desktop assistant"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI"""
        self.setWindowTitle("Kai - Desktop Assistant")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create 3D renderer
        self.renderer = Kai3DRenderer()
        layout.addWidget(self.renderer, 1)
        
        # Create control panel
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)
        
        # Set window flags for desktop overlay
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
    def create_control_panel(self) -> QWidget:
        """Create control panel for Kai"""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 200);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout(panel)
        
        # State selector
        state_label = QLabel("State:")
        state_label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(state_label)
        
        self.state_combo = QComboBox()
        self.state_combo.addItems([state.value for state in KaiState])
        self.state_combo.setStyleSheet("""
            QComboBox {
                background-color: #404040;
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.state_combo.currentTextChanged.connect(self.on_state_changed)
        layout.addWidget(self.state_combo)
        
        # Zoom slider
        zoom_label = QLabel("Zoom:")
        zoom_label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(zoom_label)
        
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(10)
        self.zoom_slider.setMaximum(100)
        self.zoom_slider.setValue(30)
        self.zoom_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #404040;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4ecdc4;
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
        """)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        layout.addWidget(self.zoom_slider)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff5252;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        return panel
        
    def on_state_changed(self, state_name: str):
        """Handle state change"""
        state = KaiState(state_name)
        self.renderer.set_state(state)
        
    def on_zoom_changed(self, value: int):
        """Handle zoom change"""
        self.renderer.camera_distance = value / 10.0
        self.renderer.update()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Create and show Kai window
    window = KaiDesktopWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
