srpm:
	set -e; \
	dnf -y install rpmdevtools wget curl; \
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
	ls -la "orcaslicer-$${VERSION}-src.tar.gz"; \
	\
	echo "=== Preparing rpmbuild tree ==="; \
	rpmdev-setuptree; \
	mkdir -p "$$HOME/rpmbuild/SOURCES" "$$HOME/rpmbuild/SPECS"; \
	ls -la "$$HOME/rpmbuild"; \
	cp "orcaslicer-$${VERSION}-src.tar.gz" "$$HOME/rpmbuild/SOURCES/"; \
	\
	echo "=== Generating spec file from template ==="; \
	test -f orcaslicer.spec || { echo "ERROR: orcaslicer.spec not found in repo root"; exit 1; }; \
	sed -e "s/@VERSION@/$${VERSION}/g" \
	    -e "s/@RELEASE@/1/g" \
	    orcaslicer.spec > "$$HOME/rpmbuild/SPECS/orcaslicer.spec"; \
	cat "$$HOME/rpmbuild/SPECS/orcaslicer.spec"; \
	\
	echo "=== Building SRPM ==="; \
	rpmbuild -bs \
	  --define "_sourcedir $$HOME/rpmbuild/SOURCES" \
	  --define "_srcrpmdir $(outdir)" \
	  "$$HOME/rpmbuild/SPECS/orcaslicer.spec"; \
	\
	echo "=== Done, result: ==="; \
	ls -la "$(outdir)"
