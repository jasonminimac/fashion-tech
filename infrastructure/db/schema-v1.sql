-- Fashion Tech Platform — DB Schema v1
-- PostgreSQL DDL
-- Generated: 2026-03-18

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─────────────────────────────────────────
-- 1. users
-- ─────────────────────────────────────────
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           TEXT NOT NULL UNIQUE,
    display_name    TEXT,
    password_hash   TEXT,
    role            TEXT NOT NULL DEFAULT 'consumer' CHECK (role IN ('consumer', 'retailer', 'admin')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users (email);

-- ─────────────────────────────────────────
-- 2. body_scans
-- ─────────────────────────────────────────
CREATE TABLE body_scans (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    status          TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'complete', 'failed')),
    s3_key          TEXT,                        -- path to raw scan data in S3
    glb_s3_key      TEXT,                        -- path to processed .glb in S3
    scan_metadata   JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_body_scans_user_id ON body_scans (user_id);
CREATE INDEX idx_body_scans_status  ON body_scans (status);

-- ─────────────────────────────────────────
-- 3. garments
-- ─────────────────────────────────────────
CREATE TABLE garments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    retailer_id     UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    brand           TEXT,
    category        TEXT,                        -- e.g. 'top', 'bottom', 'dress', 'outerwear'
    sku             TEXT,
    metadata        JSONB,
    is_published    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_garments_retailer_id ON garments (retailer_id);
CREATE INDEX idx_garments_category    ON garments (category);
CREATE INDEX idx_garments_is_published ON garments (is_published);

-- ─────────────────────────────────────────
-- 4. garment_assets
-- ─────────────────────────────────────────
CREATE TABLE garment_assets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    garment_id      UUID NOT NULL REFERENCES garments (id) ON DELETE CASCADE,
    asset_type      TEXT NOT NULL CHECK (asset_type IN ('glb', 'thumbnail', 'texture', 'pattern', 'other')),
    s3_key          TEXT NOT NULL,
    content_type    TEXT,                        -- e.g. 'model/gltf-binary', 'image/png'
    file_size_bytes BIGINT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_garment_assets_garment_id  ON garment_assets (garment_id);
CREATE INDEX idx_garment_assets_asset_type  ON garment_assets (asset_type);

-- ─────────────────────────────────────────
-- 5. fit_profiles
-- ─────────────────────────────────────────
CREATE TABLE fit_profiles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    scan_id         UUID REFERENCES body_scans (id) ON DELETE SET NULL,
    measurements    JSONB NOT NULL DEFAULT '{}',  -- height, chest, waist, hips, inseam, etc.
    fit_preferences JSONB NOT NULL DEFAULT '{}',  -- preferred fit: slim, regular, relaxed
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_fit_profiles_user_id ON fit_profiles (user_id);
CREATE INDEX idx_fit_profiles_scan_id ON fit_profiles (scan_id);

-- ─────────────────────────────────────────
-- 6. outfits
-- ─────────────────────────────────────────
CREATE TABLE outfits (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    name            TEXT,
    garment_ids     UUID[] NOT NULL DEFAULT '{}',  -- ordered list of garment IDs in the outfit
    is_public       BOOLEAN NOT NULL DEFAULT FALSE,
    metadata        JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_outfits_user_id   ON outfits (user_id);
CREATE INDEX idx_outfits_is_public ON outfits (is_public);

-- ─────────────────────────────────────────
-- 7. retailer_access
-- ─────────────────────────────────────────
CREATE TABLE retailer_access (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    retailer_id     UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    client_id       TEXT NOT NULL UNIQUE,
    client_secret   TEXT NOT NULL,               -- hashed
    scopes          TEXT[] NOT NULL DEFAULT '{"garments:read","garments:write"}',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_used_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_retailer_access_retailer_id ON retailer_access (retailer_id);
CREATE INDEX idx_retailer_access_client_id   ON retailer_access (client_id);
CREATE INDEX idx_retailer_access_is_active   ON retailer_access (is_active);

-- ─────────────────────────────────────────
-- auto-update updated_at via trigger
-- ─────────────────────────────────────────
CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
DECLARE
  tbl TEXT;
BEGIN
  FOREACH tbl IN ARRAY ARRAY[
    'users', 'body_scans', 'garments', 'garment_assets',
    'fit_profiles', 'outfits', 'retailer_access'
  ]
  LOOP
    EXECUTE format(
      'CREATE TRIGGER set_updated_at
       BEFORE UPDATE ON %I
       FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();',
      tbl
    );
  END LOOP;
END;
$$;
