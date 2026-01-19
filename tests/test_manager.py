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


def test_load_template():
    """Test loading a template."""
    with tempfile.TemporaryDirectory() as tmpdir:
        template_dir = Path(tmpdir)
        
        # Create a test template
        template_file = template_dir / "test_template.json"
        template_file.write_text('''
        {
            "name": "Test Template",
            "resolution": [1280, 720],
            "fps": 60,
            "clips": [],
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
    assert len(manager.project.clips) == 1


def test_apply_action_via_manager():
    """Test applying actions through manager."""
    manager = VideoProjectManager(storage_backend="memory")
    manager.create_project("Test", resolution=(1920, 1080))
    manager.add_clip(clip_type="text", source="Test", duration=5.0)
    
    clip_id = manager.project.clips[0].id
    
    manager.apply_action("trim_clip", clip_id=clip_id, new_duration=3.0)
    
    assert manager.project.clips[0].duration == 3.0


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
    assert len(project.clips) == 1


def test_get_project_info():
    """Test getting project information."""
    manager = VideoProjectManager(storage_backend="memory")
    manager.create_project("Info", resolution=(1920, 1080))
    manager.add_clip(clip_type="text", source="A", duration=5.0, start=0.0)
    manager.add_clip(clip_type="text", source="B", duration=3.0, start=5.0)
    
    info = manager.get_project_info()
    
    assert info["name"] == "Info"
    assert info["num_clips"] == 2
    assert info["total_duration"] == 8.0


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
    assert len(actions) > 0


def test_list_templates():
    """Test listing templates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        template_dir = Path(tmpdir)
        (template_dir / "template1.json").write_text('{"name":"T1","resolution":[1920,1080],"fps":30,"clips":[],"background_color":[0,0,0]}')
        (template_dir / "template2.json").write_text('{"name":"T2","resolution":[1920,1080],"fps":30,"clips":[],"background_color":[0,0,0]}')
        
        manager = VideoProjectManager(storage_backend="memory", template_dir=template_dir)
        templates = manager.list_templates()
        
        assert "template1" in templates
        assert "template2" in templates
