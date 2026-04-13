from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import campaigns, users, auth, tracking

app = FastAPI(
    title="LionSafe",
    description="Azərbaycan bank sektoru üçün phishing simulasiya platforması",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(tracking.router, prefix="/t", tags=["tracking"])


@app.get("/health")
def health():
    return {"status": "ok", "service": "LionSafe"}
