# Fashion Tech Database Schema Design

**Date:** 2026-03-17  
**Revision:** 1.0  
**Engine:** PostgreSQL 14+  
**Status:** Phase 1 MVP  

---

## Schema Overview

```
USERS (1) ──── (N) SCANS
 │
 ├─────────── (N) OUTFITS
 │
 └─────────── (N) SAVED_FAVOURITE_GARMENTS

OUTFITS (1) ──── (N) OUTFIT_ITEMS
             │
             └─── (N) GARMENTS

GARMENTS (1) ──── (N) GARMENT_VARIANTS
 │
 ├─────────── (N) GARMENT_SIZES
 │
 ├─────────── (N) GARMENT_CATEGORIES
 │
 └─────────── (1) RETAIL_PARTNERS

SCANS (1) ──── (1) S3_FILES (metadata)
 │
 └─────────── (N) SCAN_MEASUREMENTS (body dimensions)
```

---

## Table Definitions

### 1. USERS

Stores user profiles and authentication data.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url VARCHAR(500),
    
    -- Profile metadata
    gender VARCHAR(50),  -- "male", "female", "non-binary", null
    age_range VARCHAR(50),  -- "18-25", "26-35", etc. (not exact DOB for privacy)
    height_cm INT,  -- for size recommendation
    preferred_fit VARCHAR(50),  -- "tight", "normal", "loose"
    
    -- Settings
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    receives_marketing BOOLEAN DEFAULT true,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    deleted_at TIMESTAMP,  -- soft delete
    
    -- Constraints
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'),
    CONSTRAINT valid_height CHECK (height_cm IS NULL OR (height_cm > 100 AND height_cm < 250))
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
```

**Notes:**
- `password_hash` stored with bcrypt (not plain text)
- `deleted_at` allows soft deletes (retain data for analytics, recovery)
- `gender`, `age_range`, `height_cm` optional (improves size recommendations)
- `avatar_url` points to S3 or CDN

---

### 2. SCANS

Stores metadata for 3D body scans.

```sql
CREATE TABLE scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Scan info
    name VARCHAR(255) DEFAULT 'Scan',  -- user-assigned name ("My full body", "Torso only", etc.)
    scan_type VARCHAR(50) NOT NULL,  -- "lidar", "photogrammetry", "manual_upload"
    
    -- Files (stored in S3)
    scan_file_key VARCHAR(500) NOT NULL,  -- S3 path: "scans/{user_id}/{scan_id}/body.glTF"
    scan_file_size_bytes INT,  -- for quota management
    rigged_file_key VARCHAR(500),  -- "scans/{user_id}/{scan_id}/rigged.glTF"
    rigged_file_size_bytes INT,
    
    -- Metadata
    mesh_vertex_count INT,  -- for quality/complexity tracking
    metadata JSONB,  -- {"camera": "iPhone 13 Pro", "environment": "indoor", "clothing": "tight", ...}
    
    -- Status
    processing_status VARCHAR(50) DEFAULT 'pending',  -- "pending", "processing", "completed", "failed"
    error_message TEXT,  -- if processing_status = 'failed'
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    deleted_at TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_scan_type CHECK (scan_type IN ('lidar', 'photogrammetry', 'manual_upload')),
    CONSTRAINT valid_status CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed'))
);

CREATE INDEX idx_scans_user_id ON scans(user_id);
CREATE INDEX idx_scans_created_at ON scans(created_at DESC);
CREATE INDEX idx_scans_status ON scans(processing_status);
```

**Notes:**
- `scan_file_key` is the S3 path (not the file itself)
- `rigged_file_key` is populated after Blender pipeline completes
- `metadata` is JSONB for flexible capture (camera model, environment, clothing worn, etc.)
- `processing_status` tracks the Blender integration pipeline

---

### 3. SCAN_MEASUREMENTS

Stores body measurements extracted from scans (used for size recommendations).

```sql
CREATE TABLE scan_measurements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_id UUID NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
    
    -- Key measurements (in cm)
    chest_cm INT,
    waist_cm INT,
    hips_cm INT,
    shoulder_width_cm INT,
    arm_length_cm INT,
    inseam_cm INT,
    
    -- Derived metrics
    bmi DECIMAL(5, 2),  -- if height available
    body_shape VARCHAR(50),  -- "pear", "apple", "hourglass", "rectangle", etc. (ML-derived)
    
    -- Confidence scores (0-100)
    measurement_confidence JSONB,  -- {"chest_cm": 95, "waist_cm": 92, ...}
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_measurements_scan_id ON scan_measurements(scan_id);
```

**Notes:**
- Populated by 3D Scanning Lead after mesh processing
- Used for size recommendations and fit algorithms
- `measurement_confidence` tracks ML model certainty

---

### 4. GARMENTS

Central catalogue of available garments.

```sql
CREATE TABLE garments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identity
    sku VARCHAR(100) UNIQUE NOT NULL,  -- SKU or manufacturer code
    name VARCHAR(255) NOT NULL,
    brand_name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Classification
    category_id UUID REFERENCES garment_categories(id),
    subcategory VARCHAR(100),  -- "shirt", "jeans", "dress", etc.
    color VARCHAR(100),
    material_composition JSONB,  -- {"cotton": 95, "elastane": 5}
    material_care TEXT,  -- washing instructions
    
    -- Pricing
    retail_price_usd DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Retail integration
    retail_partner_id UUID REFERENCES retail_partners(id),
    external_product_url VARCHAR(500),  -- link to retailer's page
    external_product_id VARCHAR(100),  -- retailer's internal ID
    
    -- 3D Model info
    model_file_key VARCHAR(500) NOT NULL,  -- S3 path: "garments/{brand}/{sku}/model.fbx"
    texture_files JSONB,  -- {"diffuse": "...", "normal": "...", "roughness": "..."}
    model_format VARCHAR(20) DEFAULT 'fbx',  -- "fbx", "glTF", "obj"
    
    -- Metadata
    is_published BOOLEAN DEFAULT false,  -- Phase 1 = manual approval
    publish_date TIMESTAMP,
    
    -- Sizing info (stored separately in garment_sizes)
    is_unisex BOOLEAN DEFAULT false,
    has_variants BOOLEAN DEFAULT false,  -- color/size options
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_price CHECK (retail_price_usd > 0)
);

CREATE INDEX idx_garments_brand ON garments(brand_name);
CREATE INDEX idx_garments_category ON garments(category_id);
CREATE INDEX idx_garments_sku ON garments(sku);
CREATE INDEX idx_garments_published ON garments(is_published);
```

**Notes:**
- `sku` is unique identifier for inventory tracking
- `model_file_key` points to S3 (manufacturers upload via B2B portal)
- `external_product_url` is the "Buy Now" link
- `is_published` allows manual moderation before public visibility (Phase 1)

---

### 5. GARMENT_SIZES

Defines sizing options and fit parameters for each garment.

```sql
CREATE TABLE garment_sizes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    garment_id UUID NOT NULL REFERENCES garments(id) ON DELETE CASCADE,
    
    -- Size label
    size_label VARCHAR(50) NOT NULL,  -- "XS", "S", "M", "L", "XL", "28", "30", etc.
    size_order INT NOT NULL,  -- for sorting ("XS"=1, "S"=2, ..., "XL"=5)
    
    -- Fit parameters (used for virtual try-on scaling)
    chest_cm_min INT,
    chest_cm_max INT,
    waist_cm_min INT,
    waist_cm_max INT,
    hips_cm_min INT,
    hips_cm_max INT,
    
    -- Material properties
    fabric_stretch_factor DECIMAL(3, 2) DEFAULT 1.0,  -- 1.0 = no stretch, 1.2 = 20% stretch
    fabric_drape DECIMAL(3, 2) DEFAULT 1.0,  -- weight/flow parameter for cloth sim
    
    -- Availability
    stock_available INT DEFAULT 0,  -- for Phase 2 inventory integration
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_size_per_garment UNIQUE(garment_id, size_label)
);

CREATE INDEX idx_sizes_garment_id ON garment_sizes(garment_id);
```

**Notes:**
- `chest_cm_min/max` define the range this size fits
- `fabric_stretch_factor` used by Clothing Lead to adjust fit for stretchy materials
- `fabric_drape` fed to Blender cloth sim for realistic wrinkles

---

### 6. GARMENT_CATEGORIES

Taxonomy for browsing and filtering garments.

```sql
CREATE TABLE garment_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) UNIQUE,  -- for URL-safe names
    description TEXT,
    icon_url VARCHAR(500),
    
    -- Hierarchy
    parent_id UUID REFERENCES garment_categories(id),
    display_order INT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT no_circular_ref CHECK (id != parent_id)
);

CREATE INDEX idx_categories_parent ON garment_categories(parent_id);
```

**Examples:**
- Women's → Dresses, Tops, Bottoms, Outerwear, Accessories
- Men's → Shirts, Pants, Jackets, ...
- Unisex → ...

---

### 7. OUTFITS

User-created outfit combinations (saved looks).

```sql
CREATE TABLE outfits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scan_id UUID NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
    
    -- Outfit info
    name VARCHAR(255) NOT NULL,
    description TEXT,
    thumbnail_url VARCHAR(500),  -- render of the full outfit
    
    -- Visibility settings
    is_private BOOLEAN DEFAULT true,  -- "private" (me only), "friends" (Phase 2), "public"
    shared_with_users JSONB,  -- list of user IDs for future sharing
    
    -- Metadata
    occasion VARCHAR(100),  -- "casual", "business", "party", "sports", etc.
    season VARCHAR(50),  -- "spring", "summer", "fall", "winter"
    color_palette JSONB,  -- ["navy", "white", "gray"]
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_outfit_per_scan CHECK (scan_id IS NOT NULL)
);

CREATE INDEX idx_outfits_user_id ON outfits(user_id);
CREATE INDEX idx_outfits_scan_id ON outfits(scan_id);
```

**Notes:**
- Each outfit is tied to a specific body scan (user can have multiple scans)
- `thumbnail_url` is a pre-rendered image of the outfit (S3 or CDN)
- `occasion`, `season` help with discovery/recommendations (Phase 2)

---

### 8. OUTFIT_ITEMS

Maps garments to outfits (many-to-many with ordering).

```sql
CREATE TABLE outfit_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    outfit_id UUID NOT NULL REFERENCES outfits(id) ON DELETE CASCADE,
    garment_id UUID NOT NULL REFERENCES garments(id) ON DELETE RESTRICT,
    garment_size_id UUID NOT NULL REFERENCES garment_sizes(id),
    
    -- Order in outfit (for display)
    display_order INT NOT NULL,  -- 1 = base layer, 2 = mid layer, 3 = top, 4 = bottom, etc.
    
    -- Variants (for multi-color options)
    color_selected VARCHAR(100),
    variant_selected VARCHAR(100),  -- e.g., "checked pattern"
    
    -- Notes
    notes TEXT,  -- "perfect fit", "might be tight", etc.
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_garment_per_outfit UNIQUE(outfit_id, garment_id)
);

CREATE INDEX idx_outfit_items_outfit_id ON outfit_items(outfit_id);
CREATE INDEX idx_outfit_items_garment_id ON outfit_items(garment_id);
```

**Notes:**
- `display_order` determines layering in 3D render
- `color_selected`, `variant_selected` allow multi-variant garments (e.g., same dress in red, blue, black)

---

### 9. RETAIL_PARTNERS

Metadata for brand/retailer partnerships.

```sql
CREATE TABLE retail_partners (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identity
    name VARCHAR(255) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE,
    website_url VARCHAR(500),
    logo_url VARCHAR(500),
    
    -- API integration (Phase 2)
    api_endpoint VARCHAR(500),
    api_key_encrypted VARCHAR(500),  -- encrypted in DB, decrypted in app
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    contact_email VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_partners_active ON retail_partners(is_active);
```

**Notes:**
- Phase 1: Manual integration (just store URLs)
- Phase 2: Automated sync (API for inventory, pricing)
- `api_key_encrypted` only populated if partner has API

---

### 10. SAVED_FAVOURITE_GARMENTS

Allows users to bookmark garments for later.

```sql
CREATE TABLE saved_favourite_garments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    garment_id UUID NOT NULL REFERENCES garments(id) ON DELETE CASCADE,
    
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_favourite UNIQUE(user_id, garment_id)
);

CREATE INDEX idx_favourites_user_id ON saved_favourite_garments(user_id);
```

---

## Indices & Performance Tuning

### Query Patterns

```sql
-- Find user's recent scans
SELECT * FROM scans 
WHERE user_id = $1 AND deleted_at IS NULL 
ORDER BY created_at DESC LIMIT 10;

-- Search for garments by category
SELECT g.* FROM garments g 
JOIN garment_categories gc ON g.category_id = gc.id 
WHERE gc.slug = $1 AND g.is_published = true 
ORDER BY g.created_at DESC;

-- Get outfit items with garment details
SELECT oi.*, g.name, g.brand_name, gs.size_label 
FROM outfit_items oi 
JOIN garments g ON oi.garment_id = g.id 
JOIN garment_sizes gs ON oi.garment_size_id = gs.id 
WHERE oi.outfit_id = $1 
ORDER BY oi.display_order;

-- Find garment sizes that fit a body scan
SELECT gs.* FROM garment_sizes gs 
WHERE gs.garment_id = $1 
AND gs.chest_cm_min <= $2 AND gs.chest_cm_max >= $2 
AND gs.waist_cm_min <= $3 AND gs.waist_cm_max >= $3;
```

### Index Summary

| Table | Column | Type | Rationale |
|-------|--------|------|-----------|
| users | email | UNIQUE | Login lookups |
| scans | user_id | INDEX | User's scan history |
| scans | created_at | INDEX DESC | Sort by recent |
| scans | processing_status | INDEX | Filter by pipeline status |
| garments | category_id | INDEX | Browse by category |
| garments | sku | UNIQUE | Inventory tracking |
| garments | is_published | INDEX | Filter public garments |
| garment_sizes | garment_id | INDEX | Find sizes for a garment |
| outfits | user_id | INDEX | User's outfit library |
| outfits | scan_id | INDEX | Outfits for a specific scan |
| outfit_items | outfit_id | INDEX | Garments in an outfit |
| saved_favourite_garments | user_id | INDEX | User's bookmarks |

### Full-Text Search (Phase 2)

```sql
-- Add full-text search for garment names, brands, descriptions
ALTER TABLE garments ADD COLUMN search_text TSVECTOR;

CREATE INDEX idx_garments_search ON garments USING GIN(search_text);

-- Query: Find garments matching "blue cotton dress"
SELECT * FROM garments 
WHERE search_text @@ to_tsquery('english', 'blue & cotton & dress');
```

---

## Constraints & Data Integrity

### Soft Deletes
- `users.deleted_at IS NULL` filter for active users
- `scans.deleted_at IS NULL` filter for active scans
- Allows GDPR "right to be forgotten" while retaining historical data

### Foreign Key Behavior
- `REFERENCES users(id) ON DELETE CASCADE` → Deleting user deletes their scans/outfits
- `REFERENCES garments(id) ON DELETE RESTRICT` → Can't delete garment if in use (prevents data loss)

### Business Rules
- A user can have multiple scans
- A scan can be used in multiple outfits
- An outfit has exactly one scan (to maintain consistent fit)
- A garment can appear in many outfits (many-to-many via outfit_items)

---

## Migrations Strategy

### Migration Files (using Alembic)

```
migrations/
├── env.py
├── script.py.mako
└── versions/
    ├── 001_initial_schema.py
    ├── 002_add_garment_sizes.py
    ├── 003_add_outfit_tables.py
    └── ...
```

**Phase 1 Initial Migration:**
1. Create users, scans, scan_measurements
2. Create garments, garment_sizes, garment_categories, retail_partners
3. Create outfits, outfit_items, saved_favourite_garments
4. Add indexes
5. Seed initial categories

**Phase 2 Migrations (examples):**
- Add vector embedding columns for ML recommendations
- Add subscription/billing tables
- Add social sharing features

---

## Data Retention & Archival

### Retention Policy

| Data | Retention | Archive | Notes |
|------|-----------|---------|-------|
| Active users | Indefinite | N/A | Keep for service delivery |
| Deleted users | 30 days | Then purge | GDPR compliance |
| Scans (active) | 1 year | S3 Glacier | User can delete earlier |
| Scans (deleted) | 30 days | Then purge | Recovery window |
| Garment catalogue | Indefinite | N/A | Core product data |
| Outfits | Indefinite | N/A | User-generated content |
| Logs | 90 days | CloudWatch/ELK | Monitoring + compliance |

---

## Next Steps

1. **Implement SQLAlchemy ORM models** (mirror these tables)
2. **Write Alembic migrations**
3. **Add seed data** (categories, test garments)
4. **Integration tests** (CRUD operations for each table)
5. **Performance testing** (query optimization with realistic data volume)

---

**Status:** Ready for API Design  
**Last Updated:** 2026-03-17
