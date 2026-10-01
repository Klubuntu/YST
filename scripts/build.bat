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

python -m PyInstaller build\YST.spec ^
    --distpath dist ^
    --workpath build\yst ^
    --onefile ^
    --name YST || goto :error

certutil -hashfile dist\YST.exe SHA256 > dist\YST.exe.sha256
type dist\YST.exe.sha256
echo Built dist\YST.exe
exit /b 0

:error
echo Build failed.
exit /b 1