# PharmaChain
# PharmaChain 💊

PharmaChain is a microservices-based pharmacy management system built using FastAPI, Docker, SQLite, and a frontend interface. The project demonstrates modern backend architecture with authentication, inventory management, sales management, API gateway integration, and containerized deployment.

---

# 🚀 Features

* 🔐 Authentication Service
* 📦 Inventory Management Service
* 💰 Sales Management Service
* 🌐 API Gateway
* 🐳 Dockerized Microservices Architecture
* ⚡ FastAPI Backend Services
* 🗄 SQLite Database Integration
* 🎨 Frontend Integration
* 🔄 REST API Communication

---

# 🏗 Architecture

```text
Frontend
   ↓
API Gateway
   ↓
---------------------------------
| Auth Service                |
| Inventory Service           |
| Sales Service               |
---------------------------------
   ↓
SQLite Databases
```

---

# 🛠 Tech Stack

## Backend

* Python
* FastAPI
* Uvicorn
* SQLite

## Frontend

* HTML
* CSS
* JavaScript

## DevOps

* Docker
* Docker Compose

---

# 📂 Project Structure

```text
pharmachain/
│
├── api_gateway/
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── auth_service/
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── inventory_service/
│   ├── main.py
│   ├── inventory.db
│   ├── Dockerfile
│   └── requirements.txt
│
├── sales_service/
│   ├── main.py
│   ├── sales.db
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   └── index.html
│
├── docker-compose.yml
├── start_windows.bat
├── start_mac_linux.sh
└── README.md
```

---

# ⚙️ Installation & Setup

## 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/pharmachain.git
cd pharmachain
```

---

## 2️⃣ Create Virtual Environment (Optional)

```bash
python -m venv venv
```

Activate virtual environment:

### Windows

```bash
venv\Scripts\activate
```

### Linux/Mac

```bash
source venv/bin/activate
```

---

# ▶️ Run Using Docker

## Start All Services

```bash
docker-compose up --build
```

---

# ▶️ Run Without Docker

## API Gateway

```bash
cd api_gateway
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Auth Service

```bash
cd auth_service
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

## Inventory Service

```bash
cd inventory_service
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```

## Sales Service

```bash
cd sales_service
pip install -r requirements.txt
uvicorn main:app --reload --port 8003
```

---

# 🌐 API Endpoints

## Authentication Service

| Method | Endpoint  | Description       |
| ------ | --------- | ----------------- |
| POST   | /login    | User Login        |
| POST   | /register | User Registration |

---

## Inventory Service

| Method | Endpoint   | Description         |
| ------ | ---------- | ------------------- |
| GET    | /inventory | Get inventory items |
| POST   | /inventory | Add inventory item  |

---

## Sales Service

| Method | Endpoint | Description    |
| ------ | -------- | -------------- |
| GET    | /sales   | Get sales data |
| POST   | /sales   | Create sale    |

---

# 🐳 Docker Services

The project uses Docker Compose to manage:

* API Gateway
* Authentication Service
* Inventory Service
* Sales Service
* Frontend

---

# 📸 Screenshots

Add your project screenshots here.

Example:

```text
screenshots/homepage.png
screenshots/dashboard.png
```

---

# 🔒 Security Features

* Authentication-based access
* Microservice isolation
* API Gateway routing

---

# 📈 Future Improvements

* JWT Authentication
* Role-Based Access Control
* PostgreSQL/MySQL integration
* Kubernetes deployment
* Cloud deployment (AWS/Azure)
* Payment integration
* Analytics dashboard

---

# 🎯 Learning Outcomes

This project demonstrates:

* Microservices architecture
* REST API development
* FastAPI backend development
* Docker containerization
* API Gateway implementation
* Service communication
* Database integration

---

# 👨‍💻 Author

Developed by Avula Pranitha

---

# 📄 License

This project is for educational and learning purposes.
