srpm:
	set -e; \
	\
	echo "=== Installing build tools ==="; \
	dnf -y install --skip-unavailable rpmdevtools wget curl; \
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
	ls -lh "orcaslicer-$${VERSION}-src.tar.gz"; \
	\
	echo "=== Preparing rpmbuild tree ==="; \
	rpmdev-setuptree; \
	mkdir -p "$$HOME/rpmbuild/SOURCES" "$$HOME/rpmbuild/SPECS"; \
	cp "orcaslicer-$${VERSION}-src.tar.gz" "$$HOME/rpmbuild/SOURCES/"; \
	cp patches/use-system-deps.patch "$$HOME/rpmbuild/SOURCES/" 2>/dev/null || true; \
	\
	echo "=== Generating spec file from template ==="; \
	test -f orcaslicer.spec || { echo "ERROR: orcaslicer.spec not found in repo root"; exit 1; }; \
	sed -e "s/@VERSION@/$${VERSION}/g" \
	    -e "s/@RELEASE@/2/g" \
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
