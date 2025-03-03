@echo off
echo Installing Browser Time Analyzer...

:: Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This installer requires administrator privileges.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

:: Create program directory
echo Creating program directory...
mkdir "%ProgramFiles%\Browser Time Analyzer" 2>nul

:: Copy files
echo Copying files...
copy /Y "Browser Time Analyzer.exe" "%ProgramFiles%\Browser Time Analyzer"
if errorlevel 1 (
    echo Failed to copy executable file.
    pause
    exit /b 1
)

:: Create desktop shortcut
echo Creating desktop shortcut...
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%USERPROFILE%\Desktop\Browser Time Analyzer.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%ProgramFiles%\Browser Time Analyzer\Browser Time Analyzer.exe" >> CreateShortcut.vbs
echo oLink.IconLocation = "%ProgramFiles%\Browser Time Analyzer\Browser Time Analyzer.exe,0" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%ProgramFiles%\Browser Time Analyzer" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs

echo.
echo Installation complete! You can find Browser Time Analyzer on your desktop.
echo If you don't see the shortcut, you may need to refresh your desktop.
pause 