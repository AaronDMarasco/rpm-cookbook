Name: %{project_}
Version: %{version_}
Release: %{release_}%{?dist}
BuildArch: noarch
License: MIT
Summary: My Project That Likes Git

# Remove this line if you have executables with debug info in the source tree:
%global debug_package %{nil}

%description
Not much to say. Nothing in here. But, I know where I came from:

%{?hash_:ReleaseID: %{hash_}}

%prep
# Empty; rpmlint recommends it is present anyway

%build
# Empty; rpmlint recommends it is present anyway

%install
# Empty; rpmlint recommends it is present anyway

%clean
%{__rm} -rf --preserve-root %{buildroot}

%files
# None
