# Changelog

## 0.2.1

- Use system -devel packages for 7 bundled dependencies (TBB, Blosc, NLopt, Cereal, GLEW, GMP, MPFR)
- Added USE_SYSTEM_LIBS cmake option to deps build system
- Switched main build to single-config Ninja generator
- Removed bundled CGAL/OpenCV/OCCT/OpenVDB from system deps list (API incompatibilities with Fedora 44 system versions)
- Removed bundled OpenEXR from system deps list (system 3.x lacks IlmBase::Half required by bundled FindOpenVDB)
- New BuildRequires: tbb-devel, blosc-devel, NLopt-devel, cereal-devel, glew-devel, gmp-devel, mpfr-devel

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
