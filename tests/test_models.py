"""Tests for core models."""

import pytest
from moviely.models import ProjectState, Clip, Effect


def test_clip_creation():
    """Test creating a basic clip."""
    clip = Clip(
        id="test1",
        type="video",
        source="/dev/null",  # Dummy path for testing
        duration=10.0,
        start=0.0
    )
    assert clip.id == "test1"
    assert clip.duration == 10.0
    assert clip.volume == 1.0


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
    assert len(project.clips) == 0


def test_project_add_clip():
    """Test adding clips to a project."""
    project = ProjectState(
        name="Test",
        resolution=(1920, 1080),
        fps=30
    )
    
    clip = Clip(
        id="clip1",
        type="text",
        source="Hello World",
        duration=5.0
    )
    
    project.add_clip(clip)
    assert len(project.clips) == 1
    assert project.clips[0].id == "clip1"


def test_project_duplicate_clip_id():
    """Test that duplicate clip IDs are rejected."""
    project = ProjectState(
        name="Test",
        resolution=(1920, 1080),
        fps=30
    )
    
    clip1 = Clip(id="same", type="text", source="A", duration=1.0)
    clip2 = Clip(id="same", type="text", source="B", duration=1.0)
    
    project.add_clip(clip1)
    
    with pytest.raises(ValueError, match="already exists"):
        project.add_clip(clip2)


def test_project_get_clip_by_id():
    """Test retrieving clips by ID."""
    project = ProjectState(
        name="Test",
        resolution=(1920, 1080),
        fps=30
    )
    
    clip = Clip(id="findme", type="text", source="Test", duration=1.0)
    project.add_clip(clip)
    
    found = project.get_clip_by_id("findme")
    assert found is not None
    assert found.id == "findme"
    
    not_found = project.get_clip_by_id("nothere")
    assert not_found is None


def test_project_remove_clip():
    """Test removing clips from a project."""
    project = ProjectState(
        name="Test",
        resolution=(1920, 1080),
        fps=30
    )
    
    clip = Clip(id="remove", type="text", source="Test", duration=1.0)
    project.add_clip(clip)
    assert len(project.clips) == 1
    
    removed = project.remove_clip("remove")
    assert removed is True
    assert len(project.clips) == 0
    
    removed_again = project.remove_clip("remove")
    assert removed_again is False


def test_project_total_duration():
    """Test calculating total project duration."""
    project = ProjectState(
        name="Test",
        resolution=(1920, 1080),
        fps=30
    )
    
    # Empty project
    assert project.get_total_duration() == 0.0
    
    # Add clips
    project.add_clip(Clip(id="c1", type="text", source="A", duration=5.0, start=0.0))
    project.add_clip(Clip(id="c2", type="text", source="B", duration=3.0, start=5.0))
    
    # Total should be start + duration of longest clip
    assert project.get_total_duration() == 8.0


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
