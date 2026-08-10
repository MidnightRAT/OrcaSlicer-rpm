# -*- rpm-spec -*-
#
# OrcaSlicer RPM spec
# Версія: @VERSION@
# Встановлення: /opt/OrcaSlicer
# Стратегія залежностей: максимальне використання системних бібліотек
#   (-devel пакети Fedora), бундлюються лише ті, яких немає у сумісній
#   версії в дистрибутиві (Boost 1.84, wxWidgets 3.3.2, OpenVDB custom fork,
#   OCCT 7.6, OpenEXR 2.5.5, TBB 2021.5, Blosc, GLEW, OpenCSG, libnoise).
#
# Patches:
#   0001 — deps/CMakeLists.txt: виявлення системних бібліотек (не-FLATPAK):
#         OpenSSL, CURL, PNG, JPEG, Freetype, Eigen3, CGAL, Cereal, NLopt,
#         Draco, Qhull, GLFW, OpenCV, GMP, MPFR. Якщо пакета немає —
#         повернення до bundled-збірки (fail-safe).
#         Також: система-ворот CGAL >= 6.0.0. У CGAL 6 змінено API
#         Surface_mesh::property_map (повертає std::optional замість pair),
#         а OrcaSlicer 2.4.2 писався під bundled CGAL 5.6.3 — тому занадто
#         новий системний CGAL ігнорується і будується bundled 5.6.3
#         (інакше не збирається CutSurface.cpp).
#   0002 — deps/CGAL/CGAL.cmake: bundled CGAL залежить лише від dep_Boost.
#         Eigen/GMP/MPFR беруться з системи, тому додаткові dep_*-цілі
#         (dep_Eigen/dep_GMP/dep_MPFR) можуть не існувати.
#   0003 — src/libslic3r/CMakeLists.txt: системний OpenCV Fedora не має
#         target/lib `opencv_world` (bundled OpenCV його створював).
#         Замінюємо `opencv_world` на {OpenCV_LIBRARIES} (opencv_core,
#         opencv_imgproc, opencv_imgcodecs) і додаємо include-шлях.

Name:           orca-slicer
Version:        @VERSION@
Release:        @RELEASE@%{?dist}
Summary:        Open-source FDM slicer for 3D printers (OrcaSlicer)
License:        AGPL-3.0-only
URL:            https://github.com/OrcaSlicer/OrcaSlicer
Source0:        OrcaSlicer-%{version}.tar.gz
Source1:        README.md

# Патч 1: deps/CMakeLists.txt — системні бібліотеки (замість bundled) + CGAL-ворота
Patch1:         0001-deps-system-libraries.patch
# Патч 2: deps/CGAL/CGAL.cmake — bundled CGAL залежить лише від dep_Boost
Patch2:         0002-cgal-bundled-depends.patch
# Патч 3: main tree — системний OpenCV (немає target/lib opencv_world)
Patch3:         0003-main-opencv-system.patch

# Тестування та debug-пакунок не збираємо; бінарник не стрипуємо
%global debug_package %{nil}

# ────────────────────────────────────────────────────────────────────────────
# Build tools
# ────────────────────────────────────────────────────────────────────────────
BuildRequires:  cmake >= 3.13
BuildRequires:  ninja-build
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  git
BuildRequires:  git-lfs
BuildRequires:  make
BuildRequires:  patch
BuildRequires:  automake
BuildRequires:  autoconf
BuildRequires:  libtool
BuildRequires:  m4
BuildRequires:  gettext
BuildRequires:  perl-FindBin
BuildRequires:  perl-IPC-Cmd
BuildRequires:  python3
BuildRequires:  wget

# ── Системні devel-пакети (з них беруться бібліотеки) ──────────────────────
# Eigen3 5.0.1 = точне співпадіння з вимогою main (find_package Eigen3 5.0.1)
BuildRequires:  eigen3-devel >= 5.0.1
# Boost системно не використовується (бундл 1.84), проте CGAL потребує заголовки
BuildRequires:  boost-devel >= 1.83
# TBB бундлиться (статичний, 2021.5); системний 2022 як fallback
BuildRequires:  tbb-devel >= 2021.5
# GLFW 3.4 = точне співпадіння — system
BuildRequires:  glfw-devel >= 3.4
# GLEW бундлиться (потрібен OpenCSG)
BuildRequires:  glew-devel >= 2.2
# NLopt 2.10 > бундл 2.5 — system
BuildRequires:  NLopt-devel >= 2.5
# CGAL — header-only. Системний CGAL на Fedora (6.1.x) має несумісне API
# (найпа клас property_map), тому завжди будується bundled 5.6.3 (ворот >= 6.0).
# CGAL-devel тримаємо для probe/фолбеку (якщо в майбутньому в дистро буде < 6).
BuildRequires:  CGAL-devel >= 5.6
# cereal 1.3.2 > бундл 1.3.0 — header-only, system
BuildRequires:  cereal-devel >= 1.3
# GMP 6.3.0 > бундл 6.2.1 — system
BuildRequires:  gmp-devel >= 6.2
# MPFR 4.2.2 = точне співпадіння — system
BuildRequires:  mpfr-devel >= 4.2
# Qhull: main завжди компілює власний з deps_src/, devel потрібен як запасний
BuildRequires:  qhull-devel >= 8.0
# Draco 1.5.7 = точне співпадіння — system
BuildRequires:  draco-devel >= 1.5.7
BuildRequires:  draco-static
# Blosc 1.21.6 бундлиться (OpenVDB fork вимагає совмесність)
BuildRequires:  blosc-devel >= 1.17
# zlib-ng compat — system
BuildRequires:  zlib-ng-compat-devel
# libpng 1.6.58 > бундл 1.6.35 — system
BuildRequires:  libpng-devel >= 1.6
BuildRequires:  expat-devel
# freetype 2.14 > бундл 2.12 — system (потрібен також OCCT)
BuildRequires:  freetype-devel >= 2.12
# libjpeg-turbo 3.1.3 > бундл 3.0.1 — system
BuildRequires:  libjpeg-turbo-devel >= 3.0
# OpenSSL 3.5.7 > бундл 1.1.1w — system
BuildRequires:  openssl-devel >= 3.1
# libcurl — system (у бандлі 7.75)
BuildRequires:  libcurl-devel
# OpenCV 4.13 > бундл 4.6 — system. У Fedora немає target/lib opencv_world
# (що створював bundled збірки) — цю різницю закриває Патч 3 (OpenCV_LIBRARIES).
BuildRequires:  opencv-devel >= 4.6

# ── Системні GUI/graphics залежності ────────────────────────────────────────
BuildRequires:  dbus-devel
BuildRequires:  gtk3-devel
BuildRequires:  mesa-libGLU-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  libglvnd-devel
BuildRequires:  wayland-devel
BuildRequires:  wayland-protocols-devel
BuildRequires:  eglexternalplatform-devel
BuildRequires:  extra-cmake-modules
BuildRequires:  libsecret-devel
BuildRequires:  webkit2gtk4.1-devel
BuildRequires:  gstreamer1-devel
BuildRequires:  gstreamer1-plugins-good
BuildRequires:  gstreamermm-devel
BuildRequires:  libspnav-devel
BuildRequires:  libmspack-devel
BuildRequires:  libquadmath-devel
BuildRequires:  fontconfig-devel
BuildRequires:  desktop-file-utils

# ────────────────────────────────────────────────────────────────────────────
# Runtime Requires (головні динамічні залежності; точні обирає rpm auto-deps)
# ────────────────────────────────────────────────────────────────────────────
Requires:       tbb >= 2021.5
Requires:       openssl-libs >= 3.1
Requires:       libcurl
Requires:       dbus-libs
Requires:       gtk3
Requires:       mesa-libGL
Requires:       mesa-libGLU
Requires:       libglvnd-glx
Requires:       gstreamer1
Requires:       gstreamer1-plugins-good
Requires:       libsecret
Requires:       NLopt
Requires:       opencv >= 4.6
Requires:       glfw
Requires:       draco

%description
OrcaSlicer — відкритий FDM-слайсер на базі Bambu Studio/PrusaSlicer
(проєкт SoftFever), що офіційно підтримується для багатьох FDM-принтерів.

Встановлення: /opt/OrcaSlicer

Особливості:
- Підтримка багатоматеріального друку та різних технологій слайсінгу (Arachne)
- Вбудовані інструменти калібрування (Pressure Advance, Flow, Temp Tower...)
- Мережевий друк та стріббінг (Bambu / generic printers)
- Профілі для широкого кола принтерів

Бібліотеки беруться переважно із системних -devel пакетів (OpenSSL, libcurl,
libpng, libjpeg-turbo, freetype, expat, zlib-ng, Eigen3, cereal, GMP, MPFR,
NLopt, Draco, Qhull, GLFW, OpenCV). CGAL системно не береться (Fedora 6.1.x має
несумісне API) — будується bundled 5.6.3. Бундлюються також версії, яких
немає у дистрибутиві або які потребують індивідуальних патчів (Boost, wxWidgets,
OpenVDB, OCCT, OpenEXR, TBB, Blosc, OpenCSG, GLEW, libnoise).

# ────────────────────────────────────────────────────────────────────────────
%prep
%setup -q -n OrcaSlicer-%{version}

# Застосовуємо патчі
%patch -P1 -p1
%patch -P2 -p1
%patch -P3 -p1

# ────────────────────────────────────────────────────────────────────────────
%build
# Обмеження паралелізму (велике споживання RAM у bundled deps)
export CMAKE_BUILD_PARALLEL_LEVEL=2
export CMAKE_POLICY_VERSION_MINIMUM=3.5

# ── Крок 1: залежності (deps/) ───────────────────────────────────────────────
# Бундлюємо: Boost 1.84, wxWidgets 3.3.2, OpenVDB (custom fork tamasmeszaros),
#            OCCT 7.6.0, OpenEXR 2.5.5, TBB 2021.5, Blosc,
#            GLEW (local src), OpenCSG 1.4.2, libnoise,
#            CGAL 5.6.3 (системний на Fedora 6.1.x має несумісне з 2.4.2 API).
# Системні: OpenSSL, libcurl, expat, zlib-ng, libpng, libjpeg-turbo, freetype,
#            Eigen3, cereal, GMP, MPFR, NLopt, Draco, Qhull, GLFW, OpenCV.

mkdir -p deps/build
cmake -S deps -B deps/build \
    -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
    -DDEP_WX_GTK3=ON \
    -DDESTDIR="%{_builddir}/OrcaSlicer-%{version}/deps/build/OrcaSlicer_dep"

cmake --build deps/build

# Звільняємо місце: прибираємо сирці та проміжні кеші dep_*-prefix.
# Збережені libs/headers (OrcaSlicer_dep/usr/local) залишаються.
find deps/build -maxdepth 1 -type d -name 'dep_*-prefix' -print0 | \
while IFS= read -r -d '' d; do
    rm -rf "$d/src" "$d/stamp" 2>/dev/null || true
done
rm -rf deps/build/downloads
rm -rf deps/DL_CACHE

# ── Крок 2: основна збірка ───────────────────────────────────────────────────
# Одно-конфігураційний Ninja + CMAKE_BUILD_TYPE=Release (НЕ "Ninja Multi-Config").
# Причина: системні qhull/glfw з Fedora експортують imported-тільки NOCONFIG
# конфігурації; multi-config генератор на стадії validate вимагає
# IMPORTED_LOCATION_<config> (RelWithDebInfo/Release) і падає з
# "IMPORTED_LOCATION not set". Single-config цього повністю уникає.
mkdir -p build
cmake -S . -B build \
    -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
    -DCMAKE_PREFIX_PATH="%{_builddir}/OrcaSlicer-%{version}/deps/build/OrcaSlicer_dep/usr/local" \
    -DCMAKE_INSTALL_PREFIX=/opt/OrcaSlicer \
    -DSLIC3R_STATIC=1 \
    -DSLIC3R_GTK=3 \
    -DBBL_RELEASE_TO_PUBLIC=1 \
    -DBBL_INTERNAL_TESTING=0 \
    -DORCA_TOOLS=ON \
    -DSLIC3R_PCH=ON \
    -DBUILD_TESTS=OFF

cmake --build build --target OrcaSlicer
cmake --build build --target OrcaSlicer_profile_validator

# ────────────────────────────────────────────────────────────────────────────
%install
# cmake install з DESTDIR (-> /opt/OrcaSlicer/bin, /opt/OrcaSlicer/resources)
DESTDIR=%{buildroot} cmake --install build

# Wrapper-скрипт в /usr/bin (щоб desktop Exec=orca-slicer працював)
install -D -m 755 /dev/stdin %{buildroot}%{_bindir}/orca-slicer << 'LAUNCHER'
#!/usr/bin/bash
DIR="/opt/OrcaSlicer"
exec "$DIR/bin/orca-slicer" "$@"
LAUNCHER

# .desktop у стандартне місце
install -D -m 644 \
    %{buildroot}/opt/OrcaSlicer/resources/applications/com.orcaslicer.OrcaSlicer.desktop \
    %{buildroot}%{_datadir}/applications/orca-slicer.desktop

# Іконки з вбудованих ресурсів
for SIZE in 32 128 192; do
    install -D -m 644 \
        resources/images/OrcaSlicer_${SIZE}px.png \
        %{buildroot}%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/OrcaSlicer.png
done

# Документація (README)
install -D -m 644 %{SOURCE1} %{buildroot}%{_pkgdocdir}/README.md

# Dev-артефакти внутрішньої mini-бібліотеки stb_dxt (header + cmake export)
# встановлюються upstream `install()`-правилами, але в рантаймі не потрібні.
rm -rf %{buildroot}/opt/OrcaSlicer/include %{buildroot}/opt/OrcaSlicer/lib

# ────────────────────────────────────────────────────────────────────────────
%post
/usr/bin/update-desktop-database %{_datadir}/applications &>/dev/null ||:
/usr/bin/gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor &>/dev/null ||:

%postun
/usr/bin/update-desktop-database %{_datadir}/applications &>/dev/null ||:
/usr/bin/gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor &>/dev/null ||:

# ────────────────────────────────────────────────────────────────────────────
%files
%license LICENSE.txt
%dir /opt/OrcaSlicer
/opt/OrcaSlicer/LICENSE.txt
/opt/OrcaSlicer/bin/
/opt/OrcaSlicer/resources/
%{_bindir}/orca-slicer
%{_datadir}/applications/orca-slicer.desktop
%{_datadir}/icons/hicolor/32x32/apps/OrcaSlicer.png
%{_datadir}/icons/hicolor/128x128/apps/OrcaSlicer.png
%{_datadir}/icons/hicolor/192x192/apps/OrcaSlicer.png
%doc %{_pkgdocdir}/README.md

# ────────────────────────────────────────────────────────────────────────────
%changelog
* Sun Aug 09 2026 OrcaSlicer RPM Packager <orca@softfever.org> - @VERSION@-@RELEASE@
- Перша версія пакування OrcaSlicer для Fedora (COPR)
- deps/CMakeLists.txt: максимальне використання системних -devel бібліотек
  (OpenSSL, libcurl, libpng, libjpeg-turbo, freetype, expat, zlib-ng,
  Eigen3, CGAL, cereal, GMP, MPFR, NLopt, Draco, Qhull, GLFW, OpenCV)
  з поверненням до bundled fallback, якщо пакет відсутній
- Бундлюються лише: Boost, wxWidgets, OpenVDB, OCCT, OpenEXR, TBB, Blosc,
  GLEW, OpenCSG, libnoise
- Встановлення в /opt/OrcaSlicer з desktop/icon інтеграцією
