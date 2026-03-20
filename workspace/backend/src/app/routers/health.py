"""Health check routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.app.dependencies import get_db

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health():
    """Basic liveness check."""
    return {"status": "ok", "service": "fashion-tech-api"}


@router.get("/ready")
def readiness(db: Session = Depends(get_db)):
    """Readiness check: verify DB connectivity."""
    checks: dict = {"database": False, "s3": False}

    # DB check
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as exc:
        checks["database_error"] = str(exc)

    # S3 check (best-effort)
    try:
        from src.app.config import settings
        import boto3
        s3 = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.S3_ENDPOINT_URL or None,
        )
        s3.head_bucket(Bucket=settings.S3_BUCKET)
        checks["s3"] = True
    except Exception as exc:
        checks["s3_error"] = str(exc)

    all_ready = all(v is True for k, v in checks.items() if not k.endswith("_error"))
    status_code = 200 if all_ready else 503

    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=status_code,
        content={"status": "ready" if all_ready else "degraded", "checks": checks},
    )
