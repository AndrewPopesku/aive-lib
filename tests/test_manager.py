"""Tests for VideoProjectManager."""

import pytest
from pathlib import Path
from moviely.manager import VideoProjectManager
from moviely.errors import MovielyError
import tempfile


def test_create_project():
    """Test creating a new project."""
    manager = VideoProjectManager(storage_backend="memory")

    project = manager.create_project(
        name="TestProject",
        resolution=(1920, 1080),
        fps=30
    )

    assert project.name == "TestProject"
    assert manager.project is not None
    # Should have default tracks
    assert len(project.tracks) == 3
    assert project.get_tracks_by_type("video")
    assert project.get_tracks_by_type("audio")
    assert project.get_tracks_by_type("text")


def test_load_template():
    """Test loading a template."""
    with tempfile.TemporaryDirectory() as tmpdir:
        template_dir = Path(tmpdir)

        # Create a test template with track-based schema
        template_file = template_dir / "test_template.json"
        template_file.write_text('''
        {
            "name": "Test Template",
            "resolution": [1280, 720],
            "fps": 60,
            "tracks": [
                {"id": "v1", "name": "Video 1", "type": "video", "clips": [], "volume": 1.0, "visible": true, "locked": false}
            ],
            "background_color": [0, 0, 0]
        }
        ''')

        manager = VideoProjectManager(
            storage_backend="memory",
            template_dir=template_dir
        )

        project = manager.load_template("test_template")
        assert project.name == "Test Template"
        assert project.fps == 60
        assert len(project.tracks) == 1


def test_add_clip_via_manager():
    """Test adding clips through manager."""
    manager = VideoProjectManager(storage_backend="memory")
    manager.create_project("Test", resolution=(1920, 1080))

    clip = manager.add_clip(
        clip_type="text",
        source="Hello World",
        duration=5.0
    )

    assert clip.source == "Hello World"
    # Clip should be in the text track (default for text clips)
    text_track = manager.get_default_track("text")
    assert len(text_track.clips) == 1


def test_add_clip_to_specific_track():
    """Test adding clips to a specific track."""
    manager = VideoProjectManager(storage_backend="memory")
    manager.create_project("Test", resolution=(1920, 1080))

    video_track = manager.get_default_track("video")

    clip = manager.add_clip(
        clip_type="text",
        source="Hello",
        duration=5.0,
        track_id=video_track.id
    )

    assert len(video_track.clips) == 1
    assert video_track.clips[0].id == clip.id


def test_insert_clip_via_manager():
    """Test inserting clips through manager."""
    manager = VideoProjectManager(storage_backend="memory")
    manager.create_project("Test", resolution=(1920, 1080))

    text_track = manager.get_default_track("text")

    # Add initial clips
    manager.add_clip(clip_type="text", source="A", duration=1.0)
    manager.add_clip(clip_type="text", source="C", duration=1.0)

    # Insert in the middle
    clip = manager.insert_clip(
        clip_type="text",
        source="B",
        duration=1.0,
        track_id=text_track.id,
        index=1
    )

    assert len(text_track.clips) == 3
    assert text_track.clips[0].source == "A"
    assert text_track.clips[1].source == "B"
    assert text_track.clips[2].source == "C"


def test_create_track_via_manager():
    """Test creating tracks through manager."""
    manager = VideoProjectManager(storage_backend="memory")
    manager.create_project("Test", resolution=(1920, 1080))

    initial_count = len(manager.project.tracks)

    track = manager.create_track(track_type="video", name="Extra Video")

    assert len(manager.project.tracks) == initial_count + 1
    assert track.name == "Extra Video"
    assert track.type == "video"


def test_apply_action_via_manager():
    """Test applying actions through manager."""
    manager = VideoProjectManager(storage_backend="memory")
    manager.create_project("Test", resolution=(1920, 1080))

    text_track = manager.get_default_track("text")
    manager.add_clip(clip_type="text", source="Test", duration=5.0)

    clip_id = text_track.clips[0].id

    manager.apply_action(
        "trim_clip",
        track_id=text_track.id,
        clip_id=clip_id,
        duration=3.0
    )

    assert text_track.clips[0].duration == 3.0


def test_save_and_load_project():
    """Test saving and loading projects."""
    manager = VideoProjectManager(storage_backend="memory")
    manager.create_project("SaveTest", resolution=(1920, 1080))
    manager.add_clip(clip_type="text", source="Test", duration=5.0)

    # Save
    manager.save_project("test.json")

    # Create new manager and load
    manager2 = VideoProjectManager(storage_backend="memory")
    manager2.storage = manager.storage  # Share storage for test

    project = manager2.load_project("test.json")
    assert project.name == "SaveTest"
    assert project.get_clip_count() == 1


def test_get_project_info():
    """Test getting project information."""
    manager = VideoProjectManager(storage_backend="memory")
    manager.create_project("Info", resolution=(1920, 1080))
    manager.add_clip(clip_type="text", source="A", duration=5.0)
    manager.add_clip(clip_type="text", source="B", duration=3.0)

    info = manager.get_project_info()

    assert info["name"] == "Info"
    assert info["clip_count"] == 2
    assert info["total_duration"] == 8.0
    assert "tracks" in info
    assert len(info["tracks"]) == 3  # Default tracks


def test_no_active_project_error():
    """Test that operations without active project raise error."""
    manager = VideoProjectManager(storage_backend="memory")

    with pytest.raises(MovielyError, match="No active project"):
        manager.save_project()

    with pytest.raises(MovielyError, match="No active project"):
        manager.render("output.mp4")

    with pytest.raises(MovielyError, match="No active project"):
        manager.add_clip("text", "test", 1.0)


def test_list_actions():
    """Test listing available actions."""
    manager = VideoProjectManager(storage_backend="memory")
    actions = manager.list_actions()

    assert "add_clip" in actions
    assert "trim_clip" in actions
    assert "create_track" in actions
    assert len(actions) > 0


def test_list_templates():
    """Test listing templates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        template_dir = Path(tmpdir)
        (template_dir / "template1.json").write_text(
            '{"name":"T1","resolution":[1920,1080],"fps":30,"tracks":[],"background_color":[0,0,0]}'
        )
        (template_dir / "template2.json").write_text(
            '{"name":"T2","resolution":[1920,1080],"fps":30,"tracks":[],"background_color":[0,0,0]}'
        )

        manager = VideoProjectManager(storage_backend="memory", template_dir=template_dir)
        templates = manager.list_templates()

        assert "template1" in templates
        assert "template2" in templates


def test_get_default_track():
    """Test getting default tracks by type."""
    manager = VideoProjectManager(storage_backend="memory")
    manager.create_project("Test", resolution=(1920, 1080))

    video_track = manager.get_default_track("video")
    audio_track = manager.get_default_track("audio")
    text_track = manager.get_default_track("text")

    assert video_track is not None
    assert video_track.type == "video"
    assert audio_track is not None
    assert audio_track.type == "audio"
    assert text_track is not None
    assert text_track.type == "text"


def test_gap_clip_via_manager():
    """Test adding gap clips through manager."""
    manager = VideoProjectManager(storage_backend="memory")
    manager.create_project("Test", resolution=(1920, 1080))

    video_track = manager.get_default_track("video")

    clip = manager.add_clip(
        clip_type="gap",
        source=None,
        duration=2.0,
        track_id=video_track.id
    )

    assert clip.type == "gap"
    assert clip.duration == 2.0
    assert clip.source is None
