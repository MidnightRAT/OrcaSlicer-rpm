srpm:
	dnf -y install rpmdevtools wget curl

	VERSION=$$(curl -s https://api.github.com/repos/OrcaSlicer/OrcaSlicer/releases/latest \
	  | grep '"tag_name"' | cut -d '"' -f 4 | sed 's/^v//'); \
	echo "Latest version: $${VERSION}"; \
	\
	wget -q "https://github.com/OrcaSlicer/OrcaSlicer/archive/refs/tags/v$${VERSION}.tar.gz" \
	  -O orcaslicer-$${VERSION}-src.tar.gz; \
	\
	rpmdev-setuptree; \
	cp orcaslicer-$${VERSION}-src.tar.gz ~/rpmbuild/SOURCES/; \
	\
	sed -e "s/@VERSION@/$${VERSION}/g" \
	    -e "s/@RELEASE@/1/g" \
	    orcaslicer.spec > ~/rpmbuild/SPECS/orcaslicer.spec; \
	\
	rpmbuild -bs \
	  --define "_sourcedir $$HOME/rpmbuild/SOURCES" \
	  --define "_srcrpmdir $(outdir)" \
	  ~/rpmbuild/SPECS/orcaslicer.spec
