# This spoofs the build host for both 32- and 64-bit applications

default: testrpm

# To use:
# 1. Add libmyhostname as a target that calls rpmbuild
# 2. Add "myhostnameclean" as a target to your "clean"
# 3. Call rpmbuild or any other program with $(SPOOF_HOSTNAME) prefix

MYHOSTNAME_MNAME:=$(shell uname -m)
libmyhostname:=libmyhostname_$(MYHOSTNAME_MNAME).so
MYHOSTNAME_PWD:=$(shell pwd)
SPOOF_HOSTNAME:=LD_PRELOAD=$(MYHOSTNAME_PWD)/myhostname/\$$LIB/$(libmyhostname)

.PHONY: myhostnameclean
.SILENT: myhostnameclean
.IGNORE: myhostnameclean
myhostnameclean:
	rm -rf myhostname

# Linux doesn't support explicit 32- vs. 64-bit LD paths like Solaris, but ld.so
# does accept a literal "$LIB" in the path to expand to lib vs lib64. So we need
# to make our own private library tree myhostname/lib{,64} to feed to rpmbuild.
.PHONY: libmyhostname
.SILENT: libmyhostname
libmyhostname: /usr/include/gnu/stubs-32.h /lib/libgcc_s.so.1
	mkdir -p myhostname/lib{,64}
	$(MAKE) -I $(MYHOSTNAME_PWD) -s --no-print-directory -C myhostname/lib   -f $(MYHOSTNAME_PWD)/Makefile $(libmyhostname) MYHOSTARCH=32
	$(MAKE) -I $(MYHOSTNAME_PWD) -s --no-print-directory -C myhostname/lib64 -f $(MYHOSTNAME_PWD)/Makefile $(libmyhostname) MYHOSTARCH=64

.SILENT: /usr/include/gnu/stubs-32.h /lib/libgcc_s.so.1
/usr/include/gnu/stubs-32.h:
	echo "You need to install the 'glibc-devel.i686' package."
	echo "'sudo yum install glibc-devel.i686' should do it for you."
	false

/lib/libgcc_s.so.1:
	echo "You need to install the 'libgcc.i686' package."
	echo "'sudo yum install libgcc.i686' should do it for you."
	false

.SILENT: libmyhostname $(libmyhostname) libmyhostname_$(MYHOSTNAME_MNAME).o libmyhostname_$(MYHOSTNAME_MNAME).c
$(libmyhostname): libmyhostname_$(MYHOSTNAME_MNAME).o
	echo "Building $(MYHOSTARCH)-bit version of hostname spoofing library."
	gcc -m$(MYHOSTARCH) -shared -o $@ $<

libmyhostname_$(MYHOSTNAME_MNAME).o: libmyhostname_$(MYHOSTNAME_MNAME).c
	gcc -m$(MYHOSTARCH) -fPIC -rdynamic -g -c -Wall $<

libmyhostname_$(MYHOSTNAME_MNAME).c:
	echo "$$libmyhostname_body" > $@

define libmyhostname_body
#include <asm/errno.h>
#include <netdb.h>
#include <string.h>

int gethostname(char *name, size_t len) {
	const char *myhostname = "buildhost_$(MYHOSTNAME_MNAME).myprojectname.proj";
	if (len < strlen(myhostname))
		return EINVAL;
	strcpy(name, myhostname);
	return 0;
}

struct hostent *gethostbyname(const char *name) {
	return NULL;  /* Let it fail */
}

endef
export libmyhostname_body

## End of Recipe. Example Usage Code:
.PHONY: clean testrpm
.SILENT: clean testrpm

project?=myproject
version?=1.2
release?=3
RPM_TEMP?=$(CURDIR)/rpmbuild-tmpdir

clean: myhostnameclean

define do_build
	rpmbuild -ba \
	  --define="_topdir   $(RPM_TEMP)" \
	  --define="project_  $(project)"  \
	  --define="version_  $(version)"  \
	  --define="release_  $(release)"  \
	  project.spec
	cp -v --target-directory=. $(RPM_TEMP)/SRPMS/*.rpm $(RPM_TEMP)/RPMS/*/*.rpm
endef

testrpm: clean libmyhostname
	$(do_build)
	echo "Build hosts: (without spoof)"
	rpm -qip $(project)-$(version)-$(release).src.rpm $(project)-$(version)-$(release).noarch.rpm | grep "Build Host"
	$(SPOOF_HOSTNAME) $(do_build)
	echo "Build hosts: (with spoof)"
	rpm -qip $(project)-$(version)-$(release).src.rpm $(project)-$(version)-$(release).noarch.rpm | grep "Build Host"
