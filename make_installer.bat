@echo off
echo Building Browser Time Analyzer...

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Install required packages
pip install pyinstaller pandas matplotlib python-dateutil

REM Build the executable
pyinstaller --onefile --windowed --icon=resources/icon.ico --name="Browser Time Analyzer" src/main.py

REM Create installer directory
rmdir /s /q "Browser Time Analyzer Installer" 2>nul
mkdir "Browser Time Analyzer Installer"

REM Copy files to installer directory
copy "dist\Browser Time Analyzer.exe" "Browser Time Analyzer Installer\" /Y
copy "install.bat" "Browser Time Analyzer Installer\" /Y
copy "resources\icon.ico" "Browser Time Analyzer Installer\" /Y

echo.
echo Build complete! The installer package is in the "Browser Time Analyzer Installer" folder.
echo Please run install.bat from that folder as administrator to install the application.
pause 