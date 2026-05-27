#!/bin/bash
echo "======================================"
echo "  PharmaChain — Starting All Services"
echo "======================================"

# Install all deps
for svc in auth_service inventory_service sales_service api_gateway; do
  echo "[setup] Installing $svc dependencies..."
  cd $svc && pip install -r requirements.txt -q && cd ..
done

# Start each service in background
echo ""
echo "[1/4] Starting Auth Service on :8001..."
cd auth_service && uvicorn main:app --port 8001 --reload &
cd ..

echo "[2/4] Starting Inventory Service on :8002..."
cd inventory_service && uvicorn main:app --port 8002 --reload &
cd ..

echo "[3/4] Starting Sales Service on :8003..."
cd sales_service && uvicorn main:app --port 8003 --reload &
cd ..

echo "[4/4] Starting API Gateway on :8000..."
cd api_gateway && uvicorn main:app --port 8000 --reload &
cd ..

echo ""
echo "======================================"
echo "  All services running!"
echo ""
echo "  API Gateway:        http://localhost:8000"
echo "  API Docs:           http://localhost:8000/docs"
echo "  Auth Docs:          http://localhost:8001/docs"
echo "  Inventory Docs:     http://localhost:8002/docs"
echo "  Sales Docs:         http://localhost:8003/docs"
echo ""
echo "  Open frontend/index.html in your browser"
echo "======================================"
echo ""
echo "Press Ctrl+C to stop all services."
wait
