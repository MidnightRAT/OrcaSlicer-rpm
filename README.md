# OrcaSlicer RPM

[![Build OrcaSlicer RPM](https://github.com/MidnightRAT/OrcaSlicer-rpm/actions/workflows/build-rpm.yml/badge.svg)](https://github.com/MidnightRAT/OrcaSlicer-rpm/actions/workflows/build-rpm.yml)
[![Latest Release](https://img.shields.io/github/v/release/MidnightRAT/OrcaSlicer-rpm)](https://github.com/MidnightRAT/OrcaSlicer-rpm/releases/latest)

RPM packaging for [OrcaSlicer](https://github.com/OrcaSlicer/OrcaSlicer) — open-source FDM slicer for 3D printers, built with **maximum use of system libraries** from Fedora `-devel` packages.

## Donate

[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support%20me%20on%20Ko--fi-ff5e5b?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/redeyesnightrat)

## Dependency strategy

Where possible the package uses **system libraries** from Fedora `-devel` packages:

- OpenSSL, libcurl, libpng, libjpeg-turbo, freetype, expat, zlib-ng
- Eigen3, cereal (header-only)
- GMP, MPFR, NLopt, Draco, Qhull, GLFW, OpenCV

> **CGAL is a special case.** Fedora ships CGAL 6.1.x, but CGAL ≥ 6 changed the
> `Surface_mesh::property_map` API (returns `std::optional` instead of a pair),
> and OrcaSlicer 2.4.2 was written against the bundled CGAL 5.6.3 — building with
> system CGAL 6 breaks `CutSurface.cpp`. The deps patch probes the system CGAL
> and **rejects any version ≥ 6.0**, falling back to the bundled CGAL 5.6.3 build.

Only libraries with no compatible version in the distribution (or requiring custom patches) are **bundled** via `deps/`:

- Boost 1.84, wxWidgets 3.3.2, OpenVDB (custom `tamasmeszaros` fork), OCCT 7.6.0,
  OpenEXR 2.5.5, TBB 2021.5, Blosc, GLEW, OpenCSG, libnoise, **CGAL 5.6.3**

The system-detection logic lives in three patches:

- `patches/0001-deps-system-libraries.patch` — `deps/CMakeLists.txt` probes the
  system for the libraries above on non-Flatpak Linux builds and skips the
  bundled build for whatever is found (plus the CGAL ≥ 6.0 gate). If a package
  is missing the graph **falls back to the bundled build automatically**
  (fail-safe, no hard error).
- `patches/0002-cgal-bundled-depends.patch` — bundled CGAL's external project
  only depends on `dep_Boost`; Eigen/GMP/MPFR come from the system and their
  `dep_*` targets may not exist.
- `patches/0003-main-opencv-system.patch` — Fedora's OpenCV has no
  `opencv_world` target/lib (the bundled one did), so `src/libslic3r/CMakeLists.txt`
  links `${OpenCV_LIBRARIES}` (core/imgproc/imgcodecs) and adds the include dir.

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
> before packaging.

## Installation

### From COPR (Fedora, Recommended)

```bash
sudo dnf copr enable chirikrat/OrcaSlicer-rpm
sudo dnf install orca-slicer
```

### From GitHub Release

Download the latest `orca-slicer-*.x86_64.rpm` from [Releases](https://github.com/MidnightRAT/OrcaSlicer-rpm/releases) and install:

```bash
sudo dnf install orca-slicer-*.x86_64.rpm
```

### Build from Source

```bash
# Install build tools
sudo dnf install -y rpm-build rpmdevtools git git-lfs wget curl \
  cmake ninja-build gcc gcc-c++ make patch pkgconf \
  autoconf automake libtool m4 \
  perl-FindBin perl-IPC-Cmd \
  texinfo gettext python3 \
  boost-devel eigen3-devel tbb-devel \
  glfw-devel glew-devel NLopt-devel CGAL-devel cereal-devel \
  gmp-devel mpfr-devel qhull-devel draco-devel draco-static \
  zlib-ng-compat-devel libpng-devel expat-devel freetype-devel \
  libjpeg-turbo-devel openssl-devel libcurl-devel opencv-devel blosc-devel \
  dbus-devel gtk3-devel webkit2gtk4.1-devel \
  mesa-libGLU-devel mesa-libGL-devel libglvnd-devel \
  wayland-devel wayland-protocols-devel eglexternalplatform-devel \
  extra-cmake-modules libsecret-devel \
  gstreamer1-devel gstreamer1-plugins-good gstreamermm-devel \
  libspnav-devel libmspack-devel libquadmath-devel fontconfig-devel \
  desktop-file-utils

# Determine version and build RPM
VERSION=$(curl -sL https://api.github.com/repos/OrcaSlicer/OrcaSlicer/releases/latest | grep tag_name | cut -d '"' -f 4 | sed 's/^v//')
rpmdev-setuptree
wget -q "https://github.com/OrcaSlicer/OrcaSlicer/archive/refs/tags/v${VERSION}.tar.gz" \
  -O ~/rpmbuild/SOURCES/OrcaSlicer-${VERSION}.tar.gz
cp README.md ~/rpmbuild/SOURCES/
cp patches/0*.patch ~/rpmbuild/SOURCES/
sed -e "s/@VERSION@/${VERSION}/g" -e "s/@RELEASE@/5/g" \
  orca-slicer.spec > ~/rpmbuild/SPECS/orca-slicer.spec
rpmbuild -ba ~/rpmbuild/SPECS/orca-slicer.spec
```

> The `%prep`/`%build` downloads and builds the bundled `deps/` (needs network
> access and lots of RAM); building takes a long time. System libraries are
> resolved at configure time from the `-devel` packages listed above.
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
> > into `/opt/OrcaSlicer`; remaining warnings (`files-duplicate`,
> > `unstripped-binary-or-object`) come from upstream web assets and the
> > intentional no-debug/no-strip choice in the spec.

## CI/CD

### GitHub Actions

Automatically:

1. Checks for new OrcaSlicer releases (weekly schedule)
2. Builds src.rpm and x86_64.rpm in Fedora 44 container
3. Uploads artifacts to GitHub Releases

### COPR

Automatically builds for Fedora 43+ from the latest main branch:

- [COPR Project Page](https://copr.fedorainfracloud.org/projects/chirikrat/OrcaSlicer-rpm/)

**Note:** Workflows do not trigger on changes to README.md or `.copr/**`.

## Project Structure

```
OrcaSlicer-rpm/
├── .copr/Makefile              # COPR SRPM build script
├── .github/workflows/          # GitHub Actions workflow
├── orca-slicer.spec            # RPM spec file
├── patches/
│   ├── 0001-deps-system-libraries.patch
│   ├── 0002-cgal-bundled-depends.patch
│   └── 0003-main-opencv-system.patch
└── README.md
```

## License

AGPL-3.0 (same as OrcaSlicer)