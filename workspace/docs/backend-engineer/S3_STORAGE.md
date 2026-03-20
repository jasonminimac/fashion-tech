# S3 & Cloud Storage Integration Plan

**Date:** 2026-03-17  
**Version:** 1.0  
**Status:** MVP Phase 1  
**Provider:** AWS S3 (with local MinIO fallback for dev)  

---

## Overview

Fashion Tech uses AWS S3 to store large binary files (3D scans, garment models, textures) while PostgreSQL stores metadata and relationships. This document outlines the storage architecture, file organization, access patterns, and cost optimization.

---

## Storage Architecture

### File Types & Sizes

| File Type | Size | Volume | Storage | Access Pattern |
|-----------|------|--------|---------|-----------------|
| Body scans (glTF) | 50-200MB | 1 per user/week | S3 Standard | User owned, private, infrequent |
| Rigged scans (glTF) | 100-300MB | 1 per user/week | S3 Standard | User owned, private, cached |
| Garment models (FBX) | 5-50MB | ~1-2 per brand | S3 Standard | Shared, public, frequently accessed |
| Textures (PNG/JPG) | 1-10MB | ~3 per garment | S3 Standard | Shared, public, frequently accessed |
| Outfit previews (PNG) | 0.5-2MB | ~5 per user | S3 Standard | User owned, semi-public, cacheable |
| User avatars (JPG) | 0.1-1MB | 1 per user | S3 Standard | Shared, public, frequently accessed |

### Storage Tiers

| Tier | Use Case | Cost | Retrieval Time |
|------|----------|------|-----------------|
| S3 Standard | Current/active files | $0.023/GB/month | Instant |
| S3 Intelligent-Tiering | Mixed access patterns | $0.0125/GB/month | Auto-optimized |
| S3 Glacier Instant | Archive after 1 year | $0.004/GB/month | Milliseconds |
| S3 Glacier Flexible | Long-term archive | $0.0036/GB/month | 1-5 minutes |

**Phase 1 Strategy:** All files on S3 Standard (simplicity, predictable cost)
**Phase 2:** Enable Intelligent-Tiering for automatic cost optimization

---

## Bucket Structure

### S3 Bucket Layout

```
fashion-tech-storage/
│
├── scans/
│   ├── {user_id}/
│   │   ├── {scan_id}/
│   │   │   ├── scan_original.glTF          (raw input from scanner)
│   │   │   ├── scan_original.bin           (binary data)
│   │   │   ├── rigged.glTF                 (after Blender pipeline)
│   │   │   ├── rigged.bin
│   │   │   ├── measurements.json           (body measurements as metadata)
│   │   │   └── thumbnail.jpg               (preview image)
│   │   └── {scan_id_2}/
│   │       └── ...
│   └── {user_id_2}/
│       └── ...
│
├── garments/
│   ├── {brand_slug}/
│   │   ├── {sku}/
│   │   │   ├── model.fbx                   (3D model)
│   │   │   ├── model.glTF                  (alternative format)
│   │   │   ├── textures/
│   │   │   │   ├── diffuse_color.png
│   │   │   │   ├── normal.png
│   │   │   │   ├── roughness.png
│   │   │   │   └── metallic.png
│   │   │   └── metadata.json               (size charts, fit params)
│   │   └── {sku_2}/
│   │       └── ...
│   └── {brand_slug_2}/
│       └── ...
│
├── outfits/
│   ├── {user_id}/
│   │   ├── {outfit_id}/
│   │   │   ├── preview_front.png           (rendered front view)
│   │   │   ├── preview_side.png            (rendered side view)
│   │   │   └── preview_back.png            (rendered back view)
│   │   └── {outfit_id_2}/
│   │       └── ...
│   └── {user_id_2}/
│       └── ...
│
└── avatars/
    ├── {user_id}.jpg                       (user profile picture)
    └── {user_id_2}.jpg
```

### S3 Path Conventions

**Scans:**
- **Path:** `scans/{user_id}/{scan_id}/scan_original.glTF`
- **Rationale:** User-indexed for easy access control, scan-indexed for organization
- **Access:** Private to user (signed URLs)

**Garments:**
- **Path:** `garments/{brand_slug}/{sku}/model.fbx`
- **Rationale:** Brand-indexed for bulk operations, SKU-indexed for cataloguing
- **Access:** Public (via CloudFront CDN, Phase 2)

**Outfits:**
- **Path:** `outfits/{user_id}/{outfit_id}/preview_front.png`
- **Rationale:** User-indexed, outfit-indexed, multi-view support
- **Access:** Private or semi-public based on outfit sharing setting

**Avatars:**
- **Path:** `avatars/{user_id}.jpg`
- **Rationale:** Simple, flat structure for frequent access
- **Access:** Public (via CloudFront CDN, Phase 2)

---

## Upload Strategy

### 1. Small Files (<5MB) - Direct Upload

**Flow:**
```
Client → FastAPI → S3 (direct)
```

**Implementation:**
```python
import boto3
from fastapi import UploadFile

s3_client = boto3.client('s3')

@router.post("/users/{user_id}/avatar")
async def upload_avatar(user_id: str, file: UploadFile):
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(400, "Invalid file type")
    
    # Read and upload
    file_key = f"avatars/{user_id}.jpg"
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=file_key,
        Body=await file.read(),
        ContentType=file.content_type,
        Metadata={"user_id": user_id}
    )
    
    return {"success": True, "file_key": file_key}
```

---

### 2. Large Files (>5MB) - Multipart Upload

**Flow:**
```
Client → (1) Get presigned URLs from FastAPI
       → (2) Upload chunks directly to S3
       → (3) Notify FastAPI when complete
```

**Why multipart?**
- Resume partial uploads
- Better network handling
- Parallel chunk uploads
- Better for large files

**Implementation:**

**Step 1: Initiate Multipart Upload**
```python
@router.post("/scans/upload-initiate")
async def initiate_scan_upload(
    user_id: str,
    current_user: dict = Depends(get_current_user)
) -> dict:
    # Verify user owns the account
    if current_user["user_id"] != user_id:
        raise HTTPException(403, "Forbidden")
    
    # Create database record
    scan_id = str(uuid.uuid4())
    file_key = f"scans/{user_id}/{scan_id}/scan_original.glTF"
    
    # Initiate multipart upload on S3
    response = s3_client.create_multipart_upload(
        Bucket=BUCKET_NAME,
        Key=file_key,
        Metadata={"user_id": user_id, "scan_id": scan_id}
    )
    upload_id = response["UploadId"]
    
    # Store in DB
    await db.scans.create(
        id=scan_id,
        user_id=user_id,
        scan_file_key=file_key,
        processing_status="pending",
        metadata={"upload_id": upload_id, "parts": []}
    )
    
    # Generate presigned URLs for parts (up to 5GB total)
    parts = []
    chunk_size = 50_000_000  # 50MB chunks
    part_count = (file_size_bytes + chunk_size - 1) // chunk_size
    
    for part_num in range(1, part_count + 1):
        presigned_url = s3_client.generate_presigned_url(
            'upload_part',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': file_key,
                'UploadId': upload_id,
                'PartNumber': part_num
            },
            ExpiresIn=3600  # 1 hour
        )
        parts.append({
            "part_number": part_num,
            "url": presigned_url,
            "size_bytes": chunk_size
        })
    
    return {
        "success": True,
        "data": {
            "scan_id": scan_id,
            "upload_id": upload_id,
            "parts": parts,
            "expiration": datetime.utcnow() + timedelta(hours=1)
        }
    }
```

**Step 2: Client Uploads Chunks**
```javascript
// Client-side pseudocode
async function uploadScan(file) {
  const { scan_id, upload_id, parts } = await initializeUpload();
  const uploadedParts = [];
  
  for (const part of parts) {
    const chunk = file.slice(
      (part.part_number - 1) * part.size_bytes,
      part.part_number * part.size_bytes
    );
    
    const response = await fetch(part.url, {
      method: 'PUT',
      body: chunk
    });
    
    uploadedParts.push({
      part_number: part.part_number,
      etag: response.headers.get('ETag')
    });
  }
  
  // Notify backend when complete
  await completeUpload(scan_id, upload_id, uploadedParts);
}
```

**Step 3: Complete Multipart Upload**
```python
@router.post("/scans/{scan_id}/upload-complete")
async def complete_scan_upload(
    scan_id: str,
    upload_data: dict,
    current_user: dict = Depends(get_current_user)
) -> dict:
    # Retrieve upload metadata from DB
    scan = await db.scans.get(scan_id)
    if scan["user_id"] != current_user["user_id"]:
        raise HTTPException(403, "Forbidden")
    
    # Complete multipart upload on S3
    upload_id = scan["metadata"]["upload_id"]
    parts = upload_data["parts"]  # [{"part_number": 1, "etag": "..."}, ...]
    
    response = s3_client.complete_multipart_upload(
        Bucket=BUCKET_NAME,
        Key=scan["scan_file_key"],
        UploadId=upload_id,
        MultipartUpload={"Parts": parts}
    )
    
    # Update DB: mark as processing, trigger Blender pipeline
    await db.scans.update(
        scan_id,
        processing_status="processing",
        metadata={"...": "..."}
    )
    
    # Queue background job: Blender pipeline
    await background_task_queue.enqueue(
        "process_scan_blender_pipeline",
        scan_id=scan_id
    )
    
    return {
        "success": True,
        "data": {"scan_id": scan_id, "status": "processing"}
    }
```

---

## Download Strategy

### Signed URLs (Secure, Temporary Access)

```python
def generate_signed_url(file_key: str, expiration_seconds: int = 3600) -> str:
    """Generate a time-limited URL for accessing S3 objects."""
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': file_key},
        ExpiresIn=expiration_seconds
    )
    return url

@router.get("/scans/{scan_id}/download")
async def download_scan(
    scan_id: str,
    current_user: dict = Depends(get_current_user)
) -> dict:
    scan = await db.scans.get(scan_id)
    if scan["user_id"] != current_user["user_id"]:
        raise HTTPException(403, "Forbidden")
    
    # Return signed URLs for both original and rigged files
    return {
        "success": True,
        "data": {
            "scan_file_url": generate_signed_url(scan["scan_file_key"]),
            "rigged_file_url": generate_signed_url(scan["rigged_file_key"]),
            "expires_in": 3600
        }
    }
```

### Public Files (Garments, Avatars) - CloudFront CDN

**Phase 2+:** Use CloudFront CDN in front of S3 for:
- Reduced S3 request costs (cache hits pay CDN, not S3)
- Global distribution (faster downloads)
- DDOS protection

```python
# For public files, use CloudFront URL instead of S3 signed URL
def get_cloudfront_url(file_key: str) -> str:
    return f"https://cdn.fashiontech.com/{file_key}"

# Example:
garment_model_url = get_cloudfront_url("garments/brand-x/sku123/model.glTF")
avatar_url = get_cloudfront_url("avatars/user123.jpg")
```

---

## Access Control

### Bucket Policies

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowPublicReadGarments",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::fashion-tech-storage/garments/*",
      "Condition": {
        "StringLike": {
          "aws:Referer": "https://fashiontech.com/*"
        }
      }
    },
    {
      "Sid": "DenyPublicReadScans",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::fashion-tech-storage/scans/*"
    },
    {
      "Sid": "AllowBackendFullAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:role/fashion-tech-backend"
      },
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::fashion-tech-storage/*"
    }
  ]
}
```

### IAM Role for Backend

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3FullAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket",
        "s3:CreateMultipartUpload",
        "s3:UploadPart",
        "s3:CompleteMultipartUpload",
        "s3:AbortMultipartUpload"
      ],
      "Resource": [
        "arn:aws:s3:::fashion-tech-storage",
        "arn:aws:s3:::fashion-tech-storage/*"
      ]
    }
  ]
}
```

---

## Local Development (MinIO)

**Why MinIO?**
- S3-compatible API (can reuse code)
- Runs locally in Docker
- No AWS account needed for dev/testing

**Setup:**
```bash
# Start MinIO
docker run -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"

# Access console: http://localhost:9001
# S3 endpoint: http://localhost:9000
```

**Python Configuration:**
```python
import os
import boto3

if os.getenv("ENV") == "development":
    s3_client = boto3.client(
        's3',
        endpoint_url='http://localhost:9000',
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minioadmin',
        region_name='us-east-1'
    )
else:
    s3_client = boto3.client(
        's3',
        region_name=os.getenv("AWS_REGION", "us-east-1")
    )
```

---

## Cost Estimation (Phase 1)

### Assumptions
- 1,000 users, each uploads 1 scan/month
- Average scan size: 150MB
- 500 garment models in catalogue (5MB each)
- 500 textures per garment (2MB each)

### Monthly Costs

| Category | Volume | Cost |
|----------|--------|------|
| Scans (storage) | 1,000 * 150MB = 150GB | $3.45 |
| Garments (storage) | 500 * 5MB = 2.5GB | $0.06 |
| Textures (storage) | 500 * 500 * 2MB = 500GB | $11.50 |
| Total storage | ~652GB | **$15.01** |
| S3 requests (1M/month) | | $0.40 |
| Data transfer out (100GB/month) | | $8.50 |
| **Total** | | **~$24/month** |

### Cost Optimization (Phase 2+)
- Use S3 Intelligent-Tiering: ~30% savings
- Enable CloudFront caching: ~40% reduction in data transfer
- Archive old scans to Glacier: ~95% savings on cold storage

---

## Monitoring & Alerts

### CloudWatch Metrics

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

def log_s3_metric(metric_name: str, value: float, unit: str = "Bytes"):
    cloudwatch.put_metric_data(
        Namespace='FashionTech/S3',
        MetricData=[{
            'MetricName': metric_name,
            'Value': value,
            'Unit': unit,
            'Timestamp': datetime.utcnow()
        }]
    )

# Log upload sizes
log_s3_metric('ScanUploadSize', file_size_bytes, 'Bytes')
log_s3_metric('UploadCount', 1, 'Count')
```

### Alerts
- Storage > 1TB: notify ops team
- Upload failure rate > 5%: page on-call
- Request errors > 1%: investigate
- Data transfer spike: check for misuse

---

## Next Steps

1. **Set up S3 bucket** with proper policies and encryption
2. **Implement upload endpoints** (avatar, scans)
3. **Implement download endpoints** (signed URLs)
4. **Set up MinIO locally** for development
5. **Integration tests** for upload/download flows
6. **Monitor costs** and optimize in Phase 2

---

**Status:** Ready for Implementation  
**Last Updated:** 2026-03-17
