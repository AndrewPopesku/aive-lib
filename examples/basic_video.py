"""
Basic video composition example.

This example demonstrates:
- Creating a project from scratch
- Adding multiple clips
- Applying effects
- Rendering the final video
"""

from moviely import VideoProjectManager

def main():
    # Initialize manager
    manager = VideoProjectManager()
    
    # Create a new project
    print("Creating project...")
    manager.create_project(
        name="Basic Video",
        resolution=(1920, 1080),
        fps=30
    )
    
    # Add a video clip from Pexels
    print("Adding video clip from Pexels...")
    video_clip = manager.add_clip(
        clip_type="video",
        source="https://videos.pexels.com/video-files/3571264/3571264-uhd_2560_1440_30fps.mp4",
        duration=10.0,
        start=0.0
    )
    
    # Add a text overlay
    print("Adding text overlay...")
    text_clip = manager.add_clip(
        clip_type="text",
        source="Welcome to Moviely!",
        duration=5.0,
        start=2.0,
        track_layer=2
    )
    
    # Apply fade effect to text
    print("Applying fade effect...")
    manager.apply_action(
        "apply_effect",
        clip_id=text_clip.id,
        effect_type="fade",
        parameters={"fade_in": 0.5, "fade_out": 0.5}
    )
    
    # Get project info
    info = manager.get_project_info()
    print(f"\nProject Info:")
    print(f"  Name: {info['name']}")
    print(f"  Resolution: {info['resolution']}")
    print(f"  Total clips: {info['num_clips']}")
    print(f"  Duration: {info['total_duration']}s")
    
    # Save project
    print("\nSaving project...")
    manager.save_project("basic_video.json")
    
    # Render video
    print("Rendering video...")
    output = manager.render("output_basic.mp4", preset="fast")
    print(f"Video rendered to: {output}")

if __name__ == "__main__":
    main()
