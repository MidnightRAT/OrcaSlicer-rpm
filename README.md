# OrcaSlicer RPM

[![Build OrcaSlicer RPM](https://github.com/MidnightRAT/OrcaSlicer-rpm/actions/workflows/build-rpm.yml/badge.svg)](https://github.com/MidnightRAT/OrcaSlicer-rpm/actions/workflows/build-rpm.yml)
[![Latest Release](https://img.shields.io/github/v/release/MidnightRAT/OrcaSlicer-rpm)](https://github.com/MidnightRAT/OrcaSlicer-rpm/releases/latest)

RPM packaging for [OrcaSlicer](https://github.com/OrcaSlicer/OrcaSlicer) — open-source FDM slicer for 3D printers, built with **maximum use of system libraries** from Fedora `-devel` packages.

## Donate

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/redeyesnightrat)

## Dependency strategy

Where possible the package uses **system libraries** from Fedora 45 `-devel` packages:

- Python 3.12 (embedded interpreter), FFmpeg 9.0, Assimp 6.0.5, LibDataChannel 0.23,
  OCCT 7.9.3, Blosc, Boost 1.90 (static), CGAL 6.2.1, OpenCV 4.13, uv
- OpenSSL, libcurl, libpng, libjpeg-turbo, freetype, expat, zlib-ng (system ZLIB)
- Eigen3 5.0.1, cereal (header-only), GMP, MPFR, NLopt, Draco, Qhull, GLFW

> **CGAL.** OrcaSlicer 2.5 requires `find_package(CGAL 6.2)`, and Fedora 45 ships
> exactly CGAL 6.2.1 — so CGAL is used from the system. The deps patch keeps a
> version gate: a system CGAL older than 6.2 is rejected and the bundled
> CGAL 6.2.1 build is used as a fallback instead.

Only libraries with no compatible version in the distribution (or requiring custom patches) are **bundled** via `deps/`:

- wxWidgets 3.3.2 (Fedora has wxGTK 3.2), TBB 2021.5 (static),
  OpenVDB (custom `tamasmeszaros` fork) + OpenEXR 2.5.5 for it,
  libnoise, SolveSpace/SLVS, wxInspector

The system-detection logic lives in six patches:

- `patches/0001-deps-system-libraries.patch` — `deps/CMakeLists.txt` probes the
  system for the libraries above on non-Flatpak Linux builds and skips the
  bundled build for whatever is found (plus the CGAL ≥ 6.2 gate). If a package
  is missing the graph **falls back to the bundled build automatically**
  (fail-safe, no hard error). Also adds `cmake/modules/FindBlosc.cmake`,
  because Fedora only ships a `c-blosc-config.cmake` dummy config while
  OpenVDB needs a `Blosc::blosc` target.
- `patches/0002-bundled-deps-guard-depends.patch` — bundled `CGAL`/`Eigen`/
  `OpenVDB`/`MPFR` external projects only depend on the `dep_*` targets that
  actually exist; the rest (Boost/Eigen/GMP/MPFR/Blosc) come from the system
  and their targets are skipped.
- `patches/0003-main-python-boost-system.patch` — the main build uses the
  distribution's Python 3.12 (version range `3.12...3.13`, since a bare `3.12`
  means "≥ 3.12" and would pick python3.15) and system Boost
  (`Boost_NO_SYSTEM_PATHS FALSE`); `Python3_ROOT_DIR` is only pinned when the
  bundled CPython layout really exists.
- `patches/0004-main-opencv-occt-system.patch` — Fedora's OpenCV has no
  `opencv_world` target/lib (the bundled one did), so `src/libslic3r/CMakeLists.txt`
  links `${OpenCV_LIBRARIES}` (core/imgproc/imgcodecs); `OpenCASCADE_DIR` is
  only pinned when the bundled OCCT config is present in the deps prefix.
  The OCCT hunk is version-agnostic and applies to OrcaSlicer 2.5.0–2.5.2.
- `patches/0005-src-python-ffmpeg-install-guards.patch` — `INSTALL_RPATH` gets
  `$ORIGIN`, and the POST_BUILD libpython copy / FFmpeg `.so` `install()`s are
  guarded so they only run when the bundled Python/FFmpeg actually exists.
- `patches/0006-occt-7.9-boost-asio-compat.patch` — OCCT 7.9 (Fedora) compat:
  `Standard_Failure::what()` → `GetMessageString()`, the missing
  `GC_MakeSegment2d.hxx` → `GCE2d_MakeSegment`; Boost.Asio 1.90:
  `basic_resolver_iterator` → `basic_resolver_results::begin()`.
  Also disables `ORCA_BUILD_PYTHON_STUBGEN_MODULE` (static boost_log can't be
  linked into a shared module).

> **Build generator gotcha:** the main build must use **single-config Ninja**
> (`-G Ninja` + `-DCMAKE_BUILD_TYPE=Release`), **not** upstream's
> `Ninja Multi-Config`. Fedora's qhull/glfw package configs export imported
> targets with only a `NOCONFIG` configuration; a multi-config generator fails
> at configure-time validation with `IMPORTED_LOCATION not set`.

> **Packaging gotcha (`stb_dxt`):** the in-tree header-only mini-library
> `deps_src/stb_dxt/CMakeLists.txt` unconditionally runs `install()` that drops
> `include/stb_dxt/stb_dxt.h` and `lib/cmake/stb_dxt/stb_dxtTargets.cmake` into
> the install prefix. These build-only dev artifacts are **not** covered by the
> spec's `%files`, so `rpmbuild` aborts at the packaging phase with
> *"installed (but not packaged) files"*. The `%install` section removes
> `%{buildroot}/opt/OrcaSlicer/include` and `%{buildroot}/opt/OrcaSlicer/lib`
> before packaging, then recreates `lib/python` as the system-Python skeleton
> (see below).

### Embedded Python

The GUI embeds CPython 3.12. The bundled CPython build is skipped in favour of
Fedora's `python3.12` / `python3.12-devel`, and `%install` creates a skeleton
that satisfies the `python home` lookup in `PythonInterpreter.cpp` without
copying any interpreter files into the package:

```
/opt/OrcaSlicer/lib/python/lib/python3.12 -> /usr/lib64/python3.12
/opt/OrcaSlicer/lib/python/bin/python3.12 -> /usr/bin/python3.12
```

Python packages installed from the GUI go through the system `uv`
(`/usr/bin/uv`, baked in via `-DORCA_BUNDLED_UV_EXECUTABLE`).

## Installation

### From COPR (Fedora, Recommended)

```bash
sudo dnf copr enable chirikrat/OrcaSlicer-rpm
sudo dnf install orca-slicer
```

### From GitHub Release

Download the latest `orca-slicer-*.x86_64.rpm` (or `*.aarch64.rpm`) from [Releases](https://github.com/MidnightRAT/OrcaSlicer-rpm/releases) and install:

```bash
sudo dnf install orca-slicer-*.x86_64.rpm    # x86_64
sudo dnf install orca-slicer-*.aarch64.rpm   # aarch64
```

### Build from Source

```bash
# Bootstrap tools
sudo dnf install -y rpm-build rpmdevtools git git-lfs wget curl unzip

# Determine version and prepare the rpmbuild tree
VERSION=$(curl -sL https://api.github.com/repos/OrcaSlicer/OrcaSlicer/releases/latest \
  | grep -oE '"tag_name"[[:space:]]*:[[:space:]]*"[^"]*"' | head -n 1 \
  | cut -d '"' -f 4 | sed 's/^v//')
rpmdev-setuptree
wget -q "https://github.com/OrcaSlicer/OrcaSlicer/archive/refs/tags/v${VERSION}.tar.gz" \
  -O ~/rpmbuild/SOURCES/OrcaSlicer-${VERSION}.tar.gz
cp README.md ~/rpmbuild/SOURCES/
cp patches/0*.patch ~/rpmbuild/SOURCES/
sed -e "s/@VERSION@/${VERSION}/g" -e "s/@RELEASE@/1/g" \
  orca-slicer.spec > ~/rpmbuild/SPECS/orca-slicer.spec

# All BuildRequires come from the spec itself (single source of truth)
sudo dnf builddep -y ~/rpmbuild/SPECS/orca-slicer.spec

# Build: parallelism defaults to 2 (CI/COPR, 7 GB RAM); use 12 on a big box
rpmbuild -ba --define "orca_jobs 12" ~/rpmbuild/SPECS/orca-slicer.spec
```

> The `%build` downloads and builds the bundled `deps/` (needs network access);
> building takes a long time. System libraries are resolved at configure time
> from the `-devel` packages installed by `dnf builddep`.
>
> `rpmbuild -ba` produces **both** the SRPM (`~/rpmbuild/SRPMS/*.src.rpm`) and
> the binary RPM (`~/rpmbuild/RPMS/x86_64/*.x86_64.rpm`). Verify the artifacts
> with:
>
> ```bash
> rpmlint ~/rpmbuild/RPMS/x86_64/orca-slicer*.rpm   # 0 real errors
> rpm -qlp ~/rpmbuild/RPMS/x86_64/orca-slicer*.rpm  # file list
> ldd /opt/OrcaSlicer/bin/orca-slicer                # no "not found"
> /opt/OrcaSlicer/bin/orca-slicer --help             # smoke test
> ```
>
> > rpmlint reports `dir-or-file-in-opt` errors by design — the package installs
> > into `/opt/OrcaSlicer`; the remaining findings (`binary-or-shlib-defines-rpath`
> > for the intentional `$ORIGIN` RUNPATH, `dangling-symlink` for the absolute
> > system-Python symlinks, `files-duplicate`/`files-duplicated-waste`,
> > `unstripped-binary-or-object`) come from upstream web assets, the system-
> > Python skeleton and the intentional no-debug/no-strip choice in the spec.

## CI/CD

### GitHub Actions

Automatically:

1. Checks for new OrcaSlicer releases (weekly schedule)
2. Builds src.rpm and RPMs for **x86_64** (`ubuntu-latest`) and **aarch64**
   (`ubuntu-24.04-arm`) in Fedora 45 containers
   (`dnf builddep` installs everything the spec requires)
3. Uploads artifacts to GitHub Releases

### COPR

Automatically builds for Fedora 45 (**x86_64 and aarch64**) from the latest main branch:

- [COPR Project Page](https://copr.fedorainfracloud.org/coprs/chirikrat/OrcaSlicer-rpm/)

**Note:** Workflows do not trigger on changes to README.md or `.copr/**`.

## Project Structure

```
OrcaSlicer-rpm/
├── .copr/Makefile              # COPR SRPM build script
├── .github/workflows/          # GitHub Actions workflow
├── orca-slicer.spec            # RPM spec file (template: @VERSION@ / @RELEASE@ = 1)
├── patches/
│   ├── 0001-deps-system-libraries.patch
│   ├── 0002-bundled-deps-guard-depends.patch
│   ├── 0003-main-python-boost-system.patch
│   ├── 0004-main-opencv-occt-system.patch
│   ├── 0005-src-python-ffmpeg-install-guards.patch
│   └── 0006-occt-7.9-boost-asio-compat.patch
└── README.md
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full release history.

## License

AGPL-3.0 (same as OrcaSlicer)