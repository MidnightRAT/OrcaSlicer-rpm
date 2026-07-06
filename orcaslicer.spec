%global debug_package %{nil}

Name:           orcaslicer
Version:        @VERSION@
Release:        @RELEASE@%{?dist}
Summary:        Open-source slicer for FDM 3D printers
License:        AGPL-3.0
URL:            https://github.com/OrcaSlicer/OrcaSlicer
Source0:        %{name}-%{version}-src.tar.gz

# Runtime deps
Requires:       gtk3
Requires:       webkit2gtk4.1
Requires:       mesa-libGL
Requires:       mesa-libEGL
Requires:       dbus-libs
Requires:       libX11
Requires:       pango
Requires:       fontconfig
Requires:       freetype

# Build deps
BuildRequires:  cmake >= 3.13
BuildRequires:  ninja-build
BuildRequires:  gcc gcc-c++
BuildRequires:  pkgconf
BuildRequires:  autoconf automake libtool m4
BuildRequires:  git wget file
BuildRequires:  perl-FindBin perl-IPC-Cmd
BuildRequires:  libquadmath-devel
BuildRequires:  nasm
BuildRequires:  dbus-devel gtk3-devel webkit2gtk4.1-devel
BuildRequires:  glew-devel glfw-devel mesa-libGLU-devel mesa-libGL-devel
BuildRequires:  libjpeg-turbo-devel libpng-devel
BuildRequires:  openssl-devel libcurl-devel
BuildRequires:  freetype-devel fontconfig-devel pango-devel
BuildRequires:  eigen3-devel cereal-devel
BuildRequires:  extra-cmake-modules eglexternalplatform-devel
BuildRequires:  gstreamer1-devel gstreamer1-plugins-base-devel gstreamermm-devel
BuildRequires:  wayland-protocols-devel libxkbcommon-devel
BuildRequires:  libX11-devel libXi-devel libXrandr-devel libXinerama-devel
BuildRequires:  libXcursor-devel libXcomposite-devel libXdamage-devel libXext-devel
BuildRequires:  libXtst-devel libXfixes-devel libXmu-devel
BuildRequires:  at-spi2-core-devel libepoxy-devel
BuildRequires:  libspnav-devel libsecret-devel libmspack-devel
BuildRequires:  texinfo
BuildRequires:  chrpath

%description
OrcaSlicer is an open-source slicer for FDM 3D printers.
Based on PrusaSlicer/BambuStudio, supporting STL, OBJ, 3MF file formats.

%prep
%setup -n OrcaSlicer-%{version}

%build
export CMAKE_POLICY_VERSION_MINIMUM=3.5

# Limit parallelism to avoid OOM on CI (GitHub Actions has ~7GB RAM)
NPROC_DEPS=2
NPROC_BUILD=2

# Build dependencies
mkdir -p deps/build
cmake -S deps -B deps/build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DDEP_WX_GTK3=ON
cmake --build deps/build -j${NPROC_DEPS}

# Build main app
mkdir -p build
cmake -S . -B build -G "Ninja Multi-Config" \
  -DCMAKE_PREFIX_PATH="$(pwd)/deps/build/OrcaSlicer_dep/usr/local" \
  -DSLIC3R_STATIC=1 \
  -DSLIC3R_GTK=3 \
  -DBBL_RELEASE_TO_PUBLIC=1 \
  -DBBL_INTERNAL_TESTING=0 \
  -DSLIC3R_PCH=OFF
cmake --build build --config Release --target OrcaSlicer -j${NPROC_BUILD}

# Generate localization
./scripts/run_gettext.sh || true

%install
# Create installation directories
mkdir -p %{buildroot}/opt/OrcaSlicer/bin/crashpad
mkdir -p %{buildroot}/opt/OrcaSlicer/resources

# Install binary
cp build/src/Release/orca-slicer %{buildroot}/opt/OrcaSlicer/bin/
chmod 755 %{buildroot}/opt/OrcaSlicer/bin/orca-slicer
# Fix RPATHs - remove build-time paths
chrpath -d %{buildroot}/opt/OrcaSlicer/bin/orca-slicer 2>/dev/null || true

# Install bundled shared libraries
cp -f build/src/Release/libaosl.so %{buildroot}/opt/OrcaSlicer/bin/ 2>/dev/null || true

# Install crashpad handler
cp -f build/src/Release/crashpad/crashpad_handler %{buildroot}/opt/OrcaSlicer/bin/crashpad/ 2>/dev/null || true

# Install resources
cp -R resources/* %{buildroot}/opt/OrcaSlicer/resources/

# Create launcher script
printf '#!/usr/bin/bash\nDIR=$(dirname "$(readlink -f "$0")")\nexport LD_LIBRARY_PATH="$DIR/bin:$LD_LIBRARY_PATH"\nexec "$DIR/bin/orca-slicer" "$@"\n' > %{buildroot}/opt/OrcaSlicer/orca-slicer.sh
chmod 755 %{buildroot}/opt/OrcaSlicer/orca-slicer.sh

# Desktop integration
mkdir -p %{buildroot}/usr/share/applications
cat > %{buildroot}/usr/share/applications/orcaslicer.desktop << 'DESKTOP'
[Desktop Entry]
Name=OrcaSlicer
Comment=Open-source slicer for FDM 3D printers
Exec=/opt/OrcaSlicer/orca-slicer.sh %f
Icon=orcaslicer
Terminal=false
Type=Application
Categories=Utility;Engineering;
MimeType=model/stl;model/obj;application/x-3mf;
DESKTOP

# Install icons
for size in 32 128 192; do
  mkdir -p %{buildroot}/usr/share/icons/hicolor/${size}x${size}/apps
  cp resources/images/OrcaSlicer_${size}px.png \
     %{buildroot}/usr/share/icons/hicolor/${size}x${size}/apps/orcaslicer.png 2>/dev/null || true
done

# License
install -Dm644 LICENSE.txt %{buildroot}/usr/share/licenses/%{name}/LICENSE

%files
/opt/OrcaSlicer
/usr/share/applications/orcaslicer.desktop
/usr/share/icons/hicolor/*/apps/orcaslicer.png
/usr/share/licenses/%{name}/LICENSE

%changelog
