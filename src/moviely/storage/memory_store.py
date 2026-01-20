"""In-memory storage backend for testing."""

from typing import Dict, Optional
from aive.models import ProjectState
from aive.errors import StorageError
import copy


class MemoryStore:
    """In-memory storage for project state (useful for testing)."""
    
    def __init__(self):
        """Initialize memory store."""
        self._projects: Dict[str, ProjectState] = {}
    
    def save(self, project: ProjectState, filename: Optional[str] = None) -> str:
        """Save project to memory.
        
        Args:
            project: Project state to save
            filename: Optional key (defaults to project name)
            
        Returns:
            Key used for storage
        """
        key = filename or f"{project.name}.json"
        # Deep copy to prevent external modifications
        self._projects[key] = copy.deepcopy(project)
        return key
    
    def load(self, filename: str) -> ProjectState:
        """Load project from memory.
        
        Args:
            filename: Key to load
            
        Returns:
            Loaded project state
        """
        if filename not in self._projects:
            raise StorageError(f"Project not found in memory: {filename}")
        
        # Return a deep copy
        return copy.deepcopy(self._projects[filename])
    
    def list_projects(self) -> list[str]:
        """List all saved projects.
        
        Returns:
            List of project keys
        """
        return list(self._projects.keys())
    
    def delete(self, filename: str) -> bool:
        """Delete a project from memory.
        
        Args:
            filename: Key to delete
            
        Returns:
            True if deleted, False if not found
        """
        if filename in self._projects:
            del self._projects[filename]
            return True
        return False
    
    def exists(self, filename: str) -> bool:
        """Check if a project exists in memory.
        
        Args:
            filename: Key to check
            
        Returns:
            True if exists
        """
        return filename in self._projects
    
    def clear(self) -> None:
        """Clear all projects from memory."""
        self._projects.clear()
