Table of Contents

* [rpm-cookbook](#rpm-cookbook)
  * [Importing a Pre-Existing File Tree](#importing-a-pre-existing-file-tree)
  * [Git Problems](#git-problems)
    * [Git Branch or Tag in Release](#git-branch-or-tag-in-release)
    * [Monotonic Release Numbers](#monotonic-release-numbers)
  * [Jenkins Job Number in Release](#jenkins-job-number-in-release)
  * [Having Multiple Versions](#having-multiple-versions)
    * [Symlinks to Latest](#symlinks-to-latest)
  * [Spoofing RPM Host Name](#spoofing-rpm-host-name)





# rpm-cookbook
Cookbook of RPM techniques

I (Aaron D. Marasco) have been creating RPM packages since the CentOS 4 timeframe([1], [2], [3]). I decided to collate some of the things I've done before that I keep referencing.

Feel free to create a new chapter and submit a PR!

## Importing a Pre-Existing File Tree
### Reasoning

### Recipe


## Git Problems
### Git Branch or Tag in Release
#### Reasoning

#### Recipe

### Monotonic Release Numbers
#### Reasoning

#### Recipe

## Jenkins Job Number in Release
### Reasoning

### Recipe


## Having Multiple Versions
### Symlinks to Latest
#### Reasoning

#### Recipe

## Spoofing RPM Host Name
### Reasoning
When distributing RPMs, you might not want people to know the build host. It shouldn't matter to the end user, and your security folks might not want internal hostnames or DNS information published for no good reason.

Newer versions of `rpmbuild` support defining `_buildhost`; I have not tested that capability myself.

### Recipe
This recipe requires you wrap your `rpmbuild` command with a script or `Makefile`. Using the `Makefile` below, you would have `make` call `$(SPOOF_HOSTNAME) rpmbuild ...`.

Edit the `Makefile` yourself where it says "`.myprojectname.proj`" - you can optionally _not_ have it use the `buildhost_<arch>` prefix as well.

[`Makefile`](fake_buildhost/Makefile):
```Makefile
# This spoofs the build host for both 32- and 64-bit applications

# To use:
# 1. Add libmyhostname as a target that calls rpmbuild
# 2. Add "myhostnameclean" as a target to your "clean"
# 3. Call rpmbuild or any other program with $(SPOOF_HOSTNAME) prefix

MYHOSTNAME_MNAME:=$(shell uname -m)
libmyhostname:=libmyhostname_$(MYHOSTNAME_MNAME).so
MYHOSTNAME_PWD:=$(shell pwd)
SPOOF_HOSTNAME:=LD_PRELOAD=$(MYHOSTNAME_PWD)/myhostname/\$LIB/$(libmyhostname)

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
	echo "$libmyhostname_body" > $@

define libmyhostname_body
#include <string.h>
#include <asm/errno.h>

int gethostname(char *name, size_t len) {
	const char *myhostname = "buildhost_$(MYHOSTNAME_MNAME).myprojectname.proj";
	if (len < strlen(myhostname))
		return(EINVAL);
	strcpy(name, myhostname);
	return(0);
}
endef
export libmyhostname_body

```

### How It Works
It sets `LD_PRELOAD` to intercept all 32- or 64-bit calls to `gethostname` and replace them with the text you provide.


  [1]: https://stackoverflow.com/search?q=user:836748+[rpm]
  [2]: https://stackoverflow.com/search?q=user:836748+[rpmbuild]
  [3]: https://stackoverflow.com/search?q=user:836748+[rpm-spec]
