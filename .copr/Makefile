srpm:
	set -e; \
	\
	echo "=== Installing build tools ==="; \
	dnf -y install --skip-unavailable rpmdevtools wget curl unzip; \
	\
	echo "=== Fetching latest release version ==="; \
	VERSION=$$(curl -sfL https://api.github.com/repos/OrcaSlicer/OrcaSlicer/releases/latest \
	  | grep -oE '"tag_name"[[:space:]]*:[[:space:]]*"[^"]*"' | head -n 1 \
	  | cut -d '"' -f 4 | sed 's/^v//'); \
	if ! printf '%s' "$$VERSION" | grep -Eq '^[0-9]+(\.[0-9]+)+$$'; then \
	  echo "ERROR: failed to determine latest version from GitHub API (got: '$$VERSION')"; \
	  exit 1; \
	fi; \
	echo "Latest version: $${VERSION}"; \
	\
	echo "=== Downloading source tarball ==="; \
	wget -q "https://github.com/OrcaSlicer/OrcaSlicer/archive/refs/tags/v$${VERSION}.tar.gz" \
	  -O "OrcaSlicer-$${VERSION}.tar.gz"; \
	ls -lh "OrcaSlicer-$${VERSION}.tar.gz"; \
	\
	echo "=== Preparing rpmbuild tree ==="; \
	rpmdev-setuptree; \
	mkdir -p "$$HOME/rpmbuild/SOURCES" "$$HOME/rpmbuild/SPECS"; \
	cp "OrcaSlicer-$${VERSION}.tar.gz" "$$HOME/rpmbuild/SOURCES/"; \
	cp README.md "$$HOME/rpmbuild/SOURCES/"; \
	\
	echo "=== Copying patches ==="; \
	for p in patches/0*.patch; do \
	  if [ -f "$$p" ]; then \
	    cp "$$p" "$$HOME/rpmbuild/SOURCES/"; \
	    echo "  Copied: $$p"; \
	  fi; \
	done; \
	\
	echo "=== Generating spec file from template ==="; \
	test -f orca-slicer.spec || { echo "ERROR: orca-slicer.spec not found in repo root"; exit 1; }; \
	sed -e "s/@VERSION@/$${VERSION}/g" \
	    -e "s/@RELEASE@/1/g" \
	    orca-slicer.spec > "$$HOME/rpmbuild/SPECS/orca-slicer.spec"; \
	\
	echo "=== Building SRPM ==="; \
	rpmbuild -bs \
	  --define "_sourcedir $$HOME/rpmbuild/SOURCES" \
	  --define "_srcrpmdir $(outdir)" \
	  "$$HOME/rpmbuild/SPECS/orca-slicer.spec"; \
	\
	echo "=== Done ==="; \
	ls -la "$(outdir)"