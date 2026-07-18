# Changelog

## 0.2.1

- Додано `.gitignore` (виключено `build/`, `*.rpm`)
- Оновлено README: оновлено badge, структуру проєкту
- Оновлено CHANGELOG

## 0.2.0

- **Повний перехід на FHS-сумісну збірку** з системними пакетами
  - `SLIC3R_FHS=ON`, `SLIC3R_STATIC=OFF`
  - Використання системних пакетів: Boost, OCCT, OpenCV, OpenVDB, cereal, eigen3, glew, glfw
- **Bundled deps**: wxWidgets-orca 3.3.2, libnoise 1.0, CGAL 5.6.3
- **Патч 0013 (occt-7.9-step-libs)**: заміна старих імен бібліотек OCCT STEP (TKSTEP*, TKXDESTEP → TKDESTEP)
- **wxBUILD_DEBUG_LEVEL=1**: виправлено undefined references до wxFormatString::Validate та wxOnAssert
- **default_patch_fuzz 1**: сумісність патчів з fuzz-зміщенням
- **rm -rf /var/cache/dnf** в Containerfile для економії місця
- **Два GitHub Actions workflow**:
  - `release.yml` — збірка RPM з релізів OrcaSlicer
  - `nightly.yml` — нічна збірка з main (вівторок/четвер ~09:15 UTC)
- **Оновлено .copr/Makefile** для COPR
- **Containerfile** для локального тестування в podman
- Обмеження паралелізму до 8 потоків
- Позначення bundled deps: wxWidgets-orca, libnoise, CGAL

## 0.1.3

- Added COPR packaging for automated Fedora builds
- Simplified COPR Makefile (SRPM-only, no deps pre-build)
- Enabled network access for RPM builds in COPR
- Removed libquadmath-devel from COPR SRPM step (unavailable on aarch64)
- Added libquadmath-devel to spec BuildRequires (required on x86_64)
- Conditional deps skip in spec (uses pre-built deps when available)

## 0.1.2

- Fixed MimeType in .desktop file: corrected 3MF format identifier

## 0.1.1

- Fixed OOM: limited build parallelism to 2 jobs (GitHub Actions ~7GB RAM)
- Disabled workflow triggers on CHANGELOG.md and README.md changes
- Updated documentation

## 0.1.0

- Initial RPM packaging for OrcaSlicer
- GitHub Actions workflow for automated builds in Fedora 44 container
- Spec file with full dependency list for building from source
- Desktop integration (launcher script, .desktop file, icons)
