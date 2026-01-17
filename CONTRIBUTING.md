# Contributing to PlotSenseAI

Thank you for your interest in contributing to PlotSenseAI! 🎉

We welcome contributions of all kinds: bug fixes, new features, documentation improvements, and more.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Issue Guidelines](#issue-guidelines)

## Code of Conduct

Be respectful and inclusive. We're all here to learn and build something great together.

## Getting Started

> **💡 Tip**: We recommend using [uv](https://docs.astral.sh/uv/) for dependency management. It's 10-100x faster than pip and provides better dependency resolution. All commands below show both uv and pip options.

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/PlotSenseAI.git
cd PlotSenseAI
```

### 2. Set Up Development Environment

**Python Backend:**

**Using uv (Recommended - 10-100x faster):**

```bash
# Install uv if not already installed
# Visit https://docs.astral.sh/uv/getting-started/installation/
# Or run: curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync all dependencies including dev extras
uv sync --all-extras

# Activate the virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install pre-commit hooks
uv run pre-commit install
```

**Using pip (Traditional):**

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e .
pip install pytest pytest-cov pytest-mock flake8 autopep8 pre-commit bandit

# Install pre-commit hooks
pre-commit install
```

**Frontend (Optional):**

```bash
cd web
npm install
```

### 3. Set Up API Keys

```bash
# Create a .env file
echo "GROQ_API_KEY=your-api-key-here" > .env
```

Get your free API key from [Groq Cloud](https://console.groq.com/home).

## Development Workflow

### Branching Strategy

We use the following branch structure:

- **`main`** - Production-ready code
- **`dev`** - Active development branch
- **`feature/<feature-name>`** - New features
- **`fix/<bug-name>`** - Bug fixes
- **`docs/<doc-name>`** - Documentation updates

### Creating a Feature Branch

```bash
# Make sure you're on dev and up to date
git checkout dev
git pull origin dev

# Create your feature branch
git checkout -b feature/your-feature-name
```

### Making Changes

1. **Write your code** following our coding standards
2. **Add tests** for new functionality
3. **Run tests** to ensure everything works
4. **Update documentation** if needed
5. **Commit your changes** with descriptive messages

## Coding Standards

### Python

We follow PEP 8 with some modifications:

- **Line length**: 150 characters (configured in `setup.cfg`)
- **Docstrings**: Use Google-style docstrings
- **Type hints**: Add type hints to function signatures
- **Imports**: Organize imports (stdlib, third-party, local)

**Example:**

```python
from typing import Optional
import pandas as pd
from plotsense.module import helper


def process_dataframe(
    df: pd.DataFrame,
    column: str,
    threshold: Optional[float] = None
) -> pd.DataFrame:
    """
    Process DataFrame by filtering on a column.

    Args:
        df: Input DataFrame to process.
        column: Column name to filter on.
        threshold: Optional threshold value for filtering.

    Returns:
        Filtered DataFrame.

    Raises:
        ValueError: If column doesn't exist in DataFrame.
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found")
    # Implementation
    return df
```

### TypeScript/React

- Follow ESLint rules (configured in `web/eslint.config.js`)
- Use functional components with TypeScript
- Prefer const over let
- Use meaningful variable names

**Example:**

```typescript
import { useState } from 'react';

interface Props {
  title: string;
  onAction: () => void;
}

export function Component({ title, onAction }: Props) {
  const [isActive, setIsActive] = useState(false);

  return (
    <div>
      <h1>{title}</h1>
      <button onClick={onAction}>Click me</button>
    </div>
  );
}
```

## Testing Requirements

### Python Testing

**All PRs must include tests.** We use pytest.

#### Running Tests

**Using uv:**

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=plotsense --cov-report=html

# Run specific test file
uv run pytest test/test_plotgen.py

# Run specific test
uv run pytest test/test_plotgen.py::TestPlotFunctions::test_create_scatter

# Run by marker
uv run pytest -m unit            # Unit tests only
uv run pytest -m "not slow"      # Skip slow tests
```

**Using pip/pytest directly:**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=plotsense --cov-report=html

# Run specific test file
pytest test/test_plotgen.py

# Run specific test
pytest test/test_plotgen.py::TestPlotFunctions::test_create_scatter

# Run by marker
pytest -m unit            # Unit tests only
pytest -m "not slow"      # Skip slow tests
```

#### Writing Tests

```python
import pytest
from plotsense import plotgen


class TestYourFeature:
    """Test suite for your feature."""

    @pytest.mark.unit
    def test_basic_functionality(self, sample_dataframe):
        """Test that basic functionality works."""
        result = your_function(sample_dataframe)
        assert result is not None

    def test_error_handling(self):
        """Test that errors are raised appropriately."""
        with pytest.raises(ValueError):
            your_function(invalid_input)
```

**Use fixtures from `test/conftest.py`:**

- `sample_dataframe`: Standard 100-row DataFrame
- `small_dataframe`: 20-row DataFrame
- `large_dataframe`: 1000-row DataFrame
- `mock_groq_client`: Mocked API client

#### Coverage Requirements

- **Minimum**: 70% line and branch coverage
- **Target**: 80%+ for new code
- PRs that decrease coverage may be rejected

### Frontend Testing

**Component tests are required for UI changes.**

```bash
cd web

# Run tests
npm test

# Run with coverage
npm run test:coverage

# Run with UI
npm run test:ui
```

#### Writing Component Tests

```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { YourComponent } from './YourComponent'


describe('YourComponent', () => {
  it('should render correctly', () => {
    render(<YourComponent title="Test" />)
    expect(screen.getByText('Test')).toBeInTheDocument()
  })

  it('should handle user interaction', async () => {
    const user = userEvent.setup()
    const handleClick = vi.fn()

    render(<YourComponent onClick={handleClick} />)
    await user.click(screen.getByRole('button'))

    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
```

### Pre-commit Checks

Before committing, ensure:

**Using uv:**

```bash
# Pre-commit hooks pass
uv run pre-commit run --all-files

# Python linting
uv run flake8 plotsense

# Python security
uv run bandit -r plotsense

# Tests pass
uv run pytest -v

# Frontend (if applicable)
cd web
npm run lint
npx tsc --noEmit
npm test
```

**Using pip:**

```bash
# Pre-commit hooks pass
pre-commit run --all-files

# Python linting
flake8 plotsense

# Python security
bandit -r plotsense

# Tests pass
pytest -v

# Frontend (if applicable)
cd web
npm run lint
npx tsc --noEmit
npm test
```

## Pull Request Process

### 1. Ensure Your PR is Ready

- [ ] All tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] Branch is up to date with `dev`

### 2. Create Pull Request

1. Push your branch to GitHub
2. Open a Pull Request against `dev` (not `main`)
3. Fill out the PR template completely
4. Link related issues
5. Request review from maintainers

### 3. PR Review Process

- CI/CD checks must pass
- At least one maintainer review required
- Address all review comments
- Maintain a respectful dialogue

### 4. After Approval

- Squash commits if requested
- Ensure final tests pass
- Maintainer will merge to `dev`
- Feature will be included in next release

## Commit Message Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/).

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Adding/updating tests
- **build**: Build system changes
- **ci**: CI/CD changes
- **chore**: Maintenance tasks

### Examples

```bash
# Good commit messages
feat(recommender): add support for time series data
fix(plotgen): handle NaN values in scatter plots
docs(testing): update pytest configuration guide
test(explainer): add edge case tests for empty plots

# Bad commit messages
update code
fix bug
changes
wip
```

### Commit Message Best Practices

- Use present tense ("add feature" not "added feature")
- Use imperative mood ("move cursor to..." not "moves cursor to...")
- Keep subject line under 72 characters
- Reference issues and PRs in footer: "Closes #123"

## Issue Guidelines

### Before Creating an Issue

1. Search existing issues to avoid duplicates
2. Check if it's already fixed in `dev` branch
3. Gather all relevant information

### Bug Reports

Use the bug report template and include:

- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Full error traceback
- Environment details
- Minimal reproducible example

### Feature Requests

Use the feature request template and include:

- Problem statement
- Proposed solution
- Example usage
- Benefits
- Alternatives considered

### Questions

Use the question template for:

- Usage questions
- Clarification requests
- Best practices discussions

## Development Tips

### Running Specific Tests During Development

**Using uv:**

```bash
# Stop on first failure
uv run pytest -x

# Show print statements
uv run pytest -s

# Verbose output
uv run pytest -vv
```

**Using pip:**

```bash
# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Verbose output
pytest -vv
```

### Debugging Tests

**Using uv:**

```bash
# Drop into debugger on failure
uv run pytest --pdb

# Show local variables
uv run pytest -l
```

**Using pip:**

```bash
# Drop into debugger on failure
pytest --pdb

# Show local variables
pytest -l
```

### Code Coverage

**Using uv:**

```bash
# Generate HTML coverage report
uv run pytest --cov=plotsense --cov-report=html
# Open htmlcov/index.html in browser

# Show missing lines
uv run pytest --cov=plotsense --cov-report=term-missing
```

**Using pip:**

```bash
# Generate HTML coverage report
pytest --cov=plotsense --cov-report=html
# Open htmlcov/index.html in browser

# Show missing lines
pytest --cov=plotsense --cov-report=term-missing
```

### Linting Auto-fix

**Using uv:**

```bash
# Auto-fix Python formatting issues
uv run autopep8 --in-place --recursive plotsense/

# Auto-fix frontend issues
cd web && npm run lint -- --fix
```

**Using pip:**

```bash
# Auto-fix Python formatting issues
autopep8 --in-place --recursive plotsense/

# Auto-fix frontend issues
cd web && npm run lint -- --fix
```

## Getting Help

- **Questions**: Open a question issue or discussion
- **Bugs**: Open a bug report
- **Feature Ideas**: Open a feature request
- **Chat**: <!-- Add link to Discord/Slack if available -->

## Recognition

Contributors will be:

- Listed in project contributors
- Mentioned in release notes
- Given credit in relevant documentation

Thank you for contributing to PlotSenseAI! 🚀

---

For detailed testing documentation, see [TESTING.md](TESTING.md).
