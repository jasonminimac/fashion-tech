# API Specification — Fashion Tech Backend

**Base URL:** `https://api.fashiontech.app/v1` (production) | `http://localhost:8000` (local)  
**Auth:** Bearer JWT — include `Authorization: Bearer <token>` on protected endpoints.  
**Format:** JSON (`Content-Type: application/json`)

---

## Auth

### POST /auth/register

Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "Jane Smith"
}
```

**Response 201:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "Jane Smith",
  "created_at": "2026-03-18T20:00:00Z"
}
```

---

### POST /auth/login

**Request:**
```json
{ "email": "user@example.com", "password": "SecurePass123!" }
```

**Response 200:**
```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

### POST /auth/refresh

**Request:** `{ "refresh_token": "<jwt>" }`  
**Response 200:** Same as login.

---

### POST /auth/logout

🔒 Auth required. Invalidates current session.  
**Response 204:** No content.

---

## Users

### GET /users/me 🔒

**Response 200:**
```json
{
  "id": "550e8400...",
  "email": "user@example.com",
  "full_name": "Jane Smith",
  "measurements": null,
  "created_at": "2026-03-18T20:00:00Z"
}
```

### PATCH /users/me 🔒

**Request:** `{ "full_name": "Jane Doe" }`  
**Response 200:** Updated user object.

### PATCH /users/me/password 🔒

**Request:** `{ "current_password": "...", "new_password": "..." }`  
**Response 204:** No content.

---

## Body Scans

### POST /scans 🔒

Initiate a scan upload (multipart form data).

**Request:** `multipart/form-data`  
- `scan_file`: point cloud / mesh file  
- `device_type`: `iphone_lidar` | `android_depth`

**Response 201:**
```json
{
  "id": "scan-uuid",
  "status": "processing",
  "upload_url": "https://s3.../presigned-url",
  "created_at": "2026-03-18T20:00:00Z"
}
```

### GET /scans 🔒

List user scans. Query params: `limit`, `offset`.

### GET /scans/{scan_id} 🔒

Get a specific scan and its measurements.

---

## Garments

### GET /garments

Browse catalogue. Query params: `category`, `brand`, `search`, `limit`, `offset`.

### GET /garments/{garment_id}

**Response 200:**
```json
{
  "id": "garment-uuid",
  "name": "Classic White Shirt",
  "brand": "Zara",
  "category": "tops",
  "sizes": ["XS","S","M","L","XL"],
  "fit_data": { "chest": 96, "waist": 80 },
  "images": ["https://..."]
}
```

### GET /garments/categories

Returns available categories.

---

## Outfits

### POST /outfits 🔒

**Request:**
```json
{
  "name": "Summer Look",
  "garment_ids": ["id1", "id2", "id3"]
}
```

**Response 201:** Outfit object.

### GET /outfits 🔒

List user outfits.

### GET /outfits/{outfit_id} 🔒

Get outfit with all garments.

### PATCH /outfits/{outfit_id} 🔒

Update outfit name or garments.

### DELETE /outfits/{outfit_id} 🔒

**Response 204.**

---

## Retailers

### GET /retailers

List integrated retailers.

### GET /retailers/{retailer_id}/garments

Garments from a specific retailer.

---

## Health

### GET /health

**Response 200:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "environment": "production"
}
```

### GET /health/ready

Readiness check — verifies DB + S3 connectivity.

**Response 200:**
```json
{
  "status": "ready",
  "checks": {
    "database": "ok",
    "s3": "ok"
  }
}
```

---

## Error Responses

All errors follow:

```json
{
  "detail": "Human-readable error message"
}
```

| Status | Meaning |
|--------|---------|
| 400 | Bad request / validation error |
| 401 | Missing or invalid JWT |
| 403 | Forbidden |
| 404 | Resource not found |
| 422 | Unprocessable entity (Pydantic validation) |
| 500 | Internal server error |
