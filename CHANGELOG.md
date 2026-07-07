# Changelog

## 0.1.1

- Fixed OOM: limited build parallelism to 2 jobs (GitHub Actions ~7GB RAM)
- Disabled workflow triggers on CHANGELOG.md and README.md changes
- Updated documentation

## 0.1.0

- Initial RPM packaging for OrcaSlicer
- GitHub Actions workflow for automated builds in Fedora 44 container
- Spec file with full dependency list for building from source
- Desktop integration (launcher script, .desktop file, icons)
