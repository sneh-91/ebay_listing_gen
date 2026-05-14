from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes.ebay import router as ebay_router
from app.routes.health import router as health_router
from app.routes.listings import router as listings_router
from app.storage.db import init_database

settings = get_settings()

app = FastAPI(title="ListCraft AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(listings_router)
app.include_router(ebay_router)


@app.on_event("startup")
def startup() -> None:
    init_database()
