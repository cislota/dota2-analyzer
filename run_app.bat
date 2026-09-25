@echo off
setlocal

cd /d "%~dp0"

set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo Virtual environment not found: .venv
    echo Create it and install dependencies:
    echo   python -m venv .venv
    echo   .venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

if not exist "%~dp0app.py" (
    echo Application file not found: app.py
    pause
    exit /b 1
)

echo Starting Dota 2 Match Analyzer...
echo Open http://localhost:8501 if the browser does not open automatically.
echo.

"%PYTHON_EXE%" -m streamlit run app.py

if errorlevel 1 (
    echo.
    echo Failed to start the application.
    pause
    exit /b 1
)

endlocal
