from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.app.config import settings
from src.app.routers import auth, users, scans, garments, outfits, health, retailers
from src.app.database.engine import engine
from src.app.models.base import Base

# Create tables on startup (dev convenience — production uses Alembic migrations)
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    print("🚀 Fashion Tech API starting...")
    print(f"   Environment: {settings.ENVIRONMENT}")
    print(f"   Docs: {settings.docs_url}")
    yield
    print("🛑 Fashion Tech API shutting down...")

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=(
        "Fashion Tech — 3D body scanning & virtual try-on API. "
        "Phase 1 MVP — Week 2. "
        "All endpoints wired and operational."
    ),
    lifespan=lifespan,
    docs_url=settings.docs_url,
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(auth.router, prefix="/v1")
app.include_router(users.router, prefix="/v1")
app.include_router(scans.router, prefix="/v1")
app.include_router(garments.router, prefix="/v1")
app.include_router(outfits.router, prefix="/v1")
app.include_router(retailers.router, prefix="/v1")


@app.get("/")
async def root():
    """Root endpoint — API status."""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "running",
        "docs": settings.docs_url,
        "week": "2",
        "pipeline_mode": "mock" if __import__("os").environ.get("DEV_PIPELINE_MOCK", "true") == "true" else "live",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
