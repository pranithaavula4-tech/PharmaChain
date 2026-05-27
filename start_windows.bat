@echo off
setlocal
set "PY=%~dp0.venv311\Scripts\python.exe"

if not exist "%PY%" (
    echo ERROR: Python 3.11 virtual environment not found at "%~dp0.venv311"
    echo Create it first with:
    echo   py -3.11 -m venv .venv311
    pause
    exit /b 1
)

echo =====================================
echo   PharmaChain — Starting All Services
echo =====================================

echo.
echo [1/4] Installing Auth Service dependencies...
cd auth_service
"%PY%" -m pip install -r requirements.txt -q
start "Auth Service :8001" cmd /k ""%PY%" -m uvicorn main:app --port 8001 --reload"
cd ..

echo [2/4] Installing Inventory Service dependencies...
cd inventory_service
"%PY%" -m pip install -r requirements.txt -q
start "Inventory Service :8002" cmd /k ""%PY%" -m uvicorn main:app --port 8002 --reload"
cd ..

echo [3/4] Installing Sales Service dependencies...
cd sales_service
"%PY%" -m pip install -r requirements.txt -q
start "Sales Service :8003" cmd /k ""%PY%" -m uvicorn main:app --port 8003 --reload"
cd ..

echo [4/4] Installing API Gateway dependencies...
cd api_gateway
"%PY%" -m pip install -r requirements.txt -q
start "API Gateway :8000" cmd /k ""%PY%" -m uvicorn main:app --port 8000 --reload"
cd ..

echo.
echo ======================================
echo   All services started!
echo.
echo   API Gateway:        http://localhost:8000
echo   API Docs:           http://localhost:8000/docs
echo   Auth Service:       http://localhost:8001/docs
echo   Inventory Service:  http://localhost:8002/docs
echo   Sales Service:      http://localhost:8003/docs
echo.
echo   Open frontend/index.html in your browser
echo ======================================
echo.
pause
