# Contributing

Contributions are welcome! This guide will help you get started.

## Ways to Contribute

- **Report bugs** - Open an issue describing the problem
- **Suggest features** - Open an issue with your idea
- **Improve documentation** - Fix typos, clarify instructions
- **Submit code** - Fix bugs or add features

## Development Setup

### Prerequisites

- [FreeCAD](https://www.freecadweb.org/) 0.21+ or 1.0+
- [mise](https://mise.jdx.dev/) - Tool version manager (optional but recommended)
- Python 3.11

### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/spkane/freecad-macro-cut-for-magnets.git
cd freecad-macro-cut-for-magnets

# Install mise (if not already installed)
curl https://mise.run | sh

# Install tools and setup pre-commit hooks
mise trust
mise install
just setup
```

### Running Quality Checks

```bash
# Run all pre-commit checks
just all

# Or run specific checks
just quality::lint          # Linting only
just quality::format        # Auto-format code
just quality::markdown-fix  # Fix markdown issues
```

## Code Style

- Follow [PEP 8](https://pep8.org/) for Python code
- Use [ruff](https://github.com/astral-sh/ruff) for linting and formatting
- Keep functions focused and well-documented
- Add comments for complex logic

## Pull Request Process

1. **Fork** the repository
2. **Create a branch** for your changes: `git checkout -b feature/my-feature`
3. **Make your changes** and commit them
4. **Run quality checks**: `just all`
5. **Push** to your fork
6. **Open a Pull Request** with a clear description

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```text
feat: add new feature
fix: resolve bug in hole placement
docs: update installation instructions
chore: update dependencies
```

## Testing

### Manual Testing

1. Install the macro in FreeCAD
2. Test with various object types and sizes
3. Verify hole placement is correct
4. Check that surface penetration detection works

### Test Cases to Cover

- [ ] Simple cube with XY plane cut
- [ ] Complex object with angled datum plane
- [ ] Thin-walled object (verify hole skipping)
- [ ] Very small object (verify minimum spacing)
- [ ] Large object with many holes

## Documentation

Documentation is built with [MkDocs](https://www.mkdocs.org/) and [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

```bash
# Serve documentation locally
just documentation::serve

# Build documentation
just documentation::build
```

## Questions?

- Open an issue for questions about contributing
- Check existing issues for similar discussions
