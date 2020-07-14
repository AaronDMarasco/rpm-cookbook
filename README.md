Table of Contents

* [rpm-cookbook](#rpm-cookbook)
  * [How to...](#how-to)
    * [... define Version, Release, etc. in another file, environment variable, etc.](#define-version,-release,-etc--in-another-file,-environment-variable,-etc)
    * [... call `rpmbuild` from a `Makefile`](#call--rpmbuild--from-a--makefile)
    * [... disable debug packaging](#disable-debug-packaging)
  * [Quick Tips](#quick-tips)
    * [Don't Put Single % In Comments](#don't-put-single-%-in-comments)
    * [Extract All Files](#extract-all-files)
    * [Extract a Single File](#extract-a-single-file)
    * [Change (or No) Compression](#change-(or-no)-compression)
    * [Set Output of a Random Shell Command Into Variable](#set-output-of-a-random-shell-command-into-variable)
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

I (Aaron D. Marasco) have been creating RPM packages since the CentOS 4 timeframe([1], [2], [3]). I decided to collate some of the things I've done before that I keep referencing in new projects, as well as answering some of the most common questions I see. This should be considered a *complement* and *not a replacement* for the [*Fedora Packaging Guidelines*](https://fedoraproject.org/wiki/Category:Packaging_guidelines).

Each "chapter" is a separate directory, and any specfiles or `Makefile`s are transcluded, so they are available as source files in the git repo. No need to copy and paste from your browser!

Feel free to create a new chapter and submit a PR!

## How to...
### ... define Version, Release, etc. in another file, environment variable, etc.
This is shown in:
 * [Importing a Pre-Existing File Tree](#importing-a-pre-existing-file-tree)
### ... call `rpmbuild` from a `Makefile`
This is shown in:
 * [Importing a Pre-Existing File Tree](#importing-a-pre-existing-file-tree)
### ... disable debug packaging
While **not recommended**, because debug packages are very useful, this is shown in:
 * [Importing a Pre-Existing File Tree](#importing-a-pre-existing-file-tree)
----

## Quick Tips
In reviewing some of the most highly voted answers on Stack Overflow, I decided to collate a few:

### Don't Put Single % In Comments
This happens [a](https://stackoverflow.com/a/14063974/836748) [*lot*](https://stackoverflow.com/a/18440679/836748). You need to double it with `%%` or a multi-line macro will only have the first line commented out!

### Extract All Files
Use `rpm2cpio` with `cpio`:
```bash
$ rpm2cpio package-version.rpm | cpio -div
```

### Extract a Single File
As noted [here](https://stackoverflow.com/a/16605713/836748), use `rpm2cpio` with `cpio --to-stdout`:
```bash
$ rpm2cpio package-3.8.3.rpm | cpio -iv --to-stdout ./usr/share/doc/package-3.8.3/README > /tmp/README
./usr/share/doc/package-3.8.3/README
2173 blocks
```

### Change (or No) Compression
As noted [here](https://stackoverflow.com/a/10255406/836748):
```rpm-spec
%define _source_payload w0.gzdio
%define _binary_payload w0.gzdio
```
These will send `-0` to `gzip` to effectively not compress. The `0` can be 0-9 to change the level. The `gz` can be changed:
 * `bz` for bzip2
 * `xz` for XZ/LZMA (on some versions of RPM)

### Set Output of a Random Shell Command Into Variable
As noted [here](https://stackoverflow.com/a/10694815/836748):
```rpm-spec
%global your_var %(shell your commands)
```

----

## Importing a Pre-Existing File Tree
### Reasoning
This is probably one of the most common questions on Stack Overflow. It might be because you don't know enough about RPMs to "do it right" or you just want to "get it done."

I'm a little reluctant to include this, because doing it the "right way" isn't all that hard.

**This is not recommended** but sometimes inevitable:
 * The build system is too complicated (seldom)
 * You're packaging something already installed
   * that you have no control over
   * was installed by a GUI installer and you want to repackage
   * you don't have source code for

### Recipe
This recipe has two parts, a [`Makefile`](pre-existing_file_tree/Makefile) and a [specfile](pre-existing_file_tree/project.spec). There is also an example [`.gitignore`](pre-existing_file_tree/.gitignore) that might be useful as well.

[`Makefile`](pre-existing_file_tree/Makefile):
```Makefile
# These can be overriden on the command line
PROJECT?=myproject
VERSION?=0.1
RELEASE?=1

INPUT?=/opt/project
OUTPUT?=/opt/project

# End of configuration
# Make's realpath won't expand ~
REAL_INPUT=$(shell realpath -e $(INPUT))

TARBALL?=$(PROJECT).tar

RPM_TEMP?=$(CURDIR)/rpmbuild-tmpdir

ifeq ($(REAL_INPUT),)
  $(error Error parsing INPUT=$(INPUT))
endif

# Even real files are declared "phony" since dependencies otherwise broken
default: rpm
.PHONY: clean rpm $(TARBALL) filelist.txt
.SILENT: clean rpm $(TARBALL) filelist.txt

clean:
	rm -rf $(RPM_TEMP) $(TARBALL) $(PROJECT)*.rpm filelist.txt

rpm: $(TARBALL) filelist.txt
	mkdir -p $(RPM_TEMP)/SOURCES
	cp --target-directory=$(RPM_TEMP)/SOURCES/ $^
	rpmbuild -ba \
		--define="_topdir $(RPM_TEMP)" \
		--define "outdir $(OUTPUT)" \
		--define "project_ $(PROJECT)" \
		--define "version_ $(VERSION)" \
		--define "release_ $(RELEASE)" \
		project.spec
	cp -v --target-directory=. $(RPM_TEMP)/SRPMS/*.rpm $(RPM_TEMP)/RPMS/*/*.rpm

# The transform will replace the absolute path with a relative one with a new top-level of "proj-ver", which is what RPM prefers
$(TARBALL): filelist.txt
	echo "Building tarball of $(shell cat $< | wc -l) files"
	tar --files-from=$< --owner=0 --group=0 --absolute-names --transform 's|^$(REAL_INPUT)|$(PROJECT)-$(VERSION)|' -cf $@

filelist.txt: $(REAL_INPUT)
	find $(REAL_INPUT) -type f -not -path '*/\.git/*' > $@

```

[specfile](pre-existing_file_tree/project.spec):
```rpm-spec
Name: %{project_}
Version: %{version_}
Release: %{release_}
License: MIT
Summary: My Poorly Packaged Project
Source0: %{name}.tar
# Remove this line if you have executables with debug info in the source tree:
%global debug_package %{nil}
BuildRequires: sed tar

%description
This RPM is effectively a fancy tarball.

%prep
set -o pipefail
# Default setup - extract the tarball
%setup -q
# Generate the file list with absolute target pathnames)
tar tf %{SOURCE0} | sed -e 's|^%{name}-%{version}|%{outdir}|' > parsed_filelist.txt

%build
# Empty; rpmlint recommendeds it is present anyway

%install
%{__mkdir_p} %{buildroot}/%{outdir}/
%{__cp} --target-directory=%{buildroot}/%{outdir}/ -Rv .
%{__rm} %{buildroot}/%{outdir}/parsed_filelist.txt

%clean
%{__rm} -rf --preserve-root %{buildroot}

%files -f parsed_filelist.txt

```

### How It Works
The `Makefile` takes various variables and generates a temporary tarball as well as a file listing that are used by the specfile. It uses that to build the `%files` directive and has an empty `%build` phase.

|  Variable  |         Default         |             Use Case             |
|:----------:|:-----------------------:|:--------------------------------:|
| `INPUT`    | `/opt/project`          | Source Tree to Copy              |
| `OUTPUT`   | `/opt/project`          | Destination on Target Machine    |
| `PROJECT`  | myproject               | Base Name of the RPM             |
| `VERSION`  | 0.1                     | Version of the RPM               |
| `RELEASE`  | 1                       | Release/ Build of the RPM        |
| `TARBALL`  | `{PROJECT}.tar`         | Temporary tarball used to build  |
| `RPM_TEMP` | `{CWD}/rpmbuild-tmpdir` | Temporary directory to build RPM |


----


## Git Problems
### Git Branch or Tag in Release
#### Reasoning

#### Recipe

----

### Monotonic Release Numbers
#### Reasoning

#### Recipe

----

## Jenkins Job Number in Release
### Reasoning

### Recipe

----


## Having Multiple Versions
### Symlinks to Latest
#### Reasoning

#### Recipe

----

## Spoofing RPM Host Name
### Reasoning
When distributing RPMs, you might not want people to know the build host. It shouldn't matter to the end user, and your security folks might not want internal hostnames or DNS information published for no good reason.

Newer versions of `rpmbuild` support defining `_buildhost`; I have not tested that capability myself.

### Recipe
This recipe requires you wrap your `rpmbuild` command with a script or `Makefile`. Using the `Makefile` below, you would have `make` call `$(SPOOF_HOSTNAME) rpmbuild ...`.

Edit the `Makefile` yourself where it says "`.myprojectname.proj`" - you can optionally _not_ have it use the `buildhost_<arch>` prefix as well.

Other usage notes are at the top of the `Makefile`.

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
It sets [`LD_PRELOAD`](view-source:https://man7.org/linux/man-pages/man8/ld.so.8.html) to intercept all 32- or 64-bit calls to [`gethostname()`](https://man7.org/linux/man-pages/man2/gethostname.2.html) and replace them with the text you provide.


  [1]: https://stackoverflow.com/search?q=user:836748+[rpm]
  [2]: https://stackoverflow.com/search?q=user:836748+[rpmbuild]
  [3]: https://stackoverflow.com/search?q=user:836748+[rpm-spec]
