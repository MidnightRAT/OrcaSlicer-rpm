# OrcaSlicer RPM

RPM packaging for [OrcaSlicer](https://github.com/OrcaSlicer/OrcaSlicer) — open-source slicer for FDM 3D printers.

## How it works

GitHub Actions automatically builds an RPM package for the latest OrcaSlicer release:

1. Triggers on push to `main`, manual dispatch, or weekly schedule
2. Runs in a Fedora 44 container
3. Downloads the latest release source tarball from GitHub
4. Builds all dependencies from source via OrcaSlicer's `deps/` system
5. Compiles OrcaSlicer and packages it as RPM
6. Uploads the RPM and SRPM as artifacts and publishes them to a GitHub Release

## Manual build

```bash
# Install build dependencies (Fedora 44)
sudo dnf install -y \
  rpm-build rpmdevtools git wget curl unzip \
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

# Set up RPM build tree
rpmdev-setuptree

# Download source (replace VERSION)
VERSION=2.4.1
wget -q "https://github.com/OrcaSlicer/OrcaSlicer/archive/refs/tags/v${VERSION}.tar.gz" \
  -O orcaslicer-${VERSION}-src.tar.gz
cp orcaslicer-${VERSION}-src.tar.gz ~/rpmbuild/SOURCES/

# Create spec from template
sed -e "s/@VERSION@/${VERSION}/g" -e "s/@RELEASE@/1/g" \
  orcaslicer.spec > ~/rpmbuild/SPECS/orcaslicer.spec

# Build
rpmbuild -ba ~/rpmbuild/SPECS/orcaslicer.spec
```

## Installing the RPM

```bash
sudo dnf install ~/rpmbuild/RPMS/x86_64/orcaslicer-*.rpm
```

OrcaSlicer will be available in `/opt/OrcaSlicer/` with desktop integration.
