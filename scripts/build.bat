@echo off
setlocal
cd /d "%~dp0\.."

echo Budowanie StudentPlanner...
pyinstaller --noconfirm --clean scripts\StudentPlanner.spec
if errorlevel 1 (
    echo Build nie powiodl sie.
    exit /b 1
)

echo.
echo ============================================
echo  GOTOWE
echo ============================================
pause
