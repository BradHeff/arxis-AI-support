@ECHO off
REM This script builds the Python application using PyInstaller.
REM Usage: build.cmd <name>

C:\Users\Support\AppData\Local\Programs\Python\Python313\Scripts\pyinstaller.exe --clean --noconsole --noconfirm --onefile --distpath="scrap/dist" --workpath="scrap/build" --name=%1 --hidden-import="ttkbootstrap" --hidden-import="OpenSSL" --hidden-import="ldap3" --hidden-import="PIL" --hidden-import="tkthread" --hidden-import="requests" --hidden-import="datetime" --hidden-import="PIL.ImageTk" --icon="icon.ico" --version-file="version.rc" main.py
IF %ERRORLEVEL% NEQ 0 (
    ECHO Build failed with error code %ERRORLEVEL%.
    EXIT /B %ERRORLEVEL%
)
exit
