# -*- rpm-spec -*-
#
# OrcaSlicer RPM spec
# Версія: @VERSION@
# Встановлення: /opt/OrcaSlicer
# Стратегія залежностей: максимальне використання системних бібліотек
#   (-devel пакети Fedora 45). Бундлюються лише ті бібліотеки, для яких
#   у дистрибутиві немає сумісного RPM-пакета:
#     wxWidgets 3.3        (Fedora 45 має wxGTK 3.2.11, main вимагає 3.3),
#     TBB 2021.5           (потрібен статичний, у Fedora лише shared),
#     OpenVDB custom fork  (tamasmeszaros; RPM є лише для апстріму 13.x),
#     OpenEXR 2.5.5        (його потребує той форк; у Fedora 3.4),
#     libnoise             (RPM немає),
#     SolveSpace / SLVS    (RPM немає),
#     wxInspector          (RPM немає).
#   Решта, включно з Python 3.12, FFmpeg, Assimp, LibDataChannel, OCCT,
#   Blosc, Boost, CGAL, OpenCV, береться з системи.
#
# Patches:
#   0001 — deps/CMakeLists.txt: виявлення системних бібліотек (не-FLATPAK):
#         PNG, JPEG, OpenSSL, CURL, Eigen3, CGAL (>= 6.2), cereal, NLopt,
#         Draco, Qhull, GLFW, OpenCV, Assimp, OpenCASCADE, LibDataChannel,
#         Blosc, Boost (статичний), FFmpeg (pkg-config), Python3 3.12,
#         GMP, MPFR. Якщо пакета немає — повернення до bundled-збірки
#         (fail-safe). Ворота CGAL: системний CGAL < 6.2 відкидається
#         (OrcaSlicer 2.5 вимагає find_package(CGAL 6.2)).
#   0002 — deps/{CGAL,Eigen,OpenVDB,MPFR}/*.cmake: DEPENDS тепер посилається
#         лише на ті dep_*-цілі, які реально існують (побудовані), а не на
#         ті, що замінені системними пакетами.
#   0003 — CMakeLists.txt: системний Python 3.12 (версійний діапазон
#         3.12...3.13, бо "3.12" означає ">= 3.12" і вибрав би python3.15),
#         Python3_ROOT_DIR лише якщо bundled-розкладка реально існує,
#         Boost_NO_SYSTEM_PATHS=FALSE (системний boost-devel/boost-static).
#   0004 — src/libslic3r/CMakeLists.txt: opencv_world -> ${OpenCV_LIBRARIES}
#         (системний OpenCV не має target opencv_world), OpenCASCADE_DIR
#         лише якщо bundled OCCT є в префіксі deps.
#   0005 — src/CMakeLists.txt: INSTALL_RPATH додає $ORIGIN, POST_BUILD-копія
#         libpython та install() FFmpeg .so виконуються лише якщо відповідні
#         файли існують (системний Python/FFmpeg їх не створює).
#   0006 — OCCT 7.9.3 (Fedora) та Boost.Asio 1.90: Standard_Failure::what()
#         -> GetMessageString(), GC_MakeSegment2d -> GCE2d_MakeSegment;
#         basic_resolver_iterator -> basic_resolver_results::begin().
#         ORCA_BUILD_PYTHON_STUBGEN_MODULE=OFF (static boost_log не лінкується
#         в shared module).
#
# Паралелізм: за замовчуванням 2 (GitHub Actions/COPR, 7 ГБ RAM).
# Локально: rpmbuild -ba --define "orca_jobs 12"

Name:           orca-slicer
Version:        @VERSION@
Release:        @RELEASE@%{?dist}
Summary:        Open-source FDM slicer for 3D printers (OrcaSlicer)
License:        AGPL-3.0-only
URL:            https://github.com/OrcaSlicer/OrcaSlicer
Source0:        OrcaSlicer-%{version}.tar.gz
Source1:        README.md

# Патч 1: deps/CMakeLists.txt — системні бібліотеки (замість bundled)
Patch1:         0001-deps-system-libraries.patch
# Патч 2: deps/{CGAL,Eigen,OpenVDB,MPFR} — умовні DEPENDS
Patch2:         0002-bundled-deps-guard-depends.patch
# Патч 3: основний CMakeLists — системний Python 3.12 і системний Boost
Patch3:         0003-main-python-boost-system.patch
# Патч 4: src/libslic3r — системний OpenCV і OCCT
Patch4:         0004-main-opencv-occt-system.patch
# Патч 5: src/CMakeLists — захист install()/POST_BUILD без bundled Python/FFmpeg
Patch5:         0005-src-python-ffmpeg-install-guards.patch
# Патч 6: сумісність з системним OCCT 7.9.3 (Fedora) та Boost.Asio 1.90 —
#   Standard_Failure::what() -> GetMessageString(),
#   GC_MakeSegment2d.hxx -> GCE2d_MakeSegment (OCCT < 8),
#   basic_resolver_iterator -> basic_resolver_results::begin()
Patch6:         0006-occt-7.9-boost-asio-compat.patch

# Тестування та debug-пакунок не збираємо; бінарник не стрипуємо
%global debug_package %{nil}

# Fedora додає -flto=auto до CFLAGS/CXXFLAGS за замовчуванням, що для
# OrcaSlicer (великий бінарник) призводить до вичерпання /tmp під час
# LTO-лінкування ("Disk quota exceeded"). Вимикаємо LTO.
%global _lto_cflags %{nil}
%global _lto_ldflags %{nil}

# Паралелізм збірки. CI/COPR (обмежені RAM) лишають 2; локально:
#   rpmbuild -ba --define "orca_jobs 12"
%{!?orca_jobs: %global orca_jobs 2}

# ────────────────────────────────────────────────────────────────────────────
# Build tools
# ────────────────────────────────────────────────────────────────────────────
# >= 3.19: патч 0003 використовує версійний діапазон find_package(Python3 ...)
BuildRequires:  cmake >= 3.19
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
BuildRequires:  pkgconf
BuildRequires:  wget

# ── Системні devel-пакети (з них беруться бібліотеки) ──────────────────────
# Python 3.12 — embedded-інтерпретатор GUI (патч 0003), bundled CPython не збирається
BuildRequires:  python3.12
BuildRequires:  python3.12-devel >= 3.12
# Eigen3 5.0.1 = точне співпадіння з вимогою main (find_package Eigen3 5.0.1)
BuildRequires:  eigen3-devel >= 5.0.1
# Boost статичний: SLIC3R_STATIC=1 (патч 0003 прибирає Boost_NO_SYSTEM_PATHS)
BuildRequires:  boost-devel >= 1.83
BuildRequires:  boost-static >= 1.83
# TBB бундлиться (статичний, 2021.5) - у Fedora лише shared, а SLIC3R_STATIC=1
# вимагає статичної версії; системний tbb-devel не потрібен і лише міг би
# засіяти заголовки в /usr/include/tbb замість bundled-версії
# GLFW 3.4 = точне співпадіння — system
BuildRequires:  glfw-devel >= 3.4
# NLopt 2.11 > бундл 2.5 — system
BuildRequires:  NLopt-devel >= 2.5
# CGAL: OrcaSlicer 2.5 вимагає CGAL 6.2; Fedora 45 має рівно 6.2.1 — system.
# Старіший системний CGAL відкидається воротами патча 0001 і будується
# bundled 6.2.1 (фолбек).
BuildRequires:  CGAL-devel >= 6.2
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
# Blosc 1.21.6 — system (патч 0001 + cmake/modules/FindBlosc.cmake)
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
# (що створював bundled збірки) — цю різницю закриває Патч 4 (OpenCV_LIBRARIES).
BuildRequires:  opencv-devel >= 4.6
# Assimp 6.0.5 — system (бандл 5.4.3)
BuildRequires:  assimp-devel >= 6.0
# LibDataChannel 0.23.1 — system (бандл 0.24.5)
BuildRequires:  libdatachannel-devel >= 0.23
# OCCT 7.9.3 — system (бандл 8.0.1); Патч 4 прибирає хардкод OpenCASCADE_DIR
BuildRequires:  opencascade-devel >= 7.9
# FFmpeg 9.0 — system (бандл 7.0.3); Патч 5 захищає file(COPY)/install()
# від відсутності bundled libav*.so
BuildRequires:  ffmpeg-free-devel >= 7.0
# uv — system (замість автозавантаження під час configure)
BuildRequires:  uv >= 0.11

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
# libquadmath існує лише в x86-білдах Fedora: на aarch64 пакета немає
# (нічого не надає), тому на цій архітектурі buildroot його не вирішить.
# На x86_64 його вимагає boost-devel, тож тут залишаємо явно.
%ifarch x86_64
BuildRequires:  libquadmath-devel
%endif
BuildRequires:  fontconfig-devel
BuildRequires:  desktop-file-utils

# ────────────────────────────────────────────────────────────────────────────
# Runtime Requires (головні динамічні залежності; точні обирає rpm auto-deps)
# ────────────────────────────────────────────────────────────────────────────
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
# Embedded Python: скелет /opt/OrcaSlicer/lib/python вказує на системну
# інсталяцію 3.12 (/usr/lib64/python3.12 + /usr/bin/python3.12)
Requires:       python3.12
# Встановлення Python-пакетів у GUI виконується через uv
Requires:       uv

%description
OrcaSlicer — відкритий FDM-слайсер на базі Bambu Studio/PrusaSlicer
(проєкт SoftFever), що офіційно підтримується для багатьох FDM-принтерів.

Встановлення: /opt/OrcaSlicer

Особливості:
- Підтримка багатоматеріального друку та різних технологій слайсінгу (Arachne)
- Вбудовані інструменти калібрування (Pressure Advance, Flow, Temp Tower...)
- Мережевий друк та стріббінг (Bambu / generic printers)
- Профілі для широкого кола принтерів

Бібліотеки беруться переважно із системних -devel пакетів Fedora 45
(OpenSSL, libcurl, libpng, libjpeg-turbo, freetype, expat, zlib-ng, Eigen3,
cereal, GMP, MPFR, NLopt, Draco, Qhull, GLFW, OpenCV, Assimp, LibDataChannel,
OCCT, Blosc, Boost, CGAL 6.2, FFmpeg, Python 3.12, uv). Бундлюються лише
ті, для яких у дистрибутиві немає сумісного пакета (wxWidgets 3.3, TBB,
кастомний OpenVDB разом з OpenEXR 2.5.5, libnoise, SolveSpace, wxInspector).

# ────────────────────────────────────────────────────────────────────────────
%prep
%setup -q -n OrcaSlicer-%{version}

# Застосовуємо патчі
%patch -P1 -p1
%patch -P2 -p1
%patch -P3 -p1
%patch -P4 -p1
%patch -P5 -p1
%patch -P6 -p1

# ────────────────────────────────────────────────────────────────────────────
%build
# Зупиняємося на першій помилці: інакше rpmbuild помітить лише статус
# останньої команди секції.
set -e
# Паралелізм: 2 за замовчуванням (CI/COPR), локально --define "orca_jobs 12"
export CMAKE_BUILD_PARALLEL_LEVEL=%{orca_jobs}
export CMAKE_POLICY_VERSION_MINIMUM=3.5

# ── Крок 1: залежності (deps/) ───────────────────────────────────────────────
# Бундлюємо: wxWidgets 3.3, TBB 2021.5 (статичний),
#            OpenVDB (custom fork tamasmeszaros) + OpenEXR 2.5.5 для нього,
#            libnoise, SolveSpace (SLVS), wxInspector.
# Системні:  OpenSSL, libcurl, expat, zlib-ng, libpng, libjpeg-turbo, freetype,
#            Eigen3, cereal, GMP, MPFR, NLopt, Draco, Qhull, GLFW, OpenCV,
#            Assimp, OCCT, LibDataChannel, Blosc, Boost, FFmpeg, Python 3.12.

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
    -DSLIC3R_STATIC_EXCLUDE_CURL=1 \
    -DSLIC3R_GTK=3 \
    -DBBL_RELEASE_TO_PUBLIC=1 \
    -DBBL_INTERNAL_TESTING=0 \
    -DORCA_TOOLS=ON \
    -DSLIC3R_PCH=ON \
    -DORCA_BUNDLED_UV_EXECUTABLE=/usr/bin/uv \
    -DORCA_BUILD_PYTHON_STUBGEN_MODULE=OFF \
    -DBUILD_TESTS=OFF

cmake --build build --target OrcaSlicer
cmake --build build --target OrcaSlicer_profile_validator

# ────────────────────────────────────────────────────────────────────────────
%install
set -e
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
rm -rf %{buildroot}/opt/OrcaSlicer/include
rm -rf %{buildroot}/opt/OrcaSlicer/lib

# Системний uv: бінарник запам'ятовує шлях /usr/bin/uv (ORCA_BUNDLED_UV_EXECUTABLE),
# тому копія в пакеті не потрібна — прибираємо, щоб не дублювати системний пакет.
rm -rf %{buildroot}/opt/OrcaSlicer/resources/tools/uv
rmdir --ignore-fail-on-non-empty %{buildroot}/opt/OrcaSlicer/resources/tools 2>/dev/null || :

# ── Скелет системного Python для embedded-інтерпретатора ────────────────────
# PythonInterpreter шукає python home як <resources>/../lib/python і вимагає
# наявності lib/python3.12/encodings та bin/python3.12. Системна інсталяція
# Python 3.12 лежить в %{_libdir}/python3.12 (/usr/lib64 на x86_64 та aarch64)
# і /usr/bin/python3.12 — зв'язуємо її, не ввозячи копії в пакет.
install -d %{buildroot}/opt/OrcaSlicer/lib/python/lib
install -d %{buildroot}/opt/OrcaSlicer/lib/python/bin
ln -sfn %{_libdir}/python3.12 %{buildroot}/opt/OrcaSlicer/lib/python/lib/python3.12
ln -sfn /usr/bin/python3.12 %{buildroot}/opt/OrcaSlicer/lib/python/bin/python3.12

# ────────────────────────────────────────────────────────────────────────────
%post
/usr/bin/update-desktop-database %{_datadir}/applications &>/dev/null ||:
/usr/bin/gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor &>/dev/null ||:

%postun
/usr/bin/update-desktop-database %{_datadir}/applications &>/dev/null ||:
/usr/bin/gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor &>/dev/null ||:

# ────────────────────────────────────────────────────────────────────────────
%files
%license /opt/OrcaSlicer/LICENSE.txt
%dir /opt/OrcaSlicer
/opt/OrcaSlicer/bin/
/opt/OrcaSlicer/resources/
/opt/OrcaSlicer/lib/
%{_bindir}/orca-slicer
%{_datadir}/applications/orca-slicer.desktop
%{_datadir}/icons/hicolor/32x32/apps/OrcaSlicer.png
%{_datadir}/icons/hicolor/128x128/apps/OrcaSlicer.png
%{_datadir}/icons/hicolor/192x192/apps/OrcaSlicer.png
%doc %{_pkgdocdir}/README.md

# ────────────────────────────────────────────────────────────────────────────
%changelog
* Tue Nov 24 2026 OrcaSlicer RPM Packager <orca@softfever.org> - @VERSION@-@RELEASE@
- Пакування оновлено під OrcaSlicer 2.5.2 (усі шість патчів застосовуються
  чисто); нумерацію збірки скинуто: 2.5.1-7 -> 2.5.2-1
- aarch64 (Fedora 45): libquadmath-devel лише під %ifarch x86_64 (на aarch64
  пакета немає, нічого не надає; на x86_64 його вимагає boost-devel)
- Скелет системного Python: symlink через %{_libdir} замість хардкоду /usr/lib64
- CI: матриця x86_64 (ubuntu-latest) + aarch64 (ubuntu-24.04-arm), артефакти
  per-arch, окремий release-джоб завантажує RPM обох архітектур одним заходом
* Sun Nov 15 2026 OrcaSlicer RPM Packager <orca@softfever.org> - @VERSION@-@RELEASE@
- Перевірено повну збірку під OrcaSlicer 2.5.1 (CI завжди бере найновіший реліз)
- Патч 0004 зроблено version-agnostic (OCCT-блок застосовується до 2.5.0 і 2.5.1)
- ZLIB тепер системний (zlib-ng-compat-devel) замість bundled zlib
* Sat Nov 07 2026 OrcaSlicer RPM Packager <orca@softfever.org> - @VERSION@-@RELEASE@
- Адаптація під OrcaSlicer 2.5.0 та бібліотеки Fedora 45
- Нові патчі 0003-0006: системний Python 3.12, системний Boost,
  умовні install()/POST_BUILD для bundled Python/FFmpeg,
  сумісність з OCCT 7.9.3 і Boost.Asio 1.90
- Системні замість бандлів: Python 3.12, FFmpeg 9.0, Assimp 6.0.5,
  LibDataChannel 0.23.1, OCCT 7.9.3, Blosc 1.21.6, Boost 1.90, uv, CGAL 6.2.1
- CGAL 6.2.1 з системи (OrcaSlicer 2.5 вимагає CGAL 6.2); ворота
  інвертовано: bundled-фолбек лише якщо системний CGAL < 6.2
- Прибрано glew-devel / OpenCSG: GLEW і OpenCSG видалені в 2.5.0
- Скелет /opt/OrcaSlicer/lib/python -> системна інсталяція Python 3.12
- Паралелізм винесено в RPM-макрос orca_jobs (2 для CI/COPR,
  локально --define "orca_jobs 12")
- LTO вимкнено (Fedora auto-LTO вичерпував /tmp при лінкуванні)
- stubgen-модуль вимкнено (ORCA_BUILD_PYTHON_STUBGEN_MODULE=OFF):
  static boost_log не лінкується в shared module
- CI: fedora:45, dnf builddep замість дубльованого списку пакетів
* Sun Aug 09 2026 OrcaSlicer RPM Packager <orca@softfever.org> - @VERSION@-@RELEASE@
- Перша версія пакування OrcaSlicer для Fedora (COPR)
- deps/CMakeLists.txt: максимальне використання системних -devel бібліотек
  (OpenSSL, libcurl, libpng, libjpeg-turbo, freetype, expat, zlib-ng,
  Eigen3, CGAL, cereal, GMP, MPFR, NLopt, Draco, Qhull, GLFW, OpenCV)
  з поверненням до bundled fallback, якщо пакет відсутній
- Бундлюються лише: Boost, wxWidgets, OpenVDB, OCCT, OpenEXR, TBB, Blosc,
  GLEW, OpenCSG, libnoise
- Встановлення в /opt/OrcaSlicer з desktop/icon інтеграцією
