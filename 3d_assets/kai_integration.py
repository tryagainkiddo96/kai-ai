"""
Kai 3D Integration Module
Integrates the 3D model with Kai's desktop assistant
"""

import sys
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Callable
from enum import Enum
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QTimer, pyqtSignal, QObject
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("Warning: PyQt5 not available")

try:
    from kai_renderer import KaiDesktopWindow, KaiState, Kai3DRenderer
    RENDERER_AVAILABLE = True
except ImportError:
    RENDERER_AVAILABLE = False
    print("Warning: kai_renderer not available")


class KaiEmotion(Enum):
    """Kai's emotional states"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    EXCITED = "excited"
    CURIOUS = "curious"
    SLEEPY = "sleepy"
    ALERT = "alert"
    PLAYFUL = "playful"


class Kai3DIntegration(QObject):
    """Integrates 3D model with Kai's desktop assistant"""
    
    # Signals for thread-safe communication
    state_changed = pyqtSignal(str)
    emotion_changed = pyqtSignal(str)
    animation_triggered = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.app = None
        self.window = None
        self.renderer = None
        self.running = False
        self.integration_thread = None
        
        # Emotion to state mapping
        self.emotion_state_map = {
            KaiEmotion.NEUTRAL: KaiState.IDLE,
            KaiEmotion.HAPPY: KaiState.TAIL_WAG,
            KaiEmotion.EXCITED: KaiState.EXCITED,
            KaiEmotion.CURIOUS: KaiState.HEAD_TILT,
            KaiEmotion.SLEEPY: KaiState.SLEEPING,
            KaiEmotion.ALERT: KaiState.IDLE,
            KaiEmotion.PLAYFUL: KaiState.TAIL_WAG,
        }
        
        # Current state
        self.current_emotion = KaiEmotion.NEUTRAL
        self.current_state = KaiState.IDLE
        
        # Callbacks
        self.on_state_change_callback: Optional[Callable] = None
        self.on_emotion_change_callback: Optional[Callable] = None
        
    def initialize(self) -> bool:
        """Initialize the 3D integration"""
        if not PYQT_AVAILABLE:
            print("Error: PyQt5 not available")
            return False
            
        if not RENDERER_AVAILABLE:
            print("Error: Kai renderer not available")
            return False
            
        # Create QApplication if it doesn't exist
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
            
        # Create Kai window
        self.window = KaiDesktopWindow()
        self.renderer = self.window.renderer
        
        # Connect signals
        self.state_changed.connect(self._handle_state_change)
        self.emotion_changed.connect(self._handle_emotion_change)
        self.animation_triggered.connect(self._handle_animation_trigger)
        
        print("✅ Kai 3D Integration initialized")
        return True
        
    def start(self):
        """Start the 3D integration"""
        if not self.window:
            print("Error: Integration not initialized")
            return
            
        self.running = True
        self.window.show()
        
        # Start integration thread for background processing
        self.integration_thread = threading.Thread(target=self._integration_loop, daemon=True)
        self.integration_thread.start()
        
        print("✅ Kai 3D Integration started")
        
    def stop(self):
        """Stop the 3D integration"""
        self.running = False
        if self.window:
            self.window.close()
        print("✅ Kai 3D Integration stopped")
        
    def _integration_loop(self):
        """Background integration loop"""
        while self.running:
            # Process any pending updates
            time.sleep(0.1)
            
    def set_emotion(self, emotion: KaiEmotion):
        """Set Kai's emotional state"""
        if emotion == self.current_emotion:
            return
            
        self.current_emotion = emotion
        self.emotion_changed.emit(emotion.value)
        
    def set_state(self, state: KaiState):
        """Set Kai's behavioral state"""
        if state == self.current_state:
            return
            
        self.current_state = state
        self.state_changed.emit(state.value)
        
    def trigger_animation(self, animation_name: str):
        """Trigger a specific animation"""
        self.animation_triggered.emit(animation_name)
        
    def _handle_state_change(self, state_name: str):
        """Handle state change signal"""
        try:
            state = KaiState(state_name)
            if self.renderer:
                self.renderer.set_state(state)
            self.current_state = state
            
            if self.on_state_change_callback:
                self.on_state_change_callback(state)
                
            print(f"Kai state changed to: {state_name}")
        except ValueError:
            print(f"Invalid state: {state_name}")
            
    def _handle_emotion_change(self, emotion_name: str):
        """Handle emotion change signal"""
        try:
            emotion = KaiEmotion(emotion_name)
            self.current_emotion = emotion
            
            # Map emotion to state
            if emotion in self.emotion_state_map:
                state = self.emotion_state_map[emotion]
                self.set_state(state)
                
            if self.on_emotion_change_callback:
                self.on_emotion_change_callback(emotion)
                
            print(f"Kai emotion changed to: {emotion_name}")
        except ValueError:
            print(f"Invalid emotion: {emotion_name}")
            
    def _handle_animation_trigger(self, animation_name: str):
        """Handle animation trigger signal"""
        try:
            state = KaiState(animation_name)
            self.set_state(state)
        except ValueError:
            print(f"Invalid animation: {animation_name}")
            
    def react_to_user_input(self, user_input: str):
        """React to user input with appropriate emotion and animation"""
        user_input_lower = user_input.lower()
        
        # Determine emotion based on user input
        if any(word in user_input_lower for word in ["hello", "hi", "hey", "greetings"]):
            self.set_emotion(KaiEmotion.HAPPY)
            self.trigger_animation("tail_wag")
        elif any(word in user_input_lower for word in ["?", "what", "how", "why", "when", "where"]):
            self.set_emotion(KaiEmotion.CURIOUS)
            self.trigger_animation("head_tilt")
        elif any(word in user_input_lower for word in ["!", "wow", "amazing", "great", "awesome"]):
            self.set_emotion(KaiEmotion.EXCITED)
            self.trigger_animation("tail_wag")
        elif any(word in user_input_lower for word in ["tired", "sleep", "rest", "quiet"]):
            self.set_emotion(KaiEmotion.SLEEPY)
            self.trigger_animation("sitting")
        elif any(word in user_input_lower for word in ["play", "fun", "game", "run"]):
            self.set_emotion(KaiEmotion.PLAYFUL)
            self.trigger_animation("tail_wag")
        elif any(word in user_input_lower for word in ["help", "problem", "issue", "error"]):
            self.set_emotion(KaiEmotion.ALERT)
            self.trigger_animation("head_tilt")
        else:
            self.set_emotion(KaiEmotion.NEUTRAL)
            self.trigger_animation("idle")
            
    def react_to_ai_response(self, ai_response: str):
        """React to AI response with appropriate emotion and animation"""
        response_lower = ai_response.lower()
        
        # Determine emotion based on AI response
        if any(word in response_lower for word in ["success", "done", "completed", "finished"]):
            self.set_emotion(KaiEmotion.HAPPY)
            self.trigger_animation("tail_wag")
        elif any(word in response_lower for word in ["error", "failed", "problem", "issue"]):
            self.set_emotion(KaiEmotion.ALERT)
            self.trigger_animation("head_tilt")
        elif any(word in response_lower for word in ["interesting", "curious", "wonder"]):
            self.set_emotion(KaiEmotion.CURIOUS)
            self.trigger_animation("head_tilt")
        elif any(word in response_lower for word in ["great", "excellent", "perfect", "amazing"]):
            self.set_emotion(KaiEmotion.EXCITED)
            self.trigger_animation("tail_wag")
        else:
            self.set_emotion(KaiEmotion.NEUTRAL)
            self.trigger_animation("idle")
            
    def react_to_system_event(self, event_type: str, event_data: Dict = None):
        """React to system events"""
        if event_type == "file_saved":
            self.set_emotion(KaiEmotion.HAPPY)
            self.trigger_animation("tail_wag")
        elif event_type == "file_error":
            self.set_emotion(KaiEmotion.ALERT)
            self.trigger_animation("head_tilt")
        elif event_type == "command_executed":
            self.set_emotion(KaiEmotion.NEUTRAL)
            self.trigger_animation("idle")
        elif event_type == "command_error":
            self.set_emotion(KaiEmotion.ALERT)
            self.trigger_animation("head_tilt")
        elif event_type == "idle_timeout":
            self.set_emotion(KaiEmotion.SLEEPY)
            self.trigger_animation("sitting")
        elif event_type == "user_active":
            self.set_emotion(KaiEmotion.HAPPY)
            self.trigger_animation("tail_wag")
        else:
            self.set_emotion(KaiEmotion.NEUTRAL)
            self.trigger_animation("idle")
            
    def set_position(self, x: int, y: int):
        """Set Kai's window position"""
        if self.window:
            self.window.move(x, y)
            
    def set_size(self, width: int, height: int):
        """Set Kai's window size"""
        if self.window:
            self.window.resize(width, height)
            
    def set_transparency(self, alpha: float):
        """Set Kai's window transparency (0.0 to 1.0)"""
        if self.window:
            self.window.setWindowOpacity(alpha)
            
    def set_always_on_top(self, on_top: bool):
        """Set whether Kai's window stays on top"""
        if self.window:
            if on_top:
                self.window.setWindowFlags(self.window.windowFlags() | Qt.WindowStaysOnTopHint)
            else:
                self.window.setWindowFlags(self.window.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.window.show()
            
    def register_state_change_callback(self, callback: Callable):
        """Register callback for state changes"""
        self.on_state_change_callback = callback
        
    def register_emotion_change_callback(self, callback: Callable):
        """Register callback for emotion changes"""
        self.on_emotion_change_callback = callback


class Kai3DManager:
    """Manages Kai's 3D integration lifecycle"""
    
    def __init__(self):
        self.integration = None
        self.running = False
        
    def start(self) -> bool:
        """Start Kai's 3D integration"""
        if self.running:
            print("Kai 3D integration already running")
            return True
            
        self.integration = Kai3DIntegration()
        
        if not self.integration.initialize():
            print("Failed to initialize Kai 3D integration")
            return False
            
        self.integration.start()
        self.running = True
        
        print("✅ Kai 3D Manager started")
        return True
        
    def stop(self):
        """Stop Kai's 3D integration"""
        if not self.running:
            return
            
        if self.integration:
            self.integration.stop()
            
        self.running = False
        print("✅ Kai 3D Manager stopped")
        
    def get_integration(self) -> Optional[Kai3DIntegration]:
        """Get the integration instance"""
        return self.integration


# Global instance
_kai_3d_manager = None


def get_kai_3d_manager() -> Kai3DManager:
    """Get the global Kai 3D manager instance"""
    global _kai_3d_manager
    if _kai_3d_manager is None:
        _kai_3d_manager = Kai3DManager()
    return _kai_3d_manager


def start_kai_3d() -> bool:
    """Start Kai's 3D integration"""
    manager = get_kai_3d_manager()
    return manager.start()


def stop_kai_3d():
    """Stop Kai's 3D integration"""
    manager = get_kai_3d_manager()
    manager.stop()


def react_to_user_input(user_input: str):
    """React to user input"""
    manager = get_kai_3d_manager()
    if manager.running and manager.integration:
        manager.integration.react_to_user_input(user_input)


def react_to_ai_response(ai_response: str):
    """React to AI response"""
    manager = get_kai_3d_manager()
    if manager.running and manager.integration:
        manager.integration.react_to_ai_response(ai_response)


def react_to_system_event(event_type: str, event_data: Dict = None):
    """React to system event"""
    manager = get_kai_3d_manager()
    if manager.running and manager.integration:
        manager.integration.react_to_system_event(event_type, event_data)


def main():
    """Test the 3D integration"""
    print("Testing Kai 3D Integration...")
    
    # Start integration
    if not start_kai_3d():
        print("Failed to start Kai 3D integration")
        return
        
    # Test reactions
    print("\nTesting reactions...")
    
    react_to_user_input("Hello Kai!")
    time.sleep(2)
    
    react_to_user_input("What is the weather?")
    time.sleep(2)
    
    react_to_ai_response("Task completed successfully!")
    time.sleep(2)
    
    react_to_system_event("file_saved")
    time.sleep(2)
    
    react_to_user_input("Let's play a game!")
    time.sleep(2)
    
    # Keep running
    print("\nKai 3D integration running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping Kai 3D integration...")
        stop_kai_3d()
        print("Done!")


if __name__ == "__main__":
    main()
