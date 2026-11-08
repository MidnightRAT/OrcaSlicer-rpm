# Changelog

All notable changes to the OrcaSlicer RPM packaging project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- (none yet)

## [2.5.0-7] — 2026-11-08

### Changed
- Adapted packaging to **OrcaSlicer 2.5.0** and **Fedora 45** libraries.
- System libraries now used instead of bundled builds: Python 3.12, FFmpeg 9.0,
  Assimp 6.0.5, LibDataChannel 0.23.1, OCCT 7.9.3, Blosc 1.21.6, Boost 1.90
  (static), CGAL 6.2.1, OpenCV 4.13, uv (plus the pre-existing system set).
- Bundled only: wxWidgets 3.3, TBB (static), custom OpenVDB fork + OpenEXR 2.5.5,
  libnoise, SolveSpace/SLVS, wxInspector.
- CGAL now comes from the system (OrcaSlicer 2.5 requires `find_package(CGAL 6.2)`);
  the deps gate rejects system CGAL older than 6.2 and falls back to the bundled
  build otherwise.
- Removed `glew-devel` / OpenCSG (dropped upstream in 2.5.0).
- Parallelism moved into the `orca_jobs` RPM macro (default 2 for CI/COPR;
  local builds use `--define "orca_jobs 12"`).
- LTO disabled (`_lto_cflags`/`_lto_ldflags` set to empty): Fedora's auto-LTO
  exhausted `/tmp` during linking.
- Python stubgen module disabled (`ORCA_BUILD_PYTHON_STUBGEN_MODULE=OFF`): the
  static `boost_log` cannot be linked into a shared module.
- CI workflow: Fedora 45 container, `dnf builddep` instead of a duplicated
  dependency list, `RELEASE=7`.
- COPR Makefile: `RELEASE=7`.

### Added
- Embedded-Python skeleton under `/opt/OrcaSlicer/lib/python` using symlinks to
  the system Python 3.12 installation (`/usr/lib64/python3.12`,
  `/usr/bin/python3.12`) — no bundled CPython.
- Six patches (see `patches/`): system-library detection with CGAL ≥ 6.2 gate and
  `cmake/modules/FindBlosc.cmake`; conditional `DEPENDS` in bundled deps;
  system Python 3.12 (version range `3.12...3.13`) and Boost; system OpenCV/OCCT;
  guarded `install()`/`POST_BUILD` for bundled Python/FFmpeg; OCCT 7.9 / Boost.Asio
  1.90 compatibility shims.

### Fixed
- `Standard_Failure::what()` → `GetMessageString()` for OCCT 7.9.
- Missing `GC_MakeSegment2d.hxx` → `GCE2d_MakeSegment` on OCCT < 8.
- `boost::asio::ip::basic_resolver_iterator` → `basic_resolver_results::begin()`
  for Boost.Asio 1.90.
- `find_package(Python3 3.12)` (bare) replaced with the range `3.12...3.13`,
  since a bare `3.12` means "≥ 3.12" and would select python3.15.
- `opencv_world` → `${OpenCV_LIBRARIES}` (system OpenCV has no `opencv_world`).
- `OpenCASCADE_DIR` only pinned when the bundled OCCT config exists.
- `install()`/`POST_BUILD` libpython copy and FFmpeg `.so` installs guarded to
  run only when the bundled artifacts exist.

## [2.4.2-6] — 2026-08-09

### Added
- Initial RPM packaging of OrcaSlicer for Fedora (COPR).
- `deps/CMakeLists.txt`: maximum use of system `-devel` libraries (OpenSSL,
  libcurl, libpng, libjpeg-turbo, freetype, expat, zlib-ng, Eigen3, CGAL,
  cereal, GMP, MPFR, NLopt, Draco, Qhull, GLFW, OpenCV) with fallback to the
  bundled build when a package is missing.
- Bundled only: Boost, wxWidgets, OpenVDB, OCCT, OpenEXR, TBB, Blosc, GLEW,
  OpenCSG, libnoise.
- Installation into `/opt/OrcaSlicer` with desktop/icon integration.
