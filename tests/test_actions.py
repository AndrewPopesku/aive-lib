"""Tests for action registry and actions."""

import pytest
from moviely.models import ProjectState, Clip
from moviely.engine.actions import ActionRegistry
from moviely.errors import InvalidActionError


def test_list_actions():
    """Test listing registered actions."""
    actions = ActionRegistry.list_actions()
    assert "add_clip" in actions
    assert "remove_clip" in actions
    assert "trim_clip" in actions


def test_add_clip_action():
    """Test add_clip action."""
    project = ProjectState(name="Test", resolution=(1920, 1080), fps=30)
    
    result = ActionRegistry.execute(
        "add_clip",
        project,
        clip_type="text",
        source="Hello World",
        duration=5.0
    )
    
    assert len(result.clips) == 1
    assert result.clips[0].source == "Hello World"
    assert result.clips[0].duration == 5.0


def test_remove_clip_action():
    """Test remove_clip action."""
    project = ProjectState(name="Test", resolution=(1920, 1080), fps=30)
    project.add_clip(Clip(id="remove_me", type="text", source="Test", duration=1.0))
    
    result = ActionRegistry.execute("remove_clip", project, clip_id="remove_me")
    assert len(result.clips) == 0


def test_remove_nonexistent_clip():
    """Test removing non-existent clip raises error."""
    project = ProjectState(name="Test", resolution=(1920, 1080), fps=30)
    
    with pytest.raises(InvalidActionError, match="not found"):
        ActionRegistry.execute("remove_clip", project, clip_id="nonexistent")


def test_trim_clip_action():
    """Test trim_clip action."""
    project = ProjectState(name="Test", resolution=(1920, 1080), fps=30)
    project.add_clip(Clip(id="trim_me", type="text", source="Test", duration=10.0, start=0.0))
    
    result = ActionRegistry.execute(
        "trim_clip",
        project,
        clip_id="trim_me",
        new_duration=5.0,
        new_start=2.0
    )
    
    clip = result.get_clip_by_id("trim_me")
    assert clip.duration == 5.0
    assert clip.start == 2.0


def test_apply_effect_action():
    """Test apply_effect action."""
    project = ProjectState(name="Test", resolution=(1920, 1080), fps=30)
    project.add_clip(Clip(id="effect_me", type="text", source="Test", duration=5.0))
    
    result = ActionRegistry.execute(
        "apply_effect",
        project,
        clip_id="effect_me",
        effect_type="fade",
        parameters={"fade_in": 1.0}
    )
    
    clip = result.get_clip_by_id("effect_me")
    assert len(clip.effects) == 1
    assert clip.effects[0].type == "fade"


def test_set_volume_action():
    """Test set_volume action."""
    project = ProjectState(name="Test", resolution=(1920, 1080), fps=30)
    project.add_clip(Clip(id="vol_me", type="audio", source="/dev/null", duration=5.0))
    
    result = ActionRegistry.execute(
        "set_volume",
        project,
        clip_id="vol_me",
        volume=0.5
    )
    
    clip = result.get_clip_by_id("vol_me")
    assert clip.volume == 0.5


def test_invalid_volume():
    """Test that invalid volume values are rejected."""
    project = ProjectState(name="Test", resolution=(1920, 1080), fps=30)
    project.add_clip(Clip(id="vol_me", type="audio", source="/dev/null", duration=5.0))
    
    with pytest.raises(InvalidActionError, match="between 0.0 and 2.0"):
        ActionRegistry.execute("set_volume", project, clip_id="vol_me", volume=3.0)


def test_crop_vertical_action():
    """Test crop_vertical action."""
    project = ProjectState(name="Test", resolution=(1920, 1080), fps=30)
    project.add_clip(Clip(id="crop_me", type="video", source="/dev/null", duration=5.0))
    
    result = ActionRegistry.execute(
        "crop_vertical",
        project,
        clip_id="crop_me",
        target_aspect="9:16"
    )
    
    clip = result.get_clip_by_id("crop_me")
    assert len(clip.effects) == 1
    assert clip.effects[0].type == "crop"


def test_invalid_action():
    """Test that invalid action name raises error."""
    project = ProjectState(name="Test", resolution=(1920, 1080), fps=30)
    
    with pytest.raises(InvalidActionError, match="not found"):
        ActionRegistry.execute("nonexistent_action", project)
