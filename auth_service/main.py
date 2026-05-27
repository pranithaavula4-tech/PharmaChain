from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt

app = FastAPI(title="PharmaChain Auth Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "pharmachain-secret-2024"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# In-memory users (in production: use database)
USERS_DB = {
    "admin":      {"password": pwd_context.hash("admin123"),    "role": "admin",      "name": "Admin User"},
    "pharmacist": {"password": pwd_context.hash("pharma123"),   "role": "pharmacist", "name": "Ravi Kumar"},
    "supervisor": {"password": pwd_context.hash("super123"),    "role": "supervisor", "name": "Priya Sharma"},
    "finance":    {"password": pwd_context.hash("finance123"),  "role": "finance",    "name": "Anita Reddy"},
}

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    name: str

def create_token(data: dict):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def role_required(*roles):
    def checker(user=Depends(verify_token)):
        if user.get("role") not in roles:
            raise HTTPException(status_code=403, detail=f"Access denied. Required roles: {list(roles)}")
        return user
    return checker

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = USERS_DB.get(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": form_data.username, "role": user["role"], "name": user["name"]})
    return {"access_token": token, "token_type": "bearer", "role": user["role"], "name": user["name"]}

@app.get("/me")
def get_me(user=Depends(verify_token)):
    return {"username": user["sub"], "role": user["role"], "name": user["name"]}

@app.get("/health")
def health():
    return {"status": "ok", "service": "auth"}
