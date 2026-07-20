# Use System -devel Libraries Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use compose:subagent (recommended) or compose:execute to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modify the OrcaSlicer RPM project to maximize usage of system -devel libraries during compilation instead of building dependencies from source.

**Architecture:** Create a CMake patch that extends the existing FLATPAK system-library pattern to all bundled dependencies, then update the RPM spec to apply this patch and add comprehensive system -devel BuildRequires.

**Tech Stack:** RPM spec, CMake, Fedora 44 system packages

## Global Constraints

- Target: Fedora 44 (per README and GitHub Actions)
- OrcaSlicer deps build system uses `ExternalProject_Add` for each dependency
- Some deps are forked (wxWidgets 3.3.2, OpenVDB, Blosc, libnoise) — these cannot use system versions
- Static linking (`-DSLIC3R_STATIC=1`) means system -devel packages must provide static libs or we must switch to shared
- wxWidgets 3.3.2 is not in Fedora repos (Fedora has 3.2.x) — must build from source
- Eigen 5.0 is not in Fedora repos (Fedora has 3.4.x) — must build from source
- Boost 1.84 is not in Fedora repos (Fedora has 1.83) — risky to use system version

---

## File Structure

| Action | File | Purpose |
|--------|------|---------|
| Create | `patches/use-system-deps.patch` | CMake patch to use system libraries |
| Modify | `orcaslicer.spec` | Add BuildRequires, apply patch, skip bundled deps |
| Modify | `.github/workflows/build-rpm.yml` | Add system deps to dnf install |
| Modify | `.copr/Makefile` | (no change needed — spec handles it) |

---

### Task 1: Create the CMake patch for system library discovery

**Files:**
- Create: `patches/use-system-deps.patch`

**What this does:** Patches `deps/CMakeLists.txt` to add `find_package()` calls for every dependency before its bundled `include()`, and conditionally skips building from source when a system version is found. Follows the existing FLATPAK pattern already used for ZLIB, PNG, EXPAT, CURL, JPEG, Freetype, OpenSSL.

- [ ] **Step 1: Create the patch directory**

```bash
mkdir -p patches
```

- [ ] **Step 2: Create the patch file**

The patch modifies `deps/CMakeLists.txt` to:
1. Add a `USE_SYSTEM_DEPS` cmake option
2. Add find_package() calls for: GMP, MPFR, GLEW, GLFW, Cereal, Qhull, NLopt, Draco, Blosc, OpenEXR, CGAL, TBB, OpenCV, OCCT
3. Wrap each `include(X/X.cmake)` in `if(NOT X_FOUND)` conditionals
4. Update `_dep_list` to only include unbuilt deps

Create file `patches/use-system-deps.patch`:

```diff
diff --git a/deps/CMakeLists.txt b/deps/CMakeLists.txt
--- a/deps/CMakeLists.txt
+++ b/deps/CMakeLists.txt
@@ -XX,XX +XX,XX @@ set(FLATPAK FALSE CACHE BOOL "Toggles various build settings for flatpak, li
 
+option(USE_SYSTEM_DEPS "Use system -devel libraries instead of building from source" OFF)
+
+if(USE_SYSTEM_DEPS)
+    # System library discovery — extend FLATPAK pattern to all deps
+    # Each find_package sets <PKG>_FOUND; individual cmake files check this
+    find_package(ZLIB QUIET)
+    find_package(PNG QUIET)
+    find_package(EXPAT QUIET)
+    find_package(CURL QUIET)
+    find_package(JPEG QUIET)
+    find_package(Freetype QUIET)
+    find_package(OpenSSL QUIET)
+    find_package(Boost QUIET COMPONENTS ${DEP_Boost_COMPONENTS})
+    find_package(GLEW QUIET)
+    find_package(glfw3 QUIET)
+    find_package(TBB QUIET)
+    find_package(Blosc QUIET)
+    find_package(OpenEXR QUIET)
+    find_package(GMP QUIET)
+    find_package(MPFR QUIET)
+    find_package(Eigen3 QUIET)
+    find_package(CGAL QUIET)
+    find_package(NLopt QUIET)
+    find_package(Qhull QUIET)
+    find_package(Draco QUIET)
+    find_package(OpenCV QUIET COMPONENTS core imgcodecs imgproc)
+    find_package(OpenCASCADE QUIET)
+    find_package(Python3 QUIET COMPONENTS Interpreter Development)
+    find_package(wxWidgets QUIET COMPONENTS core base aui gl)
+endif()
+
 if(FLATPAK)
     # flatpak bundles some deps with the layer, so attempt to find them first
     ...
 endif()
```

Then wrap each `include(X/X.cmake)`:

```diff
 set(ZLIB_PKG "")
-if (NOT ZLIB_FOUND)
+if (NOT ZLIB_FOUND AND NOT USE_SYSTEM_DEPS)
     include(ZLIB/ZLIB.cmake)
     set(ZLIB_PKG dep_ZLIB)
 endif ()
```

(Same pattern for PNG, EXPAT, CURL, JPEG, Freetype, OpenSSL, and all new deps)

And update `_dep_list` to use `${X_PKG}` variables for conditional inclusion.

- [ ] **Step 3: Verify patch structure**

Run: `ls -la patches/use-system-deps.patch`
Expected: file exists, non-empty

---

### Task 2: Update the RPM spec file

**Files:**
- Modify: `orcaslicer.spec`

**Changes:**
1. Add `Patch0: use-system-deps.patch` header
2. Add `%autosetup -p1` or `%patch0 -p1` in `%prep`
3. Expand BuildRequires with all system -devel packages
4. Add `-DUSE_SYSTEM_DEPS=ON` to deps cmake invocation
5. Add `-DCMAKE_PREFIX_PATH=/usr` to main cmake invocation
6. Remove `-DSLIC3R_STATIC=1` (switch to shared linking with system libs)
7. Add Requires for runtime shared library dependencies

- [ ] **Step 1: Add patch directive and comprehensive BuildRequires**

Replace the current BuildRequires section with:

```spec
# Build deps — system libraries
BuildRequires:  cmake >= 3.13
BuildRequires:  ninja-build
BuildRequires:  gcc gcc-c++
BuildRequires:  pkgconf
BuildRequires:  autoconf automake libtool m4
BuildRequires:  git wget file
BuildRequires:  perl-FindBin perl-IPC-Cmd
BuildRequires:  nasm
BuildRequires:  chrpath

# System -devel libraries (used instead of bundled)
BuildRequires:  zlib-devel
BuildRequires:  libpng-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  expat-devel
BuildRequires:  libcurl-devel
BuildRequires:  openssl-devel
BuildRequires:  freetype-devel
BuildRequires:  fontconfig-devel
BuildRequires:  boost-devel
BuildRequires:  boost-system boost-iostreams boost-filesystem boost-thread boost-log boost-locale boost-regex boost-date_time
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

# GUI/runtime deps
BuildRequires:  gtk3-devel
BuildRequires:  webkit2gtk4.1-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  mesa-libEGL-devel
BuildRequires:  mesa-libGLU-devel
BuildRequires:  dbus-devel
BuildRequires:  libX11-devel
BuildRequires:  pango-devel
BuildRequires:  at-spi2-core-devel
BuildRequires:  libepoxy-devel
BuildRequires:  wayland-protocols-devel
BuildRequires:  libxkbcommon-devel
BuildRequires:  libXi-devel libXrandr-devel libXinerama-devel
BuildRequires:  libXcursor-devel libXcomposite-devel libXdamage-devel libXext-devel
BuildRequires:  libXtst-devel libXfixes-devel libXmu-devel
BuildRequires:  libspnav-devel libsecret-devel libmspack-devel
BuildRequires:  extra-cmake-modules eglexternalplatform-devel
BuildRequires:  gstreamer1-devel gstreamer1-plugins-base-devel gstreamermm-devel
BuildRequires:  texinfo
BuildRequires:  libquadmath-devel
```

- [ ] **Step 2: Update %prep to apply patch**

```spec
%prep
%autosetup -n OrcaSlicer-%{version} -p1
```

- [ ] **Step 3: Update %build to use system deps**

```spec
%build
export CMAKE_POLICY_VERSION_MINIMUM=3.5

NPROC_DEPS=2
NPROC_BUILD=2

# Build only truly incompatible deps from source
# (wxWidgets 3.3.2, Eigen 5.0 — not in Fedora repos)
if [ ! -d deps/build ]; then
  echo "=== Building dependencies (system-deps mode) ==="
  mkdir -p deps/build
  cmake -S deps -B deps/build -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
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
```

- [ ] **Step 4: Update Requires for runtime deps**

```spec
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
```

- [ ] **Step 5: Verify spec syntax**

Run: `rpmlint orcaslicer.spec` (if available) or review manually for syntax errors

---

### Task 3: Update GitHub Actions workflow

**Files:**
- Modify: `.github/workflows/build-rpm.yml`

**Changes:** Add all new system -devel packages to the `dnf install` step.

- [ ] **Step 1: Update dnf install step**

Add to the `Install build dependencies` step:

```yaml
      - name: Install build dependencies
        run: |
          dnf install -y \
            rpm-build rpmdevtools git wget curl unzip \
            cmake ninja-build gcc gcc-c++ pkgconf \
            autoconf automake libtool m4 \
            perl-FindBin perl-IPC-Cmd \
            libquadmath-devel nasm \
            zlib-devel libpng-devel libjpeg-turbo-devel \
            expat-devel libcurl-devel openssl-devel \
            freetype-devel \
            boost-devel \
            cereal-devel qhull-devel glew-devel glfw3-devel \
            tbb-devel blosc-devel openexr-devel openvdb-devel \
            gmp-devel mpfr-devel eigen3-devel CGAL-devel \
            nlopt-devel draco-devel opencv-devel OpenCASCADE-devel \
            python3-devel \
            dbus-devel gtk3-devel webkit2gtk4.1-devel \
            mesa-libGLU-devel mesa-libGL-devel \
            fontconfig-devel pango-devel \
            extra-cmake-modules eglexternalplatform-devel \
            gstreamer1-devel gstreamer1-plugins-base-devel gstreamermm-devel \
            wayland-protocols-devel libxkbcommon-devel \
            libX11-devel libXi-devel libXrandr-devel libXinerama-devel \
            libXcursor-devel libXcomposite-devel libXdamage-devel libXext-devel \
            libXtst-devel libXfixes-devel libXmu-devel \
            at-spi2-core-devel libepoxy-devel \
            libspnav-devel libsecret-devel libmspack-devel \
            texinfo chrpath
```

- [ ] **Step 2: Verify workflow YAML syntax**

Run: `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/build-rpm.yml'))"` or review manually

---

### Task 4: Update README.md build instructions

**Files:**
- Modify: `README.md`

**Changes:** Update the "Build from Source" section to include all new system deps.

- [ ] **Step 1: Update dnf install command in README**

Replace the existing dnf install block with the same comprehensive list from Task 3.

---

### Task 5: Verify the complete solution

- [ ] **Step 1: Review all changed files for consistency**

Check that:
- All BuildRequires in spec match the dnf install in workflow and README
- The patch file is syntactically correct
- cmake flags are consistent between deps build and main build
- Runtime Requires match what the binary actually links against

- [ ] **Step 2: Check that wxWidgets and Eigen are still built from source**

These are NOT in Fedora repos at the required versions and must remain bundled.

- [ ] **Step 3: Final review**

Ensure no circular dependencies and that the dependency order is preserved.
