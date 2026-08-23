@echo off
title PassCraft AI v2.0 — Launcher
color 0F

echo.
echo  ================================================
echo   PassCraft AI v2.0
echo   Real ML · SHAP · HIBP Breach Check · AES-256
echo  ================================================
echo.

:: ── Navigate to the folder this .bat lives in ──
cd /d "%~dp0"

:: ── Check py launcher ──
py --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python launcher ^(py^) not found.
    echo  Download Python from https://www.python.org/downloads/
    echo  Check "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('py --version 2^>^&1') do echo  [OK] %%v found.

:: ── Install dependencies ──
echo  [2/3] Installing dependencies ^(first run may take ~60s^)...
py -m pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    echo.
    echo  [ERROR] Dependency install failed.
    echo  Try manually: py -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo  [OK] Dependencies ready.

:: ── Check if model files exist; train if missing ──
if not exist "model\rf_model.pkl" (
    echo.
    echo  [INFO] Model not found. Training now ^(one-time, ~30 seconds^)...
    py train_model.py
    if errorlevel 1 (
        echo  [ERROR] Model training failed.
        pause
        exit /b 1
    )
)
echo  [OK] ML model ready.

:: ── Launch Streamlit ──
echo.
echo  [3/3] Launching PassCraft AI...
echo  ------------------------------------------------
echo  URL: http://localhost:8501
echo  Press Ctrl+C to stop the server.
echo  ------------------------------------------------
echo.

py -m streamlit run app.py --server.port 8501 --browser.gatherUsageStats false

echo.
echo  Server stopped. Press any key to close.
pause
