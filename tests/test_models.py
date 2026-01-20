"""Tests for core models."""

import pytest
from aive.models import ProjectState, Clip, Effect, Track


def test_clip_creation():
    """Test creating a basic clip."""
    clip = Clip(
        id="test1",
        type="text",
        source="Hello World",
        duration=10.0,
    )
    assert clip.id == "test1"
    assert clip.duration == 10.0
    assert clip.volume == 1.0
    assert clip.media_start == 0.0


def test_gap_clip_creation():
    """Test creating a gap clip."""
    clip = Clip(
        id="gap1",
        type="gap",
        source=None,
        duration=2.0,
    )
    assert clip.id == "gap1"
    assert clip.type == "gap"
    assert clip.source is None
    assert clip.duration == 2.0


def test_track_creation():
    """Test creating a track."""
    track = Track(
        id="track1",
        name="Video 1",
        type="video"
    )
    assert track.id == "track1"
    assert track.name == "Video 1"
    assert track.type == "video"
    assert len(track.clips) == 0
    assert track.volume == 1.0
    assert track.visible is True
    assert track.locked is False


def test_track_add_clip():
    """Test adding clips to a track."""
    track = Track(id="track1", name="Video 1", type="video")
    clip = Clip(id="clip1", type="text", source="Hello", duration=5.0)

    track.clips.append(clip)

    assert len(track.clips) == 1
    assert track.clips[0].id == "clip1"


def test_track_get_clip_by_id():
    """Test retrieving clips by ID from a track."""
    track = Track(id="track1", name="Video 1", type="video")
    clip = Clip(id="findme", type="text", source="Test", duration=1.0)
    track.clips.append(clip)

    found = track.get_clip_by_id("findme")
    assert found is not None
    assert found.id == "findme"

    not_found = track.get_clip_by_id("nothere")
    assert not_found is None


def test_track_get_clip_index():
    """Test getting clip index by ID."""
    track = Track(id="track1", name="Video 1", type="video")
    clip1 = Clip(id="c1", type="text", source="A", duration=1.0)
    clip2 = Clip(id="c2", type="text", source="B", duration=1.0)
    track.clips.extend([clip1, clip2])

    assert track.get_clip_index("c1") == 0
    assert track.get_clip_index("c2") == 1
    assert track.get_clip_index("nothere") is None


def test_track_duration():
    """Test calculating track duration."""
    track = Track(id="track1", name="Video 1", type="video")

    assert track.get_duration() == 0.0

    track.clips.append(Clip(id="c1", type="text", source="A", duration=5.0))
    track.clips.append(Clip(id="c2", type="text", source="B", duration=3.0))

    assert track.get_duration() == 8.0


def test_track_clip_start_time():
    """Test calculating clip start times."""
    track = Track(id="track1", name="Video 1", type="video")
    track.clips.append(Clip(id="c1", type="text", source="A", duration=5.0))
    track.clips.append(Clip(id="c2", type="text", source="B", duration=3.0))
    track.clips.append(Clip(id="c3", type="text", source="C", duration=2.0))

    assert track.get_clip_start_time(0) == 0.0
    assert track.get_clip_start_time(1) == 5.0
    assert track.get_clip_start_time(2) == 8.0


def test_project_state_creation():
    """Test creating a project state."""
    project = ProjectState(
        name="Test Project",
        resolution=(1920, 1080),
        fps=30
    )
    assert project.name == "Test Project"
    assert project.resolution == (1920, 1080)
    assert project.fps == 30
    assert len(project.tracks) == 0


def test_project_get_track_by_id():
    """Test retrieving tracks by ID."""
    project = ProjectState(name="Test", resolution=(1920, 1080), fps=30)
    track = Track(id="findme", name="Video 1", type="video")
    project.tracks.append(track)

    found = project.get_track_by_id("findme")
    assert found is not None
    assert found.id == "findme"

    not_found = project.get_track_by_id("nothere")
    assert not_found is None


def test_project_get_tracks_by_type():
    """Test getting tracks by type."""
    project = ProjectState(name="Test", resolution=(1920, 1080), fps=30)
    project.tracks.append(Track(id="v1", name="Video 1", type="video"))
    project.tracks.append(Track(id="a1", name="Audio 1", type="audio"))
    project.tracks.append(Track(id="v2", name="Video 2", type="video"))

    video_tracks = project.get_tracks_by_type("video")
    assert len(video_tracks) == 2

    audio_tracks = project.get_tracks_by_type("audio")
    assert len(audio_tracks) == 1


def test_project_total_duration():
    """Test calculating total project duration."""
    project = ProjectState(name="Test", resolution=(1920, 1080), fps=30)

    # Empty project
    assert project.get_total_duration() == 0.0

    # Add tracks with clips
    track1 = Track(id="v1", name="Video 1", type="video")
    track1.clips.append(Clip(id="c1", type="text", source="A", duration=5.0))
    track1.clips.append(Clip(id="c2", type="text", source="B", duration=3.0))

    track2 = Track(id="a1", name="Audio 1", type="audio")
    track2.clips.append(Clip(id="c3", type="text", source="C", duration=10.0))

    project.tracks.extend([track1, track2])

    # Total should be the max of all track durations
    assert project.get_total_duration() == 10.0


def test_project_clip_count():
    """Test counting total clips."""
    project = ProjectState(name="Test", resolution=(1920, 1080), fps=30)

    assert project.get_clip_count() == 0

    track1 = Track(id="v1", name="Video 1", type="video")
    track1.clips.append(Clip(id="c1", type="text", source="A", duration=1.0))
    track1.clips.append(Clip(id="c2", type="text", source="B", duration=1.0))

    track2 = Track(id="a1", name="Audio 1", type="audio")
    track2.clips.append(Clip(id="c3", type="text", source="C", duration=1.0))

    project.tracks.extend([track1, track2])

    assert project.get_clip_count() == 3


def test_invalid_resolution():
    """Test that invalid resolutions are rejected."""
    with pytest.raises(ValueError):
        ProjectState(
            name="Test",
            resolution=(0, 1080),
            fps=30
        )

    with pytest.raises(ValueError):
        ProjectState(
            name="Test",
            resolution=(10000, 10000),
            fps=30
        )


def test_effect_creation():
    """Test creating an effect."""
    effect = Effect(
        type="fade",
        parameters={"fade_in": 1.0, "fade_out": 1.0}
    )
    assert effect.type == "fade"
    assert effect.parameters["fade_in"] == 1.0


def test_text_clip_requires_source():
    """Test that text clips require source content."""
    with pytest.raises(ValueError, match="require source content"):
        Clip(id="test", type="text", source=None, duration=1.0)


def test_media_start_field():
    """Test the media_start field for trimming."""
    clip = Clip(
        id="test",
        type="text",
        source="Hello",
        duration=5.0,
        media_start=2.5
    )
    assert clip.media_start == 2.5
