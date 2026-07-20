# Changelog

## 0.1.4

- Use system -devel libraries for leaf deps (NLopt, Qhull, OpenCV, OpenCASCADE)
- Added USE_SYSTEM_DEPS CMake option via patch to deps/CMakeLists.txt
- Added CMP0167 policy for CMake 4.x compatibility with FindBoost
- Added CMAKE_POLICY_DEFAULT_CMP0167=OLD to cmake invocation
- Cached podman build image (orcaslicer-build) for faster builds
- Removed -DSLIC3R_STATIC=1 to support shared system libraries
- Added runtime Requires for system shared libraries

## 0.1.3-2

- Reverted to single build-rpm.yml workflow
- Added bundled dependency sources (wxWidgets, libnoise, CGAL)
- Added symlink for resources path during post-build validation
- Copied patches to SOURCES in workflows, fixed nightly version sed

## 0.1.3

- Added COPR packaging for automated Fedora builds
- Simplified COPR Makefile (SRPM-only, no deps pre-build)
- Enabled network access for RPM builds in COPR
- Removed libquadmath-devel from COPR SRPM step (unavailable on aarch64)
- Added libquadmath-devel to spec BuildRequires (required on x86_64)
- Conditional deps skip in spec (uses pre-built deps when available)

## 0.1.2

- Fixed MimeType in .desktop file: corrected 3MF format identifier

## 0.1.1

- Fixed OOM: limited build parallelism to 2 jobs (GitHub Actions ~7GB RAM)
- Disabled workflow triggers on CHANGELOG.md and README.md changes
- Updated documentation

## 0.1.0

- Initial RPM packaging for OrcaSlicer
- GitHub Actions workflow for automated builds in Fedora 44 container
- Spec file with full dependency list for building from source
- Desktop integration (launcher script, .desktop file, icons)
