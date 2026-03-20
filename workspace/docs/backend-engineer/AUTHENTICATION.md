# Authentication & Security Strategy

**Date:** 2026-03-17  
**Version:** 1.0  
**Status:** MVP Phase 1  

---

## Overview

Fashion Tech authentication provides secure user account management with JWT-based stateless tokens, supporting email/password registration and optional OAuth2 SSO (Phase 2). This document outlines the security architecture, implementation strategy, and best practices.

---

## Authentication Architecture

### Flow Diagram

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ 1. POST /auth/register or /auth/login
       ├─────────────────────────────────────────────────────────┐
       │                                                         │
       ▼                                                         ▼
┌──────────────────────────┐                         ┌──────────────────────────┐
│  FastAPI Auth Router     │                         │  Database                │
│  - Validate input        │  ◄─────────────────────►│  - Check user exists     │
│  - Hash password         │  Query/Update            │  - Store credentials    │
│  - Generate JWT tokens   │                         │  - Audit logs            │
└──────────────┬───────────┘                         └──────────────────────────┘
               │
               │ 2. Return access + refresh tokens
               ▼
         ┌──────────────┐
         │   Client     │  (store tokens in secure storage)
         └──────┬───────┘
                │
                │ 3. Include access_token in Authorization header
                │    for subsequent requests
                ▼
         ┌──────────────┐
         │ Protected    │
         │ Endpoints    │
         └──────┬───────┘
                │
                │ 4. Validate JWT signature & claims
                ▼
         ┌──────────────────────┐
         │ FastAPI Dependency   │
         │ (get_current_user)   │
         └──────────────────────┘
```

---

## JWT Token Structure

### Access Token
**Payload:**
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "iat": 1710768000,
  "exp": 1710771600,
  "type": "access"
}
```

**Properties:**
- Expires in: **1 hour**
- Signed with: **HS256** (secret key)
- Stored by client: **Memory or localStorage** (not httpOnly)
- Used for: **Authenticating API requests**

### Refresh Token
**Payload:**
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "iat": 1710768000,
  "exp": 1710854400,
  "type": "refresh",
  "version": 1
}
```

**Properties:**
- Expires in: **7 days**
- Signed with: **HS256** (same secret as access token)
- Stored by client: **httpOnly cookie** (secure, not accessible to JS)
- Used for: **Obtaining new access tokens**
- Can be: **Rotated on each refresh** (version field for rotation tracking)

---

## Implementation Strategy

### 1. Password Security

**Hashing Algorithm:** `bcrypt`
```python
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Tuning: takes ~300ms to hash (security vs. usability)
)

# Hash password
hashed = pwd_context.hash(user_password)

# Verify password
is_valid = pwd_context.verify(user_password, hashed)
```

**Why bcrypt?**
- Slow by design (resistant to brute force)
- Salt included automatically
- Industry standard for password hashing
- No speed improvements without security degradation

**Password Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit
- At least 1 special character (!@#$%^&*)
- Not a common password (check against OWASP top 1000)

---

### 2. JWT Token Generation & Validation

**Generation (in `POST /auth/login`):**
```python
from datetime import datetime, timedelta
import jwt

SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # Store in environment, not in code
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(user_id: str, email: str):
    payload = {
        "sub": str(user_id),
        "email": email,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "access"
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def create_refresh_token(user_id: str):
    payload = {
        "sub": str(user_id),
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "type": "refresh",
        "version": 1
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token
```

**Validation (in FastAPI dependency):**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {"user_id": user_id, "email": payload.get("email")}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Usage in protected endpoint:**
```python
@router.get("/users/me")
async def get_current_profile(current_user: dict = Depends(get_current_user)):
    user = await db.users.get(current_user["user_id"])
    return user
```

---

### 3. Refresh Token Rotation (Recommended for Phase 2)

**Why rotate?**
- If refresh token leaked, attacker can obtain new access tokens indefinitely
- Rotation limits the window of vulnerability

**Strategy:**
- Each refresh token has a `version` field
- On refresh, issue new refresh token with `version + 1`
- Invalidate previous version in database

**Implementation (Phase 2):**
```python
# Store refresh token "family" in DB to detect concurrent refresh attempts
CREATE TABLE refresh_token_families (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    family_id UUID NOT NULL,  -- All tokens in same refresh chain share this
    current_version INT NOT NULL,
    revoked BOOLEAN DEFAULT false,
    created_at TIMESTAMP,
    expires_at TIMESTAMP
);

# On POST /auth/refresh:
# 1. Decode refresh token (check version)
# 2. Look up token family in DB
# 3. If version_in_token < current_version_in_db: possible token theft → revoke entire family
# 4. If version matches: issue new token with version+1, update DB
```

---

### 4. Session Management

**Stateless Tokens (MVP):**
- No session table needed
- Tokens are valid until expiration
- Can't revoke immediately (accept this limitation in MVP)

**Token Blacklist (Phase 2, if needed):**
```python
# If we need immediate revocation (e.g., user logs out):
CREATE TABLE token_blacklist (
    jti TEXT PRIMARY KEY,  -- JWT ID (claim in token)
    user_id UUID NOT NULL,
    created_at TIMESTAMP,
    expires_at TIMESTAMP
);

# On logout: add token's JTI to blacklist
# On validation: check if JTI is blacklisted (short-lived, can be pruned after token expiry)
```

---

### 5. HTTPS & CORS

**HTTPS (Production):**
```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
```

**CORS:**
```python
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = [
    "https://fashiontech.com",
    "https://www.fashiontech.com",
    "https://app.fashiontech.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600  # preflight cache time
)
```

---

### 6. Security Headers

```python
from fastapi.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

---

## OAuth2 SSO (Phase 2+)

### Flow
1. User clicks "Sign up with Google/Apple/Facebook"
2. Redirect to OAuth provider
3. Provider returns authorization code
4. Backend exchanges code for access token + user info
5. Create/update user in our DB
6. Return our JWT tokens

### Implementation (Future)
```python
# dependencies.py
from fastapi_oauth2.google import GoogleOAuth2

google_oauth = GoogleOAuth2(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    redirect_uri="https://api.fashiontech.com/v1/auth/callback/google"
)

# routers/auth.py
@router.get("/auth/google/login")
async def login_with_google():
    return await google_oauth.get_authorization_url()

@router.get("/auth/callback/google")
async def callback_google(code: str):
    user_info = await google_oauth.get_user_info(code)
    user = await db.users.get_or_create(email=user_info["email"])
    access_token = create_access_token(user["id"], user["email"])
    return {"access_token": access_token, "token_type": "bearer"}
```

---

## Audit Logging

### Log All Auth Events
```sql
CREATE TABLE auth_audit_logs (
    id UUID PRIMARY KEY,
    user_id UUID,
    event_type VARCHAR(50),  -- "login", "logout", "register", "password_change", "token_refresh"
    status VARCHAR(20),  -- "success", "failure"
    ip_address VARCHAR(45),
    user_agent TEXT,
    reason TEXT,  -- for failures (e.g., "invalid_password")
    created_at TIMESTAMP
);

-- Log query
INSERT INTO auth_audit_logs (user_id, event_type, status, ip_address, user_agent)
VALUES ($1, 'login', 'success', request.client.host, request.headers['user-agent']);
```

### Monitor & Alert
- Multiple failed login attempts (>5 in 15 min) → lock account temporarily
- Unusual login location → send verification email
- Multiple account registrations from same IP → rate limit

---

## Best Practices Summary

| Practice | Rationale |
|----------|-----------|
| Store JWT secret in env vars | Never commit secrets to git |
| Use HTTPS everywhere | Prevent token interception |
| Short access token TTL (1h) | Limit damage if token leaked |
| Longer refresh token TTL (7d) | Balance convenience + security |
| Rotate refresh tokens (Phase 2) | Detect & prevent token theft |
| Hash passwords with bcrypt | Resist brute force attacks |
| Enforce strong password policy | Reduce weak password risks |
| Log auth events | Detect & investigate suspicious activity |
| Rate limit login attempts | Prevent brute force / credential stuffing |
| CORS whitelist | Prevent unauthorized cross-origin requests |
| Secure headers | Prevent common web attacks (XSS, clickjacking) |

---

## Testing Strategy

### Unit Tests
```python
def test_create_access_token():
    token = create_access_token("user123", "user@example.com")
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "user123"
    assert payload["type"] == "access"

def test_password_hashing():
    password = "SecurePass123!"
    hashed = pwd_context.hash(password)
    assert pwd_context.verify(password, hashed)
    assert not pwd_context.verify("WrongPassword", hashed)

def test_get_current_user_expired_token():
    expired_token = jwt.encode(
        {"sub": "user123", "exp": datetime.utcnow() - timedelta(hours=1)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    with pytest.raises(HTTPException, match="Token expired"):
        get_current_user(expired_token)
```

### Integration Tests
```python
async def test_register_and_login():
    # Register
    response = await client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    assert response.status_code == 201

    # Login
    response = await client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()["data"]

async def test_protected_endpoint_requires_auth():
    response = await client.get("/users/me")
    assert response.status_code == 401
```

---

## Next Steps

1. **Implement JWT token generation** (Week 1)
2. **Implement password hashing** with bcrypt (Week 1)
3. **Set up FastAPI security dependencies** (Week 1)
4. **Implement registration & login endpoints** (Week 1)
5. **Add audit logging** (Week 1-2)
6. **Set up rate limiting** (Week 2)
7. **Test authentication flow** end-to-end (Week 2)
8. **Plan OAuth2 integration** (Phase 2 design doc)

---

**Status:** Ready for Implementation  
**Last Updated:** 2026-03-17
