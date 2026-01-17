# CLAUDE.md - AI Assistant Guidelines for This Project

## Project Overview

This is a FreeCAD macro that cuts a 3D object along a plane and adds aligned magnet holes to both pieces. It's designed for creating parts that snap together with magnets - perfect for 3D printing large objects that exceed printer bed size.

### Key Features

- Cut objects along XY, XZ, YZ planes or custom datum planes
- Automatically adds aligned magnet holes to both pieces
- Smart hole placement with configurable clearance
- Surface penetration detection to avoid holes breaking through outer surfaces

### Critical: Python Version Must Match FreeCAD

**CRITICAL**: This project **MUST** use the same Python version that the current stable FreeCAD release bundles internally. FreeCAD embeds a specific Python version (e.g., `libpython3.11.dylib`), and using a different Python version causes **fatal crashes** due to ABI incompatibility.

Before changing the Python version in `.mise.toml` or `pyproject.toml`:

1. Check which Python version FreeCAD bundles:
   - macOS: `ls /Applications/FreeCAD.app/Contents/Resources/lib/libpython*`
   - Linux: `ls /usr/lib/freecad/lib/libpython*` or check FreeCAD's Python console
1. The Python minor version (e.g., 3.11) **must match exactly**
1. Using Python 3.12+ with FreeCAD that bundles Python 3.11 will crash

Current requirement: **Python 3.11** (matching FreeCAD 1.0.x bundled Python)

---

## Project Structure

```text
freecad-macro-cut-for-magnets/
├── .github/workflows/        # CI/CD workflows
├── docs/                     # MkDocs documentation
├── just/                     # Just module files
├── macro/Cut_Object_for_Magnets/  # Main macro source
│   ├── __init__.py               # Package init (required for imports)
│   ├── CutObjectForMagnets.FCMacro  # Main macro file (GUI + entry point)
│   ├── cut_magnets_core.py       # Pure Python logic (no FreeCAD imports)
│   ├── cut_magnets_fc.py         # FreeCAD-dependent logic
│   ├── CutObjectForMagnets.svg   # Icon
│   └── README-CutObjectForMagnets.md
├── tests/
│   ├── unit/                 # pytest unit tests (no FreeCAD required)
│   ├── freecad/              # FreeCAD integration tests
│   └── just_commands/        # Just command tests
├── scripts/                  # Utility scripts
├── .pre-commit-config.yaml   # Pre-commit hooks
├── justfile                  # Task runner
├── mkdocs.yaml               # Documentation config
└── pyproject.toml            # Project configuration
```

---

## Macro Module Layout

### Why This Structure?

The macro is split into three layers to enable automated testing:

1. **cut_magnets_core.py** - Pure Python logic (vector math, parameter validation, clearance calculations). Testable with standard pytest - no FreeCAD installation required.

2. **cut_magnets_fc.py** - FreeCAD-dependent logic (cutting operations, boolean ops, shape handling). Testable inside FreeCAD using its test framework.

3. **CutObjectForMagnets.FCMacro** - GUI dialog and entry point. Imports from modules when available, falls back to embedded definitions for standalone use.

### Why `__init__.py` is Required

The `__init__.py` file makes the macro directory a proper Python package. This is required for:

- **Import resolution**: Allows `from cut_magnets_core import ...` to work
- **Package metadata**: Defines `__version__`, `__author__`, etc.
- **Test discovery**: pytest can properly discover and import modules
- **Consistency**: Both macro repos use the same structure

### Standalone Macro Support

When users install just the `.FCMacro` file (without the module files), the macro still works because:

```python
# In CutObjectForMagnets.FCMacro
_USE_MODULES = False
try:
    from cut_magnets_core import HolePlacementError
    _USE_MODULES = True
except ImportError:
    pass

if not _USE_MODULES:
    # Fallback: embedded definitions
    class HolePlacementError(Exception):
        pass
```

This fallback pattern ensures the macro works in both scenarios:

- **Development/Full install**: Uses modular code (testable)
- **Standalone install**: Uses embedded definitions (works without modules)

---

## Development Environment Setup

### Required Tools (managed via `mise`)

This project uses [`mise`](https://mise.jdx.dev/) for local development tool management. All tool versions are pinned in `.mise.toml`.

```bash
# Install mise via the Official mise installer script (if not already installed)
curl https://mise.run | sh

# Install all project tools
mise install

# Activate mise in your shell (add to .bashrc/.zshrc)
eval "$(mise activate bash)"  # or zsh/fish
```

### Package Management

This project uses `pip` for Python dependencies.

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install documentation dependencies
pip install -e ".[docs]"
```

### Workflow Commands (via `just`)

This project uses [`just`](https://just.systems/) as a command runner.

```bash
# List all commands and modules
just
just list-all

# List commands in specific modules
just list-dev           # Development utilities
just list-documentation # Documentation commands
just list-install       # Installation commands
just list-quality       # Code quality commands
just list-release       # Release commands
just list-testing       # Test commands

# Common workflows
just setup              # Full dev setup (install pre-commit hooks)
just all                # Run all quality checks

# Quality commands
just quality::check     # Run all pre-commit checks
just quality::format    # Format code with ruff
just quality::lint      # Run linting

# Documentation commands
just documentation::build  # Build documentation
just documentation::serve  # Serve locally at http://localhost:8000
```

---

## Code Quality Standards

### Pre-commit Hooks

**CRITICAL**: This project uses `pre-commit` for all code quality checks. Before finishing ANY code changes:

1. Run `just quality::check` or `pre-commit run --all-files`
1. Fix ALL issues reported
1. Re-run until all checks pass

Pre-commit runs these checks:

**Python Quality:**

- **Ruff**: Linting and import sorting
- **Ruff Format**: Code formatting
- **Bandit**: Security vulnerability scanning

**Secrets Detection:**

- **Gitleaks**: Fast regex-based secrets scanning
- **detect-secrets**: Baseline tracking for known/approved secrets

**Documentation & Config:**

- **Markdownlint**: Markdown linting with auto-fix
- **Codespell**: Spell checking in code and docs
- **YAML/JSON validation**: Config file validation

**Infrastructure:**

- **Actionlint**: GitHub Actions workflow linting
- **check-github-workflows**: GitHub workflow schema validation

### Linting Rules

- Follow PEP 8 style guidelines
- Use type hints for function signatures
- Maximum line length: 120 characters
- Use modern Python syntax (3.11+ features)

### Running Pre-commit on Specific Files

**IMPORTANT**: After editing any files, always run pre-commit hooks:

```bash
# Run pre-commit on specific files
pre-commit run --files path/to/file1.py path/to/file2.py

# Or run on all files
pre-commit run --all-files
```

---

## Testing

The macro has a hybrid testing approach with unit tests (pytest) and FreeCAD integration tests.

### Project Structure for Testing

```text
freecad-macro-cut-for-magnets/
├── macro/Cut_Object_for_Magnets/
│   ├── CutObjectForMagnets.FCMacro  # Main macro
│   ├── cut_magnets_core.py          # Pure Python logic (testable)
│   └── cut_magnets_fc.py            # FreeCAD-dependent operations
└── tests/
    ├── unit/                         # pytest tests for core logic
    │   └── test_core.py
    ├── freecad/                      # FreeCAD integration tests
    │   └── test_cut_magnets.py
    └── just_commands/                # Just command tests
        ├── conftest.py               # Shared fixtures
        └── test_*.py                 # Tests for each just module
```

### Running Tests

```bash
# Run unit tests (no FreeCAD required)
just testing::unit

# Run unit tests with coverage
just testing::unit-cov

# Run FreeCAD integration tests (requires FreeCAD)
just testing::freecad

# Run all tests
just testing::all

# Install test dependencies
just testing::install

# Run just command syntax tests (fast)
just testing::just-syntax

# Run just command runtime tests
just testing::just-runtime

# Run all just command tests
just testing::just-all

# Run full release test suite
just testing::release-test
```

### Writing Tests

- **Unit tests**: Add to `tests/unit/test_core.py` for pure Python logic
- **FreeCAD tests**: Add to `tests/freecad/test_cut_magnets.py` for FreeCAD operations
- **Just command tests**: Add to `tests/just_commands/test_<module>.py` for just commands

### Just Command Tests

The `tests/just_commands/` directory contains tests that verify all just commands work correctly:

- **Syntax tests** (`just_syntax` marker): Validate commands parse correctly using `--dry-run`
- **Runtime tests** (`just_runtime` marker): Actually execute commands and verify behavior

This ensures changes to the justfile or just modules don't break existing commands.

---

## Documentation

### Building Documentation

```bash
just documentation::build  # Build documentation
just documentation::serve  # Serve locally at http://localhost:8000
```

Documentation is built with MkDocs and deployed to GitHub Pages.

### GitHub Pages Deployment

This repo uses **artifact-based deployment** (`actions/deploy-pages@v4`), which does **not** require a `gh-pages` branch.

**Initial Setup** (one-time):

1. Go to repo **Settings** → **Pages**
2. Under **Build and deployment** → **Source**, select **"GitHub Actions"**
3. Save

**Deployment triggers**:

- Push to `main` branch (if docs paths changed)
- Manual trigger via **Actions** → **Documentation** → **Run workflow**

The workflow builds MkDocs and deploys directly via GitHub's artifact system. No branch management required.

---

## File Extension Conventions

**Use full file extensions, not DOS-style shortened versions:**

| Correct Extension | Incorrect (DOS-style) |
| ----------------- | --------------------- |
| `.yaml`           | `.yml`                |
| `.jpeg`           | `.jpg`                |
| `.html`           | `.htm`                |

---

## Macro Parameters Reference

### Plane Settings

| Parameter    | Values        | Description                           |
| ------------ | ------------- | ------------------------------------- |
| Plane Type   | Preset/Model  | Choose between preset or model plane  |
| Preset Plane | XY, XZ, YZ    | Axis-aligned cut planes               |
| Offset       | mm            | Distance from origin for preset plane |

### Hole Parameters

| Parameter             | Default | Description                              |
| --------------------- | ------- | ---------------------------------------- |
| Diameter              | 6.2mm   | Hole diameter (add clearance for magnet) |
| Depth                 | 3.0mm   | How deep holes go into each piece        |
| Number of Holes       | 6       | Total holes (evenly distributed)         |
| Edge Clearance (Pref) | 2.0mm   | Ideal distance from hole to outer edge   |
| Edge Clearance (Min)  | 0.5mm   | Absolute minimum clearance               |

---

## Macro Installation

### Quick Install (via just commands)

The easiest way to install the macro locally:

```bash
just install::macro     # Install macro to FreeCAD
just install::status    # Check installation status
just install::uninstall # Remove macro from FreeCAD
just install::cleanup   # Alias for uninstall
```

The install commands automatically detect FreeCAD's location based on your OS:

- **macOS**: `~/Library/Application Support/FreeCAD/`
- **Linux**: `~/.local/share/FreeCAD/`
- **Windows**: `%APPDATA%/FreeCAD/`

For FreeCAD 1.x+, the commands also detect versioned directories (e.g., `v1-1`, `v1-2`).

### Other Installation Methods

1. **Addon Manager**: Search for "Cut Object for Magnets" in FreeCAD's Addon Manager
2. **Manual**: Copy `CutObjectForMagnets.FCMacro` to FreeCAD's Macro folder

---

## Release Process

Releases follow a two-step process: bump, then tag.

### Step 1: Bump Version

```bash
# Update version in all source files
just release::bump 1.0.0

# Review changes
git diff

# Commit
git add -A && git commit -m "chore: bump to 1.0.0"
```

The bump command updates:

- `macro/Cut_Object_for_Magnets/CutObjectForMagnets.FCMacro` (`__version__`)
- `package.xml` (`<version>` and `<date>`)
- `macro/Cut_Object_for_Magnets/wiki-source.txt` (`|Version=` and `|Date=`)

### Step 2: Create Release Tag

```bash
# Create and push the tag (triggers GitHub workflow)
just release::tag 1.0.0
```

The tag command:

1. Verifies version in source files matches the tag
2. Creates annotated git tag
3. Pushes tag to origin
4. Triggers GitHub Actions release workflow

### Release Commands

```bash
just release::bump 1.0.0     # Update version in source files
just release::tag 1.0.0      # Create and push release tag
just release::version        # Show current version
just release::list-tags      # List all release tags
just release::latest-tag     # Show latest release tag
```

### Update FreeCAD Wiki (After Release)

```bash
just release::wiki-diff      # Check differences from live wiki
just release::wiki-show      # View wiki source content
just release::wiki-update    # Copy to clipboard & open wiki edit page
```

---

## Summary Checklist

When working on this project, ALWAYS:

- [ ] Use `mise` for tool management
- [ ] Use `just` commands for workflows
- [ ] Write docstrings for all functions
- [ ] Run `just all` before finishing - everything must pass
- [ ] Run `just testing::unit` to verify unit tests pass
- [ ] Test manually in FreeCAD for UI changes
- [ ] Update RELEASE_NOTES.md before releases
