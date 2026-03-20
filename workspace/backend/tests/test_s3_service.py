"""
Tests for s3_service: pre-signed URL generation (mocked with moto).
"""

import os
import uuid

import boto3
import pytest
from moto import mock_aws

# Point the service at moto's fake AWS
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("AWS_REGION", "us-east-1")
# Do NOT set S3_ENDPOINT_URL so boto3 routes to moto

from app.services.s3_service import (
    generate_signed_upload_url,
    generate_signed_download_url,
    scan_model_key,
    garment_model_key,
)
from app.utils.errors import S3Error


BUCKET = "test-fashion-bucket"


@pytest.fixture()
def s3_bucket():
    """Create a real moto-backed S3 bucket for each test."""
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=BUCKET)
        yield s3


# ─── Path Helpers ────────────────────────────────────────────────────────────

class TestPathHelpers:
    def test_scan_model_key(self):
        key = scan_model_key("user-1", "scan-2")
        assert key == "scans/user-1/scan-2/model.glb"

    def test_garment_model_key(self):
        key = garment_model_key("brand-1", "garment-7")
        assert key == "garments/brand-1/garment-7/model.fbx"

    def test_scan_key_with_uuids(self):
        uid = str(uuid.uuid4())
        sid = str(uuid.uuid4())
        key = scan_model_key(uid, sid)
        assert key.startswith("scans/")
        assert key.endswith("/model.glb")

    def test_garment_key_with_uuids(self):
        bid = str(uuid.uuid4())
        gid = str(uuid.uuid4())
        key = garment_model_key(bid, gid)
        assert key.startswith("garments/")
        assert key.endswith("/model.fbx")


# ─── generate_signed_upload_url ──────────────────────────────────────────────

class TestGenerateSignedUploadUrl:
    def test_returns_string(self, s3_bucket):
        url = generate_signed_upload_url(BUCKET, "test/key.glb")
        assert isinstance(url, str)
        assert len(url) > 10

    def test_url_contains_bucket(self, s3_bucket):
        url = generate_signed_upload_url(BUCKET, "path/file.glb")
        assert BUCKET in url

    def test_url_contains_key(self, s3_bucket):
        key = "scans/user-1/scan-2/model.glb"
        url = generate_signed_upload_url(BUCKET, key)
        # URL-encoded form of the path should appear in URL
        assert "scans" in url

    def test_default_expiry_5min(self, s3_bucket):
        """expires_in default is 300 (5 min) — just verify no error."""
        url = generate_signed_upload_url(BUCKET, "test.glb")
        assert url  # truthy

    def test_custom_expiry(self, s3_bucket):
        url = generate_signed_upload_url(BUCKET, "test.glb", expires_in=600)
        assert url

    def test_upload_url_is_https_or_http(self, s3_bucket):
        url = generate_signed_upload_url(BUCKET, "test.glb")
        assert url.startswith("http")

    def test_s3_error_on_invalid_bucket(self, monkeypatch):
        """A ClientError should be wrapped in S3Error."""
        import botocore.exceptions

        def bad_presign(*args, **kwargs):
            raise botocore.exceptions.ClientError(
                {"Error": {"Code": "NoSuchBucket", "Message": "The specified bucket does not exist"}},
                "generate_presigned_url",
            )

        import boto3 as real_boto3
        fake_client = boto3.client("s3", region_name="us-east-1")
        monkeypatch.setattr(fake_client, "generate_presigned_url", bad_presign)

        import app.services.s3_service as svc
        monkeypatch.setattr(svc, "_get_s3_client", lambda: fake_client)

        with pytest.raises(S3Error):
            generate_signed_upload_url("no-bucket", "key.glb")


# ─── generate_signed_download_url ────────────────────────────────────────────

class TestGenerateSignedDownloadUrl:
    def test_returns_string(self, s3_bucket):
        url = generate_signed_download_url(BUCKET, "path/file.fbx")
        assert isinstance(url, str)
        assert len(url) > 10

    def test_url_contains_bucket(self, s3_bucket):
        url = generate_signed_download_url(BUCKET, "path/file.fbx")
        assert BUCKET in url

    def test_default_expiry_1hr(self, s3_bucket):
        """expires_in default is 3600 (1 hour) — just verify no error."""
        url = generate_signed_download_url(BUCKET, "garments/b/g/model.fbx")
        assert url

    def test_custom_expiry(self, s3_bucket):
        url = generate_signed_download_url(BUCKET, "file.fbx", expires_in=7200)
        assert url

    def test_is_valid_url_format(self, s3_bucket):
        url = generate_signed_download_url(BUCKET, "test.fbx")
        assert url.startswith("http")
        # Should have query-string signature parameters
        assert "?" in url

    def test_s3_error_wrapped(self, monkeypatch):
        import botocore.exceptions

        def bad_presign(*args, **kwargs):
            raise botocore.exceptions.ClientError(
                {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
                "generate_presigned_url",
            )

        fake_client = boto3.client("s3", region_name="us-east-1")
        monkeypatch.setattr(fake_client, "generate_presigned_url", bad_presign)

        import app.services.s3_service as svc
        monkeypatch.setattr(svc, "_get_s3_client", lambda: fake_client)

        with pytest.raises(S3Error):
            generate_signed_download_url("bucket", "key.fbx")
