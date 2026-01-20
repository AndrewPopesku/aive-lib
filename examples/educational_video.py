"""
Educational video creation example.

This example demonstrates:
- Using the educational landscape template
- Syncing visuals with audio narration
- Creating chapter markers with text
- Building a complete lesson video
"""

from aive import VideoProjectManager

def create_lesson_video():
    """Create an educational video with synced narration and visuals."""
    
    manager = VideoProjectManager()
    
    # Load educational template (white background, 1920x1080)
    print("Loading educational template...")
    manager.load_template("edu_landscape")
    
    # Introduction section (0-10s)
    print("Adding introduction...")
    intro_text = manager.add_clip(
        clip_type="text",
        source="Lesson 1: Understanding Video Composition",
        duration=5.0,
        start=0.0,
        track_layer=1
    )
    
    # Main content - Visual #1 (10-30s)
    print("Adding first visual...")
    visual_1 = manager.add_clip(
        clip_type="image",
        source="https://www.pexels.com/download/video/6994624/",
        duration=20.0,
        start=10.0,
        track_layer=1
    )
    
    # Explanation text for visual #1
    explanation_1 = manager.add_clip(
        clip_type="text",
        source="Key Concept: Layered composition allows multiple elements",
        duration=15.0,
        start=10.0,
        track_layer=2
    )
    
    # Main content - Visual #2 (30-50s)
    print("Adding second visual...")
    visual_2 = manager.add_clip(
        clip_type="image",
        source="https://images.pexels.com/photos/7310202/pexels-photo-7310202.jpeg?cs=srgb&dl=pexels-rdne-7310202.jpg&fm=jpg",
        duration=20.0,
        start=30.0,
        track_layer=1
    )
    
    explanation_2 = manager.add_clip(
        clip_type="text",
        source="Example: Text overlays on layer 2",
        duration=15.0,
        start=30.0,
        track_layer=2
    )
    
    # Add narration audio (spans entire video)
    print("Adding narration...")
    audio = manager.add_clip(
        clip_type="audio",
        source="./assets/music.mp3",
        duration=50.0,
        start=0.0,
        track_layer=3
    )
    
    # Apply smooth transitions
    print("Adding transitions...")
    for clip in [intro_text, explanation_1, explanation_2]:
        manager.apply_action(
            "apply_effect",
            clip_id=clip.id,
            effect_type="fade",
            parameters={"fade_in": 0.5, "fade_out": 0.5}
        )
    
    # Adjust audio volume for clarity
    manager.apply_action(
        "set_volume",
        clip_id=audio.id,
        volume=1.0
    )
    
    # Project summary
    info = manager.get_project_info()
    print(f"\nLesson video ready:")
    print(f"  Total duration: {info['total_duration']}s")
    print(f"  Clips: {info['num_clips']}")
    print(f"  Layers used: {max(c['layer'] for c in info['clips'])}")
    
    # Save for future editing
    print("\nSaving project...")
    manager.save_project("lesson_1.json")
    
    # Render with high quality
    print("Rendering video (this may take a while)...")
    manager.render("lesson_1_final.mp4", preset="slow")
    print("Educational video complete! 📚")

if __name__ == "__main__":
    create_lesson_video()
