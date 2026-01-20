# Contributing to AIVE

Thank you for considering contributing to AIVE! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository**
   ```bash
   gh repo fork yourusername/aive --clone
   cd aive
   ```

2. **Set up development environment**
   ```bash
   # Install with dev dependencies
   uv sync --dev
   
   # Verify installation
   uv run python test_installation.py
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=aive

# Run specific test file
uv run pytest tests/test_models.py

# Run with verbose output
uv run pytest -v
```

### Code Quality

```bash
# Format code with black
uv run black src/ tests/ examples/

# Lint with ruff
uv run ruff check src/ tests/ examples/

# Type checking (if using mypy)
uv run mypy src/aive
```

### Project Structure

```
aive/
├── src/aive/          # Main package
│   ├── models.py         # Pydantic models
│   ├── manager.py        # Main manager class
│   ├── errors.py         # Custom exceptions
│   ├── engine/           # Rendering and actions
│   ├── storage/          # Storage backends
│   ├── utils/            # Utilities
│   └── server/           # MCP server
├── tests/                # Test suite
├── examples/             # Example scripts
├── templates/            # Project templates
└── docs/                 # Documentation (if applicable)
```

## Contribution Guidelines

### Adding New Features

1. **Write tests first** (TDD approach recommended)
   ```python
   # tests/test_new_feature.py
   def test_new_feature():
       # Test implementation
       pass
   ```

2. **Implement the feature**
   - Follow existing code style
   - Add docstrings
   - Handle errors appropriately

3. **Update documentation**
   - Add to README.md if user-facing
   - Update examples if relevant
   - Add docstrings to all public APIs

### Adding New Actions

To add a new video editing action:

```python
# src/aive/engine/actions.py

@ActionRegistry.register("your_action_name")
def your_action(context: ProjectState, **kwargs) -> ProjectState:
    """
    Description of what this action does.
    
    Args:
        context: Current project state
        **kwargs: Action-specific parameters
        
    Returns:
        Updated project state
    """
    # Implementation
    return context
```

Then add tests:

```python
# tests/test_actions.py

def test_your_action():
    project = ProjectState(name="Test", resolution=(1920, 1080), fps=30)
    # ... test implementation
```

### Adding New Templates

1. Create template JSON file:
   ```json
   // templates/your_template.json
   {
     "name": "Your Template",
     "resolution": [1920, 1080],
     "fps": 30,
     "clips": [],
     "background_color": [0, 0, 0]
   }
   ```

2. Test the template:
   ```python
   manager.load_template("your_template")
   ```

### Code Style

- Use **Black** for formatting (line length: 100)
- Use **Ruff** for linting
- Follow **PEP 8** conventions
- Write **clear, descriptive** variable names
- Add **type hints** to all functions
- Write **docstrings** for all public APIs

Example:
```python
def add_clip(
    self,
    clip_type: str,
    source: str,
    duration: float,
    start: float = 0.0,
    **kwargs
) -> Clip:
    """Add a clip to the project.
    
    Args:
        clip_type: Type of clip (video, audio, image, text)
        source: Path to media or text content
        duration: Duration in seconds
        start: Start time in timeline
        **kwargs: Additional parameters
        
    Returns:
        Created clip
        
    Raises:
        aiveError: If no active project
        AssetError: If source file not found
    """
```

### Testing Guidelines

- Aim for **>80% code coverage**
- Write **unit tests** for individual components
- Write **integration tests** for workflows
- Use **fixtures** for common test data
- Mock **external dependencies** (file I/O, network)

Example test structure:
```python
import pytest
from aive import VideoProjectManager

def test_feature_success():
    """Test successful operation."""
    manager = VideoProjectManager(storage_backend="memory")
    # ... test implementation
    assert expected == actual

def test_feature_error():
    """Test error handling."""
    with pytest.raises(aiveError, match="error message"):
        # ... test implementation
```

### Documentation

- Update README.md for new features
- Add examples to `examples/` directory
- Include docstrings in code
- Update CHANGELOG.md (if exists)

### Commit Messages

Follow conventional commits format:

```
type(scope): brief description

Longer description if needed.

Fixes #issue_number
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `style`: Formatting
- `chore`: Maintenance

Examples:
```
feat(actions): add video stabilization action
fix(renderer): handle missing audio tracks
docs(readme): update installation instructions
test(storage): add tests for JSON persistence
```

## Pull Request Process

1. **Update your branch**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Run all tests**
   ```bash
   uv run pytest
   ```

3. **Format and lint**
   ```bash
   uv run black src/ tests/
   uv run ruff check src/ tests/
   ```

4. **Push your changes**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Provide clear description
   - Reference related issues
   - Include screenshots/examples if applicable
   - Wait for review

### PR Checklist

- [ ] Tests pass locally
- [ ] Code is formatted with Black
- [ ] Linting passes with Ruff
- [ ] Documentation updated
- [ ] Examples added (if applicable)
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main

## Reporting Issues

### Bug Reports

Include:
- aive version
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/stack traces
- Minimal code example

### Feature Requests

Include:
- Use case description
- Proposed solution
- Alternative solutions considered
- Willingness to contribute

## Questions?

- Open a discussion on GitHub
- Check existing issues
- Review documentation

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

Thank you for contributing to aive! 🎬
