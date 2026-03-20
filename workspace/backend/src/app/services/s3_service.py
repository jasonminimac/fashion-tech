"""
S3 Service — pre-signed URL generation for uploads and downloads.

Uses boto3 to generate time-limited signed URLs for secure client-side
access to S3-compatible storage (AWS S3 or MinIO).

Environment variables required:
    AWS_REGION             — e.g. "us-east-1"
    AWS_ACCESS_KEY_ID      — Access key
    AWS_SECRET_ACCESS_KEY  — Secret key
    S3_ENDPOINT_URL        — (optional) Override endpoint (MinIO: http://localhost:9000)

Storage path conventions:
    Scans:    scans/{user_id}/{scan_id}/model.glb
    Garments: garments/{brand_id}/{garment_id}/model.fbx
"""

import os
import logging
from typing import Optional

import boto3
from botocore.exceptions import ClientError, BotoCoreError

from app.utils.errors import S3Error

logger = logging.getLogger(__name__)


def _get_s3_client():
    """Build and return a boto3 S3 client from environment variables."""
    kwargs: dict = {
        "region_name": os.environ.get("AWS_REGION", "us-east-1"),
        "aws_access_key_id": os.environ.get("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY"),
    }
    endpoint_url = os.environ.get("S3_ENDPOINT_URL")
    if endpoint_url:
        kwargs["endpoint_url"] = endpoint_url
    return boto3.client("s3", **kwargs)


def generate_signed_upload_url(
    bucket: str,
    key: str,
    expires_in: int = 300,
    content_type: Optional[str] = None,
) -> str:
    """Generate a pre-signed URL that allows a client to upload a file to S3.

    Args:
        bucket:      S3 bucket name.
        key:         Object key (path within bucket), e.g. "scans/{uid}/{sid}/model.glb".
        expires_in:  URL validity in seconds (default 300 = 5 minutes).
        content_type: Optional Content-Type constraint for the upload.

    Returns:
        A pre-signed URL string the client can use with HTTP PUT.

    Raises:
        S3Error: On boto3 / connection failure.

    Example:
        url = generate_signed_upload_url(
            bucket="fashion-tech-storage",
            key="scans/user-123/scan-456/model.glb",
            expires_in=300,
        )
    """
    client = _get_s3_client()
    params: dict = {"Bucket": bucket, "Key": key}
    if content_type:
        params["ContentType"] = content_type
    try:
        url = client.generate_presigned_url(
            "put_object",
            Params=params,
            ExpiresIn=expires_in,
        )
        logger.info("Generated upload URL for s3://%s/%s (ttl=%ds)", bucket, key, expires_in)
        return url
    except (ClientError, BotoCoreError) as exc:
        logger.error("S3 upload URL generation failed for %s/%s: %s", bucket, key, exc)
        raise S3Error(f"Failed to generate upload URL for {key}: {exc}") from exc


def generate_signed_download_url(
    bucket: str,
    key: str,
    expires_in: int = 3600,
) -> str:
    """Generate a pre-signed URL that allows a client to download a file from S3.

    Args:
        bucket:     S3 bucket name.
        key:        Object key (path within bucket).
        expires_in: URL validity in seconds (default 3600 = 1 hour).

    Returns:
        A pre-signed URL string the client can use with HTTP GET.

    Raises:
        S3Error: On boto3 / connection failure.

    Example:
        url = generate_signed_download_url(
            bucket="fashion-tech-storage",
            key="garments/brand-1/garment-7/model.fbx",
            expires_in=3600,
        )
    """
    client = _get_s3_client()
    try:
        url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
        )
        logger.info("Generated download URL for s3://%s/%s (ttl=%ds)", bucket, key, expires_in)
        return url
    except (ClientError, BotoCoreError) as exc:
        logger.error("S3 download URL generation failed for %s/%s: %s", bucket, key, exc)
        raise S3Error(f"Failed to generate download URL for {key}: {exc}") from exc


# ─── Path Helpers ────────────────────────────────────────────────────────────

def scan_model_key(user_id: str, scan_id: str) -> str:
    """Return the canonical S3 key for a body scan model.

    Example:
        key = scan_model_key("user-123", "scan-456")
        # → "scans/user-123/scan-456/model.glb"
    """
    return f"scans/{user_id}/{scan_id}/model.glb"


def garment_model_key(brand_id: str, garment_id: str) -> str:
    """Return the canonical S3 key for a garment 3D model.

    Example:
        key = garment_model_key("brand-1", "garment-7")
        # → "garments/brand-1/garment-7/model.fbx"
    """
    return f"garments/{brand_id}/{garment_id}/model.fbx"
