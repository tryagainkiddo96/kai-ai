# Kai 3D Assets

This directory contains the 3D model, rigging, and rendering components for Kai's desktop assistant.

## Overview

Kai's 3D model is designed to act as his physical body while you're on your computer. The model features Shiba Inu-like behaviors and animations that reflect Kai's emotional state and responses.

## Files

- [`kai_model.glb`](kai_model.glb) - The original 3D model file (GLB format)
- [`kai_rigger.py`](kai_rigger.py) - Script to rig the model with Shiba Inu skeleton
- [`kai_renderer.py`](kai_renderer.py) - OpenGL renderer for displaying the 3D model
- [`kai_integration.py`](kai_integration.py) - Integration module for connecting with Kai's desktop assistant

## Features

### Shiba Inu Behaviors

The 3D model includes the following Shiba Inu-like behaviors:

- **Idle** - Subtle breathing and occasional ear twitches
- **Sitting** - Kai sits down with proper leg positioning
- **Tail Wagging** - Happy tail wagging animation
- **Head Tilt** - Curious head tilt (classic Shiba look)
- **Excited** - Fast tail wagging and energetic movements
- **Sleeping** - Relaxed sleeping pose

### Emotional States

Kai's 3D model reacts to different emotional states:

- **Neutral** - Default idle state
- **Happy** - Tail wagging and perky ears
- **Excited** - Fast tail wagging and energetic movements
- **Curious** - Head tilt and alert posture
- **Sleepy** - Relaxed sitting position
- **Alert** - Alert posture with head tilt
- **Playful** - Energetic tail wagging

## Installation

### Prerequisites

Install the required Python packages:

```bash
pip install pygltflib numpy trimesh pyrender PyOpenGL PyOpenGL_accelerate
```

### Running the Rigger

To rig the 3D model with Shiba Inu skeleton and animations:

```bash
python kai_rigger.py
```

This will:
1. Load the original 3D model
2. Analyze the model structure
3. Create a Shiba Inu skeleton
4. Add animations (idle, tail wag, sitting, head tilt)
5. Save the rigged model

### Running the Renderer

To display Kai's 3D model on your desktop:

```bash
python kai_renderer.py
```

### Running the Integration

To test the integration with Kai's desktop assistant:

```bash
python kai_integration.py
```

## Usage

### Starting Kai's 3D Model

```python
from kai_integration import start_kai_3d, react_to_user_input, react_to_ai_response

# Start Kai's 3D integration
start_kai_3d()

# React to user input
react_to_user_input("Hello Kai!")

# React to AI response
react_to_ai_response("Task completed successfully!")
```

### Setting Emotional States

```python
from kai_integration import get_kai_3d_manager, KaiEmotion

manager = get_kai_3d_manager()
integration = manager.get_integration()

# Set emotional state
integration.set_emotion(KaiEmotion.HAPPY)
integration.set_emotion(KaiEmotion.CURIOUS)
integration.set_emotion(KaiEmotion.EXCITED)
```

### Setting Behavioral States

```python
from kai_integration import get_kai_3d_manager, KaiState

manager = get_kai_3d_manager()
integration = manager.get_integration()

# Set behavioral state
integration.set_state(KaiState.SITTING)
integration.set_state(KaiState.TAIL_WAG)
integration.set_state(KaiState.HEAD_TILT)
```

### Reacting to System Events

```python
from kai_integration import react_to_system_event

# React to file saved
react_to_system_event("file_saved")

# React to file error
react_to_system_event("file_error")

# React to command executed
react_to_system_event("command_executed")

# React to idle timeout
react_to_system_event("idle_timeout")
```

## Customization

### Colors

You can customize Kai's colors in [`kai_renderer.py`](kai_renderer.py):

```python
# Shiba Inu colors
self.primary_color = (0.9, 0.7, 0.4, 1.0)  # Orange/cream
self.secondary_color = (1.0, 1.0, 1.0, 1.0)  # White
self.accent_color = (0.2, 0.2, 0.2, 1.0)  # Black (nose, eyes)
```

### Animation Parameters

Adjust animation parameters in [`kai_renderer.py`](kai_renderer.py):

```python
# Animation parameters
self.breathing_amplitude = 0.02
self.breathing_speed = 1.0
self.tail_wag_speed = 3.0
self.tail_wag_amplitude = 0.3
self.ear_twitch_amplitude = 0.15
```

### Window Position and Size

Set Kai's window position and size:

```python
from kai_integration import get_kai_3d_manager

manager = get_kai_3d_manager()
integration = manager.get_integration()

# Set position
integration.set_position(100, 100)

# Set size
integration.set_size(400, 300)

# Set transparency
integration.set_transparency(0.8)

# Set always on top
integration.set_always_on_top(True)
```

## Integration with Kai's Desktop Assistant

The 3D model integrates with Kai's desktop assistant through the [`kai_integration.py`](kai_integration.py) module. This module provides:

- Automatic emotional state detection based on user input
- Automatic emotional state detection based on AI responses
- System event reactions (file saved, command executed, etc.)
- Thread-safe communication between the UI and 3D model
- Callback registration for state and emotion changes

## Troubleshooting

### Model Not Displaying

1. Ensure PyOpenGL is installed: `pip install PyOpenGL PyOpenGL_accelerate`
2. Check that your graphics drivers are up to date
3. Verify the model file exists at `kai_model.glb`

### Animations Not Working

1. Ensure pygltflib is installed: `pip install pygltflib`
2. Run the rigger script to add animations: `python kai_rigger.py`
3. Check the console for error messages

### Integration Not Working

1. Ensure PyQt5 is installed: `pip install PyQt5`
2. Check that all required modules are imported
3. Verify the integration is started: `start_kai_3d()`

## Future Enhancements

- [ ] Load and render actual GLB model geometry
- [ ] Add more complex animations (walking, running, jumping)
- [ ] Add sound effects (barking, panting)
- [ ] Add interactive elements (click to pet, drag to move)
- [ ] Add weather-based reactions (shiver when cold, pant when hot)
- [ ] Add time-based behaviors (sleepy at night, active during day)
- [ ] Add user preference learning (favorite positions, behaviors)

## License

This project is part of the Kai desktop assistant.
