"""
TikTok video automation example.

This example shows how to:
- Use the TikTok vertical template
- Crop landscape video to vertical
- Add trendy text overlays
- Apply effects for engagement
"""

from aive import VideoProjectManager

def create_tiktok_video(input_video: str, output_path: str = "tiktok_output.mp4"):
    """Create a TikTok-ready video from landscape footage."""
    
    # Initialize with memory storage (no file persistence)
    manager = VideoProjectManager(storage_backend="memory")
    
    # Load TikTok template (1080x1920, vertical)
    print("Loading TikTok template...")
    manager.load_template("tiktok_vertical")
    
    # Add the main video
    print("Adding main video...")
    video_clip = manager.add_clip(
        clip_type="video",
        source=input_video,
        duration=15.0,  # TikTok videos are typically 15-60s
        start=0.0,
        track_layer=1
    )
    
    # Crop to vertical format
    print("Cropping to vertical...")
    manager.apply_action(
        "crop_vertical",
        clip_id=video_clip.id,
        target_aspect="9:16"
    )
    
    # Add hook text at the beginning
    print("Adding hook text...")
    hook_text = manager.add_clip(
        clip_type="text",
        source="Wait for it... 👀",
        duration=2.0,
        start=0.0,
        track_layer=2
    )
    
    # Add main caption
    print("Adding main caption...")
    main_text = manager.add_clip(
        clip_type="text",
        source="This is AMAZING!",
        duration=5.0,
        start=5.0,
        track_layer=2
    )
    
    # Add fade effects to text
    for clip in [hook_text, main_text]:
        manager.apply_action(
            "apply_effect",
            clip_id=clip.id,
            effect_type="fade",
            parameters={"fade_in": 0.3, "fade_out": 0.3}
        )
    
    # Set music volume (assuming video has audio)
    manager.apply_action(
        "set_volume",
        clip_id=video_clip.id,
        volume=0.7  # Reduce volume slightly for text voiceover
    )
    
    # Show project info
    info = manager.get_project_info()
    print(f"\nProject ready:")
    print(f"  Resolution: {info['resolution']}")
    print(f"  Duration: {info['total_duration']}s")
    print(f"  Clips: {info['num_clips']}")
    
    # Render with fast preset for quick iteration
    print(f"\nRendering to {output_path}...")
    manager.render(output_path, preset="fast")
    print("Done! Ready for TikTok upload 🚀")

if __name__ == "__main__":
    # Example usage with web video
    create_tiktok_video(
        input_video="https://videos.pexels.com/video-files/3571264/3571264-uhd_2560_1440_30fps.mp4",
        output_path="my_tiktok.mp4"
    )
