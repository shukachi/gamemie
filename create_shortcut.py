"""
Creates desktop shortcut for Gamemie.
Run once: python create_shortcut.py
"""
import os
import subprocess
import sys
from PIL import Image

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
AVIF_PATH   = os.path.join(PROJECT_DIR, "assets", "fonts", "icon.avif")
ICO_PATH    = os.path.join(PROJECT_DIR, "assets", "fonts", "icon.ico")
DESKTOP     = os.path.join(os.path.expanduser("~"), "Desktop")
SHORTCUT    = os.path.join(DESKTOP, "Gamemie.lnk")
PYTHON      = sys.executable
MAIN        = os.path.join(PROJECT_DIR, "main.py")

# 1. Convert avif → ico
img = Image.open(AVIF_PATH).convert("RGBA")
img.save(ICO_PATH, format="ICO",
         sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])
print(f"Icon saved: {ICO_PATH}")

# 2. Create .lnk via PowerShell
ps = f"""
$s = (New-Object -ComObject WScript.Shell).CreateShortcut('{SHORTCUT}')
$s.TargetPath      = '{PYTHON}'
$s.Arguments       = '"{MAIN}"'
$s.WorkingDirectory= '{PROJECT_DIR}'
$s.IconLocation    = '{ICO_PATH}'
$s.Description     = 'Gamemie'
$s.Save()
"""
subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
print(f"Shortcut created: {SHORTCUT}")
