# These can be overriden on the command line
PROJECT?=myproject
VERSION?=0.1
RELEASE?=1
OUTPUTSPECFILE?=project.spec

INPUT?=/opt/project
OUTPUT?=/opt/project

# End of configuration
$(info PROJECT:$(PROJECT): VERSION:$(VERSION): RELEASE:$(RELEASE))

# Make's realpath won't expand ~
REAL_INPUT=$(shell realpath -e $(INPUT))
TARBALL?=$(PROJECT).tar
RPM_TEMP?=$(CURDIR)/rpmbuild-tmpdir

ifeq ($(REAL_INPUT),)
  $(error Error parsing INPUT=$(INPUT))
endif

# Even real files are declared "phony" since dependencies otherwise broken
default: rpm
.PHONY: clean rpm $(TARBALL) filelist-$(PROJECT).txt
.SILENT: clean rpm $(TARBALL) filelist-$(PROJECT).txt

clean:
	rm -vrf $(RPM_TEMP) $(TARBALL) $(PROJECT)*.rpm filelist-$(PROJECT).txt

rpm: $(TARBALL) $(EXTRA_SOURCES)
	mkdir -p $(RPM_TEMP)/SOURCES
	cp --target-directory=$(RPM_TEMP)/SOURCES/ $^
	rpmbuild -ba \
		--define="_topdir $(RPM_TEMP)" \
		--define "outdir  $(OUTPUT)"   \
		--define "project_ $(PROJECT)" \
		--define "version_ $(VERSION)" \
		--define "release_ $(RELEASE)" \
		$(OUTPUTSPECFILE)
	cp -v --target-directory=. $(RPM_TEMP)/SRPMS/*.rpm $(RPM_TEMP)/RPMS/*/*.rpm

# The transform will replace the absolute path with a relative one with a new top-level of "proj-ver", which is what RPM prefers
$(TARBALL): filelist-$(PROJECT).txt
	echo "Building tarball of $(shell cat $< | wc -l) files"
	tar --files-from=$< --owner=0 --group=0 --absolute-names --transform 's|^$(REAL_INPUT)|$(PROJECT)-$(VERSION)|' -cf $@
	ls -halF $@

filelist-$(PROJECT).txt: $(REAL_INPUT)
	find $(REAL_INPUT) -type f -not -path '*/\.git/*' > $@
