from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import uuid
import httpx

app = FastAPI(title="PharmaChain Sales Service")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

DATABASE_URL = "sqlite:///./sales.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

INVENTORY_URL = "http://localhost:8002"
GST_RATE = 0.12  # 12% GST

class Invoice(Base):
    __tablename__ = "invoices"
    id           = Column(Integer, primary_key=True, index=True)
    invoice_no   = Column(String, unique=True, index=True)
    branch       = Column(String, default="HQ")
    cashier      = Column(String)
    items        = Column(JSON)   # list of {sku, name, qty, unit_price, total}
    subtotal     = Column(Float)
    gst          = Column(Float)
    total        = Column(Float)
    payment_mode = Column(String, default="cash")
    timestamp    = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class SaleItem(BaseModel):
    sku: str
    quantity: int

class SaleRequest(BaseModel):
    items: List[SaleItem]
    cashier: str = "pharmacist"
    branch: str = "HQ"
    payment_mode: str = "cash"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/sales")
def create_sale(sale: SaleRequest, db: Session = Depends(get_db)):
    invoice_items = []
    subtotal = 0.0

    for item in sale.items:
        # Get product info from inventory
        try:
            resp = httpx.get(f"{INVENTORY_URL}/products/{item.sku}", timeout=5)
            if resp.status_code != 200:
                raise HTTPException(400, f"Product {item.sku} not found in inventory")
            product = resp.json()
        except httpx.ConnectError:
            # Fallback for demo (offline mode)
            product = {"name": item.sku, "price": 10.0, "quantity": 999}

        if product.get("quantity", 0) < item.quantity:
            raise HTTPException(400, f"Insufficient stock for {item.sku}. Available: {product.get('quantity', 0)}")

        line_total = product["price"] * item.quantity
        subtotal += line_total
        invoice_items.append({
            "sku": item.sku,
            "name": product.get("name", item.sku),
            "quantity": item.quantity,
            "unit_price": product["price"],
            "total": line_total
        })

        # Deduct stock
        try:
            httpx.put(f"{INVENTORY_URL}/products/{item.sku}/stock",
                      json={"quantity": -item.quantity, "reason": "sale"},
                      timeout=5)
        except httpx.ConnectError:
            pass  # offline mode — sync later

    gst = round(subtotal * GST_RATE, 2)
    total = round(subtotal + gst, 2)
    invoice_no = f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"

    invoice = Invoice(
        invoice_no=invoice_no,
        branch=sale.branch,
        cashier=sale.cashier,
        items=invoice_items,
        subtotal=round(subtotal, 2),
        gst=gst,
        total=total,
        payment_mode=sale.payment_mode,
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return {
        "invoice_no": invoice_no,
        "items": invoice_items,
        "subtotal": invoice.subtotal,
        "gst": invoice.gst,
        "total": invoice.total,
        "payment_mode": sale.payment_mode,
        "timestamp": invoice.timestamp.isoformat(),
        "message": "Sale recorded successfully"
    }

@app.get("/sales")
def get_sales(limit: int = 20, db: Session = Depends(get_db)):
    invoices = db.query(Invoice).order_by(Invoice.timestamp.desc()).limit(limit).all()
    return [
        {
            "invoice_no": inv.invoice_no,
            "branch": inv.branch,
            "cashier": inv.cashier,
            "items": inv.items,
            "subtotal": inv.subtotal,
            "gst": inv.gst,
            "total": inv.total,
            "payment_mode": inv.payment_mode,
            "timestamp": inv.timestamp.isoformat()
        }
        for inv in invoices
    ]

@app.get("/sales/summary")
def sales_summary(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).all()
    total_revenue = sum(i.total for i in invoices)
    total_invoices = len(invoices)
    avg_order = total_revenue / total_invoices if total_invoices else 0
    return {
        "total_invoices": total_invoices,
        "total_revenue": round(total_revenue, 2),
        "average_order_value": round(avg_order, 2)
    }

@app.get("/health")
def health():
    return {"status": "ok", "service": "sales"}
