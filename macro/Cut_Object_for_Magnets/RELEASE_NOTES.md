# Cut Object for Magnets Macro Release Notes

## Version 0.6.2 (2026-01-18)

Release notes for changes between v0.6.1 and v0.6.2.

### Added

- **Save preferences**: New "Save choices as defaults" checkbox saves magnet hole settings
  - Settings persist across FreeCAD sessions using FreeCAD's parameter system
  - Saves: diameter, depth, hole count, and clearance values
  - Object to cut and cut plane settings are intentionally NOT saved (context-specific)
  - Stored in `User parameter:BaseApp/Preferences/Macros/CutObjectForMagnets`

### Changed

- **Proper FreeCAD Addon**: Release being added to <https://github.com/spkane/FreeCAD-addons>.
- **Dedicated repository**: Migrated to standalone GitHub repository for independent release cycles
  - New home: <https://github.com/spkane/freecad-macro-cut-for-magnets>
  - Updated all metadata URLs (`__Web__`, `__Wiki__`, `__Communication__`) to point to new repository
- **Modular architecture**: Refactored into separate modules for better maintainability and testability
  - `cut_magnets_core.py`: Core logic (can be unit tested without FreeCAD)
  - `cut_magnets_fc.py`: FreeCAD-specific code
  - `__init__.py`: Package initialization
  - FCMacro now imports from modules when available, falls back to embedded code for standalone use
- **Addon Manager compatible layout**: Restructured installation to work with FreeCAD Addon Manager
  - Installs to `Mod/` directory with `package.xml` metadata
  - Creates symlink in `Macro/` directory for macro menu visibility
  - Uses `os.path.realpath()` to resolve symlinks for proper module discovery
- **Improved test infrastructure**: Added comprehensive just command tests and pytest fixtures

### Fixed

- **PySide6 compatibility**: Changed `dialog.exec_()` to `dialog.exec()` to fix deprecation warning

## Version 0.6.1 (2026-01-12)

Release notes for changes between v0.5.0-beta and v0.6.1.

### Added

- **FreeCAD Addon Manager metadata**: Macro now includes standard metadata fields for better Addon Manager integration
- **FreeCAD Wiki page**: Official wiki documentation at [Macro Cut Object for Magnets](https://wiki.freecad.org/Macro_Cut_Object_For_Magnets)
- **Example images**: Added screenshots showing the dialog and example output

### Changed

- **Version tracking**: Version now managed via `__Version__` metadata field instead of inline comment

### Fixed

- **Ring-shaped objects**: Improved handling of inset point calculation for hollow/ring-shaped cut faces where the inset point could land in the hole
- **Code formatting**: Minor cleanup for consistent code style

### No Functional Changes

The core cutting algorithm, magnet hole placement, and collision detection remain unchanged from the beta release. This macro is stable for production use.

### Installation

**Via FreeCAD Addon Manager:**

1. Open FreeCAD
2. Go to Macro > Macros...
3. Click "Download" tab
4. Search for "Cut Object for Magnets"
5. Click Install

**Manual Installation:**

Copy `CutObjectForMagnets.FCMacro` to your FreeCAD macro directory:

- **macOS**: `~/Library/Application Support/FreeCAD/Macro/`
- **Linux**: `~/.local/share/FreeCAD/Macro/`
- **Windows**: `%APPDATA%/FreeCAD/Macro/`
