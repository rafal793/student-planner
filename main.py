from __future__ import annotations

import os
import subprocess
import sys

from ui import StudentPlannerApp


def _tk_runtime_works() -> bool:
    # Run Tk init in a child process to avoid hard abort in main process.
    probe = (
        "import customtkinter as ctk; "
        "app = ctk.CTk(); "
        "app.destroy(); "
        "print('ok')"
    )
    result = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True)
    return result.returncode == 0 and "ok" in result.stdout


def _print_tk_help() -> None:
    print("")
    print("Student Planner: wykryto problem z runtime Tk/CustomTkinter w aktualnym Pythonie.")
    print(f"Interpreter: {sys.executable}")
    print("Objaw: system abortuje proces przy tworzeniu okna (ctk.CTk()).")
    print("")
    print("Najprostsza naprawa:")
    print("1) Zainstaluj nowszy Python (np. 3.11/3.12) z python.org.")
    print("2) Utwórz virtualenv i zainstaluj zależności.")
    print("3) Uruchom aplikację tym nowym interpreterem.")
    print("")
    print("Przykład:")
    print("  /usr/local/bin/python3.12 -m venv .venv")
    print("  source .venv/bin/activate")
    print("  pip install -r requirements.txt")
    print("  python main.py")
    print("")


def main() -> None:
    # Do not recurse when we run probes from this process.
    if os.environ.get("SP_SKIP_TK_PREFLIGHT") != "1":
        if not _tk_runtime_works():
            _print_tk_help()
            raise SystemExit(1)

    app = StudentPlannerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
