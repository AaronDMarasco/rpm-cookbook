Name: %{project_}
Version: %{version_}
Release: %{release_}%{?dist}
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
# Empty; rpmlint recommends it is present anyway

%build
# Empty; rpmlint recommends it is present anyway

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

