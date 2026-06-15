@echo off
title SpecSense AI Runner
cd /d "%~dp0"

echo ===================================================
echo             SpecSense AI Startup Console
echo ===================================================
echo.

:: Check for virtual environment in parent directory or local directory
if exist "..\venv\Scripts\python.exe" (
    set PY_PATH=..\venv\Scripts\python.exe
    echo [INFO] Using parent directory virtual environment.
) else if exist ".\venv\Scripts\python.exe" (
    set PY_PATH=.\venv\Scripts\python.exe
    echo [INFO] Using local directory virtual environment.
) else (
    echo [ERROR] Python virtual environment not found!
    echo Please make sure you have a virtual environment at ..\venv or .\venv
    pause
    exit /b 1
)

:: Check for pnpm availability
where pnpm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] pnpm command not found! Please make sure Node.js and pnpm are installed.
    pause
    exit /b 1
)

echo [INFO] Cleaning up any orphaned processes on port 8000 and 5173...
powershell -Command "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
powershell -Command "Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"

echo [INFO] Starting FastAPI Backend on http://127.0.0.1:8000...
start "SpecSense Backend" /min %PY_PATH% -m uvicorn server:app --host 127.0.0.1 --port 8000

echo [INFO] Starting Vite Frontend on http://localhost:5173...
start "SpecSense Frontend" /min pnpm --filter @workspace/frontend dev

echo [INFO] Waiting for backend to initialize on port 8000...
set /a retry_count=0

:wait_loop
set /a retry_count+=1
if %retry_count% gtr 15 (
    echo [WARNING] Backend did not start in time. Launching browser anyway...
    goto launch_browser
)
powershell -Command "if (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }"
if %errorlevel% neq 0 (
    timeout /t 1 /nobreak > nul
    goto wait_loop
)

:launch_browser
echo [INFO] Launching SpecSense AI in your default browser...
start http://localhost:5173/

echo.
echo ===================================================
echo SpecSense AI is now running! 
echo Keep this window open to keep the servers active.
echo To stop the servers, close this window or press CTRL+C.
echo ===================================================
echo.

:: Keep script running
pause
