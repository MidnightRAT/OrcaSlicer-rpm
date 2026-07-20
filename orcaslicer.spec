%global debug_package %{nil}

Name:           orcaslicer
Version:        @VERSION@
Release:        @RELEASE@%{?dist}
Summary:        Open-source slicer for FDM 3D printers
License:        AGPL-3.0
URL:            https://github.com/OrcaSlicer/OrcaSlicer
Source0:        %{name}-%{version}-src.tar.gz
Patch0:         use-system-deps.patch

# Runtime deps — shared libraries
Requires:       gtk3
Requires:       webkit2gtk4.1
Requires:       mesa-libGL
Requires:       mesa-libEGL
Requires:       dbus-libs
Requires:       libX11
Requires:       pango
Requires:       fontconfig
Requires:       freetype
Requires:       boost-system boost-iostreams boost-filesystem boost-thread boost-log boost-locale boost-regex boost-date_time
Requires:       tbb
Requires:       gmp
Requires:       mpfr
Requires:       opencv-libs
Requires:       OpenCASCADE
Requires:       openexr-libs
Requires:       openvdb-libs
Requires:       blosc
Requires:       draco
Requires:       CGAL
Requires:       nlopt
Requires:       python3
Requires:       openssl-libs
Requires:       libcurl
Requires:       libpng
Requires:       libjpeg-turbo
Requires:       zlib
Requires:       glew
Requires:       glfw3

# Build deps — tools
BuildRequires:  cmake >= 3.13
BuildRequires:  ninja-build
BuildRequires:  gcc gcc-c++
BuildRequires:  pkgconf
BuildRequires:  autoconf automake libtool m4
BuildRequires:  git wget file
BuildRequires:  perl-FindBin perl-IPC-Cmd
BuildRequires:  libquadmath-devel
BuildRequires:  nasm
BuildRequires:  texinfo
BuildRequires:  chrpath

# Build deps — system -devel libraries (leaf deps used instead of bundled: NLopt, Qhull, OpenCV, OpenCASCADE)
BuildRequires:  zlib-devel
BuildRequires:  libpng-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  expat-devel
BuildRequires:  libcurl-devel
BuildRequires:  openssl-devel
BuildRequires:  freetype-devel
BuildRequires:  fontconfig-devel
BuildRequires:  boost-devel
BuildRequires:  cereal-devel
BuildRequires:  qhull-devel
BuildRequires:  glew-devel
BuildRequires:  glfw3-devel
BuildRequires:  tbb-devel
BuildRequires:  blosc-devel
BuildRequires:  openexr-devel
BuildRequires:  openvdb-devel
BuildRequires:  gmp-devel
BuildRequires:  mpfr-devel
BuildRequires:  eigen3-devel
BuildRequires:  CGAL-devel
BuildRequires:  nlopt-devel
BuildRequires:  draco-devel
BuildRequires:  opencv-devel
BuildRequires:  OpenCASCADE-devel
BuildRequires:  python3-devel

# Build deps — GUI / desktop integration
BuildRequires:  dbus-devel
BuildRequires:  gtk3-devel
BuildRequires:  webkit2gtk4.1-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  mesa-libEGL-devel
BuildRequires:  mesa-libGLU-devel
BuildRequires:  pango-devel
BuildRequires:  extra-cmake-modules
BuildRequires:  eglexternalplatform-devel
BuildRequires:  gstreamer1-devel
BuildRequires:  gstreamer1-plugins-base-devel
BuildRequires:  gstreamermm-devel
BuildRequires:  wayland-protocols-devel
BuildRequires:  libxkbcommon-devel
BuildRequires:  libX11-devel
BuildRequires:  libXi-devel
BuildRequires:  libXrandr-devel
BuildRequires:  libXinerama-devel
BuildRequires:  libXcursor-devel
BuildRequires:  libXcomposite-devel
BuildRequires:  libXdamage-devel
BuildRequires:  libXext-devel
BuildRequires:  libXtst-devel
BuildRequires:  libXfixes-devel
BuildRequires:  libXmu-devel
BuildRequires:  at-spi2-core-devel
BuildRequires:  libepoxy-devel
BuildRequires:  libspnav-devel
BuildRequires:  libsecret-devel
BuildRequires:  libmspack-devel

%description
OrcaSlicer is an open-source slicer for FDM 3D printers.
Based on PrusaSlicer/BambuStudio, supporting STL, OBJ, 3MF file formats.

%prep
%autosetup -n OrcaSlicer-%{version} -p1

%build
export CMAKE_POLICY_VERSION_MINIMUM=3.5
export CMAKE_POLICY_DEFAULT_CMP0167=OLD

# Limit parallelism to avoid OOM on CI (GitHub Actions has ~7GB RAM)
NPROC_DEPS=2
NPROC_BUILD=2

# Build only truly incompatible deps from source
# (wxWidgets 3.3.2, Eigen 5.0 — not available in Fedora repos at required versions)
if [ ! -d deps/build ]; then
  echo "=== Building dependencies (system-deps mode) ==="
  mkdir -p deps/build
  cmake -S deps -B deps/build -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_POLICY_DEFAULT_CMP0167=OLD \
    -DUSE_SYSTEM_DEPS=ON \
    -DDEP_WX_GTK3=ON
  cmake --build deps/build -j${NPROC_DEPS}
else
  echo "=== Dependencies already built, skipping ==="
fi

# Build main app — link against system + bundled libs
mkdir -p build
cmake -S . -B build -G "Ninja Multi-Config" \
  -DCMAKE_PREFIX_PATH="$(pwd)/deps/build/OrcaSlicer_dep/usr/local;/usr" \
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
MimeType=model/stl;model/obj;model/3mf
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
