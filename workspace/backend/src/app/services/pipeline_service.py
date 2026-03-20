"""
Pipeline Service — orchestrates scan processing pipeline.

Flow:
    1. Client uploads .ply file (multipart POST /v1/scans/upload)
    2. Backend stores raw .ply in S3
    3. Async task: .ply → measurements.json (scanning pipeline)
    4. Async task: .ply → rigged .glb (rigging pipeline)
    5. Both outputs stored in S3
    6. Scan record updated: status=complete, measurements persisted to DB

Design decisions:
    - asyncio.subprocess used for pipeline calls (non-blocking)
    - status polling via GET /v1/scans/{id} (status field: pending/processing/complete/failed)
    - 202 Accepted returned immediately on upload
    - Retry logic: 3 attempts with 5s backoff for transient failures
    - Local fallback: mock pipeline output if pipeline binary not available (dev mode)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import tempfile
import time
import uuid
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Pipeline binary paths (resolved from env or defaults)
SCAN_PIPELINE_CMD = os.environ.get("SCAN_PIPELINE_CMD", "python3")
SCAN_PIPELINE_SCRIPT = os.environ.get(
    "SCAN_PIPELINE_SCRIPT",
    "/workspace/projects/python/fashion-tech-processing/pipeline/pipeline.py",
)
RIGGING_PIPELINE_CMD = os.environ.get("RIGGING_PIPELINE_CMD", "python3")
RIGGING_PIPELINE_SCRIPT = os.environ.get(
    "RIGGING_PIPELINE_SCRIPT",
    "/workspace/rigging-engine/scripts/main.py",
)
PIPELINE_TIMEOUT_SECS = int(os.environ.get("PIPELINE_TIMEOUT_SECS", "120"))
DEV_MODE = os.environ.get("DEV_PIPELINE_MOCK", "true").lower() == "true"


class PipelineError(Exception):
    """Raised when a pipeline stage fails after retries."""


# ─── Mock output for dev/test ─────────────────────────────────────────────────

def _mock_measurements(scan_id: str) -> dict:
    """Return plausible mock body measurements for dev/test mode."""
    return {
        "scan_id": scan_id,
        "version": "1.0-mock",
        "measurements": {
            "chest_cm": 96.0,
            "waist_cm": 82.0,
            "hips_cm": 100.0,
            "inseam_cm": 81.0,
            "shoulder_width_cm": 44.0,
            "arm_length_cm": 62.0,
            "torso_length_cm": 60.0,
            "weight_kg": None,
            "bmi": None,
        },
        "confidence": 0.92,
        "body_shape": "athletic",
        "error_mm": 3.8,
    }


def _mock_glb_path(tmpdir: str, scan_id: str) -> str:
    """Create a minimal valid GLB stub file for dev/test mode."""
    # Minimal GLB binary: magic + version + length header
    # Real rigging would produce a full skeletal mesh
    glb_magic = b"glTF"
    glb_version = (2).to_bytes(4, "little")
    glb_length = (12).to_bytes(4, "little")
    stub = glb_magic + glb_version + glb_length

    path = os.path.join(tmpdir, f"{scan_id}.glb")
    with open(path, "wb") as f:
        f.write(stub)
    logger.info("[DEV] Created stub GLB at %s (%d bytes)", path, len(stub))
    return path


# ─── Pipeline execution helpers ───────────────────────────────────────────────

async def _run_subprocess(
    cmd: list[str],
    timeout: int = PIPELINE_TIMEOUT_SECS,
) -> tuple[int, str, str]:
    """Run a subprocess asynchronously and return (returncode, stdout, stderr)."""
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        raise PipelineError(f"Pipeline command timed out after {timeout}s: {cmd[0]}")
    return proc.returncode, stdout_b.decode(), stderr_b.decode()


async def run_scan_pipeline(
    ply_path: str,
    scan_id: str,
    retries: int = 3,
) -> dict:
    """Run the scan processing pipeline: .ply → measurements dict.

    Args:
        ply_path:  Local path to the input .ply file.
        scan_id:   UUID string for logging/output naming.
        retries:   Number of retry attempts on failure.

    Returns:
        Dict with measurement fields (chest_cm, waist_cm, etc.) + metadata.

    Raises:
        PipelineError: On all retries exhausted or fatal error.
    """
    if DEV_MODE:
        logger.info("[DEV] Mocking scan pipeline for scan_id=%s", scan_id)
        await asyncio.sleep(0.1)  # simulate work
        return _mock_measurements(scan_id)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, f"{scan_id}_measurements.json")
        cmd = [
            SCAN_PIPELINE_CMD,
            SCAN_PIPELINE_SCRIPT,
            "--input", ply_path,
            "--output", output_path,
            "--scan-id", scan_id,
        ]

        last_exc: Optional[Exception] = None
        for attempt in range(1, retries + 1):
            try:
                returncode, stdout, stderr = await _run_subprocess(cmd)
                if returncode == 0:
                    with open(output_path) as f:
                        result = json.load(f)
                    logger.info("Scan pipeline OK for scan_id=%s (attempt %d)", scan_id, attempt)
                    return result
                logger.warning(
                    "Scan pipeline attempt %d/%d failed (rc=%d): %s",
                    attempt, retries, returncode, stderr[:500],
                )
            except PipelineError as exc:
                logger.warning("Scan pipeline attempt %d/%d error: %s", attempt, retries, exc)
                last_exc = exc

            if attempt < retries:
                await asyncio.sleep(5 * attempt)

        raise PipelineError(f"Scan pipeline failed after {retries} attempts") from last_exc


async def run_rigging_pipeline(
    ply_path: str,
    scan_id: str,
    output_dir: str,
    retries: int = 3,
) -> str:
    """Run the rigging pipeline: .ply mesh → rigged .glb file.

    Args:
        ply_path:    Local path to the input .ply file.
        scan_id:     UUID string for output naming.
        output_dir:  Directory to write the output .glb file.
        retries:     Number of retry attempts on failure.

    Returns:
        Local path to the output .glb file.

    Raises:
        PipelineError: On all retries exhausted or fatal error.
    """
    if DEV_MODE:
        logger.info("[DEV] Mocking rigging pipeline for scan_id=%s", scan_id)
        await asyncio.sleep(0.1)
        return _mock_glb_path(output_dir, scan_id)

    output_path = os.path.join(output_dir, f"{scan_id}.glb")
    cmd = [
        RIGGING_PIPELINE_CMD,
        RIGGING_PIPELINE_SCRIPT,
        "--input", ply_path,
        "--output", output_path,
        "--scan-id", scan_id,
    ]

    last_exc: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            returncode, stdout, stderr = await _run_subprocess(cmd)
            if returncode == 0 and os.path.exists(output_path):
                logger.info("Rigging pipeline OK for scan_id=%s (attempt %d)", scan_id, attempt)
                return output_path
            logger.warning(
                "Rigging pipeline attempt %d/%d failed (rc=%d): %s",
                attempt, retries, returncode, stderr[:500],
            )
        except PipelineError as exc:
            logger.warning("Rigging pipeline attempt %d/%d error: %s", attempt, retries, exc)
            last_exc = exc

        if attempt < retries:
            await asyncio.sleep(5 * attempt)

    raise PipelineError(f"Rigging pipeline failed after {retries} attempts") from last_exc


# ─── Full scan processing orchestration ───────────────────────────────────────

async def process_scan(
    scan_id: str,
    ply_local_path: str,
    db_session,  # SQLAlchemy Session
    s3_bucket: str,
    user_id: str,
) -> None:
    """
    Full async pipeline: .ply → measurements (DB) + .glb (S3).

    Called as a background task after scan upload.
    Updates scan.status throughout for polling.

    Args:
        scan_id:       UUID string of the scan record.
        ply_local_path: Local path to the uploaded .ply file.
        db_session:    SQLAlchemy session (caller must handle lifecycle).
        s3_bucket:     Target S3 bucket name.
        user_id:       UUID string of the scan owner.
    """
    from src.app.models.scan import Scan, ScanMeasurement
    from src.app.services.s3_service import (
        generate_signed_upload_url,
        scan_model_key,
    )

    scan = db_session.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        logger.error("process_scan: scan %s not found in DB", scan_id)
        return

    scan.status = "processing"
    db_session.commit()
    logger.info("Processing scan %s ...", scan_id)

    start_ts = time.time()

    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # Stage 1: measurements
            measurements_data = await run_scan_pipeline(ply_local_path, scan_id)

            # Persist measurements
            meas_dict = measurements_data.get("measurements", measurements_data)
            existing = db_session.query(ScanMeasurement).filter(
                ScanMeasurement.scan_id == scan_id
            ).first()
            if existing:
                for k, v in meas_dict.items():
                    if hasattr(existing, k):
                        setattr(existing, k, v)
            else:
                measurement = ScanMeasurement(
                    scan_id=scan_id,
                    **{k: v for k, v in meas_dict.items() if hasattr(ScanMeasurement, k)},
                )
                db_session.add(measurement)

            scan.body_shape = measurements_data.get("body_shape", "unknown")
            scan.confidence_score = measurements_data.get("confidence", None)

            # Stage 2: rigging → .glb
            glb_path = await run_rigging_pipeline(ply_local_path, scan_id, tmpdir)

            # Upload .glb to S3
            glb_key = scan_model_key(user_id, scan_id)
            _upload_file_to_s3(glb_path, s3_bucket, glb_key)
            scan.rigged_file_key = glb_key

            # Also upload original .ply
            ply_key = f"scans/{user_id}/{scan_id}/raw.ply"
            _upload_file_to_s3(ply_local_path, s3_bucket, ply_key)
            scan.scan_file_key = ply_key

            scan.status = "complete"
            elapsed = time.time() - start_ts
            logger.info("Scan %s complete in %.1fs", scan_id, elapsed)

        except PipelineError as exc:
            scan.status = "failed"
            scan.error_message = str(exc)
            logger.error("Scan %s pipeline failed: %s", scan_id, exc)
        except Exception as exc:
            scan.status = "failed"
            scan.error_message = f"Unexpected error: {exc}"
            logger.exception("Scan %s unexpected error", scan_id)

        finally:
            try:
                db_session.commit()
            except Exception:
                db_session.rollback()


def _upload_file_to_s3(local_path: str, bucket: str, key: str) -> None:
    """Upload a local file to S3. Uses mock in dev mode."""
    if DEV_MODE:
        logger.info("[DEV] Mock S3 upload: %s → s3://%s/%s", local_path, bucket, key)
        return

    import boto3
    s3 = boto3.client("s3")
    s3.upload_file(local_path, bucket, key)
    logger.info("Uploaded %s → s3://%s/%s", local_path, bucket, key)
