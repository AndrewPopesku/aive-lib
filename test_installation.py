#!/usr/bin/env python3
"""
Quick test to verify Moviely installation.
This creates a simple text-only video without requiring external media files.
"""

from moviely import VideoProjectManager
import sys

def test_installation():
    """Test basic Moviely functionality."""
    
    print("Testing Moviely installation...\n")
    
    try:
        # Test 1: Create manager
        print("✓ Creating VideoProjectManager...")
        manager = VideoProjectManager(storage_backend="memory")
        
        # Test 2: Create project
        print("✓ Creating project...")
        manager.create_project(
            name="Installation Test",
            resolution=(1280, 720),
            fps=30
        )
        
        # Test 3: Add text clip (no external files needed)
        print("✓ Adding text clip...")
        manager.add_clip(
            clip_type="text",
            source="Moviely is working!",
            duration=5.0,
            start=0.0
        )
        
        # Test 4: Apply action
        print("✓ Applying action...")
        clip_id = manager.project.clips[0].id
        manager.apply_action(
            "apply_effect",
            clip_id=clip_id,
            effect_type="fade",
            parameters={"fade_in": 1.0}
        )
        
        # Test 5: Get project info
        print("✓ Getting project info...")
        info = manager.get_project_info()
        
        # Test 6: List actions and templates
        print("✓ Listing actions and templates...")
        actions = manager.list_actions()
        templates = manager.list_templates()
        
        print("\n" + "="*50)
        print("✅ All tests passed!")
        print("="*50)
        print(f"\nProject Info:")
        print(f"  Name: {info['name']}")
        print(f"  Resolution: {info['resolution']}")
        print(f"  FPS: {info['fps']}")
        print(f"  Clips: {info['num_clips']}")
        print(f"  Duration: {info['total_duration']}s")
        print(f"\nAvailable Actions: {len(actions)}")
        print(f"Available Templates: {len(templates)}")
        print("\nMoviely is ready to use! 🎬")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_installation()
    sys.exit(0 if success else 1)
