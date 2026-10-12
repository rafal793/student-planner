@echo off
setlocal
cd /d "%~dp0\.."

echo Instalacja zaleznosci Student Planner...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Nie udalo sie uruchomic pip. Sprawdz czy Python jest zainstalowany i dodany do PATH.
    exit /b 1
)

python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Instalacja nie powiodla sie.
    exit /b 1
)

echo.
echo Gotowe. Uruchom aplikacje: python app.py
pause
