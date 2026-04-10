@echo off
setlocal
title UKIP - Universal Knowledge Intelligence Platform
color 0A

set "MODE=%~1"
if "%MODE%"=="" set "MODE=start-all"

echo.
echo  ============================================
echo   UKIP - Local Development Control
echo  ============================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo  [ERROR] Python virtual environment not found.
    echo  Run: python -m venv .venv ^&^& .venv\Scripts\pip install -r requirements.lock
    pause
    exit /b 1
)

if not exist "frontend\node_modules" (
    echo  [ERROR] Frontend dependencies not installed.
    echo  Run: cd frontend ^&^& npm install
    pause
    exit /b 1
)

if not exist "frontend\.env.local" (
    echo  [INFO] Creating frontend\.env.local from example...
    copy "frontend\.env.local.example" "frontend\.env.local" >nul
)

where docker >nul 2>&1
if %errorlevel%==0 (
    echo  [INFO] Ensuring local PostgreSQL is running via docker-compose.dev.yml...
    docker compose -f docker-compose.dev.yml up -d postgres
) else (
    echo  [WARN] Docker not found in Windows PATH.
    echo  [WARN] If Docker runs inside WSL Ubuntu, start PostgreSQL there before starting UKIP.
)

if /I "%MODE%"=="help" goto usage
if /I "%MODE%"=="backend" goto backend
if /I "%MODE%"=="frontend" goto frontend
if /I "%MODE%"=="restart-backend" goto backend
if /I "%MODE%"=="restart-frontend" goto frontend
if /I "%MODE%"=="restart-all" goto startall
if /I "%MODE%"=="start-all" goto startall

echo  [ERROR] Unknown option: %MODE%
goto usage

:kill8000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    echo  [INFO] Stopping process on port 8000 ^(PID %%a^)...
    taskkill /F /PID %%a >nul 2>&1
)
goto :eof

:kill3004
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3004 " ^| findstr "LISTENING"') do (
    echo  [INFO] Stopping process on port 3004 ^(PID %%a^)...
    taskkill /F /PID %%a >nul 2>&1
)
goto :eof

:backend
call :kill8000
echo  [INFO] Starting Backend ^(FastAPI on port 8000^)...
start "UKIP Backend" cmd /k "title UKIP Backend && cd /d %~dp0 && .venv\Scripts\alembic upgrade head && .venv\Scripts\python -m uvicorn backend.main:app --reload --port 8000"
echo.
echo  [OK] Backend launch requested.
goto end

:frontend
call :kill3004
echo  [INFO] Starting Frontend ^(Next.js on port 3004^)...
start "UKIP Frontend" cmd /k "title UKIP Frontend && cd /d %~dp0\frontend && npm run dev"
echo.
echo  [OK] Frontend launch requested.
goto end

:startall
call :kill8000
call :kill3004
echo  [1/2] Launching backend...
start "UKIP Backend" cmd /k "title UKIP Backend && cd /d %~dp0 && .venv\Scripts\alembic upgrade head && .venv\Scripts\python -m uvicorn backend.main:app --reload --port 8000"
echo  [2/2] Launching frontend...
start "UKIP Frontend" cmd /k "title UKIP Frontend && cd /d %~dp0\frontend && npm run dev"
echo.
echo  ============================================
echo   Services starting in separate windows:
echo    Backend  ^>  http://localhost:8000
echo    Frontend ^>  http://localhost:3004
echo    API Docs ^>  http://localhost:8000/docs
echo  ============================================
echo.
echo  Press any key to open the app in your browser...
pause >nul
start http://localhost:3004
goto end

:usage
echo  Usage:
echo    start.bat                 ^> start backend + frontend
echo    start.bat start-all       ^> start backend + frontend
echo    start.bat restart-all     ^> restart backend + frontend
echo    start.bat backend         ^> start backend only
echo    start.bat frontend        ^> start frontend only
echo    start.bat restart-backend ^> restart backend only
echo    start.bat restart-frontend^> restart frontend only
echo    start.bat help            ^> show this help
goto end

:end
endlocal
