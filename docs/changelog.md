# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.1] - 2026-01-12

### Changed

- Split from monorepo into standalone repository
- Updated documentation URLs

## [0.5.0-beta] - 2026-01-05

### Added

- Initial release
- XY, XZ, YZ preset plane support
- Model plane support (datum planes and planar faces)
- Angled cut capability via datum planes
- Surface penetration detection
- Configurable hole parameters (diameter, depth, count)
- Progress tracking with progress bar
- Dual-part validation (validates holes work for both parts)
- Minimum spacing enforcement (2x diameter between holes)
- Smart hole repositioning when initial placement fails
- Object selection combo box
- Preferred and minimum edge clearance settings

### Technical

- Uses boolean operations for cutting
- Collision detection via test cylinder intersection
- Evenly distributes holes around cut face perimeter

---

## Version Numbering

This project uses [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible changes
- **MINOR** version for new features (backwards compatible)
- **PATCH** version for bug fixes (backwards compatible)

Pre-release versions use suffixes:

- `-alpha` - Early development, may have breaking changes
- `-beta` - Feature complete, testing phase
- `-rc.N` - Release candidate N
