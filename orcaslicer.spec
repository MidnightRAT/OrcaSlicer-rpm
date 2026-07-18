%global debug_package %{nil}
%global _smp_nthreads 2
%global _default_patch_fuzz 1

%global wx_version 3.3.2
%global cgal_version 5.6.3
%global libnoise_version 1.0

Name:           orcaslicer
Version:        2.4.2
Release:        3%{?dist}
Summary:        Open-source slicer for FDM 3D printers
License:        AGPL-3.0
URL:            https://github.com/OrcaSlicer/OrcaSlicer
Source0:        https://github.com/OrcaSlicer/OrcaSlicer/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}-src.tar.gz
Source1:        https://github.com/SoftFever/Orca-deps-wxWidgets/archive/refs/tags/orca-%{wx_version}.tar.gz#/Orca-deps-wxWidgets-orca-%{wx_version}.tar.gz
Source2:        https://github.com/SoftFever/Orca-deps-libnoise/archive/refs/tags/%{libnoise_version}.zip#/Orca-deps-libnoise-%{libnoise_version}.zip
Source3:        https://github.com/CGAL/cgal/releases/download/v%{cgal_version}/CGAL-%{cgal_version}.zip#/CGAL-%{cgal_version}.zip

Patch0:         0001-system-boost.patch
Patch1:         0002-occt-cmake-dir.patch
Patch2:         0003-opencv-include.patch
Patch3:         0004-openvdb-config.patch
Patch4:         0005-opencv-world.patch
Patch5:         0006-boost-io_context.patch
Patch6:         0007-boost-process-v1.patch
Patch7:         0008-boost-process-mediaplay.patch
Patch8:         0009-boost-process-removable.patch
Patch9:         0010-boost-bonjour.patch
Patch10:        0011-boost-tcpconsole.patch
Patch11:        0012-boost-filesystem.patch
Patch12:        0013-occt-7.9-step-libs.patch


Provides:       bundled(wxWidgets-orca) = %{wx_version}
Provides:       bundled(libnoise) = %{libnoise_version}
Provides:       bundled(CGAL) = %{cgal_version}

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

# Build deps — системні
BuildRequires:  cmake >= 3.13
BuildRequires:  ninja-build
BuildRequires:  gcc gcc-c++
BuildRequires:  pkgconf
BuildRequires:  autoconf automake libtool m4
BuildRequires:  git wget file
BuildRequires:  perl-FindBin perl-IPC-Cmd
BuildRequires:  nasm
BuildRequires:  boost-devel >= 1.83
BuildRequires:  opencascade-devel >= 7.9.3
BuildRequires:  opencv-devel >= 4.0
BuildRequires:  openvdb-devel >= 5.0
BuildRequires:  cereal-devel
BuildRequires:  eigen3-devel
BuildRequires:  json-devel
BuildRequires:  glew-devel
BuildRequires:  glfw-devel
BuildRequires:  dbus-devel gtk3-devel webkit2gtk4.1-devel
BuildRequires:  mesa-libGLU-devel mesa-libGL-devel
BuildRequires:  libjpeg-turbo-devel libpng-devel
BuildRequires:  openssl-devel libcurl-devel
BuildRequires:  freetype-devel fontconfig-devel pango-devel
BuildRequires:  extra-cmake-modules eglexternalplatform-devel
BuildRequires:  gstreamer1-devel gstreamer1-plugins-base-devel
BuildRequires:  wayland-protocols-devel libxkbcommon-devel
BuildRequires:  libX11-devel libXi-devel libXrandr-devel libXinerama-devel
BuildRequires:  libXcursor-devel libXcomposite-devel libXdamage-devel libXext-devel
BuildRequires:  libXtst-devel libXfixes-devel libXmu-devel
BuildRequires:  at-spi2-core-devel libepoxy-devel
BuildRequires:  libspnav-devel libsecret-devel libmspack-devel
BuildRequires:  texinfo chrpath
BuildRequires:  gmp-devel mpfr-devel
BuildRequires:  NLopt-devel
BuildRequires:  blosc-devel imath-devel draco-devel draco-static
BuildRequires:  pcre2-devel libwebp-devel

%description
OrcaSlicer is an open-source slicer for FDM 3D printers.
Based on PrusaSlicer/BambuStudio, supporting STL, OBJ, 3MF file formats.

%prep
%setup -n OrcaSlicer-%{version}

# Apply patches
%patch -P 0 -p1
%patch -P 1 -p1
%patch -P 2 -p1
%patch -P 4 -p1
%patch -P 5 -p1
%patch -P 6 -p1
%patch -P 7 -p1
%patch -P 8 -p1
%patch -P 9 -p1
%patch -P 10 -p1
%patch -P 11 -p1
%patch -P 12 -p1

# Remove bundled FindOpenVDB.cmake to use system one
rm -f cmake/modules/FindOpenVDB.cmake

# Extract bundled dep sources into current build directory
tar xzf %{SOURCE1}
unzip -q %{SOURCE2}
unzip -q %{SOURCE3}

%build
# Limit parallelism
NPROC=2

# Bundled deps prefix
BUNDLED_PREFIX=$(pwd)/_bundled
mkdir -p "$BUNDLED_PREFIX"

# ---- 1. wxWidgets-orca 3.3.2 ----
echo "=== Building wxWidgets-orca %{wx_version} ==="
mkdir -p _build_wx && cd _build_wx
cmake -G Ninja \
  ../Orca-deps-wxWidgets-orca-%{wx_version} \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$BUNDLED_PREFIX" \
  -DCMAKE_INSTALL_LIBDIR=lib \
  -DwxBUILD_TOOLKIT=gtk3 \
  -DwxBUILD_SHARED=OFF \
  -DwxBUILD_PRECOMP=ON \
  -DwxBUILD_DEBUG_LEVEL=1 \
  -DwxBUILD_SAMPLES=OFF \
  -DwxUSE_MEDIACTRL=ON \
  -DwxUSE_DETECT_SM=OFF \
  -DwxUSE_PRIVATE_FONTS=ON \
  -DwxUSE_OPENGL=ON \
  -DwxUSE_GLCANVAS_EGL=ON \
  -DwxUSE_WEBREQUEST=ON \
  -DwxUSE_WEBVIEW=ON \
  -DwxUSE_WEBVIEW_IE=OFF \
  -DwxUSE_REGEX=sys \
  -DwxUSE_LIBSDL=OFF \
  -DwxUSE_XTEST=OFF \
  -DwxUSE_STC=OFF \
  -DwxUSE_AUI=ON \
  -DwxUSE_LIBPNG=sys \
  -DwxUSE_ZLIB=sys \
  -DwxUSE_LIBJPEG=sys \
  -DwxUSE_LIBTIFF=OFF \
  -DwxUSE_LIBWEBP=sys \
  -DwxUSE_EXPAT=sys \
  -DwxUSE_NANOSVG=OFF \
  -DCMAKE_POLICY_VERSION_MINIMUM=3.5
cmake --build . -j%{_smp_nthreads}
cmake --install .
# Copy private headers (Orca requires them)
SRC_HDR="$PWD/../Orca-deps-wxWidgets-orca-%{wx_version}/include/wx"
DST_HDR="$BUNDLED_PREFIX/include/wx-3.3/wx"
mkdir -p "$DST_HDR/private" "$DST_HDR/generic/private" "$DST_HDR/gtk/private"
cp -r "$SRC_HDR/private/."      "$DST_HDR/private/" 2>/dev/null || true
cp -r "$SRC_HDR/generic/private/." "$DST_HDR/generic/private/" 2>/dev/null || true
cp -r "$SRC_HDR/gtk/private/."  "$DST_HDR/gtk/private/" 2>/dev/null || true
cd ..

# ---- 2. libnoise 1.0 ----
echo "=== Building libnoise %{libnoise_version} ==="
mkdir -p _build_noise && cd _build_noise
cmake -G Ninja \
  ../Orca-deps-libnoise-%{libnoise_version} \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$BUNDLED_PREFIX" \
  -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
  -DCMAKE_POLICY_VERSION_MINIMUM=3.5
cmake --build . -j%{_smp_nthreads}
cmake --install .
cd ..

# ---- 3. CGAL 5.6.3 ----
echo "=== Building CGAL %{cgal_version} ==="
mkdir -p _build_cgal && cd _build_cgal
cmake -G Ninja \
  ../CGAL-%{cgal_version} \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$BUNDLED_PREFIX" \
  -DBUILD_SHARED_LIBS=OFF \
  -DWITH_CGAL_Core=ON \
  -DWITH_CGAL_ImageIO=OFF \
  -DWITH_CGAL_Qt5=OFF \
  -DWITH_CGAL_Qt6=OFF \
  -DCGAL_HEADER_ONLY=OFF \
  -DCMAKE_POLICY_VERSION_MINIMUM=3.5
cmake --build . -j%{_smp_nthreads}
cmake --install .
cd ..

# ---- 4. OrcaSlicer main app ----
echo "=== Building OrcaSlicer ==="
mkdir -p _build_orca && cd _build_orca
cmake -G Ninja \
  .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DSLIC3R_FHS=ON \
  -DSLIC3R_STATIC=OFF \
  -DSLIC3R_GUI=ON \
  -DSLIC3R_DESKTOP_INTEGRATION=OFF \
  -DCMAKE_PREFIX_PATH="$BUNDLED_PREFIX" \
  -DCMAKE_MODULE_PATH="/usr/lib64/cmake/OpenVDB" \
  -DSLIC3R_PCH=OFF \
  -DCMAKE_POLICY_VERSION_MINIMUM=3.5
cmake --build . -j%{_smp_nthreads} --target OrcaSlicer

# Generate localization
./scripts/run_gettext.sh || true
cd ..

%install
# Create installation directories
mkdir -p %{buildroot}/opt/OrcaSlicer/bin/crashpad
mkdir -p %{buildroot}/opt/OrcaSlicer/resources

# Install binary
cp _build_orca/src/orca-slicer %{buildroot}/opt/OrcaSlicer/bin/
chmod 755 %{buildroot}/opt/OrcaSlicer/bin/orca-slicer
chrpath -d %{buildroot}/opt/OrcaSlicer/bin/orca-slicer 2>/dev/null || true

# Install bundled shared libraries
cp -f _build_orca/src/libaosl.so %{buildroot}/opt/OrcaSlicer/bin/ 2>/dev/null || true

# Install crashpad handler
cp -f _build_orca/src/crashpad/crashpad_handler %{buildroot}/opt/OrcaSlicer/bin/crashpad/ 2>/dev/null || true

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
* Sat Jul 18 2026 OrcaSlicer RPM Maintainer <maintainer@example.com> - 2.4.2-3
- Reduced compilation parallelism to 2 (prevents OOM on limited RAM)

* Sat Jul 18 2026 OrcaSlicer RPM Maintainer <maintainer@example.com> - 2.4.2-2
- Added .gitignore, excluded build artifacts from repo
- Updated README and CHANGELOG

* Sat Jul 18 2026 OrcaSlicer RPM Maintainer <maintainer@example.com> - 2.4.2-1
- Initial Fedora 44 build with FHS system deps
- Bundled: wxWidgets-orca 3.3.2, libnoise 1.0, CGAL 5.6.3