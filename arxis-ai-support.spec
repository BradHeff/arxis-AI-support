Name:           arxis-ai-support
Version: 2.0.6
Release:        1%{?dist}
Summary:        Arxis AI Support is used to assist users with AI-related tasks
License: GPLv3+
URL: https://github.com/BradHeff/Arxis-AI-Support
Source0: %{name}-%{version}.tar.gz

BuildRequires: python3
Requires:      python3, python3-tkinter, python3-pillow, python3-pip


%description
Arxis AI Support is used to assist users with AI-related tasks

%install
# Create destination directories
mkdir -p %{buildroot}/usr/local/bin/
mkdir -p %{buildroot}/usr/lib/Arxis-AI-Support/
mkdir -p %{buildroot}/usr/share/pixmaps/
mkdir -p %{buildroot}/usr/share/applications/
mkdir -p %{buildroot}/etc/arxis-ai-support/

# Extract files directly from the source tarball into the buildroot. Use --strip-components
# to remove the top-level %{name}-%{version} directory so paths land under %{buildroot} as expected.
if [ -f "%{_sourcedir}/%{name}-%{version}.tar.gz" ]; then
	# Extract usr tree
	(cd %{buildroot} && tar -xzf "%{_sourcedir}/%{name}-%{version}.tar.gz" --strip-components=1 "%{name}-%{version}/usr/" ) || true
	# Extract etc/arxis-ai-support tree if present
	(cd %{buildroot} && tar -xzf "%{_sourcedir}/%{name}-%{version}.tar.gz" --strip-components=1 "%{name}-%{version}/etc/arxis-ai-support/" ) || true
fi


%post
pip3 install --user asyncio numpy ttkbootstrap pillow logging tkthread openai fsm_llm pydantic pyinstaller git+https://github.com/psf/black
chmod +x /usr/local/bin/arxis-ai-support
pwusr=$(logname)
pver=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

chmod 0644 /etc/arxis-ai-support/env || true
echo "WARNING: group 'users' not found; /etc/arxis-ai-support/env set to 0644 so applications can read it. Consider tightening permissions or using per-user config in ~/.config/arxis-ai-support/env." >/usr/share/doc/arxis-ai-support-env-perms 2>/dev/null || true

%files

/usr/local/bin/arxis-ai-support
/usr/share/applications/arxis-ai-support.desktop
/usr/share/pixmaps/arxis.png

# Install the entire library directory. Exclude bytecode caches and pyc files
# which are build artifacts and not intended to be packaged.
# Package the entire library directory and resource files. Exclude caches/pyc
# Keep the single directory entry to avoid listing files twice.
/usr/lib/Arxis-AI-Support/
%exclude /usr/lib/Arxis-AI-Support/__pycache__
%exclude /usr/lib/Arxis-AI-Support/__pycache__/*


%config(noreplace) /etc/arxis-ai-support/env
%doc /etc/arxis-ai-support/env.sample


%changelog
* Mon Dec 23 2024 Brad Heffernan <brad.heffernan83@outlook.com>
- 
