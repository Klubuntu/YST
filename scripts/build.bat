@echo off
REM Build the Windows executable.
REM
REM   scripts\build.bat              -> dist\YST.exe
REM
REM PyInstaller only produces a Windows binary on Windows; use CI or a Windows
REM host for the release build.
setlocal
cd /d "%~dp0.."

python -m pip install -r requirements.txt pyinstaller || goto :error

REM A .spec build is already onefile, and PyInstaller rejects --onefile and
REM --name there; the name comes from YST_BINARY_NAME instead.
set YST_BINARY_NAME=YST

python -m PyInstaller build\YST.spec ^
    --distpath dist ^
    --workpath build\yst || goto :error

certutil -hashfile dist\YST.exe SHA256 > dist\YST.exe.sha256
type dist\YST.exe.sha256
echo Built dist\YST.exe
exit /b 0

:error
echo Build failed.
exit /b 1