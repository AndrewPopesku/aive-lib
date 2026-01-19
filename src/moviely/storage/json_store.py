"""JSON-based storage backend."""

from pathlib import Path
from typing import Optional
import json
from moviely.models import ProjectState
from moviely.errors import StorageError


class JSONStore:
    """File-based JSON storage for project state."""
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize JSON store.
        
        Args:
            base_path: Base directory for storing projects. Defaults to ./projects
        """
        self.base_path = base_path or Path.cwd() / "projects"
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save(self, project: ProjectState, filename: Optional[str] = None) -> Path:
        """Save project to JSON file.
        
        Args:
            project: Project state to save
            filename: Optional filename (defaults to project name)
            
        Returns:
            Path to saved file
        """
        try:
            filename = filename or f"{project.name}.json"
            file_path = self.base_path / filename
            
            with open(file_path, 'w') as f:
                json.dump(project.model_dump(), f, indent=2)
            
            return file_path
        except Exception as e:
            raise StorageError(f"Failed to save project: {e}")
    
    def load(self, filename: str) -> ProjectState:
        """Load project from JSON file.
        
        Args:
            filename: Name of file to load
            
        Returns:
            Loaded project state
        """
        try:
            file_path = self.base_path / filename
            
            if not file_path.exists():
                raise StorageError(f"Project file not found: {filename}")
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            return ProjectState(**data)
        except StorageError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to load project: {e}")
    
    def list_projects(self) -> list[str]:
        """List all saved projects.
        
        Returns:
            List of project filenames
        """
        return [f.name for f in self.base_path.glob("*.json")]
    
    def delete(self, filename: str) -> bool:
        """Delete a project file.
        
        Args:
            filename: Name of file to delete
            
        Returns:
            True if deleted, False if not found
        """
        file_path = self.base_path / filename
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def exists(self, filename: str) -> bool:
        """Check if a project file exists.
        
        Args:
            filename: Name of file to check
            
        Returns:
            True if exists
        """
        return (self.base_path / filename).exists()
