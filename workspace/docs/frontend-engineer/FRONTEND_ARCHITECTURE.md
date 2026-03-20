# Frontend Architecture — Fashion Tech MVP

**Author:** Frontend Engineer  
**Date:** 2026-03-17  
**Phase:** MVP (Phase 1)  
**Status:** Design Document

---

## Overview

This document outlines the technical architecture for the Fashion Tech web-based 3D viewer and outfit builder. The frontend is a **React-based single-page application (SPA)** that:

1. Loads animated 3D body models (glTF format, exported from Blender)
2. Renders them in a high-performance 3D viewport
3. Provides UI controls for animation playback and garment selection
4. Allows users to build outfits (add/remove/swap garments) and save them
5. Displays fit/sizing information and retail partner links

---

## Technology Stack

### Core Framework
- **React 18+** — Component-based UI, hooks for state management
- **TypeScript** — Type safety and better developer experience
- **Vite** — Fast build tool and dev server (faster than Create React App)

### 3D Rendering
- **Three.js (Primary)** — Mature WebGL 3D library, excellent glTF support, large ecosystem
- **drei (Optional)** — React-friendly Three.js utilities (if using react-three-fiber)

**Decision Rationale:**
- Three.js is battle-tested for fashion/retail 3D experiences (Gucci, Nike, Adidas all use it)
- glTF support is first-class; Blender exports glTF natively
- Performance is excellent (60fps achievable on mid-range hardware)
- Large community means faster debugging and more reusable components

### UI & Styling
- **React** (built-in) — Component structure
- **Tailwind CSS** — Utility-first CSS, responsive design, fashion-forward aesthetics
- **shadcn/ui** — Pre-built, accessible component library (buttons, modals, sidebars)
- **framer-motion** — Smooth animations and transitions

### State Management
- **React Context + useReducer** — For global app state (user scans, outfit data, animations)
- **TanStack Query (React Query)** — For server state (garment catalogue, outfit history)

**Decision Rationale:**
- Context is sufficient for MVP; no need for Redux complexity
- React Query handles caching and synchronization with the backend efficiently

### HTTP & API
- **axios** or **fetch** — Simple HTTP requests
- **API client abstraction** — Typed API calls (TypeScript)

---

## Architecture Layers

### 1. **Presentation Layer (UI Components)**

```
┌─────────────────────────────────────────────────┐
│           App Shell / Layout                     │
├─────────────────────────────────────────────────┤
│  Header (logo, user menu)  │  Main Content      │
│  Navigation               │  Viewport (3D) +    │
│                            │  Animation Controls │
├─────────────────────────────────────────────────┤
│  Sidebar (Outfit Builder)                       │
│  - Garment List                                 │
│  - Selected Outfit                              │
│  - Fit/Size Info                                │
│  - Save/Share Controls                          │
└─────────────────────────────────────────────────┘
```

**Key Components:**
- `App` — Root component, layout orchestration
- `Viewport3D` — Canvas-based 3D viewer (React wrapper around Three.js)
- `AnimationControls` — Play/pause/speed controls
- `GarmentSelector` — Browse and select garments
- `OutfitBuilder` — Current outfit display, swap/remove controls
- `SizeChart` — Fit information sidebar

### 2. **3D Layer (Three.js Integration)**

```
┌─────────────────────────────────────────┐
│  THREE Scene Manager                    │
├─────────────────────────────────────────┤
│  ├─ Scene                               │
│  ├─ Camera (Orthographic for fashion)   │
│  ├─ Lighting (3-point setup)            │
│  ├─ Body Model (glTF, animated)         │
│  ├─ Garments (glTF, positioned)         │
│  └─ Controls (OrbitControls)            │
└─────────────────────────────────────────┘
```

**Responsibilities:**
- Load and parse glTF models
- Manage Three.js scene hierarchy
- Handle animation playback (mixers, actions)
- Handle camera and viewport interactions
- Render garment swaps (add/remove/update materials)

### 3. **Data/State Layer**

```
React Context / useReducer
├─ User State
│  ├─ currentScan (body model)
│  ├─ loadedAnimations (walk, run, idle)
│  └─ animationSpeed
├─ Outfit State
│  ├─ selectedGarments (array of garment IDs + sizes)
│  ├─ currentOutfitName
│  └─ isSaved
└─ UI State
    ├─ viewMode (front/back/side/360)
    ├─ animationPlaying
    └─ selectedGarmentIndex
```

**Backed by:**
- React Query for server data (garment catalogue, user outfits)
- LocalStorage for temporary outfit drafts

### 4. **API Integration Layer**

**Endpoints (from Backend Engineer):**
```
GET  /api/garments                  — List all garments
GET  /api/garments/:id              — Get garment details
GET  /api/garments/:id/model        — Download glTF model
GET  /api/users/:userId/scans       — List user's body scans
GET  /api/users/:userId/outfits     — List saved outfits
POST /api/users/:userId/outfits     — Save new outfit
PUT  /api/users/:userId/outfits/:id — Update outfit
GET  /api/size-chart/:garmentId     — Get fit information
```

---

## Component Hierarchy

```
App
├── Header
│   ├── Logo / Branding
│   ├── User Menu (Profile, Logout)
│   └── Help / Settings
├── MainContent
│   ├── Viewport3D (Canvas)
│   │   └── Three.js Scene
│   │       ├── Body Model
│   │       ├── Garments
│   │       └── Lights/Camera
│   └── AnimationControls
│       ├── PlayButton
│       ├── AnimationSelector (walk/run/idle)
│       ├── SpeedSlider
│       └── RotationControls
└── Sidebar
    ├── GarmentSelector
    │   ├── SearchBar
    │   ├── FilterTabs (category, brand, color)
    │   └── GarmentGrid
    │       └── GarmentCard
    │           ├── Thumbnail
    │           ├── Name / Brand
    │           ├── Price
    │           └── AddButton
    ├── OutfitBuilder
    │   ├── OutfitName
    │   ├── SelectedGarmentsList
    │   │   └── GarmentItem
    │   │       ├── Preview
    │   │       ├── Name / Size
    │   │       ├── SwapButton
    │   │       └── RemoveButton
    │   ├── SizeChart (for selected garment)
    │   └── SaveOutfitButton
    └── RetailLinks
        ├── "Buy Now" buttons (per garment)
        └── Size guide links
```

---

## Data Flow

### Initial Load

```
1. User loads app
   ↓
2. Fetch user's latest scan (API: GET /api/users/:userId/scans)
   ↓
3. Load body model (glTF) into Three.js scene
   ↓
4. Load animation library (walk, run, idle cycles)
   ↓
5. Fetch garment catalogue (API: GET /api/garments)
   ↓
6. Render UI, ready for interaction
```

### User Selects Garment

```
1. Click garment in GarmentSelector
   ↓
2. Fetch garment model (API: GET /api/garments/:id/model)
   ↓
3. Load glTF into Three.js scene
   ↓
4. Position garment relative to body (pre-calculated offsets from Blender)
   ↓
5. Add to OutfitBuilder list
   ↓
6. Fetch fit/size info (API: GET /api/size-chart/:garmentId)
   ↓
7. Display in SizeChart sidebar
```

### User Saves Outfit

```
1. Click "Save Outfit" button
   ↓
2. Prompt for outfit name (modal)
   ↓
3. Collect outfit data:
   - bodyScalId
   - garmentIds + sizes selected
   - animation preferences
   ↓
4. POST to API (POST /api/users/:userId/outfits)
   ↓
5. Receive outfitId from backend
   ↓
6. Update UI (show "Outfit Saved" + share/edit options)
```

---

## Performance Targets

| Metric | Target | Strategy |
|--------|--------|----------|
| **Initial Page Load** | <3s | Code-splitting, lazy-load garments, cache glTF models |
| **3D Viewport FPS** | 60 fps | Optimize lighting, use instancing for multiple garments, lower poly if needed |
| **Garment Swap Time** | <200ms | Preload garment models in background, use object pooling for scene updates |
| **Animation Playback** | Smooth, no jank | Use requestAnimationFrame, avoid main-thread blocking |
| **UI Responsiveness** | <100ms interaction latency | React optimization (memo, useCallback), efficient state updates |

### Optimization Strategies

1. **Model Optimization**
   - Use compressed glTF (glb format)
   - LOD (Level of Detail) models for distant views
   - Draco compression for geometry

2. **Scene Optimization**
   - Reuse materials and geometries
   - Use Three.js frustum culling (built-in)
   - Batch similar draw calls
   - Consider instancing if multiple identical garments

3. **Code Splitting**
   - Lazy-load garment selector
   - Lazy-load outfit history
   - Separate 3D library code from UI

4. **Caching**
   - Cache loaded glTF models in memory
   - Use React Query for HTTP caching
   - LocalStorage for draft outfits

5. **Asset Delivery**
   - CDN for model hosting
   - Appropriate texture resolution (2K max for fashion)
   - WebP textures with fallback to PNG

---

## API Contract

### Models

**User Scan:**
```typescript
interface UserScan {
  id: string
  userId: string
  name: string
  created: ISO8601
  modelUrl: string // glTF/glb URL
  height: number // cm
  measurements?: {
    chest: number
    waist: number
    hips: number
  }
}
```

**Garment:**
```typescript
interface Garment {
  id: string
  name: string
  brand: string
  category: string // "dress", "shirt", "pants", etc.
  color: string[]
  price: number
  currency: string
  sizes: string[] // ["XS", "S", "M", "L", "XL"]
  modelUrl: string // glTF/glb
  thumbnailUrl: string
  fitData: {
    sizeS: { bust: number, length: number, ... }
    sizeM: { ... }
    // ...
  }
  retailUrl: string
}
```

**Outfit:**
```typescript
interface Outfit {
  id: string
  userId: string
  scanId: string
  name: string
  garments: {
    garmentId: string
    size: string
    color: string
  }[]
  created: ISO8601
  updated: ISO8601
}
```

---

## Error Handling

### Network Errors
- Graceful fallback if garment fails to load
- Retry with exponential backoff
- Show user-friendly error messages

### 3D Rendering Errors
- Catch glTF parsing errors, show feedback
- Handle missing textures gracefully
- Provide fallback materials

### State Consistency
- Validate outfit data before saving
- Handle concurrent updates (if multiple tabs)
- Clear invalid cache on errors

---

## Security & Privacy

1. **Authentication**
   - User scans are tied to user account
   - API calls include auth token (JWT or session cookie)

2. **Data Privacy**
   - Scans are stored securely on backend (encrypted at rest)
   - GDPR compliance (user can export/delete their data)

3. **Content Security**
   - glTF models validated on load (no arbitrary code execution)
   - API responses validated against TypeScript types

---

## Browser Support

- **Modern browsers:** Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Desktop focus (MVP):** Windows, macOS, Linux
- **Mobile (Phase 2):** Responsive design ready, but touch controls TBD

---

## Development Workflow

### Project Structure

```
fashion-tech-frontend/
├── public/
│   ├── index.html
│   └── assets/
├── src/
│   ├── components/
│   │   ├── Viewport3D.tsx
│   │   ├── AnimationControls.tsx
│   │   ├── GarmentSelector.tsx
│   │   ├── OutfitBuilder.tsx
│   │   └── common/
│   │       ├── Header.tsx
│   │       └── Sidebar.tsx
│   ├── scenes/
│   │   ├── SceneManager.ts  (Three.js orchestration)
│   │   ├── ModelLoader.ts
│   │   └── AnimationController.ts
│   ├── hooks/
│   │   ├── useScene.ts
│   │   ├── useOutfit.ts
│   │   └── useGarments.ts
│   ├── context/
│   │   ├── OutfitContext.tsx
│   │   └── AnimationContext.tsx
│   ├── api/
│   │   ├── client.ts
│   │   ├── garments.ts
│   │   ├── outfits.ts
│   │   └── scans.ts
│   ├── types/
│   │   └── index.ts
│   ├── utils/
│   │   ├── three-helpers.ts
│   │   ├── api-helpers.ts
│   │   └── performance.ts
│   └── App.tsx
├── package.json
├── tsconfig.json
└── vite.config.ts
```

### Build & Deploy

- **Dev:** `npm run dev` (Vite hot-reload)
- **Build:** `npm run build` (optimized production bundle)
- **Deploy:** Vercel, Netlify, or AWS CloudFront (static hosting + API backend)

---

## Phase 1 Milestones

1. **Week 1-2:** Basic React + Vite setup, Three.js integration, glTF loader working
2. **Week 3-4:** Animation playback (mixer, play/pause, speed control)
3. **Week 5-6:** Garment loading and positioning in scene
4. **Week 6-7:** Outfit builder UI, save functionality, sizing info
5. **Week 8:** Polish, performance optimization, UX refinement

---

## Dependencies (npm packages)

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "typescript": "^5.0.0",
  "three": "^r155",
  "framer-motion": "^10.0.0",
  "tailwindcss": "^3.0.0",
  "shadcn-ui": "^0.4.0",
  "@tanstack/react-query": "^5.0.0",
  "axios": "^1.6.0",
  "zustand": "^4.0.0" (optional, simpler than Context)
}
```

---

## Known Unknowns / Decisions Pending

1. **Orbit Controls vs. Zoom/Pan?** — Need UX design input
   - OrbitControls (rotate body) feels more fashion-like
   - Simple zoom/pan might be clearer for outfit focus
   - **Decision:** Start with orbit controls, gather user feedback

2. **Material Accuracy** — How photorealistic do garments need to be?
   - MVP: Solid colors + basic normal maps
   - Phase 2: PBR (physically-based rendering) for fabrics
   - **Decision:** Start simple, iterate on feedback

3. **Mobile Support Timeline** — When does responsive UI matter?
   - MVP targets desktop
   - Design for responsiveness, implement mobile gestures in Phase 2
   - **Decision:** Write mobile-friendly code, test on iPhone, but don't optimize yet

4. **Garment Physics Preview** — Static draping vs. real-time simulation?
   - MVP: Static mesh (pre-draped in Blender)
   - Phase 2: Real-time cloth sim
   - **Decision:** Start with static, keep architecture extensible

---

## Next Steps

1. Set up repository and build infrastructure (Vite + TypeScript)
2. Create SceneManager (Three.js wrapper) and test glTF loading
3. Build Viewport3D React component wrapping Three.js canvas
4. Implement animation playback controls
5. Begin UI component library (buttons, selectors, modals)

---

**Document Version:** 1.0  
**Last Updated:** 2026-03-17
