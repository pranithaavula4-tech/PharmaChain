from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
import httpx
import jwt

app = FastAPI(title="PharmaChain API Gateway", version="1.0")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

AUTH_URL      = "http://localhost:8001"
INVENTORY_URL = "http://localhost:8002"
SALES_URL     = "http://localhost:8003"

SECRET_KEY = "pharmachain-secret-2024"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{AUTH_URL}/login", auto_error=False)

def verify_token(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ── Auth routes ──────────────────────────────────────────────
@app.post("/auth/login")
async def login(request: Request):
    body = await request.body()
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{AUTH_URL}/login", content=body,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    return JSONResponse(resp.json(), status_code=resp.status_code)

@app.get("/auth/me")
async def me(user=Depends(verify_token)):
    return user

# ── Inventory routes ─────────────────────────────────────────
@app.get("/inventory/products")
async def get_products(user=Depends(verify_token)):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{INVENTORY_URL}/products")
    return JSONResponse(resp.json())

@app.get("/inventory/products/{sku}")
async def get_product(sku: str, user=Depends(verify_token)):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{INVENTORY_URL}/products/{sku}")
    return JSONResponse(resp.json(), status_code=resp.status_code)

@app.post("/inventory/products")
async def add_product(request: Request, user=Depends(verify_token)):
    if user.get("role") not in ("admin", "supervisor"):
        raise HTTPException(403, "Only admin/supervisor can add products")
    body = await request.json()
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{INVENTORY_URL}/products", json=body)
    return JSONResponse(resp.json(), status_code=resp.status_code)

@app.get("/inventory/alerts/low-stock")
async def low_stock(user=Depends(verify_token)):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{INVENTORY_URL}/alerts/low-stock")
    return JSONResponse(resp.json())

@app.get("/inventory/alerts/expiring")
async def expiring(user=Depends(verify_token)):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{INVENTORY_URL}/alerts/expiring")
    return JSONResponse(resp.json())

# ── Sales routes ─────────────────────────────────────────────
@app.post("/sales")
async def create_sale(request: Request, user=Depends(verify_token)):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{SALES_URL}/sales", json=body)
    return JSONResponse(resp.json(), status_code=resp.status_code)

@app.get("/sales")
async def get_sales(user=Depends(verify_token)):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{SALES_URL}/sales")
    return JSONResponse(resp.json())

@app.get("/sales/summary")
async def sales_summary(user=Depends(verify_token)):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{SALES_URL}/sales/summary")
    return JSONResponse(resp.json())

# ── Health check ──────────────────────────────────────────────
@app.get("/health")
async def health():
    results = {}
    for name, url in [("auth", AUTH_URL), ("inventory", INVENTORY_URL), ("sales", SALES_URL)]:
        try:
            async with httpx.AsyncClient(timeout=2) as client:
                r = await client.get(f"{url}/health")
                results[name] = "ok" if r.status_code == 200 else "error"
        except Exception:
            results[name] = "unreachable"
    return {"gateway": "ok", "services": results}
