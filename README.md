Table of Contents

* [rpm-cookbook](#rpm-cookbook)
  * [Overview](#overview)
  * [Quick Tips](#quick-tips)
    * [RPM Preprocessor is Really Dumb](#rpm-preprocessor-is-really-dumb)
    * [Extract All Files](#extract-all-files)
    * [Extract a Single File](#extract-a-single-file)
    * [Change Compression or No Compression](#change-compression-or-no-compression)
    * [Set Output of a Shell Command Into Variable](#set-output-of-a-shell-command-into-variable)
    * [Request User Input on Install](#request-user-input-on-install)
    * [Provide Output to User on Install](#provide-output-to-user-on-install)
    * [Warn User if Wrong Distribution](#warn-user-if-wrong-distribution)
  * [How to...](#how-to)
    * [Define key parameters elsewhere](#define-key-parameters-elsewhere)
    * [Call rpmbuild from a Makefile](#call-rpmbuild-from-a-makefile)
    * [Disable debug packaging](#disable-debug-packaging)
    * [Include Jenkins Job Number in Release](#include-jenkins-job-number-in-release)
    * [Provide Older Versions of Libraries](#provide-older-versions-of-libraries)
  * [Importing a Pre-Existing File Tree](#importing-a-pre-existing-file-tree)
  * [Git Problems and Tricks](#git-problems-and-tricks)
    * [Git Branch or Tag in Release](#git-branch-or-tag-in-release)
    * [Monotonic Release Numbers](#monotonic-release-numbers)
    * [Embedding Source Hash in Description](#embedding-source-hash-in-description)
    * [Jenkins Build Number in Release](#jenkins-build-number-in-release)
  * [Having Multiple Versions](#having-multiple-versions)
    * [Symlinks to Latest](#symlinks-to-latest)
  * [Spoofing RPM Host Name](#spoofing-rpm-host-name)





# rpm-cookbook
Cookbook of RPM techniques

## Overview
I (Aaron D. Marasco) have been creating RPM packages since the CentOS 4 timeframe([1], [2], [3]). I decided to collate some of the things I've done before that I keep referencing in new projects, as well as answering some of the most common questions I come across. This should be considered a *complement* and *not a replacement* for the [*Fedora Packaging Guidelines*](https://fedoraproject.org/wiki/Category:Packaging_guidelines). It's also *not* a generic "How To Make RPMs" guide, but more of a "shining a flashlight into a dusty corner to see if I can do *this*."

Each chapter is a separate directory, so any source code files are transcluded by [Travis-CI](https://travis-ci.com/github/AaronDMarasco/rpm-cookbook) using [`markdown-include`](https://www.npmjs.com/package/markdown-include). All files are available individually in the git repo &mdash; no need to copy and paste from your browser; clone the source!

Feel free to create a new chapter and submit a PR!
----

## Quick Tips
In reviewing some of the most highly voted answers on Stack Overflow, I decided to gather a few here that don't require a full example to explain:

### RPM Preprocessor is Really Dumb
**Don't** put single `%` in comments... this happens [a](https://stackoverflow.com/a/14063974/836748) [*lot*](https://stackoverflow.com/a/18440679/836748). You need to double it with `%%`, or a multi-line macro will only have the first line commented out! Newer versions of `rpmbuild` will _at least_ warn you now.

### Extract All Files
Use `rpm2cpio` with `cpio`. This will extract all files treating the current directory as `/`:
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

### Change Compression or No Compression
As noted [here](https://stackoverflow.com/a/10255406/836748):
```rpm-spec
%define _source_payload w0.gzdio
%define _binary_payload w0.gzdio
```
These will send `-0` to `gzip` to effectively not compress. The `0` can be 0-9 to change the level. The `gz` can be changed:
 * `bz` for bzip2
 * `xz` for XZ/LZMA (on some versions of RPM)

### Set Output of a Shell Command Into Variable
As noted [here](https://stackoverflow.com/a/10694815/836748):
```rpm-spec
%global your_var %(your commands)
```

### Request User Input on Install
**Don't**. This breaks *many* things, for example automated configuration (KickStart or puppet).

### Provide Output to User on Install
`rpm` will show all commands if told to be "extra verbose" with `-vv`. However, all output to `stderr` is shown to the user. Specific syntax can be found in many recipes, including an extreme example [below](#warn-user-if-wrong-distribution).

### Warn User if Wrong Distribution
On a previous project, we had people install the CentOS 7 RPMs on a CentOS 6 box. Normally, this would fail because things like your C libraries won't match. But it was a `noarch` package... This was helpful; figured I would include it here. Unfortunately, it is *very* CentOS-specific:
```bash
# Check if somebody is installing on the wrong platform
if [ -n "%{dist}" ]; then
  PKG_VER=`echo %{dist} | perl -ne '/el(\d)/ && print $1'`
  THIS_VER=`perl -ne '/release (\d)/ && print $1' /etc/redhat-release`
  if [ -n "${PKG_VER}" -a -n "${THIS_VER}" ]; then
    if [ ${PKG_VER} -ne ${THIS_VER} ]; then
      for i in `seq 20`; do echo ""; done
        echo "WARNING: This RPM is for CentOS${PKG_VER}, but you seem to be running CentOS${THIS_VER}" >&2
        echo "You might want to uninstall these RPMs immediately and get the CentOS${THIS_VER} version." >&2
      for i in `seq 5`; do echo "" >&2; done
    fi
  fi
fi
```

----

## How to...
### Define key parameters elsewhere
The techniques to define Version, Release, etc. in another file, environment variable, etc. are shown in most chapters, including [Importing a Pre-Existing File Tree](#importing-a-pre-existing-file-tree). As an alternative to using the `rpmbuild` command line's `--define` option, you can also pre-process the specfile using `sed`, `autotools`, etc. I've seen them all and done them all for various reasons.

### Call rpmbuild from a Makefile
This is shown in most chapters, including [Git Branch or Tag in Release](#git-branch-or-tag-in-release).

### Disable debug packaging
While **not recommended**, because debug packages are very useful, this is shown in most chapters as well.

### Include Jenkins Job Number in Release
This is shown in the `git` chapter as [Jenkins Build Number in Release](#jenkins-build-number-in-release)

### Provide Older Versions of Libraries
This is normally done using a `compat` package; an example is shown in [Symlinks to Latest](#symlinks-to-latest)

----

## Importing a Pre-Existing File Tree
### Reasoning
This is probably one of the most common questions on Stack Overflow. It might be because you don't know enough about RPMs to "do it right" or you just want to "get it done."

I'm a little reluctant to include this, because doing it the "right way" isn't all that hard.

**This is not recommended** but sometimes inevitable:
 * The build system is too complicated (seldom)
 * You're packaging something already installed that...
   * ... you have no control over
   * ... was installed by a GUI installer and you want to repackage for local usage
   * ... you don't have source code for

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
.PHONY: clean rpm $(TARBALL) filelist.txt
.SILENT: clean rpm $(TARBALL) filelist.txt

clean:
	rm -vrf $(RPM_TEMP) $(TARBALL) $(PROJECT)*.rpm filelist.txt

rpm: $(TARBALL) filelist.txt
	mkdir -p $(RPM_TEMP)/SOURCES
	cp --target-directory=$(RPM_TEMP)/SOURCES/ $^
	rpmbuild -ba \
		--define="_topdir $(RPM_TEMP)" \
		--define "outdir  $(OUTPUT)"   \
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

----

## Git Problems and Tricks
### Git Branch or Tag in Release
and
### Monotonic Release Numbers
and
### Embedding Source Hash in Description
and
### Jenkins Build Number in Release
#### Overview
This chapter handles all of the above requirements and is very much intertwined, so you'll have to rip out the parts you want.

#### Reasoning
 * **Branch or Tag in Release**: When checking what version of your software is installed on a machine, it's nice to instantly be able to tell if it's one of your "release" versions or a development branch that somebody was working with. If it is a branch, *which*?
 * **Monotonic Release Numbers**: Git hashes aren't easily sorted, so there's no way for `rpm`/`yum`/`dnf` to know that `1.1-7289cc5` is actually _newer_ than `1.1-dc650cc`. By default, they would be *incorrectly* sorted lexicographically.
   * This allows your CI process to update a repository and `yum upgrade` does the right thing.
 * **Embedding Source Hash**: There's nothing better than "ground truth" when somebody asks for help and they can tell you _exactly_ what RPMs they're dealing with thanks to  `rpm -qi yourpackage`.
 * **Build Number in Release**: When testing RPMs, it's easier to go back and see what CI job created the RPMs.

### How It Works
A little `git` command-line magic (along with some `perl` and `sed` regex) gets us what we want. It's not obviously straight-forward because it works around various problematic scenarios that I've experienced:
 * Detached `HEAD` build (*e.g.* Jenkins)
 * It's in both a branch *and* a tag
 * `origin` has moved forward since the checkout happened, but _before_ our code is run, resulting in things like `mybranch~2`
 * The branch name is obnoxiously long because it has a prefix like `bugfix--BUG13-Broken-CLI`
   * *Any* prefix ending in `--` is stripped
 * The branch has "." or other characters in it that are invalid for the RPM release field
 * A "release version" is in a specially named _branch_ (not tag) of the format `v1.0` or `v.1.1.3`

To compute the monotonic number, it counts the number of six-minute time periods that have passed since the last release (which requires a manual "bump" in the `Makefile` every version).

External information needed:
|    Variable    |         Default         |             Use Case             |
|:--------------:|:-----------------------:|:--------------------------------:|
| `project`      | myproject               | Base Name of the RPM             |
| `version`      | 0.1                     | Version of the RPM               |
| `release`      | snapshot<etc...>        | Release/ Build of the RPM        |
| `BUILD_NUMBER` | (n/a)                   | Job number from Jenkins          |
| `RPM_TEMP`     | `{CWD}/rpmbuild-tmpdir` | Temporary directory to build RPM |


Obviously, `BUILD_NUMBER` is Jenkins-specific. It could just as easily be `CI_JOB_ID` on [GitLab](https://docs.gitlab.com/ee/ci/variables/predefined_variables.html) or `TRAVIS_BUILD_NUMBER` for [Travis-CI](https://docs.travis-ci.com/user/environment-variables/#default-environment-variables).

#### Recipe
This recipe has two parts, a [`Makefile`](git/Makefile) and a [specfile](git/project.spec).

[`Makefile`](git/Makefile):
```Makefile
# These can be overriden on the command line
project?=myproject
version?=$(or $(git_version),0.1)
release?=snapshot$(tag)$(git_tag)
# End of configuration

RPM_TEMP?=$(CURDIR)/rpmbuild-tmpdir

##### Set variables that affect the naming of the packages
# The general package naming scheme is:
# <project>-<version>[-<release>][_<tag>][_J<job>][_<branch>][<dist>]
# where:
# <project> is our base project name
# <version> is a normal versioning scheme 1.2.3
# <release> is a label that defaults to "snapshot" if not overridden

# These are only applied if not a specific versioned release:
# <tag> is a monotonic sequence number/timestamp within a release cycle
# <job> is a Jenkins job reference if this process is run under Jenkins
# <branch> is a git branch reference if not "master" or cannot be determined
# <dist> added by RPM building, e.g. el7.x86_64

# This changes every 6 minutes which is enough for updated releases (snapshots).
# It is rebased after a release so it is relative within its release cycle.
timestamp := $(shell printf %05d $(shell expr `date -u +"%s"` / 360 - 4429931))
# Get the git branch and clean it up from various prefixes and suffixes tacked on
git_branch :=$(notdir $(shell git name-rev --name-only HEAD | \
                              perl -pe 's/~[^\d]*$//' | perl -pe 's/^.*?--//'))
git_version:=$(shell echo $(git_branch) | perl -ne '/^v[\.\d]+$/ && print')
git_hash   :=$(shell h=`(git tag --points-at HEAD | head -n1) 2>/dev/null`;\
                     [ -z "$h" ] && h=`git rev-list --max-count=1 HEAD`; echo $h)
# Any non alphanumeric (or .) strings converted to single _
git_tag    :=$(if $(git_version),,$(strip\
               $(if $(BUILD_NUMBER),_J$(BUILD_NUMBER)))$(strip\
               $(if $(filter-out undefined master,$(git_branch)),\
                    _$(shell echo $(git_branch) | sed -e 's/[^A-Za-z0-9.]\+/_/g'))))
tag:=$(if $(git_version),,_$(timestamp))

# $(info GIT_BRANCH:$(git_branch): GIT_VERSION:$(git_version): GIT_HASH:$(git_hash): GIT_TAG:$(git_tag): TAG:$(tag))
$(info PROJECT:$(project): VERSION:$(version): RELEASE:$(release) GIT_HASH:$(git_hash):)

default: rpm
.PHONY: clean rpm
.SILENT: clean rpm

clean:
	rm -vrf $(RPM_TEMP) $(project)*.rpm

rpm:
	rpmbuild -ba \
	  --define="_topdir   $(RPM_TEMP)" \
	  --define="project_  $(project)"  \
	  --define="version_  $(version)"  \
	  --define="release_  $(release)"  \
	  --define="hash_     $(git_hash)" \
	  project.spec
	cp -v --target-directory=. $(RPM_TEMP)/SRPMS/*.rpm $(RPM_TEMP)/RPMS/*/*.rpm

```

[specfile](git/project.spec):
```rpm-spec
Name: %{project_}
Version: %{version_}
Release: %{release_}
BuildArch: noarch
License: MIT
Summary: My Project That Likes Git

# Remove this line if you have executables with debug info in the source tree:
%global debug_package %{nil}

%description
Not much to say. Nothing in here. But, I know where I came from:

%{?hash_:ReleaseID: %{hash_}}

%prep
# Empty; rpmlint recommendeds it is present anyway

%build
# Empty; rpmlint recommendeds it is present anyway

%install
# Empty; rpmlint recommendeds it is present anyway

%clean
%{__rm} -rf --preserve-root %{buildroot}

%files
# None

```

----

## Having Multiple Versions
### Symlinks to Latest
#### Reasoning
This one is very specific to a workflow in an office I was in, and might not be "generically" useful. Their pre-RPM deployment method was to extract a tarball into a directory and then update a symlink that ended with `-latest` to point to it. For testing, you could simply manipulate that symlink to point to the versions you wanted to use.

This recipe allows you to build `compat` packages with the old libraries, similar to the official Fedora-recommended practice. However, the multiple version numbers in the RPM name can be confusing, so we replace the "." in the _original_ version with "p", *e.g.* `1.0.1` => `1p0p1`.

### How It Works
The [`Makefile`](multiple_versions/latest_symlink/Makefile) creates an array to generate 3 RPMs: `myproject`, `myproject-compat1p0p1` (1.0.1 compat), and `myproject-compat1p1` (1.1 compat). It will build the RPM(s) using the [specfile](multiple_versions/latest_symlink/project.spec).

**Warning**: The `Makefile` targets `test` and `clean` will use `sudo` to manipulate the demo RPMs to show the various effects of installation order, etc. It is recommended that you review the source before running it to ensure you are comfortable with the commands it is executing as `root` on your machine.

External information accepted:
| Variable    | Default                                             | Use Case                         |
|-------------|-----------------------------------------------------|----------------------------------|
| `rpm_names` | myproject myproject-compat1p0p1 myproject-compat1p1 | RPMs to Build                    |
| `version`   | 1.2                                                 | Version of the CURRENT Project   |
| `release`   | 1                                                   | Release/ Build of the RPM        |
| `RPM_TEMP`  | `{CWD}/rpmbuild-tmpdir`                             | Temporary directory to build RPM |


The `specfile` is where the "real" magic is; it will:
 * Determine the "base project name" (`%{base_project}`) by removing anything that comes after a "-"
 * Generate the "latest" symlink name (`%{target_link}`) to be used in various places
 * Decide if this is the "base" RPM or one of the compatible ones
   * `%if "%{name}" != "%{base_project}"`
 * If it determines this is a "compat" RPM, it will:
   * Generate the version number it is compatible with (`%{compat_version}`)
   * Automatically tell RPM that this RPM `Obsoletes` the original RPM with the same version numbers
   * Tells RPM that this RPM also `Provides` a specific _exact_ version of the base RPM
     * This is needed if you have other RPMs that depend explicitly on certain versions (which is why you're going through this trouble in the first place)
   * Generate a `%triggerpostun` stanza that will "take over" the symlink if the base RPM is removed and this one left behind
     * *Note*: If you have multiple compat versions, which one will perform this is nondeterministic!
 * Generate a `%post` section that will:
   * If it is **the base RPM**, will *always* point the symlink to itself
   * If it is **a compat RPM**, will point *a new symlink* to itself *iff* one doesn't already exist
 * Generate a `%postun` section that will, if it's the _last_ RPM uninstalled (so updates will not trigger):
   * Will remove the symlink *iff* it points to the RPM being removed
   * If possible alternatives still exist (`/<orgdir>/<project>*`), will warn if the symlink is now missing, and will present a list of candidates

Any "business logic" in `%build`, `%install`, etc. should use the same comparison above (`%{name}` vs. `%{base_project}`) to determine which files should be used (along with `%{compat_version}`).

What it *doesn't* do (or does "wrong"):
 * It does _not_ declare the symlink as a `%ghost` file; this will cause it to _always_ be removed on _any_ package removal
   * Some more manipulations in `%preun` might be able to get around this, *e.g.* saving off a copy and then putting it back if it pointed elsewhere
 * It does not properly add the symlink to the RPM database:
   * No RPMs can depend on the exact path of the "latest" symlink
   * The RPM DB cannot be queried for it, *e.g.* `rpm -q --whatprovides /path/to/symlink`
 * It does not force the "compat" RPMs to `Require` the newest base; that is something you can choose to add

#### Recipe
This recipe has two parts, a [`Makefile`](multiple_versions/latest_symlink/Makefile) and a [specfile](multiple_versions/latest_symlink/project.spec).

[`Makefile`](multiple_versions/latest_symlink/Makefile):
```Makefile
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
	echo "Removing all (depending on order, a warning may occur):"
	sudo rpm -e myproject myproject-compat1p0p1 myproject-compat1p1
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
	echo "Now removing main package (should be told that 1.1 is a candidate; 1.1 should step up):"
	sudo rpm -e myproject
	tree -a /opt/my_org/
	echo "Removing compat 1.1 only (no warnings; removed symlink but no candidates remain):"
	sudo rpm -e myproject-compat1p1
	echo "Now install compat 1.1 only:"
	sudo rpm -i myproject-compat1p1-1.2-1.noarch.rpm
	echo "Symlink now 1.1:"
	tree -a /opt/my_org/
	echo "Now install compat 1.0.1 and immediately delete (it should leave symlink alone):"
	sudo rpm -i myproject-compat1p0p1-1.2-1.noarch.rpm
	sudo rpm -e myproject-compat1p0p1
	tree -a /opt/my_org/
	echo "Removing compat 1.1 only (should clean up the symlink):"
	sudo rpm -e myproject-compat1p1
	echo "What's left behind in /opt/my_org/:"
	tree -a /opt/my_org/

```

[specfile](multiple_versions/latest_symlink/project.spec):
```rpm-spec
Name: %{project_}
Version: %{version_}
Release: %{release_}
BuildArch: noarch
License: MIT
Summary: My Project That Likes Symlinks

# Remove this line if you have executables with debug info in the source tree:
%global debug_package %{nil}

%global orgdir /opt/my_org
%global outdir %{orgdir}/%{name}
# Compute the "base" project name if we are myproj-compatXpY
%global base_project %(echo %{name} | cut -f1 -d-)
%global target_link %{orgdir}/%{base_project}-latest

%if "%{name}" != "%{base_project}"
BuildRequires: /usr/bin/perl
# Convert that myproj-compatXpY to X.Y
%global compat_version %(echo %{name} | perl -ne '/-compat(.*)/ && print $1' | tr p .)
Obsoletes: %{base_project} = %{compat_version}
Provides: %{base_project} = %{compat_version}
# Take over symlink if needed (if main is removed)
%triggerpostun -- %{base_project}
[ $2 = 0 ] || exit 0
if [ ! -e %{target_link} ]; then
  >&2 echo "%{name}: %{target_link} was removed; pointing it at me instead"
  ln -s %{outdir} %{target_link}
fi
%endif

%description
Not much to say. Nothing in here.

But we share the symlink %{target_link} across two or more packages.

%prep
# Empty; rpmlint recommendeds it is present anyway

%build
# Empty; rpmlint recommendeds it is present anyway

%install
%{__mkdir_p} %{buildroot}/%{outdir}/
touch %{buildroot}/%{outdir}/myfile.txt

%post
%if "%{name}" != "%{base_project}"
# We are "compat" package - only write symlink if it doesn't already exist
if [ ! -e %{target_link} ]; then
  >&2 echo "%{name}: %{target_link} does not yet exist; setting it to point to compat-%{compat_version}"
  ln -s %{outdir} %{target_link}
fi
%else
# We are main package - always take over symlink
if [ -e %{target_link} ]; then
  >&2 echo "%{name}: %{target_link} being updated. Was `readlink -e %{target_link}`"
  rm -f %{target_link}
fi

# Add a symlink to "us"
ln -s %{outdir} %{target_link}
%endif

%postun
[ $1 = 0 ] || exit 0
# See if symlink points to us explicitly
if [ x"%{outdir}" == x"`readlink %{target_link}`" ]; then
  rm -f %{target_link}
fi

# All packages warn about missing symlink if there are potential candidates
if [ ! -e %{target_link} ]; then
  CANDIDATES=$(cd %{orgdir} && find . -maxdepth 1 -type d -name '%{base_project}*')
  if [ -n "${CANDIDATES}" ]; then
    >&2 echo "%{name}: %{target_link} is removed and may need to be manually updated; candidate(s): ${CANDIDATES}"
  fi
fi

%clean
%{__rm} -rf --preserve-root %{buildroot}

%files
%dir %{outdir}
%{outdir}/myfile.txt


```

----

## Spoofing RPM Host Name
### Reasoning
When distributing RPMs, you might not want people to know the build host. It shouldn't matter to the end user, and your security folks might not want internal hostnames or DNS information published for no good reason.

Newer versions of `rpmbuild` support defining `_buildhost`; I have not tested that capability myself.

### How It Works
It sets [`LD_PRELOAD`](view-source:https://man7.org/linux/man-pages/man8/ld.so.8.html) to intercept all 32- or 64-bit calls to [`gethostname()`](https://man7.org/linux/man-pages/man2/gethostname.2.html) and [`gethostbyname()`](https://man7.org/linux/man-pages/man3/gethostbyname.3.html) to replace them with the text you provide. Only later versions of `rpmbuild` call `gethostbyname()`.

### Recipe
This recipe requires you wrap your `rpmbuild` command with a script or `Makefile`. Using the `Makefile` below, you would have `make` call `$(SPOOF_HOSTNAME) rpmbuild ...`.

There is a default target `testrpm` that will build some RPMs with and without the hostname spoofing as an example; at its conclusion you should see:
```
Build hosts: (with spoof)
Build Host  : buildhost_x86_64.myprojectname.proj
Build Host  : buildhost_x86_64.myprojectname.proj
```
Scroll back in your terminal and compare this to the default output after "Build hosts: (without spoof)".

Edit the `Makefile` yourself where it says "`.myprojectname.proj`" - you can optionally _not_ have it use the `buildhost_<arch>` prefix as well.

Other usage notes are at the top of the `Makefile` with an example at the bottom.

[`Makefile`](fake_buildhost/Makefile):
```Makefile
# This spoofs the build host for both 32- and 64-bit applications

default: testrpm

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

```



  [1]: https://stackoverflow.com/search?q=user:836748+[rpm]
  [2]: https://stackoverflow.com/search?q=user:836748+[rpmbuild]
  [3]: https://stackoverflow.com/search?q=user:836748+[rpm-spec]
