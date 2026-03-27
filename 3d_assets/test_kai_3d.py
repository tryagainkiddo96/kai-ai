"""
Test script for Kai 3D model
Tests rendering, animations, and integration
"""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_rigger():
    """Test the rigger module"""
    print("=" * 50)
    print("Testing Kai Rigger")
    print("=" * 50)
    
    try:
        from kai_rigger import KaiModelRigger
        
        model_path = Path(__file__).parent / "kai_model.glb"
        
        if not model_path.exists():
            print(f"[FAIL] Model file not found: {model_path}")
            return False
            
        rigger = KaiModelRigger(str(model_path))
        
        # Test model loading
        print("\n1. Testing model loading...")
        if rigger.load_model():
            print("[OK] Model loaded successfully")
        else:
            print("[FAIL] Failed to load model")
            return False
            
        # Test model analysis
        print("\n2. Testing model analysis...")
        analysis = rigger.analyze_model()
        print(f"   Meshes: {len(analysis['meshes'])}")
        print(f"   Nodes: {len(analysis['nodes'])}")
        print(f"   Has Skeleton: {analysis['has_skeleton']}")
        print(f"   Has Animations: {analysis['has_animations']}")
        print("[OK] Model analysis completed")
        
        # Test skeleton creation
        print("\n3. Testing skeleton creation...")
        if rigger.create_shiba_skeleton():
            print("[OK] Skeleton created successfully")
        else:
            print("[FAIL] Failed to create skeleton")
            return False
            
        # Test animation creation
        print("\n4. Testing animation creation...")
        if rigger.create_idle_animation():
            print("[OK] Idle animation created")
        else:
            print("[FAIL] Failed to create idle animation")
            
        if rigger.create_tail_wag_animation():
            print("[OK] Tail wag animation created")
        else:
            print("[FAIL] Failed to create tail wag animation")
            
        if rigger.create_sitting_animation():
            print("[OK] Sitting animation created")
        else:
            print("[FAIL] Failed to create sitting animation")
            
        if rigger.create_head_tilt_animation():
            print("[OK] Head tilt animation created")
        else:
            print("[FAIL] Failed to create head tilt animation")
            
        # Test model saving
        print("\n5. Testing model saving...")
        output_path = Path(__file__).parent / "kai_model_rigged.glb"
        if rigger.save_model(str(output_path)):
            print(f"[OK] Rigged model saved to: {output_path}")
        else:
            print("[FAIL] Failed to save rigged model")
            return False
            
        print("\n[OK] All rigger tests passed!")
        return True
        
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Test error: {e}")
        return False


def test_renderer():
    """Test the renderer module"""
    print("\n" + "=" * 50)
    print("Testing Kai Renderer")
    print("=" * 50)
    
    try:
        from kai_renderer import Kai3DRenderer, KaiState
        
        print("\n1. Testing renderer initialization...")
        renderer = Kai3DRenderer()
        print("[OK] Renderer initialized")
        
        print("\n2. Testing state management...")
        for state in KaiState:
            renderer.set_state(state)
            print(f"   Set state: {state.value}")
        print("[OK] State management working")
        
        print("\n3. Testing animation calculations...")
        renderer.animation_time = 0.0
        breathing = renderer.calculate_breathing()
        tail_wag = renderer.calculate_tail_wag()
        ear_twitch = renderer.calculate_ear_twitch()
        head_tilt = renderer.calculate_head_tilt()
        leg_bend = renderer.calculate_leg_bend()
        
        print(f"   Breathing offset: {breathing:.4f}")
        print(f"   Tail wag angle: {tail_wag:.4f}")
        print(f"   Ear twitch: {ear_twitch:.4f}")
        print(f"   Head tilt: {head_tilt:.4f}")
        print(f"   Leg bend: {leg_bend:.4f}")
        print("[OK] Animation calculations working")
        
        print("\n4. Testing state-specific animations...")
        renderer.set_state(KaiState.TAIL_WAG)
        tail_wag = renderer.calculate_tail_wag()
        print(f"   Tail wag (excited): {tail_wag:.4f}")
        
        renderer.set_state(KaiState.SITTING)
        leg_bend = renderer.calculate_leg_bend()
        print(f"   Leg bend (sitting): {leg_bend:.4f}")
        
        renderer.set_state(KaiState.HEAD_TILT)
        head_tilt = renderer.calculate_head_tilt()
        print(f"   Head tilt (curious): {head_tilt:.4f}")
        print("[OK] State-specific animations working")
        
        print("\n[OK] All renderer tests passed!")
        return True
        
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Test error: {e}")
        return False


def test_integration():
    """Test the integration module"""
    print("\n" + "=" * 50)
    print("Testing Kai Integration")
    print("=" * 50)
    
    try:
        from kai_integration import Kai3DIntegration, KaiEmotion, KaiState
        
        print("\n1. Testing integration initialization...")
        integration = Kai3DIntegration()
        print("[OK] Integration initialized")
        
        print("\n2. Testing emotion mapping...")
        for emotion in KaiEmotion:
            integration.set_emotion(emotion)
            print(f"   Set emotion: {emotion.value}")
        print("[OK] Emotion mapping working")
        
        print("\n3. Testing state mapping...")
        for state in KaiState:
            integration.set_state(state)
            print(f"   Set state: {state.value}")
        print("[OK] State mapping working")
        
        print("\n4. Testing user input reactions...")
        test_inputs = [
            "Hello Kai!",
            "What is the weather?",
            "This is amazing!",
            "I'm tired",
            "Let's play a game!",
            "Help me with this problem"
        ]
        
        for user_input in test_inputs:
            integration.react_to_user_input(user_input)
            print(f"   Reacted to: '{user_input}'")
            time.sleep(0.1)
        print("[OK] User input reactions working")
        
        print("\n5. Testing AI response reactions...")
        test_responses = [
            "Task completed successfully!",
            "Error: File not found",
            "Interesting question...",
            "Great job!",
            "Processing your request..."
        ]
        
        for ai_response in test_responses:
            integration.react_to_ai_response(ai_response)
            print(f"   Reacted to: '{ai_response}'")
            time.sleep(0.1)
        print("[OK] AI response reactions working")
        
        print("\n6. Testing system event reactions...")
        test_events = [
            "file_saved",
            "file_error",
            "command_executed",
            "command_error",
            "idle_timeout",
            "user_active"
        ]
        
        for event in test_events:
            integration.react_to_system_event(event)
            print(f"   Reacted to: {event}")
            time.sleep(0.1)
        print("[OK] System event reactions working")
        
        print("\n[OK] All integration tests passed!")
        return True
        
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Test error: {e}")
        return False


def test_dependencies():
    """Test required dependencies"""
    print("=" * 50)
    print("Testing Dependencies")
    print("=" * 50)
    
    dependencies = [
        ("PyQt5", "PyQt5"),
        ("numpy", "numpy"),
        ("pygltflib", "pygltflib"),
        ("trimesh", "trimesh"),
        ("PyOpenGL", "OpenGL"),
    ]
    
    all_ok = True
    
    for package_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"[OK] {package_name} is installed")
        except ImportError:
            print(f"[FAIL] {package_name} is NOT installed")
            all_ok = False
            
    return all_ok


def main():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("Kai 3D Model Test Suite")
    print("=" * 50)
    
    # Test dependencies first
    if not test_dependencies():
        print("\n[FAIL] Some dependencies are missing. Please install them:")
        print("   pip install pygltflib numpy trimesh pyrender PyOpenGL PyOpenGL_accelerate")
        return
        
    # Run tests
    results = {
        "Rigger": test_rigger(),
        "Renderer": test_renderer(),
        "Integration": test_integration()
    }
    
    # Print summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "[PASSED]" if passed else "[FAILED]"
        print(f"{test_name}: {status}")
        
    all_passed = all(results.values())
    
    if all_passed:
        print("\n[OK] All tests passed!")
    else:
        print("\n[FAIL] Some tests failed!")
        
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
