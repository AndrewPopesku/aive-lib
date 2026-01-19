"""Template management system."""

from pathlib import Path
from typing import Optional
import json
from moviely.models import ProjectState
from moviely.errors import ValidationError
try:
    from importlib.resources import files
except ImportError:
    files = None


class TemplateManager:
    """Manages project templates."""
    
    def __init__(self, template_dir: Optional[Path] = None):
        """Initialize template manager.
        
        Args:
            template_dir: Directory containing templates
        """
        self.template_dir = template_dir
        if not template_dir:
            # Try to use package templates
            try:
                if files:
                    template_path = files('moviely').joinpath('../templates')
                    self.template_dir = Path(str(template_path))
                else:
                    raise ImportError
            except:
                self.template_dir = Path(__file__).parent.parent.parent.parent / "templates"

        self.template_dir.mkdir(parents=True, exist_ok=True)
    
    def load_template(self, name: str) -> ProjectState:
        """Load a template by name.
        
        Args:
            name: Template name (without .json extension)
            
        Returns:
            ProjectState initialized from template
        """
        template_path = self.template_dir / f"{name}.json"
        
        if not template_path.exists():
            raise ValidationError(f"Template not found: {name}")
        
        try:
            with open(template_path, 'r') as f:
                data = json.load(f)
            
            # Validate and create project
            return ProjectState(**data)
        except Exception as e:
            raise ValidationError(f"Failed to load template '{name}': {e}")
    
    def save_template(self, project: ProjectState, name: str) -> Path:
        """Save a project as a template.
        
        Args:
            project: Project to save as template
            name: Template name
            
        Returns:
            Path to saved template
        """
        template_path = self.template_dir / f"{name}.json"
        
        try:
            with open(template_path, 'w') as f:
                json.dump(project.model_dump(), f, indent=2)
            
            return template_path
        except Exception as e:
            raise ValidationError(f"Failed to save template: {e}")
    
    def list_templates(self) -> list[str]:
        """List available templates.
        
        Returns:
            List of template names
        """
        return [f.stem for f in self.template_dir.glob("*.json")]
    
    def delete_template(self, name: str) -> bool:
        """Delete a template.
        
        Args:
            name: Template name
            
        Returns:
            True if deleted
        """
        template_path = self.template_dir / f"{name}.json"
        if template_path.exists():
            template_path.unlink()
            return True
        return False
    
    def template_exists(self, name: str) -> bool:
        """Check if a template exists.
        
        Args:
            name: Template name
            
        Returns:
            True if exists
        """
        return (self.template_dir / f"{name}.json").exists()
