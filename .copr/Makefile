srpm:
	set -e; \
	BASEDIR=$$(pwd); \
	\
	echo "=== Installing build dependencies ==="; \
	dnf -y install rpmdevtools wget curl \
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
	  texinfo chrpath; \
	\
	echo "=== Fetching latest release version ==="; \
	VERSION=$$(curl -sf https://api.github.com/repos/OrcaSlicer/OrcaSlicer/releases/latest \
	  | grep '"tag_name"' | cut -d '"' -f 4 | sed 's/^v//'); \
	if [ -z "$$VERSION" ]; then \
	  echo "ERROR: failed to determine latest version from GitHub API"; \
	  exit 1; \
	fi; \
	echo "Latest version: $${VERSION}"; \
	\
	echo "=== Downloading source tarball ==="; \
	wget -q "https://github.com/OrcaSlicer/OrcaSlicer/archive/refs/tags/v$${VERSION}.tar.gz" \
	  -O "orcaslicer-$${VERSION}-src.tar.gz"; \
	\
	echo "=== Extracting source ==="; \
	rm -rf _src; \
	mkdir -p _src; \
	tar xzf "orcaslicer-$${VERSION}-src.tar.gz" -C _src; \
	\
	echo "=== Building dependencies ==="; \
	export CMAKE_POLICY_VERSION_MINIMUM=3.5; \
	cd "_src/OrcaSlicer-$${VERSION}"; \
	mkdir -p deps/build; \
	cmake -S deps -B deps/build -G Ninja \
	  -DCMAKE_BUILD_TYPE=Release \
	  -DDEP_WX_GTK3=ON; \
	cmake --build deps/build -j2; \
	cd "$$BASEDIR"; \
	\
	echo "=== Repackaging with dependencies ==="; \
	rm -f "orcaslicer-$${VERSION}-src.tar.gz"; \
	tar czf "orcaslicer-$${VERSION}-src.tar.gz" -C _src "OrcaSlicer-$${VERSION}"; \
	rm -rf _src; \
	ls -lh "orcaslicer-$${VERSION}-src.tar.gz"; \
	\
	echo "=== Preparing rpmbuild tree ==="; \
	rpmdev-setuptree; \
	mkdir -p "$$HOME/rpmbuild/SOURCES" "$$HOME/rpmbuild/SPECS"; \
	cp "orcaslicer-$${VERSION}-src.tar.gz" "$$HOME/rpmbuild/SOURCES/"; \
	\
	echo "=== Generating spec file from template ==="; \
	test -f orcaslicer.spec || { echo "ERROR: orcaslicer.spec not found in repo root"; exit 1; }; \
	sed -e "s/@VERSION@/$${VERSION}/g" \
	    -e "s/@RELEASE@/1/g" \
	    orcaslicer.spec > "$$HOME/rpmbuild/SPECS/orcaslicer.spec"; \
	\
	echo "=== Building SRPM ==="; \
	rpmbuild -bs \
	  --define "_sourcedir $$HOME/rpmbuild/SOURCES" \
	  --define "_srcrpmdir $(outdir)" \
	  "$$HOME/rpmbuild/SPECS/orcaslicer.spec"; \
	\
	echo "=== Done ==="; \
	ls -la "$(outdir)"
