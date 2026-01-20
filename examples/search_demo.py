"""
Search and download media example.

This example demonstrates:
- Searching for videos on Pexels
- Searching for music on Jamendo
- Downloading media to local cache
- Creating a project with downloaded media
- Rendering the final video

Requirements:
    Set environment variables before running:
    - PEXELS_API_KEY
    - JAMENDO_CLIENT_ID
"""

import asyncio
from aive import VideoProjectManager


async def main():
    # Initialize manager
    manager = VideoProjectManager()

    print("=" * 50)
    print("aive Search Demo")
    print("=" * 50)

    # 1. Search for background video on Pexels
    print("\n[1/5] Searching for nature videos on Pexels...")
    video_results = await manager.search_media(
        query="nature sunset",
        provider="pexels",
        media_type="video",
        limit=3
    )

    print(f"Found {len(video_results)} videos:")
    for i, result in enumerate(video_results, 1):
        print(f"  {i}. {result.title or 'Untitled'} by {result.author}")
        print(f"     Duration: {result.duration}s, Resolution: {result.width}x{result.height}")
        print(f"     Preview: {result.preview_url}")

    # 2. Search for music on Jamendo
    print("\n[2/5] Searching for relaxing music on Jamendo...")
    music_results = await manager.search_music(
        query="relaxing ambient",
        limit=3
    )

    print(f"Found {len(music_results)} tracks:")
    for i, result in enumerate(music_results, 1):
        print(f"  {i}. {result.title} by {result.author}")
        print(f"     Duration: {result.duration}s")

    # 3. Download the first video and music track
    if video_results and music_results:
        print("\n[3/5] Downloading media files...")

        video_path = await manager.download_media(video_results[0])
        print(f"  Video downloaded to: {video_path}")

        music_path = await manager.download_media(music_results[0])
        print(f"  Music downloaded to: {music_path}")

        # 4. Create project and add clips
        print("\n[4/5] Creating project with downloaded media...")
        manager.create_project(
            name="Search Demo Video",
            resolution=(1920, 1080),
            fps=30
        )

        # Add video clip (use shorter duration if video is longer)
        video_duration = min(video_results[0].duration or 10, 15)
        video_clip = manager.add_clip(
            clip_type="video",
            source=str(video_path),
            duration=video_duration,
            start=0.0,
            track_layer=1
        )
        print(f"  Added video clip: {video_clip.id}")

        # Add music track
        music_clip = manager.add_clip(
            clip_type="audio",
            source=str(music_path),
            duration=video_duration,
            start=0.0,
            track_layer=1
        )
        print(f"  Added audio clip: {music_clip.id}")

        # Set music volume
        manager.apply_action(
            "set_volume",
            clip_id=music_clip.id,
            volume=0.5
        )
        print("  Set music volume to 50%")

        # Add text overlay
        text_clip = manager.add_clip(
            clip_type="text",
            source=f"Video: {video_results[0].title or 'Nature Sunset'}\nMusic: {music_results[0].title}",
            duration=3.0,
            start=1.0,
            track_layer=2
        )
        print(f"  Added text overlay: {text_clip.id}")

        # Get project info
        info = manager.get_project_info()
        print("\nProject Summary:")
        print(f"  Name: {info['name']}")
        print(f"  Resolution: {info['resolution']}")
        print(f"  Clips: {info['num_clips']}")
        print(f"  Duration: {info['total_duration']}s")

        # 5. Render the video
        print("\n[5/5] Rendering video...")
        output_path = manager.render("output_search_demo.mp4", preset="fast")
        print(f"  Video rendered to: {output_path}")

        print("\n" + "=" * 50)
        print("Demo complete!")
        print("=" * 50)
    else:
        print("\nNo results found. Make sure API keys are set correctly.")


if __name__ == "__main__":
    asyncio.run(main())
