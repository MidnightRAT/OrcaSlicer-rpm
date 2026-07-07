# OrcaSlicer RPM

[![Build OrcaSlicer RPM](https://github.com/MidnightRAT/OrcaSlicer-rpm/actions/workflows/build-rpm.yml/badge.svg)](https://github.com/MidnightRAT/OrcaSlicer-rpm/actions/workflows/build-rpm.yml)
[![Latest Release](https://img.shields.io/github/v/release/MidnightRAT/OrcaSlicer-rpm)](https://github.com/MidnightRAT/OrcaSlicer-rpm/releases/latest)

RPM packaging for [OrcaSlicer](https://github.com/OrcaSlicer/OrcaSlicer) — open-source slicer for FDM 3D printers.

## Donate

[![Donate via WayForPay](https://img.shields.io/badge/Donate-WayForPay-blue?style=for-the-badge)](https://secure.wayforpay.com/donate/d29145e2b8e3c)

## What is OrcaSlicer?

OrcaSlicer is an open-source slicer compatible with most FDM printers. Based on PrusaSlicer/BambuStudio, supporting STL, OBJ, 3MF file formats.

## Features

- Automated RPM builds via GitHub Actions
- Builds against latest OrcaSlicer releases
- Includes all required dependencies
- Desktop integration with icons and .desktop file
- Support for Fedora 44+
- Correct MIME types for STL, OBJ, and 3MF file associations

## Installation

### From GitHub Release (Recommended)

Download the latest `orcaslicer-*.x86_64.rpm` from [Releases](https://github.com/MidnightRAT/OrcaSlicer-rpm/releases) and install:

```bash
sudo dnf install orcaslicer-*.x86_64.rpm
```

### Build from Source

```bash
# Install build dependencies (Fedora 44)
sudo dnf install -y rpm-build rpmdevtools git wget curl unzip \
  cmake ninja-build gcc gcc-c++ pkgconf \
  autoconf automake libtool m4 \
  perl-FindBin perl-IPC-Cmd \
  libquadmath-devel nasm \
  dbus-devel gtk3-devel webkit2gtk4.1-devel \
  glew-devel glfw-devel mesa-libGLU-devel mesa-libGL-devel \
  libjpeg-turbo-devel libpng-devel \
  openssl-devel libcurl-devel \
  freetype-devel fontconfig-devel pango-devel \
  eigen3-devel cereal-devel \
  extra-cmake-modules eglexternalplatform-devel \
  gstreamer1-devel gstreamer1-plugins-base-devel gstreamermm-devel \
  wayland-protocols-devel libxkbcommon-devel \
  libX11-devel libXi-devel libXrandr-devel libXinerama-devel \
  libXcursor-devel libXcomposite-devel libXdamage-devel libXext-devel \
  libXtst-devel libXfixes-devel libXmu-devel \
  at-spi2-core-devel libepoxy-devel \
  libspnav-devel libsecret-devel libmspack-devel \
  texinfo chrpath

# Build RPM
rpmbuild -ba orcaslicer.spec
```

## CI/CD

GitHub Actions automatically:

1. Checks for new OrcaSlicer releases (weekly schedule)
2. Builds src.rpm and x86_64.rpm in Fedora 44 container
3. Uploads artifacts to GitHub Releases

**Note:** Workflow does not trigger on changes to CHANGELOG.md or README.md.

## Project Structure

```
OrcaSlicer-rpm/
├── .github/workflows/    # GitHub Actions workflow
├── orcaslicer.spec       # RPM spec file
├── CHANGELOG.md          # Project changelog
└── README.md             # This file
```

## License

AGPL-3.0 (same as OrcaSlicer)
