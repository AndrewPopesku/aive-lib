"""Asset management utilities."""

from pathlib import Path
from typing import Optional
import hashlib
from aive.errors import AssetError


class AssetManager:
    """Manages media assets for projects."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize asset manager.
        
        Args:
            cache_dir: Directory for caching assets
        """
        self.cache_dir = cache_dir or Path.home() / ".aive" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_asset(self, path: str) -> bool:
        """Validate that an asset exists and is accessible.
        
        Args:
            path: Path to asset
            
        Returns:
            True if valid
        """
        if path.startswith(('http://', 'https://')):
            return True  # Assume remote URLs are valid
        
        file_path = Path(path)
        if not file_path.exists():
            raise AssetError(f"Asset not found: {path}")
        
        if not file_path.is_file():
            raise AssetError(f"Asset is not a file: {path}")
        
        return True
    
    def get_asset_info(self, path: str) -> dict:
        """Get information about an asset.
        
        Args:
            path: Path to asset
            
        Returns:
            Dictionary with asset info
        """
        if not self.validate_asset(path):
            return {}
        
        file_path = Path(path)
        
        return {
            "path": str(file_path.absolute()),
            "name": file_path.name,
            "size": file_path.stat().st_size,
            "extension": file_path.suffix,
            "exists": True,
        }
    
    def resolve_path(self, path: str, base_dir: Optional[Path] = None) -> str:
        """Resolve a potentially relative path.
        
        Args:
            path: Path to resolve
            base_dir: Base directory for relative paths
            
        Returns:
            Absolute path
        """
        if path.startswith(('http://', 'https://')):
            return path
        
        file_path = Path(path)
        
        if not file_path.is_absolute():
            base = base_dir or Path.cwd()
            file_path = base / file_path
        
        return str(file_path.absolute())
    
    @staticmethod
    def get_file_hash(path: str) -> str:
        """Calculate MD5 hash of a file.
        
        Args:
            path: Path to file
            
        Returns:
            MD5 hash string
        """
        md5 = hashlib.md5()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5.update(chunk)
        return md5.hexdigest()
