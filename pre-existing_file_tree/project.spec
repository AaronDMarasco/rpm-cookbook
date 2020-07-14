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
