from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List
import jwt

app = FastAPI(title="PharmaChain Inventory Service")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

DATABASE_URL = "sqlite:///./inventory.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

SECRET_KEY = "pharmachain-secret-2024"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8001/login")

class Product(Base):
    __tablename__ = "products"
    id       = Column(Integer, primary_key=True, index=True)
    sku      = Column(String, unique=True, index=True)
    name     = Column(String)
    category = Column(String)
    price    = Column(Float)
    quantity = Column(Integer, default=0)
    batch_no = Column(String)
    expiry   = Column(String)
    supplier = Column(String)
    branch   = Column(String, default="HQ")
    low_stock_threshold = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class ProductCreate(BaseModel):
    sku: str
    name: str
    category: str
    price: float
    quantity: int
    batch_no: str
    expiry: str
    supplier: str
    branch: str = "HQ"
    low_stock_threshold: int = 10

class StockUpdate(BaseModel):
    quantity: int
    reason: str = "manual"

class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    category: str
    price: float
    quantity: int
    batch_no: str
    expiry: str
    supplier: str
    branch: str
    low_stock_threshold: int
    created_at: datetime

    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_data(db: Session):
    if db.query(Product).count() == 0:
        products = [
            Product(sku="PCM500", name="Paracetamol 500mg", category="Analgesic",
                    price=2.5, quantity=500, batch_no="B001", expiry="2026-12-31",
                    supplier="Sun Pharma", branch="HQ", low_stock_threshold=50),
            Product(sku="AMX250", name="Amoxicillin 250mg", category="Antibiotic",
                    price=8.0, quantity=8, batch_no="B002", expiry="2025-06-30",
                    supplier="Cipla", branch="HQ", low_stock_threshold=20),
            Product(sku="MET500", name="Metformin 500mg", category="Antidiabetic",
                    price=3.5, quantity=300, batch_no="B003", expiry="2027-03-15",
                    supplier="Dr. Reddy's", branch="HQ", low_stock_threshold=30),
            Product(sku="ATR10", name="Atorvastatin 10mg", category="Cardiac",
                    price=12.0, quantity=5, batch_no="B004", expiry="2024-11-30",
                    supplier="Lupin", branch="HQ", low_stock_threshold=25),
            Product(sku="ORS200", name="ORS Sachet", category="Electrolyte",
                    price=1.0, quantity=1000, batch_no="B005", expiry="2026-08-20",
                    supplier="FDC", branch="HQ", low_stock_threshold=100),
        ]
        db.add_all(products)
        db.commit()

with SessionLocal() as s:
    seed_data(s)

@app.get("/products", response_model=List[ProductResponse])
def get_all_products(branch: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Product)
    if branch:
        q = q.filter(Product.branch == branch)
    return q.all()

@app.get("/products/{sku}", response_model=ProductResponse)
def get_product(sku: str, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.sku == sku).first()
    if not p:
        raise HTTPException(404, detail="Product not found")
    return p

@app.post("/products")
def add_product(product: ProductCreate, db: Session = Depends(get_db)):
    existing = db.query(Product).filter(Product.sku == product.sku).first()
    if existing:
        raise HTTPException(400, detail="SKU already exists")
    p = Product(**product.dict())
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"message": "Product added", "id": p.id}

@app.put("/products/{sku}/stock")
def update_stock(sku: str, update: StockUpdate, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.sku == sku).first()
    if not p:
        raise HTTPException(404, detail="Product not found")
    p.quantity += update.quantity
    db.commit()
    alert = p.quantity <= p.low_stock_threshold
    return {"sku": sku, "new_quantity": p.quantity, "low_stock_alert": alert}

@app.get("/alerts/low-stock")
def low_stock_alerts(db: Session = Depends(get_db)):
    items = db.query(Product).filter(Product.quantity <= Product.low_stock_threshold).all()
    return [{"sku": p.sku, "name": p.name, "quantity": p.quantity,
             "threshold": p.low_stock_threshold, "branch": p.branch} for p in items]

@app.get("/alerts/expiring")
def expiring_soon(db: Session = Depends(get_db)):
    today = date.today().isoformat()
    cutoff = date.today().replace(year=date.today().year + 1).isoformat()
    items = db.query(Product).filter(Product.expiry <= cutoff).all()
    return [{"sku": p.sku, "name": p.name, "expiry": p.expiry, "quantity": p.quantity} for p in items]

@app.get("/health")
def health():
    return {"status": "ok", "service": "inventory"}
