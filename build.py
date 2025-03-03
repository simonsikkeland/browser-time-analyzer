import os
import sys
import shutil
from pathlib import Path
import winreg
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def create_shortcut(target_path, shortcut_path, icon_path=None):
    import win32com.client
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = target_path
    if icon_path:
        shortcut.IconLocation = icon_path
    shortcut.save()

def get_desktop_path():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
    desktop_path = winreg.QueryValueEx(key, "Desktop")[0]
    winreg.CloseKey(key)
    return desktop_path

def main():
    # Check if running as admin
    if not is_admin():
        print("Please run this script as administrator")
        return

    # Install required packages
    os.system("pip install pyinstaller pywin32")
    
    # Build the executable
    os.system("pyinstaller --onefile --windowed --icon=resources/icon.ico src/main.py")
    
    # Create shortcut on desktop
    desktop_path = get_desktop_path()
    exe_path = os.path.abspath("dist/main.exe")
    shortcut_path = os.path.join(desktop_path, "Browser Time Analyzer.lnk")
    icon_path = os.path.abspath("resources/icon.ico")
    
    create_shortcut(exe_path, shortcut_path, icon_path)
    
    print("Installation complete! You can find the shortcut on your desktop.")

if __name__ == "__main__":
    main() 