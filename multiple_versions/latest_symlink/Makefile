# These can be overriden on the command line (but will break test, sorry)
rpm_names?=myproject myproject-compat1p0p1 myproject-compat1p1
version?=1.2
release?=1
# End of configuration

RPM_TEMP?=$(CURDIR)/rpmbuild-tmpdir

default: rpms
.PHONY: clean rpms test
.SILENT: clean rpms test

clean:
	rm -vrf $(RPM_TEMP) $(foreach project_, $(rpm_names), $(project_)*.rpm)
	rpm -q --whatprovides myproject >/dev/null && rpm -q --whatprovides myproject | xargs -rt sudo rpm -ev || :

define do_build
	rpmbuild -ba \
	  --define="_topdir   $(RPM_TEMP)" \
	  --define="project_  $(project_)" \
	  --define="version_  $(version)"  \
	  --define="release_  $(release)"  \
	  project.spec
	cp -v --target-directory=. $(RPM_TEMP)/SRPMS/*.rpm $(RPM_TEMP)/RPMS/*/*.rpm
endef

rpms:
	$(foreach project_, $(rpm_names), $(do_build);)

test: clean rpms
	echo "Install main RPM:"
	sudo rpm -i myproject-1.2-1.noarch.rpm
	echo "Main RPM provides:"
	rpm -q --provides myproject
	tree -a /opt/my_org/
	echo "Install compat RPMs:"
	sudo rpm -i myproject-compat1p0p1-1.2-1.noarch.rpm myproject-compat1p1-1.2-1.noarch.rpm
	echo "Compat RPMs provide:"
	rpm -q --provides myproject-compat1p0p1 myproject-compat1p1 | sort
	echo "Who provides ANY 'myproject'?"
	rpm -q --whatprovides myproject
	echo "Compat RPMs do not take over symlink:"
	tree -a /opt/my_org/
	echo "Removing all (expect a warning):"
	sudo rpm -e myproject myproject-compat1p0p1 myproject-compat1p1
	# tree -a /opt/my_org/
	echo "Now install compat 1.0.1 only:"
	sudo rpm -i myproject-compat1p0p1-1.2-1.noarch.rpm
	echo "Latest should be compat 1.0.1:"
	tree -a /opt/my_org/
	echo "Now install compat 1.1 only:"
	sudo rpm -i myproject-compat1p1-1.2-1.noarch.rpm
	echo "Latest should be compat 1.0.1 still - FIRST compat installed 'wins':"
	tree -a /opt/my_org/
	echo "Install regular; should overwrite symlink (will warn):"
	sudo rpm -i myproject-1.2-1.noarch.rpm
	tree -a /opt/my_org/
	echo "Removing compat 1.0.1 only (so no warning about broken link):"
	sudo rpm -e myproject-compat1p0p1
	tree -a /opt/my_org/
	echo "Now removing main package (should be told that 1.1 is a candidate):"
	sudo rpm -e myproject
	tree -a /opt/my_org/
	echo "Removing compat 1.1 only (no warnings; removed symlink but no candidates remain):"
	sudo rpm -e myproject-compat1p1
	echo "Now install compat 1.1 only:"
	sudo rpm -i myproject-compat1p1-1.2-1.noarch.rpm
	echo "Symlink now 1.1:"
	tree -a /opt/my_org/
	echo "Now install compat 1.0.1 and immediately deleting (it should leave symlink alone):"
	sudo rpm -i myproject-compat1p0p1-1.2-1.noarch.rpm
	sudo rpm -e myproject-compat1p0p1
	tree -a /opt/my_org/
	echo "Removing compat 1.1 only (should clean up the symlink):"
	sudo rpm -e myproject-compat1p1
	echo "What's left behind in /opt/my_org/:"
	tree -a /opt/my_org/
