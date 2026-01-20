import pytest
from aive.manager import VideoProjectManager
from aive.models import ProjectState

def test_advanced_add_clip_append():
    """Test advanced_add_clip appends when no index is provided."""
    manager = VideoProjectManager(storage_backend="memory")
    manager.create_project("Test")
    
    # Track ID for Video 1
    track_id = manager.project.tracks[0].id
    
    clip = manager.advanced_add_clip(
        clip_type="text",
        source="First",
        duration=5.0,
        track_id=track_id
    )
    
    assert len(manager.project.tracks[0].clips) == 1
    assert manager.project.tracks[0].clips[0].source == "First"

def test_advanced_add_clip_insert():
    """Test advanced_add_clip inserts when index is provided."""
    manager = VideoProjectManager(storage_backend="memory")
    manager.create_project("Test")
    track_id = manager.project.tracks[0].id
    
    manager.append_clip("text", "A", 1.0, track_id)
    manager.append_clip("text", "C", 1.0, track_id)
    
    manager.advanced_add_clip(
        clip_type="text",
        source="B",
        duration=1.0,
        track_id=track_id,
        index=1
    )
    
    clips = manager.project.tracks[0].clips
    assert len(clips) == 3
    assert clips[0].source == "A"
    assert clips[1].source == "B"
    assert clips[2].source == "C"

def test_advanced_add_clip_with_effects():
    """Test advanced_add_clip applies effects immediately."""
    manager = VideoProjectManager(storage_backend="memory")
    manager.create_project("Test")
    track_id = manager.project.tracks[0].id
    
    effects = [
        {"type": "fade", "parameters": {"fade_in": 1.0}},
        {"type": "crop", "parameters": {"width": 100, "height": 100, "x": 0, "y": 0}}
    ]
    
    clip = manager.advanced_add_clip(
        clip_type="text",
        source="Effect Test",
        duration=5.0,
        track_id=track_id,
        effects=effects
    )
    
    assert len(clip.effects) == 2
    assert clip.effects[0].type == "fade"
    assert clip.effects[1].type == "crop"

def test_advanced_add_clip_trimming():
    """Test advanced_add_clip supports media_start/duration."""
    manager = VideoProjectManager(storage_backend="memory")
    manager.create_project("Test")
    track_id = manager.project.tracks[0].id
    
    clip = manager.advanced_add_clip(
        clip_type="video",
        source="https://example.com/dummy.mp4",
        duration=10.0,
        track_id=track_id,
        media_start=5.0
    )
    
    assert clip.media_start == 5.0
    assert clip.duration == 10.0
