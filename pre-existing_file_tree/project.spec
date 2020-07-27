Name: %{project_}
Version: %{version_}
Release: %{release_}%{?dist}
License: MIT
Summary: My Poorly Packaged Project
Source0: %{name}.tar
# Remove this line if you have executables with debug info in the source tree:
%global debug_package %{nil}
BuildRequires: sed tar
# BuildRequires: hardlink

%description
This RPM is effectively a fancy tarball.

%prep
set -o pipefail
# Default setup - extract the tarball
%setup -q
# Generate the file list with absolute target pathnames)
tar tf %{SOURCE0} | sed -e 's|^%{name}-%{version}|%{outdir}|' > parsed_filelist.txt
# Fix spaces in filename in manifest by putting into double quotes
sed -i -e 's/^.* .*$/"\0"/g' parsed_filelist.txt

%build
# Empty; rpmlint recommendeds it is present anyway

%install
%{__mkdir_p} %{buildroot}/%{outdir}/
echo "Hardlinking / copying %(wc -l parsed_filelist.txt | cut -f1 -d' ') files..."
%{__cp} --target-directory=%{buildroot}/%{outdir}/ -alR . || %{__cp} --target-directory=%{buildroot}/%{outdir}/ -aR .
%{__rm} %{buildroot}/%{outdir}/parsed_filelist.txt
# hardlink -cv %{buildroot}/%{outdir}

%clean
%{__rm} -rf --preserve-root %{buildroot}

%files -f parsed_filelist.txt
