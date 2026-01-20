"""Tests for action registry and actions."""

import pytest
from moviely.models import ProjectState, Clip, Track
from moviely.engine.actions import ActionRegistry
from moviely.errors import InvalidActionError


def create_project_with_track():
    """Helper to create a project with a default track."""
    project = ProjectState(name="Test", resolution=(1920, 1080), fps=30)
    project.tracks.append(Track(id="track1", name="Video 1", type="video"))
    return project


def test_list_actions():
    """Test listing registered actions."""
    actions = ActionRegistry.list_actions()
    assert "append_clip" in actions
    assert "insert_clip" in actions
    assert "delete_clip" in actions
    assert "trim_clip" in actions
    assert "create_track" in actions


def test_create_track_action():
    """Test create_track action."""
    project = ProjectState(name="Test", resolution=(1920, 1080), fps=30)

    result = ActionRegistry.execute(
        "create_track",
        project,
        track_type="video",
        track_name="My Video Track"
    )

    assert len(result.tracks) == 1
    assert result.tracks[0].name == "My Video Track"
    assert result.tracks[0].type == "video"


def test_create_track_auto_name():
    """Test create_track auto-generates names."""
    project = ProjectState(name="Test", resolution=(1920, 1080), fps=30)

    ActionRegistry.execute("create_track", project, track_type="video")
    ActionRegistry.execute("create_track", project, track_type="video")

    assert project.tracks[0].name == "Video 1"
    assert project.tracks[1].name == "Video 2"


def test_delete_track_action():
    """Test delete_track action."""
    project = create_project_with_track()

    result = ActionRegistry.execute("delete_track", project, track_id="track1")
    assert len(result.tracks) == 0


def test_delete_nonexistent_track():
    """Test deleting non-existent track raises error."""
    project = create_project_with_track()

    with pytest.raises(InvalidActionError, match="not found"):
        ActionRegistry.execute("delete_track", project, track_id="nonexistent")


def test_append_clip_action():
    """Test append_clip action."""
    project = create_project_with_track()

    result = ActionRegistry.execute(
        "append_clip",
        project,
        track_id="track1",
        clip_type="text",
        source="Hello World",
        duration=5.0
    )

    track = result.get_track_by_id("track1")
    assert len(track.clips) == 1
    assert track.clips[0].source == "Hello World"
    assert track.clips[0].duration == 5.0


def test_append_multiple_clips():
    """Test appending multiple clips in sequence."""
    project = create_project_with_track()

    ActionRegistry.execute(
        "append_clip", project, track_id="track1",
        clip_type="text", source="A", duration=5.0
    )
    ActionRegistry.execute(
        "append_clip", project, track_id="track1",
        clip_type="text", source="B", duration=3.0
    )

    track = project.get_track_by_id("track1")
    assert len(track.clips) == 2
    assert track.get_duration() == 8.0


def test_insert_clip_action():
    """Test insert_clip action."""
    project = create_project_with_track()
    track = project.get_track_by_id("track1")

    # Add initial clips
    track.clips.append(Clip(id="c1", type="text", source="A", duration=1.0))
    track.clips.append(Clip(id="c2", type="text", source="C", duration=1.0))

    # Insert in the middle
    result = ActionRegistry.execute(
        "insert_clip",
        project,
        track_id="track1",
        index=1,
        clip_type="text",
        source="B",
        duration=1.0
    )

    track = result.get_track_by_id("track1")
    assert len(track.clips) == 3
    assert track.clips[0].source == "A"
    assert track.clips[1].source == "B"
    assert track.clips[2].source == "C"


def test_delete_clip_by_id():
    """Test delete_clip action by clip_id."""
    project = create_project_with_track()
    track = project.get_track_by_id("track1")
    track.clips.append(Clip(id="remove_me", type="text", source="Test", duration=1.0))

    result = ActionRegistry.execute(
        "delete_clip", project, track_id="track1", clip_id="remove_me"
    )

    track = result.get_track_by_id("track1")
    assert len(track.clips) == 0


def test_delete_clip_by_index():
    """Test delete_clip action by index."""
    project = create_project_with_track()
    track = project.get_track_by_id("track1")
    track.clips.append(Clip(id="c1", type="text", source="A", duration=1.0))
    track.clips.append(Clip(id="c2", type="text", source="B", duration=1.0))

    result = ActionRegistry.execute(
        "delete_clip", project, track_id="track1", index=0
    )

    track = result.get_track_by_id("track1")
    assert len(track.clips) == 1
    assert track.clips[0].id == "c2"


def test_delete_nonexistent_clip():
    """Test deleting non-existent clip raises error."""
    project = create_project_with_track()

    with pytest.raises(InvalidActionError, match="not found"):
        ActionRegistry.execute(
            "delete_clip", project, track_id="track1", clip_id="nonexistent"
        )


def test_move_clip_action():
    """Test move_clip action."""
    project = create_project_with_track()
    track = project.get_track_by_id("track1")
    track.clips.append(Clip(id="c1", type="text", source="A", duration=1.0))
    track.clips.append(Clip(id="c2", type="text", source="B", duration=1.0))
    track.clips.append(Clip(id="c3", type="text", source="C", duration=1.0))

    result = ActionRegistry.execute(
        "move_clip", project, track_id="track1", from_index=0, to_index=2
    )

    track = result.get_track_by_id("track1")
    assert track.clips[0].id == "c2"
    assert track.clips[1].id == "c3"
    assert track.clips[2].id == "c1"


def test_insert_gap_action():
    """Test insert_gap action."""
    project = create_project_with_track()
    track = project.get_track_by_id("track1")
    track.clips.append(Clip(id="c1", type="text", source="A", duration=5.0))

    result = ActionRegistry.execute(
        "insert_gap", project, track_id="track1", index=0, duration=2.0
    )

    track = result.get_track_by_id("track1")
    assert len(track.clips) == 2
    assert track.clips[0].type == "gap"
    assert track.clips[0].duration == 2.0


def test_trim_clip_action():
    """Test trim_clip action."""
    project = create_project_with_track()
    track = project.get_track_by_id("track1")
    track.clips.append(Clip(id="trim_me", type="text", source="Test", duration=10.0))

    result = ActionRegistry.execute(
        "trim_clip",
        project,
        track_id="track1",
        clip_id="trim_me",
        media_start=2.0,
        duration=5.0
    )

    track = result.get_track_by_id("track1")
    clip = track.get_clip_by_id("trim_me")
    assert clip.duration == 5.0
    assert clip.media_start == 2.0


def test_apply_effect_action():
    """Test apply_effect action."""
    project = create_project_with_track()
    track = project.get_track_by_id("track1")
    track.clips.append(Clip(id="effect_me", type="text", source="Test", duration=5.0))

    result = ActionRegistry.execute(
        "apply_effect",
        project,
        track_id="track1",
        clip_id="effect_me",
        effect_type="fade",
        parameters={"fade_in": 1.0}
    )

    track = result.get_track_by_id("track1")
    clip = track.get_clip_by_id("effect_me")
    assert len(clip.effects) == 1
    assert clip.effects[0].type == "fade"


def test_set_clip_volume_action():
    """Test set_clip_volume action."""
    project = create_project_with_track()
    track = project.get_track_by_id("track1")
    track.clips.append(Clip(id="vol_me", type="text", source="Test", duration=5.0))

    result = ActionRegistry.execute(
        "set_clip_volume",
        project,
        track_id="track1",
        clip_id="vol_me",
        volume=0.5
    )

    track = result.get_track_by_id("track1")
    clip = track.get_clip_by_id("vol_me")
    assert clip.volume == 0.5


def test_invalid_volume():
    """Test that invalid volume values are rejected."""
    project = create_project_with_track()
    track = project.get_track_by_id("track1")
    track.clips.append(Clip(id="vol_me", type="text", source="Test", duration=5.0))

    with pytest.raises(InvalidActionError, match="between 0.0 and 2.0"):
        ActionRegistry.execute(
            "set_clip_volume", project, track_id="track1", clip_id="vol_me", volume=3.0
        )


def test_crop_vertical_action():
    """Test crop_vertical action."""
    project = create_project_with_track()
    track = project.get_track_by_id("track1")
    track.clips.append(Clip(id="crop_me", type="text", source="Test", duration=5.0))

    result = ActionRegistry.execute(
        "crop_vertical",
        project,
        track_id="track1",
        clip_id="crop_me",
        target_aspect="9:16"
    )

    track = result.get_track_by_id("track1")
    clip = track.get_clip_by_id("crop_me")
    assert len(clip.effects) == 1
    assert clip.effects[0].type == "crop"


def test_update_track_action():
    """Test update_track action."""
    project = create_project_with_track()

    result = ActionRegistry.execute(
        "update_track",
        project,
        track_id="track1",
        track_name="Renamed Track",
        volume=0.8,
        visible=False,
        locked=True
    )

    track = result.get_track_by_id("track1")
    assert track.name == "Renamed Track"
    assert track.volume == 0.8
    assert track.visible is False
    assert track.locked is True


def test_locked_track_rejects_edits():
    """Test that locked tracks reject clip operations."""
    project = create_project_with_track()
    track = project.get_track_by_id("track1")
    track.locked = True

    with pytest.raises(InvalidActionError, match="locked"):
        ActionRegistry.execute(
            "append_clip", project, track_id="track1",
            clip_type="text", source="Test", duration=1.0
        )


def test_invalid_action():
    """Test that invalid action name raises error."""
    project = ProjectState(name="Test", resolution=(1920, 1080), fps=30)

    with pytest.raises(InvalidActionError, match="not found"):
        ActionRegistry.execute("nonexistent_action", project)
