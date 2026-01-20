"""Tests for storage backends."""

import pytest
from pathlib import Path
from aive.models import ProjectState, Clip, Track
from aive.storage.memory_store import MemoryStore
from aive.storage.json_store import JSONStore
from aive.errors import StorageError
import tempfile


def test_memory_store_save_load():
    """Test saving and loading from memory store."""
    store = MemoryStore()
    
    project = ProjectState(
        name="Test",
        resolution=(1920, 1080),
        fps=30
    )
    
    # Save
    key = store.save(project, "test.json")
    assert key == "test.json"
    
    # Load
    loaded = store.load("test.json")
    assert loaded.name == "Test"
    assert loaded.resolution == (1920, 1080)


def test_memory_store_not_found():
    """Test loading non-existent project."""
    store = MemoryStore()
    
    with pytest.raises(StorageError, match="not found"):
        store.load("nonexistent.json")


def test_memory_store_list_delete():
    """Test listing and deleting projects."""
    store = MemoryStore()
    
    project = ProjectState(name="Test", resolution=(1920, 1080), fps=30)
    store.save(project, "test.json")
    
    # List
    projects = store.list_projects()
    assert "test.json" in projects
    
    # Delete
    deleted = store.delete("test.json")
    assert deleted is True
    
    projects = store.list_projects()
    assert "test.json" not in projects
    
    # Delete non-existent
    deleted = store.delete("test.json")
    assert deleted is False


def test_json_store_save_load():
    """Test JSON store save and load."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = JSONStore(Path(tmpdir))
        
        project = ProjectState(
            name="JSONTest",
            resolution=(1280, 720),
            fps=60
        )
        
        # Save
        path = store.save(project)
        assert path.exists()
        
        # Load
        loaded = store.load("JSONTest.json")
        assert loaded.name == "JSONTest"
        assert loaded.fps == 60


def test_json_store_persistence():
    """Test that JSON store persists across instances."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # First instance
        store1 = JSONStore(Path(tmpdir))
        project = ProjectState(name="Persist", resolution=(1920, 1080), fps=30)
        store1.save(project)
        
        # Second instance
        store2 = JSONStore(Path(tmpdir))
        loaded = store2.load("Persist.json")
        assert loaded.name == "Persist"


def test_json_store_with_clips():
    """Test saving and loading projects with clips."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = JSONStore(Path(tmpdir))

        project = ProjectState(name="WithClips", resolution=(1920, 1080), fps=30)
        track = Track(id="track1", name="Video 1", type="video")
        track.clips.append(Clip(
            id="clip1",
            type="text",
            source="Hello",
            duration=5.0
        ))
        project.tracks.append(track)

        store.save(project)
        loaded = store.load("WithClips.json")

        assert len(loaded.tracks) == 1
        assert len(loaded.tracks[0].clips) == 1
        assert loaded.tracks[0].clips[0].id == "clip1"
        assert loaded.tracks[0].clips[0].source == "Hello"
