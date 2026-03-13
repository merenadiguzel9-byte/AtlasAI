@echo off
echo ============================================================
echo   ATLAS AI - 3D MODEL FORGE - SETUP
echo ============================================================
echo.

where node >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [!] Node.js not found. Please install it from:
    echo     https://nodejs.org/en/download
    echo     (Use the LTS version, 18+ required)
    echo.
    pause
    exit /b 1
)

echo [OK] Node.js found.
node -v
npm -v
echo.

echo [*] Installing dependencies...
npm install
IF %ERRORLEVEL% NEQ 0 (
    echo [!] npm install failed. Check your internet connection.
    pause
    exit /b 1
)

echo.
echo [OK] All dependencies installed.
echo.
echo ============================================================
echo   To START the app, run:  start.bat
echo ============================================================
pause
