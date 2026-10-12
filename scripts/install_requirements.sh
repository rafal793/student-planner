#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "Instalacja zależności Student Planner..."

if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    echo "Nie znaleziono Pythona (python3 / python)." >&2
    exit 1
fi

"$PYTHON" -m pip install --upgrade pip
"$PYTHON" -m pip install -r requirements.txt

echo
echo "Gotowe. Uruchom aplikację: $PYTHON app.py"
