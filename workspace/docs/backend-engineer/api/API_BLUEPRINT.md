# Fashion Tech API Blueprint - Phase 1

**Date:** 2026-03-17  
**Version:** 1.0 MVP  
**Base URL:** `https://api.fashiontech.com/v1`  
**Documentation:** Auto-generated at `/docs` (OpenAPI/Swagger)  

---

## Authentication

All endpoints except `/auth/register` and `/auth/login` require a Bearer token in the `Authorization` header.

```
Authorization: Bearer <access_token>
```

### Token Types
- **Access Token:** JWT valid for 1 hour
- **Refresh Token:** JWT valid for 7 days (httpOnly cookie or request body)

---

## API Endpoints

### 1. Authentication (`/auth`)

#### POST /auth/register
**Description:** Create a new user account  
**Authentication:** None  
**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "created_at": "2026-03-17T13:44:00Z"
  }
}
```

**Errors:**
- `400`: Email already exists, weak password, invalid format
- `500`: Server error

---

#### POST /auth/login
**Description:** Authenticate and receive access/refresh tokens  
**Authentication:** None  
**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "first_name": "John"
    }
  }
}
```

**Errors:**
- `401`: Invalid credentials
- `404`: User not found

---

#### POST /auth/refresh
**Description:** Refresh access token using refresh token  
**Authentication:** Required (refresh token in body or cookie)  
**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600
  }
}
```

---

#### POST /auth/logout
**Description:** Invalidate refresh token (client should discard access token)  
**Authentication:** Required  
**Request Body:** Empty  

**Response:** `200 OK`
```json
{
  "success": true,
  "data": { "message": "Logged out successfully" }
}
```

---

### 2. User Profile (`/users`)

#### GET /users/me
**Description:** Get current authenticated user's profile  
**Authentication:** Required  

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "avatar_url": "https://s3.amazonaws.com/avatars/user123.jpg",
    "height_cm": 180,
    "gender": "male",
    "preferred_fit": "normal",
    "created_at": "2026-03-17T13:44:00Z"
  }
}
```

---

#### PATCH /users/me
**Description:** Update current user's profile  
**Authentication:** Required  
**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "height_cm": 180,
  "gender": "male",
  "preferred_fit": "normal",
  "receives_marketing": true
}
```

**Response:** `200 OK` (updated user object)

---

#### PATCH /users/me/password
**Description:** Change password (requires old password)  
**Authentication:** Required  
**Request Body:**
```json
{
  "old_password": "OldPassword123!",
  "new_password": "NewPassword456!"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": { "message": "Password updated successfully" }
}
```

**Errors:**
- `400`: Weak password, passwords don't match
- `401`: Old password incorrect

---

### 3. Body Scans (`/scans`)

#### POST /scans/upload
**Description:** Initiate a scan file upload (returns S3 presigned URL for multipart upload)  
**Authentication:** Required  
**Request Body:**
```json
{
  "name": "Full body scan",
  "scan_type": "lidar",
  "file_size_bytes": 52428800,
  "file_name": "scan_2026_03_17.glTF"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "scan_id": "660f8400-e29b-41d4-a716-446655440111",
    "s3_upload_url": "https://s3.amazonaws.com/fashion-tech-scans/...",
    "s3_upload_id": "ExampleUploadId",
    "parts": [
      {
        "part_number": 1,
        "upload_url": "https://s3.amazonaws.com/...",
        "size_bytes": 10485760
      }
    ],
    "expiration": "2026-03-17T14:44:00Z"
  }
}
```

**Notes:**
- Returns multipart upload URLs for chunks (if file > 100MB)
- Client uploads directly to S3 (backend validates signature)
- Scan created in `processing` status

---

#### POST /scans/{scan_id}/complete
**Description:** Complete multipart upload and trigger processing pipeline  
**Authentication:** Required  
**Request Body:**
```json
{
  "s3_upload_id": "ExampleUploadId",
  "parts": [
    { "part_number": 1, "etag": "abc123def456" }
  ]
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "scan_id": "660f8400-e29b-41d4-a716-446655440111",
    "status": "processing",
    "message": "Scan queued for processing. You'll be notified when complete."
  }
}
```

**Async Processing:**
- Backend validates multipart upload
- Triggers Blender integration pipeline (rigging, export)
- User receives notification (email, webhook, or polling `/scans/{id}`)

---

#### GET /scans
**Description:** List user's body scans with pagination  
**Authentication:** Required  
**Query Parameters:**
- `page` (int, default: 1)
- `page_size` (int, default: 20, max: 100)
- `status` (string, optional): "pending", "processing", "completed", "failed"
- `sort` (string, default: "created_at"): "created_at", "name"
- `order` (string, default: "desc"): "asc", "desc"

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "660f8400-e29b-41d4-a716-446655440111",
      "name": "Full body scan",
      "scan_type": "lidar",
      "status": "completed",
      "created_at": "2026-03-17T13:44:00Z",
      "processed_at": "2026-03-17T13:49:00Z",
      "measurements": {
        "chest_cm": 95,
        "waist_cm": 85,
        "hips_cm": 100,
        "body_shape": "rectangle"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 5,
    "total_pages": 1
  }
}
```

---

#### GET /scans/{scan_id}
**Description:** Get detailed info for a specific scan  
**Authentication:** Required  

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "660f8400-e29b-41d4-a716-446655440111",
    "name": "Full body scan",
    "scan_type": "lidar",
    "status": "completed",
    "file_urls": {
      "scan_file": "https://s3.amazonaws.com/scans/.../body.glTF?expires=...",
      "rigged_file": "https://s3.amazonaws.com/scans/.../rigged.glTF?expires=..."
    },
    "measurements": {
      "chest_cm": 95,
      "waist_cm": 85,
      "hips_cm": 100,
      "shoulder_width_cm": 42,
      "arm_length_cm": 65,
      "inseam_cm": 82,
      "body_shape": "rectangle"
    },
    "metadata": {
      "camera": "iPhone 13 Pro",
      "mesh_vertex_count": 125000
    },
    "created_at": "2026-03-17T13:44:00Z",
    "processed_at": "2026-03-17T13:49:00Z"
  }
}
```

**Notes:**
- `file_urls` are signed S3 URLs (1-hour expiration)
- Only owner can view their scans

---

#### DELETE /scans/{scan_id}
**Description:** Delete a scan (soft delete, permanent after 30 days)  
**Authentication:** Required  

**Response:** `200 OK`
```json
{
  "success": true,
  "data": { "message": "Scan deleted successfully" }
}
```

---

### 4. Garment Catalogue (`/garments`)

#### GET /garments
**Description:** Search and browse garment catalogue  
**Authentication:** Optional (public catalogue, but with user preferences)  
**Query Parameters:**
- `page` (int, default: 1)
- `page_size` (int, default: 50, max: 200)
- `category` (string, optional): "dresses", "shirts", "pants", etc.
- `brand` (string, optional)
- `color` (string, optional)
- `price_min` (float, optional)
- `price_max` (float, optional)
- `search` (string, optional): full-text search
- `sort` (string, default: "relevance"): "relevance", "price_asc", "price_desc", "newest"

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "770f8400-e29b-41d4-a716-446655440222",
      "sku": "BRAND_DRESS_001",
      "name": "Summer Linen Dress",
      "brand": "Designer Brand",
      "category": "dresses",
      "color": "navy",
      "material": "100% linen",
      "retail_price": 125.99,
      "thumbnail_url": "https://s3.amazonaws.com/garment-thumbnails/...",
      "available_sizes": ["XS", "S", "M", "L", "XL"],
      "rating": 4.5,
      "review_count": 23
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total_count": 1234,
    "total_pages": 25
  }
}
```

---

#### GET /garments/{garment_id}
**Description:** Get detailed garment info (for outfit builder)  
**Authentication:** Optional  

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "770f8400-e29b-41d4-a716-446655440222",
    "sku": "BRAND_DRESS_001",
    "name": "Summer Linen Dress",
    "brand": "Designer Brand",
    "description": "A breathable linen dress perfect for summer...",
    "category": "dresses",
    "subcategory": "casual-dresses",
    "color": "navy",
    "material_composition": {
      "linen": 100
    },
    "material_care": "Machine wash cold...",
    "retail_price": 125.99,
    "retail_url": "https://retailer.com/product/...",
    "sizes": [
      {
        "id": "880f8400-e29b-41d4-a716-446655440333",
        "size_label": "XS",
        "chest_cm_min": 78,
        "chest_cm_max": 86,
        "waist_cm_min": 58,
        "waist_cm_max": 66,
        "hips_cm_min": 86,
        "hips_cm_max": 94,
        "fabric_stretch": 1.05
      },
      {
        "size_label": "S",
        "chest_cm_min": 86,
        "chest_cm_max": 94,
        "waist_cm_min": 66,
        "waist_cm_max": 74,
        "hips_cm_min": 94,
        "hips_cm_max": 102,
        "fabric_stretch": 1.05
      }
    ],
    "model_file": {
      "format": "fbx",
      "size_bytes": 12582912,
      "download_url": "https://s3.amazonaws.com/garments/.../model.fbx?expires=..."
    },
    "textures": {
      "diffuse": "https://s3.amazonaws.com/garments/.../diffuse.png?expires=...",
      "normal": "https://s3.amazonaws.com/garments/.../normal.png?expires=..."
    }
  }
}
```

---

#### GET /garments/categories
**Description:** List garment categories (for navigation)  
**Authentication:** None  

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "990f8400-e29b-41d4-a716-446655440444",
      "name": "Dresses",
      "slug": "dresses",
      "icon_url": "https://s3.amazonaws.com/category-icons/dresses.svg",
      "subcategories": [
        {
          "id": "aa0f8400-e29b-41d4-a716-446655440555",
          "name": "Casual Dresses",
          "slug": "casual-dresses"
        },
        {
          "name": "Formal Dresses",
          "slug": "formal-dresses"
        }
      ]
    },
    {
      "name": "Tops",
      "slug": "tops",
      "subcategories": [...]
    }
  ]
}
```

---

### 5. Outfits (`/outfits`)

#### POST /outfits
**Description:** Create a new outfit (for a specific scan)  
**Authentication:** Required  
**Request Body:**
```json
{
  "scan_id": "660f8400-e29b-41d4-a716-446655440111",
  "name": "Summer Casual Look",
  "description": "Casual summer outfit for day trips",
  "occasion": "casual",
  "season": "summer",
  "is_private": true
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "id": "bb0f8400-e29b-41d4-a716-446655440666",
    "scan_id": "660f8400-e29b-41d4-a716-446655440111",
    "name": "Summer Casual Look",
    "description": "Casual summer outfit for day trips",
    "items": [],
    "created_at": "2026-03-17T14:00:00Z"
  }
}
```

---

#### GET /outfits
**Description:** List user's saved outfits  
**Authentication:** Required  
**Query Parameters:**
- `page` (int, default: 1)
- `page_size` (int, default: 20, max: 100)
- `scan_id` (string, optional): filter by specific scan

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "bb0f8400-e29b-41d4-a716-446655440666",
      "scan_id": "660f8400-e29b-41d4-a716-446655440111",
      "name": "Summer Casual Look",
      "description": "Casual summer outfit for day trips",
      "item_count": 3,
      "thumbnail_url": "https://s3.amazonaws.com/outfit-thumbnails/...",
      "occasion": "casual",
      "season": "summer",
      "created_at": "2026-03-17T14:00:00Z"
    }
  ],
  "pagination": { "page": 1, "page_size": 20, "total_count": 5, "total_pages": 1 }
}
```

---

#### GET /outfits/{outfit_id}
**Description:** Get full outfit details (all garments + metadata)  
**Authentication:** Required  

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "bb0f8400-e29b-41d4-a716-446655440666",
    "scan_id": "660f8400-e29b-41d4-a716-446655440111",
    "name": "Summer Casual Look",
    "description": "Casual summer outfit for day trips",
    "items": [
      {
        "display_order": 1,
        "garment_id": "770f8400-e29b-41d4-a716-446655440222",
        "garment": {
          "id": "770f8400-e29b-41d4-a716-446655440222",
          "name": "Summer Linen Dress",
          "brand": "Designer Brand",
          "thumbnail": "https://s3.amazonaws.com/..."
        },
        "size_id": "880f8400-e29b-41d4-a716-446655440333",
        "size_label": "S",
        "color_selected": "navy",
        "notes": "Perfect fit"
      }
    ],
    "created_at": "2026-03-17T14:00:00Z"
  }
}
```

---

#### PATCH /outfits/{outfit_id}
**Description:** Update outfit metadata  
**Authentication:** Required  
**Request Body:**
```json
{
  "name": "Summer Casual - Updated",
  "description": "Updated description",
  "occasion": "casual",
  "is_private": false
}
```

**Response:** `200 OK` (updated outfit object)

---

#### POST /outfits/{outfit_id}/items
**Description:** Add garment to outfit  
**Authentication:** Required  
**Request Body:**
```json
{
  "garment_id": "770f8400-e29b-41d4-a716-446655440222",
  "garment_size_id": "880f8400-e29b-41d4-a716-446655440333",
  "color_selected": "navy",
  "notes": "Perfect fit!"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "id": "cc0f8400-e29b-41d4-a716-446655440777",
    "outfit_id": "bb0f8400-e29b-41d4-a716-446655440666",
    "garment_id": "770f8400-e29b-41d4-a716-446655440222",
    "display_order": 1
  }
}
```

---

#### DELETE /outfits/{outfit_id}/items/{item_id}
**Description:** Remove garment from outfit  
**Authentication:** Required  

**Response:** `200 OK`
```json
{
  "success": true,
  "data": { "message": "Item removed from outfit" }
}
```

---

#### DELETE /outfits/{outfit_id}
**Description:** Delete an outfit  
**Authentication:** Required  

**Response:** `200 OK`
```json
{
  "success": true,
  "data": { "message": "Outfit deleted successfully" }
}
```

---

### 6. Recommendations (`/recommendations`) - Phase 1 (MVP scope: basic filtering)

#### POST /recommendations/fit
**Description:** Get size recommendations based on body scan measurements  
**Authentication:** Required  
**Request Body:**
```json
{
  "scan_id": "660f8400-e29b-41d4-a716-446655440111",
  "garment_ids": ["770f8400-e29b-41d4-a716-446655440222", "770f8400-e29b-41d4-a716-446655440223"]
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "garment_id": "770f8400-e29b-41d4-a716-446655440222",
      "recommended_size_id": "880f8400-e29b-41d4-a716-446655440333",
      "recommended_size_label": "S",
      "confidence": 0.92,
      "notes": "Based on measurements: 85cm waist, 95cm chest"
    },
    {
      "garment_id": "770f8400-e29b-41d4-a716-446655440223",
      "recommended_size_id": "881f8400-e29b-41d4-a716-446655440334",
      "recommended_size_label": "S",
      "confidence": 0.87
    }
  ]
}
```

---

### 7. Health Check

#### GET /health
**Description:** Liveness check (always responds)  
**Authentication:** None  

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2026-03-17T14:00:00Z"
}
```

---

#### GET /health/ready
**Description:** Readiness check (includes dependency checks)  
**Authentication:** None  

**Response:** `200 OK` or `503 Service Unavailable`
```json
{
  "status": "ready",
  "checks": {
    "database": "ok",
    "s3": "ok",
    "redis": "ok"
  },
  "timestamp": "2026-03-17T14:00:00Z"
}
```

---

## Error Codes

| Code | HTTP Status | Meaning |
|------|-------------|---------|
| `INVALID_REQUEST` | 400 | Malformed request body or invalid parameters |
| `VALIDATION_ERROR` | 400 | Request data fails validation (field-level details included) |
| `UNAUTHORIZED` | 401 | Missing or invalid authentication token |
| `FORBIDDEN` | 403 | Authenticated but not permitted to access resource |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists (e.g., duplicate email) |
| `RATE_LIMITED` | 429 | Too many requests (include `Retry-After` header) |
| `INTERNAL_ERROR` | 500 | Server error (include request ID for debugging) |

---

## Rate Limiting

### Limits (Phase 1)

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/auth/login` | 5 attempts | 15 minutes |
| `/auth/register` | 3 registrations | 1 hour |
| `/scans/upload` | 10 uploads | 1 hour |
| `/garments` | 60 requests | 1 minute |
| All other endpoints | 100 requests | 1 minute |

### Response Headers

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1710770400
```

---

## Versioning

API versioned via URL path: `/v1/`, `/v2/`, etc.

- Current: `/v1` (March 2026)
- Future: `/v2` (backward-compatible changes; breaking changes → new version)

---

## Next Steps

1. **Implement endpoints** in FastAPI (router by router)
2. **Write Pydantic schemas** for request/response validation
3. **Implement authentication** (JWT, password hashing)
4. **Integration tests** for each endpoint
5. **Documentation** (auto-generated via `/docs`)

---

**Status:** Ready for Implementation  
**Last Updated:** 2026-03-17
