# Component Structure & Data Flow — Fashion Tech Frontend

**Author:** Frontend Engineer  
**Date:** 2026-03-17  
**Phase:** MVP (Phase 1)  
**Status:** Architecture Reference

---

## Component Hierarchy

```
App (Root)
├── Header
│   ├── Logo
│   ├── OutfitNameDisplay
│   └── UserMenu
│       ├── ProfileButton
│       ├── SettingsButton
│       └── LogoutButton
│
├── MainContent
│   ├── Viewport3D (Canvas-based 3D viewer)
│   │   └── SceneManager (Three.js orchestration)
│   │       ├── BodyModel (animated glTF)
│   │       ├── GarmentModels (array of glTF)
│   │       ├── Lights (key + fill + back + ambient)
│   │       ├── Camera (orthographic)
│   │       └── OrbitControls (rotation + zoom)
│   │
│   └── AnimationControls (below viewport)
│       ├── AnimationSelector (dropdown: walk, run, idle)
│       ├── PlayPauseButton
│       ├── SpeedSlider (0.5x - 2.0x)
│       ├── RotationToggle (auto-rotate on/off)
│       └── ViewModeButtons (front, back, 360)
│
└── Sidebar (right panel)
    ├── GarmentSelector
    │   ├── SearchInput
    │   ├── CategoryFilterTabs
    │   ├── ColorFilterButtons
    │   └── GarmentGrid
    │       └── GarmentCard[] (with Add/Remove buttons)
    │
    ├── OutfitBuilder
    │   ├── OutfitNameInput
    │   ├── SelectedGarmentsList
    │   │   └── OutfitItem[] (with Swap/Remove buttons)
    │   └── SaveOutfitButton
    │
    ├── SizeChart
    │   └── SizeChartItem[] (expandable per garment)
    │       ├── SizeTable (XS, S, M, L, XL)
    │       ├── UserFitAssessment
    │       └── BuyNowLink
    │
    └── SaveOutfitModal (overlay)
        ├── OutfitNameInput
        └── SaveButton / CancelButton
```

---

## File Structure

```
src/
├── components/
│   ├── App.tsx                          (root component, layout)
│   ├── Header.tsx                       (top bar)
│   ├── MainContent.tsx                  (left side: viewport + animation controls)
│   ├── Sidebar.tsx                      (right side: garment selector + outfit builder)
│   ├── Viewport3D.tsx                   (canvas wrapper, React interface)
│   ├── AnimationControls.tsx            (play/pause/speed controls)
│   ├── GarmentSelector/
│   │   ├── GarmentSelector.tsx          (parent component)
│   │   ├── GarmentCard.tsx              (individual garment preview)
│   │   ├── SearchBar.tsx                (search input)
│   │   ├── CategoryFilter.tsx           (filter tabs)
│   │   └── ColorFilter.tsx              (color button grid)
│   ├── OutfitBuilder/
│   │   ├── OutfitBuilder.tsx            (parent component)
│   │   ├── OutfitItem.tsx               (individual selected garment)
│   │   ├── SaveOutfitModal.tsx          (name & save dialog)
│   │   └── OutfitNameInput.tsx          (editable outfit name)
│   ├── SizeChart/
│   │   ├── SizeChart.tsx                (parent component)
│   │   ├── SizeChartItem.tsx            (expandable per-garment details)
│   │   └── SizeTable.tsx                (tabular measurements)
│   └── common/
│       ├── Button.tsx                   (reusable button)
│       ├── Modal.tsx                    (reusable modal)
│       └── Toast.tsx                    (notifications)
│
├── scenes/
│   ├── SceneManager.ts                  (Three.js core logic)
│   ├── ModelLoader.ts                   (glTF loading + caching)
│   ├── AnimationController.ts           (animation mixer management)
│   └── LightingSetup.ts                 (three-point lighting)
│
├── hooks/
│   ├── useScene.ts                      (SceneManager instance)
│   ├── useOutfit.ts                     (Outfit context hook)
│   ├── useGarments.ts                   (Garment fetching / caching)
│   ├── useAnimation.ts                  (Animation state)
│   ├── useDimensions.ts                 (Window resize tracking)
│   └── useAsync.ts                      (async data loading)
│
├── context/
│   ├── OutfitContext.tsx                (outfit state + actions)
│   ├── AnimationContext.tsx             (animation state)
│   └── AuthContext.tsx                  (user / auth state)
│
├── api/
│   ├── client.ts                        (axios instance + auth)
│   ├── garments.ts                      (garment endpoints)
│   ├── outfits.ts                       (outfit endpoints)
│   ├── scans.ts                         (body scan endpoints)
│   └── types.ts                         (API response types)
│
├── types/
│   ├── index.ts                         (shared TypeScript types)
│   ├── garment.ts
│   ├── outfit.ts
│   └── scan.ts
│
├── utils/
│   ├── three-helpers.ts                 (Three.js utilities)
│   ├── api-helpers.ts                   (API response parsing)
│   ├── performance.ts                   (FPS monitor, timing)
│   └── constants.ts                     (categories, colors, etc.)
│
├── styles/
│   ├── globals.css                      (Tailwind + globals)
│   ├── animations.css                   (custom animations)
│   └── theme.css                        (color variables)
│
├── App.tsx                              (entry point)
└── main.tsx                             (DOM render)
```

---

## State Architecture

### Global State (Context)

#### OutfitContext
```typescript
{
  // Data
  selectedGarments: Garment[]
  outfitName: string
  currentScanId: string
  isSaved: boolean
  outfitId?: string
  
  // Actions
  addGarment: (garment: Garment) => void
  removeGarment: (garmentId: string) => void
  swapGarment: (old: string, new: Garment) => void
  setOutfitName: (name: string) => void
  saveOutfit: () => Promise<void>
  loadOutfit: (id: string) => Promise<void>
  clearOutfit: () => void
}
```

#### AnimationContext
```typescript
{
  // Data
  currentAnimation: 'walk' | 'run' | 'idle'
  isPlaying: boolean
  speed: number (0.5 - 2.0)
  autoRotate: boolean
  viewMode: 'front' | 'back' | '360'
  
  // Actions
  playAnimation: (type: string) => void
  pauseAnimation: () => void
  setSpeed: (speed: number) => void
  setAutoRotate: (enabled: boolean) => void
  setViewMode: (mode: string) => void
}
```

#### AuthContext
```typescript
{
  // Data
  userId: string | null
  isLoggedIn: boolean
  userProfile?: UserProfile
  
  // Actions
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  updateProfile: (profile: UserProfile) => Promise<void>
}
```

### Local Component State

- **GarmentSelector:** searchQuery, selectedCategory, selectedColor
- **SizeChart:** expandedGarmentId
- **SaveOutfitModal:** outfitNameInput, isLoading
- **Viewport3D:** (none, all managed by SceneManager)

### Server State (React Query)

```typescript
// Queries
useQuery(['garments'], fetchGarments)
useQuery(['garments', categoryId], fetchGarmentsByCategory)
useQuery(['outfits', userId], fetchUserOutfits)
useQuery(['outfits', outfitId], fetchOutfitDetails)
useQuery(['scans', userId], fetchUserScans)

// Mutations
useMutation(saveOutfit)
useMutation(deleteOutfit)
useMutation(updateOutfit)
```

---

## Data Flow Diagrams

### 1. User Loads App

```
App Mounts
  ├─ AuthContext: Check login (localStorage or API)
  │  └─ If logged in, load userProfile + currentScan
  ├─ OutfitContext: Initialize empty outfit
  ├─ AnimationContext: Initialize defaults
  ├─ Viewport3D mounts
  │  └─ SceneManager: Create Three.js scene
  │     ├─ Load body model (currentScan.modelUrl)
  │     └─ Load animation clips
  └─ GarmentSelector: Fetch garments (React Query)
     └─ Display garment grid (filtered)
```

### 2. User Adds Garment to Outfit

```
[Click "Add" on GarmentCard]
  │
  └─→ onGarmentAdd(garment)
       └─→ OutfitContext: addGarment()
           ├─ Update selectedGarments state
           ├─ Set isSaved = false
           └─ Trigger OutfitBuilder re-render
  
  // (Automatic via props)
  └─→ OutfitBuilder receives new selectedGarments
       ├─ Re-render with new item
       └─ (optional) Show toast "Added!"
  
  // (Automatic via Viewport3D)
  └─→ Viewport3D receives updated selectedGarments
       └─→ SceneManager.updateGarments()
           ├─ Load garment model (async)
           ├─ Position on body
           ├─ Add to scene
           └─ Render (next frame)
  
  // (Automatic via OutfitItem actions)
  └─→ SizeChart auto-updates
       └─ Fetch fit data (React Query)
           └─ Display size table + buy link
```

### 3. User Saves Outfit

```
[Click "Save Outfit"]
  │
  └─→ Show SaveOutfitModal
       ├─ User enters outfit name
       └─ [Click "Save"]
           │
           └─→ OutfitContext: saveOutfit()
                ├─ POST /api/users/{userId}/outfits
                │  ├─ body: {
                │  │   name: "name",
                │  │   scanId: "...",
                │  │   garmentIds: [...],
                │  │ }
                │  └─ response: { id: "...", ... }
                ├─ Update context (isSaved = true, outfitId)
                ├─ Close modal
                └─ Show toast "Outfit saved!"
                
  // (Optional)
  └─→ React Query: invalidate outfits
       └─ Refetch user's outfit history
           └─ Update localStorage cache
```

### 4. User Swaps Animation

```
[Click AnimationSelector dropdown, choose "Run"]
  │
  └─→ onAnimationChange('run')
       └─→ AnimationContext: setAnimation('run')
           ├─ Update currentAnimation state
           └─ (no API call)
  
  // (Automatic via AnimationContext)
  └─→ AnimationControls re-render (UI update)
  
  // (Automatic via Viewport3D + SceneManager)
  └─→ Viewport3D receives animationState change
       └─→ SceneManager.playAnimation('run')
           ├─ Stop current action
           ├─ Get new action from mixer
           ├─ Set speed, loop mode
           └─ Play (updates each frame)
           
  // Result: Body in viewport immediately starts running
```

### 5. User Filters Garments

```
[Type in SearchBar or Click CategoryFilter]
  │
  └─→ setState(searchQuery or selectedCategory)
       └─→ useMemo re-computes filteredGarments
           ├─ Filter by search + category + color
           └─ Re-render grid
           
  // Result: GarmentGrid updates instantly (client-side)
```

---

## Performance Considerations

### Rendering Optimization

| Area | Strategy |
|------|----------|
| **3D Viewport** | Use requestAnimationFrame, WebGL context, optimized shaders |
| **Garment Grid** | React.memo for GarmentCard, virtualization if >100 items |
| **Outfit List** | Immutable updates (spread operator), useCallback for event handlers |
| **Search/Filter** | useMemo to avoid recomputing filtered list on every render |

### Loading & Caching

| Area | Strategy |
|------|----------|
| **glTF Models** | Cache in SceneManager.modelCache (memory), LRU eviction if needed |
| **Garment Data** | React Query with 5-minute staleTime, localStorage for offline |
| **User Scans** | Lazy-load, cache URL in localStorage |
| **Garment Metadata** | Fetch once on app start, cache in memory |

### Code Splitting

```typescript
// App.tsx
const OutfitBuilder = lazy(() => import('./OutfitBuilder'))
const GarmentSelector = lazy(() => import('./GarmentSelector'))

// Load garment selector on demand (after 3D viewer is ready)
<Suspense fallback={<Loading />}>
  <Sidebar>
    <GarmentSelector />
  </Sidebar>
</Suspense>
```

---

## API Contract

### Required Endpoints (from Backend Engineer)

**Body Scans:**
```
GET /api/users/{userId}/scans
GET /api/users/{userId}/scans/{scanId}
POST /api/users/{userId}/scans
```

**Garments:**
```
GET /api/garments?category=&color=&brand=&limit=50
GET /api/garments/{id}
GET /api/garments/{id}/model          (redirects to glTF URL or returns blob)
```

**Outfits:**
```
GET /api/users/{userId}/outfits
GET /api/users/{userId}/outfits/{outfitId}
POST /api/users/{userId}/outfits      (create)
PUT /api/users/{userId}/outfits/{id}  (update)
DELETE /api/users/{userId}/outfits/{id}
```

**Size & Fit:**
```
GET /api/garments/{id}/sizes          (size chart data)
GET /api/users/{userId}/measurements  (user's body measurements)
```

---

## Error Handling

### Network Errors

```typescript
// In useGarments hook
try {
  const data = await fetchGarments()
} catch (error) {
  if (error.status === 401) {
    // Redirect to login
  } else if (error.status === 500) {
    // Show "Server error" toast
  } else {
    // Show generic error toast
  }
  // Fallback: use cached data if available
}
```

### 3D Rendering Errors

```typescript
// In SceneManager.loadGLTF()
try {
  const gltf = await loader.load(url)
} catch (error) {
  console.error('Failed to load model', error)
  // Show placeholder mesh
  // Notify backend (telemetry)
  return fallbackMesh()
}
```

### State Consistency

```typescript
// Validate outfit before saving
if (selectedGarments.length === 0) {
  showError('Add at least one garment to save an outfit')
  return
}

if (!outfitName || outfitName.trim() === '') {
  showError('Outfit name cannot be empty')
  return
}

// Save...
```

---

## Testing Strategy

### Unit Tests

```typescript
// GarmentCard.test.tsx
it('should call onAdd when add button is clicked', () => {
  const onAdd = jest.fn()
  render(<GarmentCard {...props} onAdd={onAdd} />)
  fireEvent.click(screen.getByText('+ Add'))
  expect(onAdd).toHaveBeenCalled()
})

// OutfitContext.test.tsx
it('should add garment to outfit', () => {
  const wrapper = ({ children }) => (
    <OutfitProvider>{children}</OutfitProvider>
  )
  const { result } = renderHook(() => useOutfit(), { wrapper })
  act(() => result.current.addGarment(mockGarment))
  expect(result.current.selectedGarments).toHaveLength(1)
})
```

### Integration Tests

```typescript
// App.test.tsx
it('should load body model and render viewport on mount', async () => {
  render(<App />)
  await waitFor(() => {
    expect(screen.getByRole('canvas')).toBeInTheDocument()
  })
})

it('should update 3D viewer when garment is added', async () => {
  render(<App />)
  const addButton = await screen.findByText('+ Add')
  fireEvent.click(addButton)
  
  // Check that SceneManager.updateGarments was called
  expect(sceneManagerMock.updateGarments).toHaveBeenCalled()
})
```

### E2E Tests (Cypress / Playwright)

```typescript
// e2e/outfit-builder.spec.ts
it('should create and save an outfit', () => {
  cy.visit('/app')
  cy.contains('+ Add').first().click()
  cy.get('input[placeholder="Enter outfit name"]').type('My Outfit')
  cy.contains('Save Outfit').click()
  cy.contains('✓ Saved').should('be.visible')
})
```

---

## Development Checklist (Phase 1)

- [ ] Set up React + Vite + TypeScript project
- [ ] Configure Tailwind CSS + shadcn/ui
- [ ] Create App shell (Header + MainContent + Sidebar layout)
- [ ] Implement SceneManager (Three.js scene, camera, lights)
- [ ] Create Viewport3D component (React wrapper)
- [ ] Implement glTF model loading + caching
- [ ] Set up animation playback (mixer, actions)
- [ ] Create AnimationControls UI
- [ ] Implement GarmentSelector (grid, search, filters)
- [ ] Implement OutfitBuilder (add/remove garments)
- [ ] Create SaveOutfitModal
- [ ] Implement SizeChart display
- [ ] Set up Context API (OutfitContext, AnimationContext)
- [ ] Set up React Query for server state
- [ ] Create API client + types
- [ ] Implement save outfit functionality
- [ ] Polish UI + responsive design
- [ ] Performance testing (FPS, load time, garment swap time)
- [ ] Error handling + edge cases
- [ ] Write unit + integration tests

---

## Next Phase (Phase 2) Enhancements

- Real-time cloth simulation
- Advanced animation library (run, jump, yoga poses)
- Garment texture variants (color/pattern swaps)
- User profile + measurement tracking
- Outfit history / wishlist
- Social sharing (outfit snapshots)
- Recommendation engine (style suggestions)
- AR preview (mobile)

---

**Document Version:** 1.0  
**Last Updated:** 2026-03-17
