Name: %{project_}
Version: %{version_}
Release: %{release_}
BuildArch: noarch
License: MIT
Summary: My Project That Likes Git

# Remove this line if you have executables with debug info in the source tree:
%global debug_package %{nil}
BuildRequires: git sed tar

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