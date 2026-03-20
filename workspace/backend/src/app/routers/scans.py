"""Scan routes — Week 2: wired upload endpoint + measurements + polling.

Endpoints added this sprint:
    POST /v1/scans/upload           — multipart .ply upload → 202 + async processing
    GET  /v1/scans/{id}/measurements — retrieve body measurements for a completed scan
    GET  /v1/scans/{id}/glb-url     — retrieve signed S3 download URL for rigged .glb

Existing endpoints retained (Week 1):
    POST /v1/scans                  — create scan record (pending)
    GET  /v1/scans/{id}             — get scan + status (polling endpoint)
    GET  /v1/scans/user/{user_id}   — list scans for a user
    POST /v1/scans/{id}/upload-url  — pre-signed S3 URL for direct client upload
"""
import uuid
import tempfile
import os
import asyncio
from typing import Optional
from fastapi import APIRouter, Depends, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session

from src.app.dependencies import get_db, get_current_user
from src.app.models.scan import Scan, ScanMeasurement
from src.app.models.user import User
from src.app.schemas.scan import ScanCreate, ScanResponse, UploadUrlResponse, MeasurementResponse
from src.app.schemas.base import BaseResponse, PaginatedResponse
from src.app.utils.errors import NotFound, Forbidden, ValidationError
from src.app.config import settings

router = APIRouter(prefix="/scans", tags=["scans"])

# Max upload size: 500 MB (LiDAR .ply files can be large)
MAX_PLY_SIZE_BYTES = 500 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {
    "application/octet-stream",
    "application/ply",
    "model/x-ply",
    "application/vnd.ply",
    "",  # some clients omit content-type
}


def _scan_key(user_id: str, scan_id: str) -> str:
    return f"scans/{user_id}/{scan_id}/model.glb"


# ─── Existing Week 1 Endpoints ───────────────────────────────────────────────

@router.post("", response_model=BaseResponse, status_code=201)
def create_scan(
    payload: ScanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new body scan record (pending status)."""
    scan = Scan(
        user_id=current_user.id,
        name=payload.name,
        scan_type=payload.scan_type,
        status="pending",
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return BaseResponse.success(ScanResponse.model_validate(scan).model_dump())


@router.get("/user/{user_id}", response_model=PaginatedResponse)
def list_user_scans(
    user_id: uuid.UUID,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List scans for a user. Only the owner or an admin may access."""
    role = getattr(current_user, "role", None)
    if str(current_user.id) != str(user_id) and role != "admin":
        raise Forbidden("Cannot access another user's scans")

    from src.app.utils.validators import clamp_pagination
    limit, offset = clamp_pagination(limit, offset)

    query = db.query(Scan).filter(
        Scan.user_id == user_id,
        Scan.deleted_at.is_(None),
    )
    total = query.count()
    scans = query.order_by(Scan.created_at.desc()).offset(offset).limit(limit).all()

    return PaginatedResponse(
        data=[ScanResponse.model_validate(s).model_dump() for s in scans],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{scan_id}", response_model=BaseResponse)
def get_scan(
    scan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get scan by ID (polling endpoint for processing status).

    Status lifecycle: pending → processing → complete | failed
    Frontend should poll this every 5s after upload until status != 'processing'.
    """
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.deleted_at.is_(None),
    ).first()
    if not scan:
        raise NotFound("Scan not found")

    role = getattr(current_user, "role", None)
    if str(scan.user_id) != str(current_user.id) and role != "admin":
        raise Forbidden("Cannot access this scan")

    return BaseResponse.success(ScanResponse.model_validate(scan).model_dump())


@router.post("/{scan_id}/upload-url", response_model=BaseResponse)
def get_upload_url(
    scan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a pre-signed S3 URL for mesh upload (alternative to multipart endpoint)."""
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.deleted_at.is_(None),
    ).first()
    if not scan:
        raise NotFound("Scan not found")

    role = getattr(current_user, "role", None)
    if str(scan.user_id) != str(current_user.id) and role != "admin":
        raise Forbidden("Cannot access this scan")

    try:
        import boto3
        s3 = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.S3_ENDPOINT_URL or None,
        )
        key = _scan_key(str(current_user.id), str(scan_id))
        url = s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": settings.S3_BUCKET, "Key": key},
            ExpiresIn=3600,
        )
    except Exception:
        key = _scan_key(str(current_user.id), str(scan_id))
        url = f"{settings.S3_ENDPOINT_URL}/{settings.S3_BUCKET}/{key}?presigned=placeholder"

    return BaseResponse.success(
        UploadUrlResponse(upload_url=url, key=key).model_dump()
    )


# ─── Week 2: Multipart Upload + Async Processing ─────────────────────────────

@router.post("/upload", response_model=BaseResponse, status_code=202)
async def upload_scan(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Body scan .ply file from iPhone LiDAR"),
    scan_type: str = Form(default="lidar", description="lidar | photogrammetry"),
    scan_name: Optional[str] = Form(default=None, description="Human-readable label"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a body scan .ply file and trigger async processing.

    Returns 202 Accepted immediately. Client should poll
    GET /v1/scans/{id} for status updates.

    Pipeline stages (async background task):
        1. Store raw .ply in S3
        2. Run scan pipeline → measurements.json
        3. Run rigging pipeline → .glb
        4. Persist measurements to DB
        5. Update scan.status = 'complete'

    Error recovery: scan.status → 'failed' + scan.error_message set.
    """
    # Validate file extension
    filename = file.filename or "upload.ply"
    if not filename.lower().endswith(".ply") and not filename.lower().endswith(".obj"):
        # Also accept .obj for photogrammetry
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "none"
        if ext not in ("ply", "obj", "bin"):
            raise ValidationError(f"Unsupported file type: .{ext}. Expected .ply or .obj")

    # Read file into temp location
    tmpfile = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=f"_{scan_type}.ply",
        prefix=f"scan_{str(current_user.id)[:8]}_",
    )
    try:
        contents = await file.read()
        if len(contents) > MAX_PLY_SIZE_BYTES:
            raise ValidationError(
                f"File too large: {len(contents) // (1024*1024)}MB (max 500MB)"
            )
        tmpfile.write(contents)
        tmpfile.flush()
        ply_path = tmpfile.name
    finally:
        tmpfile.close()

    # Create scan record
    scan = Scan(
        user_id=current_user.id,
        name=scan_name or f"Scan {scan_type.title()} {filename}",
        scan_type=scan_type,
        status="pending",
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    scan_id = str(scan.id)

    # Queue background processing
    from src.app.services.pipeline_service import process_scan
    from src.app.database.engine import SessionLocal

    async def _background_process():
        """Run pipeline in isolated DB session (background task)."""
        bg_db = SessionLocal()
        try:
            await process_scan(
                scan_id=scan_id,
                ply_local_path=ply_path,
                db_session=bg_db,
                s3_bucket=settings.S3_BUCKET,
                user_id=str(current_user.id),
            )
        finally:
            bg_db.close()
            # Clean up temp file after processing
            try:
                os.unlink(ply_path)
            except OSError:
                pass

    background_tasks.add_task(asyncio.ensure_future, _background_process())

    return BaseResponse.success({
        "scan_id": scan_id,
        "status": "pending",
        "message": "Scan uploaded successfully. Processing started.",
        "poll_url": f"/v1/scans/{scan_id}",
        "estimated_seconds": 30,
    })


# ─── Week 2: Measurements Retrieval ──────────────────────────────────────────

@router.get("/{scan_id}/measurements", response_model=BaseResponse)
def get_scan_measurements(
    scan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve body measurements for a completed scan.

    Returns 404 if scan not found or not yet processed.
    Returns 409 if scan is still processing.

    Measurement fields (all in cm unless stated):
        chest_cm, waist_cm, hips_cm, inseam_cm,
        shoulder_width_cm, arm_length_cm, torso_length_cm,
        weight_kg, bmi
    """
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.deleted_at.is_(None),
    ).first()
    if not scan:
        raise NotFound("Scan not found")

    role = getattr(current_user, "role", None)
    if str(scan.user_id) != str(current_user.id) and role != "admin":
        raise Forbidden("Cannot access this scan's measurements")

    if scan.status == "processing" or scan.status == "pending":
        from fastapi import HTTPException
        raise HTTPException(
            status_code=409,
            detail={
                "error": "scan_not_ready",
                "message": f"Scan is still {scan.status}. Poll GET /v1/scans/{scan_id} for status.",
                "scan_status": scan.status,
            }
        )

    if scan.status == "failed":
        from fastapi import HTTPException
        raise HTTPException(
            status_code=422,
            detail={
                "error": "scan_failed",
                "message": "Scan processing failed. Please re-upload.",
                "error_detail": scan.error_message,
            }
        )

    measurement = db.query(ScanMeasurement).filter(
        ScanMeasurement.scan_id == scan_id
    ).first()
    if not measurement:
        raise NotFound("No measurements found for this scan")

    return BaseResponse.success({
        "scan_id": str(scan_id),
        "scan_status": scan.status,
        "body_shape": scan.body_shape,
        "confidence_score": scan.confidence_score,
        "measurements": MeasurementResponse.model_validate(measurement).model_dump(),
    })


# ─── Week 2: GLB Download URL ─────────────────────────────────────────────────

@router.get("/{scan_id}/glb-url", response_model=BaseResponse)
def get_glb_download_url(
    scan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a signed download URL for the rigged .glb file.

    Only available when scan.status = 'complete'.
    URL expires in 1 hour. Re-request for a fresh URL.
    """
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.deleted_at.is_(None),
    ).first()
    if not scan:
        raise NotFound("Scan not found")

    role = getattr(current_user, "role", None)
    if str(scan.user_id) != str(current_user.id) and role != "admin":
        raise Forbidden("Cannot access this scan")

    if scan.status != "complete":
        from fastapi import HTTPException
        raise HTTPException(
            status_code=409,
            detail={
                "error": "scan_not_complete",
                "message": f"Scan status is '{scan.status}'. GLB available only after processing completes.",
            }
        )

    if not scan.rigged_file_key:
        raise NotFound("Rigged GLB file not found for this scan")

    from src.app.services.s3_service import generate_signed_download_url
    dev_mode = os.environ.get("DEV_PIPELINE_MOCK", "true").lower() == "true"

    if dev_mode:
        url = f"http://localhost:9000/{settings.S3_BUCKET}/{scan.rigged_file_key}?dev=true"
    else:
        url = generate_signed_download_url(settings.S3_BUCKET, scan.rigged_file_key)

    return BaseResponse.success({
        "scan_id": str(scan_id),
        "glb_url": url,
        "key": scan.rigged_file_key,
        "expires_in": 3600,
    })
