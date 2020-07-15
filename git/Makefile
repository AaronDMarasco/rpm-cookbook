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
# <tag> is a monotonic sequence number/timestamp within a release cycle (when not a specific release)
# <job> is a Jenkins job reference if this process is run under Jenkins
# <branch> is a git branch reference if not "master" or "undefined"
# <dist> added by RPM building, e.g. el7.x86_64

# This changes every 6 minutes which is enough for updated releases (snapshots).
# It is rebased after a release so it is relative within its release cycle.
timestamp := $(shell printf %05d $(shell expr `date -u +"%s"` / 360 - 4429931))
# Get the git branch and clean it up from various prefixes and suffixes tacked on
git_branch :=$(notdir $(shell git name-rev --name-only HEAD | \
                              perl -pe 's/~[^\d]*$$//' | perl -pe 's/^.*?--//'))
git_version:=$(shell echo $(git_branch) | perl -ne '/^v[\.\d]+$$/ && print')
git_hash   :=$(shell h=`(git tag --points-at HEAD | head -n1) 2>/dev/null`;\
                     [ -z "$$h" ] && h=`git rev-list --max-count=1 HEAD`; echo $$h)
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
