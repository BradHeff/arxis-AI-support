Name:           arxis-ai-support
Version:        1.0.1
Release:        1%{?dist}
Summary:        Arxis AI Support is used to assist users with AI-related tasks
License: GPLv3+
URL: https://github.com/BradHeff/Arxis-AI-Support
Source0: %{name}-%{version}.tar.gz

BuildRequires: python3
Requires:      python3, python3-tkinter, python3-pillow, python3-pillow-tk, python3-pip, python3-venv


%description
Arxis AI Support is used to assist users with AI-related tasks

%install
mkdir -p %{buildroot}/usr/local/bin/
mkdir -p %{buildroot}/usr/lib/Arxis-AI-Support/
mkdir -p %{buildroot}/usr/share/pixmaps/
mkdir -p %{buildroot}/usr/share/applications/


cp %{_topdir}/BUILD/arxis-ai-support/arxis-ai-support %{buildroot}/usr/local/bin/arxis-ai-support
cp %{_topdir}/BUILD/arxis-ai-support/arxis-ai-support.desktop %{buildroot}/usr/share/applications/arxis-ai-support.desktop
cp %{_topdir}/BUILD/arxis-ai-support/arxis.png %{buildroot}/usr/share/pixmaps/arxis.png
cp %{_topdir}/BUILD/arxis-ai-support/Functions.py %{buildroot}/usr/lib/Arxis-AI-Support/Functions.py
cp %{_topdir}/BUILD/arxis-ai-support/bot.py %{buildroot}/usr/lib/Arxis-AI-Support/bot.py
cp %{_topdir}/BUILD/arxis-ai-support/support.py %{buildroot}/usr/lib/Arxis-AI-Support/support.py
cp %{_topdir}/BUILD/arxis-ai-support/main.py %{buildroot}/usr/lib/Arxis-AI-Support/main.py
cp %{_topdir}/BUILD/arxis-ai-support/Gui.py %{buildroot}/usr/lib/Arxis-AI-Support/Gui.py


%post
pip3 install --user asyncio numpy ttkbootstrap pillow logging tkthread openai fsm_llm pydantic pyinstaller git+https://github.com/psf/black
chmod +x /usr/local/bin/arxis-ai-support
pwusr=$(logname)
pver=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

%files

/usr/local/bin/arxis-ai-support
/usr/share/applications/arxis-ai-support.desktop
/usr/lib/Arxis-AI-Support/Gui.py
/usr/lib/Arxis-AI-Support/Functions.py
/usr/lib/Arxis-AI-Support/main.py
/usr/lib/Arxis-AI-Support/bot.py
/usr/lib/Arxis-AI-Support/support.py
/usr/share/pixmaps/arxis.png


%changelog
* Mon Dec 23 2024 Brad Heffernan <brad.heffernan83@outlook.com>
- 
