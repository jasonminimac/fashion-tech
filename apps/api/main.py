from fastapi import FastAPI
from routers import health, scans, garments

app = FastAPI(
    title="Fashion Tech API",
    version="0.1.0",
    description="Virtual try-on platform — pipeline skeleton",
)

app.include_router(health.router)
app.include_router(scans.router)
app.include_router(garments.router)
