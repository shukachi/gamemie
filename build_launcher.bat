@echo off
echo Установка PyInstaller...
pip install pyinstaller --quiet

echo Сборка GamemieLauncher.exe...
pyinstaller ^
  --onefile ^
  --noconsole ^
  --name GamemieLauncher ^
  --clean ^
  launcher.py

echo.
if exist dist\GamemieLauncher.exe (
    echo  ГОТОВО: dist\GamemieLauncher.exe
) else (
    echo  ОШИБКА: файл не создан
)
pause
