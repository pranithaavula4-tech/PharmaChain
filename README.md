# 💊 PharmaChain — Store Operations Platform

A working microservices-based pharmacy management system built with FastAPI + SQLite.

---

## 📁 Project Structure

```
pharmachain/
├── auth_service/         # Handles login, JWT, RBAC
├── inventory_service/    # Products, stock, batch tracking
├── sales_service/        # Invoices, POS, GST
├── api_gateway/          # Single entry point for all requests
├── frontend/
│   └── index.html        # Full dashboard UI (open in browser)
├── docker-compose.yml    # Run everything with Docker
├── start_windows.bat     # Windows one-click start
└── start_mac_linux.sh    # Mac/Linux one-click start
```

---

## 🚀 Quick Start (Without Docker)

### Prerequisites
- Python 3.10+
- pip

### Windows
```
Double-click: start_windows.bat
```

### Mac / Linux
```bash
chmod +x start_mac_linux.sh
./start_mac_linux.sh
```

### Manual Start (terminal by terminal)
```bash
# Terminal 1 — Auth Service
cd auth_service
pip install -r requirements.txt
uvicorn main:app --port 8001 --reload

# Terminal 2 — Inventory Service
cd inventory_service
pip install -r requirements.txt
uvicorn main:app --port 8002 --reload

# Terminal 3 — Sales Service
cd sales_service
pip install -r requirements.txt
uvicorn main:app --port 8003 --reload

# Terminal 4 — API Gateway
cd api_gateway
pip install -r requirements.txt
uvicorn main:app --port 8000 --reload
```

Then open `frontend/index.html` in your browser.

---

## 🐳 Quick Start (With Docker)

```bash
docker-compose up --build
```

---

## 🔑 Login Credentials

| Username    | Password     | Role         | Access                    |
|-------------|--------------|--------------|---------------------------|
| admin       | admin123     | admin        | Full access                |
| pharmacist  | pharma123    | pharmacist   | POS + Inventory view       |
| supervisor  | super123     | supervisor   | Reports + Add products     |
| finance     | finance123   | finance      | Reports + Sales view       |

---

## 🌐 Service URLs

| Service           | URL                           |
|-------------------|-------------------------------|
| API Gateway       | http://localhost:8000         |
| Swagger Docs      | http://localhost:8000/docs    |
| Auth Service      | http://localhost:8001         |
| Inventory Service | http://localhost:8002         |
| Sales Service     | http://localhost:8003         |

---

## 📡 Key API Endpoints (via Gateway)

```
POST /auth/login              Login (returns JWT)
GET  /auth/me                 Who am I?

GET  /inventory/products      List all products
POST /inventory/products      Add product (admin/supervisor)
GET  /inventory/products/{sku} Get one product
PUT  /inventory/products/{sku}/stock  Update stock
GET  /inventory/alerts/low-stock      Low stock list
GET  /inventory/alerts/expiring       Expiring soon

POST /sales                   Create sale / invoice
GET  /sales                   Sales history
GET  /sales/summary           Revenue summary

GET  /health                  All services health check
```

---

## ⚙️ Technologies Used

| Layer       | Technology                  |
|-------------|----------------------------|
| Backend     | Python, FastAPI             |
| Database    | SQLite (via SQLAlchemy ORM) |
| Auth        | JWT (PyJWT), bcrypt         |
| Messaging   | HTTP (Kafka-ready design)   |
| Frontend    | Vanilla HTML/CSS/JS         |
| Containers  | Docker, Docker Compose      |

---

## 🎯 Features

- ✅ JWT Authentication with RBAC (4 roles)
- ✅ Inventory management with batch & expiry tracking
- ✅ Point of Sale with GST calculation (12%)
- ✅ Invoice generation with unique invoice numbers
- ✅ Low stock and expiry alerts
- ✅ Sales history and revenue reports
- ✅ Microservices architecture (4 independent services)
- ✅ Full CRUD APIs with Swagger documentation
- ✅ Sample data pre-loaded (5 pharma products)

---

## 📄 Sample API Call (curl)

```bash
# 1. Login
curl -X POST http://localhost:8000/auth/login \
  -d "username=admin&password=admin123" \
  -H "Content-Type: application/x-www-form-urlencoded"

# 2. Get products (use token from step 1)
curl http://localhost:8000/inventory/products \
  -H "Authorization: Bearer <YOUR_TOKEN>"

# 3. Create a sale
curl -X POST http://localhost:8000/sales \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"items":[{"sku":"PCM500","quantity":2}],"payment_mode":"cash"}'
```
