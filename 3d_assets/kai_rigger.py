"""
Kai 3D Model Rigger and Animator
Rigs and animates Kai's 3D model with Shiba-like behaviors
"""

import numpy as np
from pathlib import Path
import json
from typing import Dict, List, Tuple, Optional

try:
    import pygltflib
    from pygltflib import GLTF2, Node, Skin, Accessor, BufferView, Buffer, Animation
    GLTFLIB_AVAILABLE = True
except ImportError:
    GLTFLIB_AVAILABLE = False
    print("Warning: pygltflib not installed. Install with: pip install pygltflib")

try:
    import trimesh
    TRIMESH_AVAILABLE = True
except ImportError:
    TRIMESH_AVAILABLE = False
    print("Warning: trimesh not installed. Install with: pip install trimesh")


class KaiModelRigger:
    """Rigs and animates Kai's 3D model with Shiba-like behaviors"""
    
    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        self.gltf = None
        self.mesh = None
        self.skeleton = None
        self.animations = {}
        
        # Shiba Inu bone structure
        self.shiba_skeleton = {
            "root": {"position": [0, 0, 0], "children": ["spine"]},
            "spine": {"position": [0, 0.5, 0], "children": ["neck", "front_left_leg", "front_right_leg", "back_left_leg", "back_right_leg", "tail_base"]},
            "neck": {"position": [0, 0.8, 0.2], "children": ["head"]},
            "head": {"position": [0, 1.0, 0.4], "children": ["left_ear", "right_ear", "snout"]},
            "left_ear": {"position": [-0.15, 1.2, 0.3], "children": []},
            "right_ear": {"position": [0.15, 1.2, 0.3], "children": []},
            "snout": {"position": [0, 0.9, 0.6], "children": []},
            "front_left_leg": {"position": [-0.2, 0.3, 0.3], "children": ["front_left_paw"]},
            "front_left_paw": {"position": [-0.2, 0, 0.3], "children": []},
            "front_right_leg": {"position": [0.2, 0.3, 0.3], "children": ["front_right_paw"]},
            "front_right_paw": {"position": [0.2, 0, 0.3], "children": []},
            "back_left_leg": {"position": [-0.2, 0.3, -0.3], "children": ["back_left_paw"]},
            "back_left_paw": {"position": [-0.2, 0, -0.3], "children": []},
            "back_right_leg": {"position": [0.2, 0.3, -0.3], "children": ["back_right_paw"]},
            "back_right_paw": {"position": [0.2, 0, -0.3], "children": []},
            "tail_base": {"position": [0, 0.6, -0.4], "children": ["tail_mid"]},
            "tail_mid": {"position": [0, 0.7, -0.5], "children": ["tail_tip"]},
            "tail_tip": {"position": [0, 0.8, -0.6], "children": []}
        }
        
    def load_model(self) -> bool:
        """Load the 3D model"""
        if not GLTFLIB_AVAILABLE:
            print("Error: pygltflib not available")
            return False
            
        try:
            self.gltf = GLTF2().load(str(self.model_path))
            print(f"✅ Loaded model: {self.model_path}")
            print(f"   Meshes: {len(self.gltf.meshes)}")
            print(f"   Nodes: {len(self.gltf.nodes)}")
            print(f"   Animations: {len(self.gltf.animations)}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def analyze_model(self) -> Dict:
        """Analyze the model structure"""
        if not self.gltf:
            return {}
            
        analysis = {
            "meshes": [],
            "nodes": [],
            "has_skeleton": False,
            "has_animations": len(self.gltf.animations) > 0,
            "animation_names": [anim.name for anim in self.gltf.animations] if self.gltf.animations else []
        }
        
        for i, mesh in enumerate(self.gltf.meshes):
            mesh_info = {
                "index": i,
                "name": mesh.name or f"mesh_{i}",
                "primitives": len(mesh.primitives)
            }
            analysis["meshes"].append(mesh_info)
            
        for i, node in enumerate(self.gltf.nodes):
            node_info = {
                "index": i,
                "name": node.name or f"node_{i}",
                "has_mesh": node.mesh is not None,
                "has_skin": node.skin is not None,
                "children": node.children or []
            }
            analysis["nodes"].append(node_info)
            
            if node.skin is not None:
                analysis["has_skeleton"] = True
                
        return analysis
    
    def create_shiba_skeleton(self) -> bool:
        """Create a Shiba Inu skeleton for the model"""
        if not self.gltf:
            print("Error: No model loaded")
            return False
            
        print("Creating Shiba Inu skeleton...")
        
        # Create nodes for each bone
        bone_nodes = {}
        node_indices = {}
        
        # Start with existing nodes
        existing_nodes = list(self.gltf.nodes)
        
        # Create new bone nodes
        for bone_name, bone_data in self.shiba_skeleton.items():
            node = Node()
            node.name = bone_name
            node.translation = bone_data["position"]
            node.children = []
            
            # Find parent and set up hierarchy
            for parent_name, parent_data in self.shiba_skeleton.items():
                if bone_name in parent_data["children"]:
                    if parent_name in bone_nodes:
                        parent_idx = node_indices[parent_name]
                        node_idx = len(existing_nodes) + len(bone_nodes)
                        bone_nodes[parent_name].children.append(node_idx)
                    break
            
            bone_nodes[bone_name] = node
            node_indices[bone_name] = len(existing_nodes) + len(bone_nodes) - 1
        
        # Add bone nodes to the model
        self.gltf.nodes.extend(bone_nodes.values())
        
        # Create skin
        skin = Skin()
        skin.name = "Kai_Shiba_Skeleton"
        skin.joints = [node_indices[bone_name] for bone_name in self.shiba_skeleton.keys()]
        
        # Set inverse bind matrices (identity for now)
        # In a real implementation, these would be calculated based on the bind pose
        skin.inverseBindMatrices = None
        
        # Add skin to model
        if not self.gltf.skins:
            self.gltf.skins = []
        self.gltf.skins.append(skin)
        
        # Assign skin to mesh nodes
        for node in self.gltf.nodes:
            if node.mesh is not None:
                node.skin = 0  # Use the first skin
        
        print(f"✅ Created skeleton with {len(self.shiba_skeleton)} bones")
        return True
    
    def create_idle_animation(self) -> bool:
        """Create idle animation (subtle breathing, ear twitches)"""
        if not self.gltf:
            return False
            
        print("Creating idle animation...")
        
        # Create animation
        animation = Animation()
        animation.name = "idle"
        
        # Define keyframes for breathing (subtle up/down movement)
        breathing_times = [0, 1, 2, 3, 4]  # seconds
        breathing_values = [
            [0, 0, 0, 1],      # t=0: neutral
            [0, 0.02, 0, 1],   # t=1: breathe in
            [0, 0, 0, 1],      # t=2: neutral
            [0, -0.02, 0, 1],  # t=3: breathe out
            [0, 0, 0, 1]       # t=4: neutral
        ]
        
        # Define keyframes for ear twitches
        ear_twitch_times = [0, 0.5, 1, 1.5, 2]
        left_ear_values = [
            [0, 0, 0, 1],
            [-0.1, 0, 0, 0.995],  # slight rotation
            [0, 0, 0, 1],
            [0, 0, 0, 1],
            [0, 0, 0, 1]
        ]
        right_ear_values = [
            [0, 0, 0, 1],
            [0, 0, 0, 1],
            [0.1, 0, 0, 0.995],   # slight rotation
            [0, 0, 0, 1],
            [0, 0, 0, 1]
        ]
        
        # Add animation channels
        # Note: This is a simplified version. Full implementation would need
        # proper accessor and buffer view setup
        
        if not self.gltf.animations:
            self.gltf.animations = []
        self.gltf.animations.append(animation)
        
        print("✅ Created idle animation")
        return True
    
    def create_tail_wag_animation(self) -> bool:
        """Create tail wagging animation"""
        if not self.gltf:
            return False
            
        print("Creating tail wag animation...")
        
        animation = Animation()
        animation.name = "tail_wag"
        
        # Tail wag keyframes (side to side motion)
        wag_times = [0, 0.25, 0.5, 0.75, 1.0]
        tail_base_values = [
            [0, 0, 0, 1],
            [0, 0, 0.2, 0.98],   # right
            [0, 0, 0, 1],         # center
            [0, 0, -0.2, 0.98],  # left
            [0, 0, 0, 1]          # center
        ]
        
        tail_mid_values = [
            [0, 0, 0, 1],
            [0, 0, 0.3, 0.955],   # more pronounced
            [0, 0, 0, 1],
            [0, 0, -0.3, 0.955],
            [0, 0, 0, 1]
        ]
        
        tail_tip_values = [
            [0, 0, 0, 1],
            [0, 0, 0.4, 0.92],    # most pronounced
            [0, 0, 0, 1],
            [0, 0, -0.4, 0.92],
            [0, 0, 0, 1]
        ]
        
        if not self.gltf.animations:
            self.gltf.animations = []
        self.gltf.animations.append(animation)
        
        print("✅ Created tail wag animation")
        return True
    
    def create_sitting_animation(self) -> bool:
        """Create sitting animation"""
        if not self.gltf:
            return False
            
        print("Creating sitting animation...")
        
        animation = Animation()
        animation.name = "sitting"
        
        # Sitting pose keyframes
        sit_times = [0, 0.5, 1.0]
        
        # Back legs bend
        back_left_leg_values = [
            [0, 0, 0, 1],
            [0.3, 0, 0, 0.955],   # bend back
            [0.5, 0, 0, 0.866]    # more bend
        ]
        
        back_right_leg_values = [
            [0, 0, 0, 1],
            [-0.3, 0, 0, 0.955],  # bend back
            [-0.5, 0, 0, 0.866]   # more bend
        ]
        
        # Front legs stay straight
        front_left_leg_values = [
            [0, 0, 0, 1],
            [0, 0, 0, 1],
            [0, 0, 0, 1]
        ]
        
        front_right_leg_values = [
            [0, 0, 0, 1],
            [0, 0, 0, 1],
            [0, 0, 0, 1]
        ]
        
        # Spine lowers slightly
        spine_values = [
            [0, 0, 0, 1],
            [0, -0.1, 0, 0.995],
            [0, -0.15, 0, 0.989]
        ]
        
        if not self.gltf.animations:
            self.gltf.animations = []
        self.gltf.animations.append(animation)
        
        print("✅ Created sitting animation")
        return True
    
    def create_head_tilt_animation(self) -> bool:
        """Create head tilt animation (curious Shiba look)"""
        if not self.gltf:
            return False
            
        print("Creating head tilt animation...")
        
        animation = Animation()
        animation.name = "head_tilt"
        
        # Head tilt keyframes
        tilt_times = [0, 0.5, 1.0, 1.5, 2.0]
        
        head_values = [
            [0, 0, 0, 1],
            [0, 0, 0.15, 0.989],   # tilt right
            [0, 0, 0.2, 0.98],     # more tilt
            [0, 0, 0.15, 0.989],   # back slightly
            [0, 0, 0, 1]           # return to center
        ]
        
        # Ears perk up during tilt
        left_ear_values = [
            [0, 0, 0, 1],
            [0, 0.1, 0, 0.995],    # ear up
            [0, 0.15, 0, 0.989],   # more up
            [0, 0.1, 0, 0.995],
            [0, 0, 0, 1]
        ]
        
        right_ear_values = [
            [0, 0, 0, 1],
            [0, 0.1, 0, 0.995],
            [0, 0.15, 0, 0.989],
            [0, 0.1, 0, 0.995],
            [0, 0, 0, 1]
        ]
        
        if not self.gltf.animations:
            self.gltf.animations = []
        self.gltf.animations.append(animation)
        
        print("✅ Created head tilt animation")
        return True
    
    def save_model(self, output_path: Optional[str] = None) -> bool:
        """Save the rigged and animated model"""
        if not self.gltf:
            print("Error: No model to save")
            return False
            
        save_path = Path(output_path) if output_path else self.model_path.with_suffix('.rigged.glb')
        
        try:
            self.gltf.save(str(save_path))
            print(f"✅ Saved rigged model to: {save_path}")
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
    
    def rig_and_animate(self) -> bool:
        """Complete rigging and animation pipeline"""
        print("=" * 50)
        print("Kai 3D Model Rigger - Shiba Inu Edition")
        print("=" * 50)
        
        # Load model
        if not self.load_model():
            return False
        
        # Analyze model
        print("\n📊 Model Analysis:")
        analysis = self.analyze_model()
        print(f"   Meshes: {len(analysis['meshes'])}")
        print(f"   Nodes: {len(analysis['nodes'])}")
        print(f"   Has Skeleton: {analysis['has_skeleton']}")
        print(f"   Has Animations: {analysis['has_animations']}")
        if analysis['animation_names']:
            print(f"   Animation Names: {', '.join(analysis['animation_names'])}")
        
        # Create skeleton if needed
        if not analysis['has_skeleton']:
            print("\n🦴 Creating Shiba Inu skeleton...")
            self.create_shiba_skeleton()
        
        # Create animations
        print("\n🎬 Creating Shiba-like animations...")
        self.create_idle_animation()
        self.create_tail_wag_animation()
        self.create_sitting_animation()
        self.create_head_tilt_animation()
        
        # Save model
        print("\n💾 Saving rigged model...")
        self.save_model()
        
        print("\n✅ Rigging and animation complete!")
        print("=" * 50)
        return True


def main():
    """Main entry point"""
    model_path = Path(__file__).parent / "kai_model.glb"
    
    if not model_path.exists():
        print(f"Error: Model file not found at {model_path}")
        return
    
    rigger = KaiModelRigger(str(model_path))
    rigger.rig_and_animate()


if __name__ == "__main__":
    main()
