# Platform Team Quick Reference

## Project Overview

**Fashion Tech** — 3D body scanning + virtual try-on platform  
**Phase 1 MVP** — Week 1 complete, live demo target Week 8  
**Tech Stack:**
- **Frontend:** React 18 + Three.js + TypeScript + Tailwind CSS (Vite dev server)
- **Backend:** FastAPI + PostgreSQL + S3 (MinIO local, AWS prod)
- **CI/CD:** GitHub Actions (test + deploy pipelines)

---

## Quick Start

### Backend (5 min)

```bash
cd fashion-tech-backend
cp .env.example .env.local

# Start dependencies (PostgreSQL + MinIO)
docker-compose up -d

# Install + run server
poetry install
poetry run uvicorn src.app.main:app --reload
# Server: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Frontend (5 min)

```bash
cd workspace
npm install
npm run dev
# Dev server: http://localhost:5173
```

---

## Key Endpoints (Week 1 — Stubs)

### Auth
```
POST   /v1/auth/register
POST   /v1/auth/login
POST   /v1/auth/logout
```

### Users
```
GET    /v1/users/me
```

### Scans
```
POST   /v1/scans/upload-initiate
GET    /v1/scans
GET    /v1/scans/{scan_id}
DELETE /v1/scans/{scan_id}
```

### Garments
```
GET    /v1/garments
GET    /v1/garments/categories
GET    /v1/garments/{garment_id}
```

### Outfits
```
POST   /v1/outfits
GET    /v1/outfits
GET    /v1/outfits/{outfit_id}
DELETE /v1/outfits/{outfit_id}
```

### Health
```
GET    /health
GET    /health/ready
```

---

## Database Tables (PostgreSQL)

1. **users** — User accounts + auth
2. **session_tokens** — JWT refresh token family
3. **scans** — 3D body scans
4. **scan_measurements** — Body measurements (chest, waist, hips, etc.)
5. **garments** — Clothing items (SKU, name, model file)
6. **garment_sizes** — Size variants (S, M, L, etc.)
7. **garment_categories** — Taxonomy (Tops, Bottoms, etc.)
8. **retail_partners** — Brands (Zara, H&M, etc.)
9. **outfits** — Saved combinations
10. **outfit_items** — Individual garments in outfit
11. **saved_favourite_garments** — Bookmarked items

**Migration:** Run `alembic upgrade head` (Week 2)

---

## File Structure

```
fashion-tech/
├── backend/                  # FastAPI + PostgreSQL
│   ├── src/app/
│   │   ├── models/          # SQLAlchemy ORM
│   │   ├── routers/         # API endpoints
│   │   ├── services/        # Business logic (S3, auth)
│   │   └── schemas/         # Pydantic validation
│   ├── docker-compose.yml   # PostgreSQL + MinIO
│   └── README.md
└── workspace/               # React + Three.js
    ├── src/
    │   ├── components/      # React components (three, outfit-builder, ui)
    │   ├── stores/          # Zustand state (auth, outfit, ui)
    │   ├── api/             # Axios client + services
    │   └── hooks/           # Custom hooks (useAuth, useOutfit, etc.)
    └── package.json
```

---

## Component Architecture (Frontend)

```
App
 ├── Layout
 │   ├── Header (navigation)
 │   └── Sidebar (filters)
 └── OutfitBuilderPage
     ├── ModelViewer (Viewport3D + SceneManager)
     │   └── Viewport3D (Three.js canvas)
     │       └── SceneManager (60fps render loop)
     └── GarmentBrowser (grid UI)
         └── GarmentCard (thumbnail)

State:
 ├── authStore (Zustand)  → user, tokens, login/logout
 ├── outfitStore (Zustand) → current outfit, selected garments
 └── uiStore (Zustand)     → sidebar, modals, filters

API:
 ├── api/client.ts (Axios)
 ├── api/auth.ts
 ├── api/scans.ts
 ├── api/garments.ts
 └── api/outfits.ts
```

---

## Model Architecture (Backend)

```
User (1 ──→ N) Scan
  │
  ├─→ SessionToken (JWT tracking)
  ├─→ Outfit (1 ──→ N OutfitItem)
  └─→ SavedFavouriteGarment

Scan
  ├─→ ScanMeasurement (1 ──→ 1)
  └─→ Outfit (1 ──→ N)

Garment (1 ──→ N GarmentSize)
  ├─→ GarmentCategory (1 ──→ N)
  ├─→ RetailPartner (1 ──→ N)
  └─→ OutfitItem (1 ──→ N)

OutfitItem
  ├─→ Outfit (N ──→ 1)
  └─→ Garment (N ──→ 1)
```

---

## Three.js SceneManager (240 lines)

**Location:** `src/components/three/SceneManager.ts`

**Features:**
- ✅ Professional 3-point lighting (key, fill, rim)
- ✅ OrbitControls (rotate, zoom, pan)
- ✅ Model loading + caching
- ✅ Animation mixer for skeletal animation
- ✅ Shadow mapping (PCF soft, 2048x2048)
- ✅ 60fps render loop (requestAnimationFrame)
- ✅ Resize observer (responsive canvas)
- ✅ Snapshot export (PNG/JPEG)

**Key Methods:**
```typescript
const manager = new SceneManager(options);

// Load models
await manager.loadModel('avatar', 'path/to/model.glb');
await manager.loadModel('garment', 'path/to/garment.glb');

// Remove model
manager.removeModel('garment');

// Camera control
manager.resetCamera();
manager.focusOnModel('avatar');
manager.setCameraState({ position: ..., target: ... });

// Render
manager.startRenderLoop();
manager.stopRenderLoop();
manager.dispose();
```

---

## Zustand Stores

### authStore
```typescript
const { user, tokens, login, logout, setUser } = useAuthStore();
```

### outfitStore
```typescript
const { currentOutfit, addGarment, removeGarment, saveOutfit } = useOutfitStore();
```

### uiStore
```typescript
const { sidebarOpen, toggleSidebar, modals, openModal } = useUiStore();
```

---

## Environment Variables

### Backend (.env.local)

```
DATABASE_URL=postgresql://developer:dev_password_123@localhost:5432/fashion_tech_dev
JWT_SECRET_KEY=<generate with: openssl rand -hex 32>
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
S3_ENDPOINT_URL=http://localhost:9000  # MinIO local
S3_BUCKET=fashion-tech-storage
AWS_REGION=us-east-1
DEBUG=True
```

### Frontend (.env.local)

```
VITE_API_BASE_URL=http://localhost:8000/v1
VITE_APP_TITLE=Fashion Tech
VITE_ENABLE_ANIMATIONS=true
```

---

## Development Workflow

1. **Branch strategy:** `main` (stable) → `develop` (integration) → feature branches
2. **Commit:** Atomic, descriptive messages
3. **PR:** Requires review + CI passing (tests + lint)
4. **Deploy:** GitHub Actions → staging → production

---

## Performance Targets

| Metric | Target | Strategy |
|--------|--------|----------|
| Render FPS | 60 fps | SceneManager + OrbitControls |
| Garment swap | <200 ms | Model cache + preload |
| Page load | <3s | Code splitting + lazy load |
| Bundle size | <500 KB | Tree shaking + Vite minify |
| API response | <100 ms | Database indexes + caching |

---

## Troubleshooting

### Backend won't start
```bash
# Check ports
lsof -i :8000
lsof -i :5432

# Check Docker
docker-compose ps
docker-compose logs postgres
```

### Frontend errors
```bash
# Clear cache
rm -rf node_modules/.vite
npm run dev -- --force

# Check React devtools
# Console should have no errors
```

### Database issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

---

## Week 1-2 Handoff

### For Backend Engineers
- [ ] Run Alembic migration: `alembic upgrade head`
- [ ] Implement endpoint business logic (replace stubs)
- [ ] Add error handling + validation
- [ ] Write unit tests

### For Frontend Engineers
- [ ] Integrate API client to backend
- [ ] Implement load states + error boundaries
- [ ] Test with real glTF models
- [ ] Performance profiling (Lighthouse)

### For DevOps
- [ ] Setup GitHub Actions CI/CD
- [ ] Create staging + production environments
- [ ] Configure AWS (RDS PostgreSQL, S3 bucket, EC2)
- [ ] SSL certificates + domain setup

---

## Resources

- **Three.js Documentation:** https://threejs.org/docs/
- **React Documentation:** https://react.dev/
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **PostgreSQL Documentation:** https://www.postgresql.org/docs/
- **Zustand Documentation:** https://github.com/pmndrs/zustand

---

**Last Updated:** 2026-03-22  
**Status:** Week 1 Complete  
**Next Review:** Week 2 Integration (2026-03-29)
