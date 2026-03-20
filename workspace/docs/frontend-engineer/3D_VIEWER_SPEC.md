# 3D Viewer Specification — Fashion Tech MVP

**Author:** Frontend Engineer  
**Date:** 2026-03-17  
**Component:** Viewport3D + SceneManager  
**Status:** Design Document

---

## Overview

The 3D Viewer is the heart of the Fashion Tech experience. It renders:
- An animated 3D body model (from user's body scan)
- Selected garments positioned on the body
- Realistic lighting
- User interaction (rotation, zoom, animation playback)

All built on **Three.js** with React as the integration layer.

---

## Component Structure

### `Viewport3D.tsx` (React Component)

**Purpose:** React wrapper around the Three.js canvas. Handles:
- Canvas DOM management
- Event listeners (resize, mouse input)
- State synchronization (animation playback, garment changes)
- Performance monitoring

```typescript
interface Viewport3DProps {
  scanUrl: string              // glTF URL of body model
  selectedGarments: Garment[]  // Garments to render
  animationState: {
    type: 'walk' | 'run' | 'idle'
    playing: boolean
    speed: number
    loopMode: 'loop' | 'once'
  }
  onGarmentSelected?: (garmentId: string) => void  // For hover/click
  viewMode?: 'front' | 'back' | '360'  // Camera preset
}

export const Viewport3D: React.FC<Viewport3DProps> = ({
  scanUrl,
  selectedGarments,
  animationState,
  viewMode = '360',
  ...
}) => {
  const mountRef = useRef<HTMLDivElement>(null)
  const sceneRef = useRef<SceneManager | null>(null)

  // Initialize Three.js scene on mount
  useEffect(() => {
    if (!mountRef.current) return

    sceneRef.current = new SceneManager(mountRef.current)
    return () => sceneRef.current?.dispose()
  }, [])

  // Load body model
  useEffect(() => {
    sceneRef.current?.loadBodyModel(scanUrl)
  }, [scanUrl])

  // Update garments
  useEffect(() => {
    sceneRef.current?.updateGarments(selectedGarments)
  }, [selectedGarments])

  // Control animation playback
  useEffect(() => {
    const { type, playing, speed } = animationState
    if (playing) {
      sceneRef.current?.playAnimation(type, speed)
    } else {
      sceneRef.current?.pauseAnimation()
    }
  }, [animationState])

  // Handle camera preset changes
  useEffect(() => {
    sceneRef.current?.setCameraPreset(viewMode)
  }, [viewMode])

  return (
    <div
      ref={mountRef}
      style={{
        width: '100%',
        height: '100%',
        position: 'relative',
      }}
    />
  )
}
```

**Responsibilities:**
- Manage React lifecycle
- Pass props to SceneManager
- Handle resize events
- Expose scene methods via ref (if needed for advanced controls)

---

### `SceneManager.ts` (Three.js Orchestration)

**Purpose:** Encapsulates all Three.js logic. A stateful manager that:
- Creates and maintains the Three.js scene, camera, renderer
- Loads and caches models
- Manages animations
- Handles garment positioning
- Optimizes rendering performance

```typescript
export class SceneManager {
  private scene: THREE.Scene
  private camera: THREE.OrthographicCamera
  private renderer: THREE.WebGLRenderer
  private controls: OrbitControls
  private clock: THREE.Clock

  // Model management
  private bodyModel: THREE.Group | null = null
  private garments: Map<string, THREE.Group> = new Map()
  private modelCache: Map<string, THREE.Group> = new Map()

  // Animation management
  private mixer: THREE.AnimationMixer | null = null
  private actions: Map<string, THREE.AnimationAction> = new Map()
  private currentAction: THREE.AnimationAction | null = null

  constructor(container: HTMLElement) {
    this.scene = new THREE.Scene()
    this.camera = this.createCamera(container)
    this.renderer = this.createRenderer(container)
    this.controls = new OrbitControls(this.camera, this.renderer.domElement)
    this.clock = new THREE.Clock()

    this.setupLighting()
    this.setupControls()
    this.startRenderLoop()

    // Handle window resize
    window.addEventListener('resize', () => this.onWindowResize(container))
  }

  private createCamera(container: HTMLElement): THREE.OrthographicCamera {
    const width = container.clientWidth
    const height = container.clientHeight
    const aspectRatio = width / height

    // Orthographic camera: no perspective distortion (fashion standard)
    const camera = new THREE.OrthographicCamera(
      -1.5 * aspectRatio,
      1.5 * aspectRatio,
      1.5,
      -1.5,
      0.1,
      1000
    )
    camera.position.set(0, 0, 2)
    camera.lookAt(0, 0, 0)

    return camera
  }

  private createRenderer(container: HTMLElement): THREE.WebGLRenderer {
    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      preserveDrawingBuffer: true,
    })
    renderer.setSize(container.clientWidth, container.clientHeight)
    renderer.setPixelRatio(window.devicePixelRatio)
    renderer.setClearColor(0xf8f8f8) // Light neutral background
    container.appendChild(renderer.domElement)

    return renderer
  }

  private setupLighting(): void {
    // Key light (main)
    const keyLight = new THREE.DirectionalLight(0xffffff, 1.0)
    keyLight.position.set(3, 4, 5)
    keyLight.target.position.set(0, 0, 0)
    keyLight.castShadow = true
    keyLight.shadow.mapSize.width = 2048
    keyLight.shadow.mapSize.height = 2048
    this.scene.add(keyLight)
    this.scene.add(keyLight.target)

    // Fill light (reduce shadows)
    const fillLight = new THREE.DirectionalLight(0xffffff, 0.5)
    fillLight.position.set(-3, 2, 5)
    this.scene.add(fillLight)

    // Back light (separation from background)
    const backLight = new THREE.DirectionalLight(0xffffff, 0.3)
    backLight.position.set(0, 2, -5)
    this.scene.add(backLight)

    // Ambient light (fill everything slightly)
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.3)
    this.scene.add(ambientLight)
  }

  private setupControls(): void {
    this.controls.autoRotate = false
    this.controls.autoRotateSpeed = 4
    this.controls.damping = true
    this.controls.dampingFactor = 0.05
    this.controls.enableZoom = true
    this.controls.zoomSpeed = 1.0
    this.controls.enablePan = true
  }

  private startRenderLoop(): void {
    const animate = () => {
      requestAnimationFrame(animate)

      // Update animation mixer
      const deltaTime = this.clock.getDelta()
      if (this.mixer) {
        this.mixer.update(deltaTime)
      }

      // Update controls
      this.controls.update()

      // Render scene
      this.renderer.render(this.scene, this.camera)
    }
    animate()
  }

  /**
   * Load body model from glTF
   */
  async loadBodyModel(url: string): Promise<void> {
    try {
      // Check cache first
      if (this.modelCache.has(url)) {
        this.bodyModel = this.modelCache.get(url)!.clone()
        this.scene.add(this.bodyModel)
        return
      }

      // Load from URL
      const gltf = await this.loadGLTF(url)
      this.bodyModel = gltf.scene

      // Extract animations
      if (gltf.animations.length > 0) {
        this.mixer = new THREE.AnimationMixer(this.bodyModel)
        gltf.animations.forEach((clip) => {
          const action = this.mixer!.clipAction(clip)
          this.actions.set(clip.name, action)
        })
      }

      // Cache and add to scene
      this.modelCache.set(url, this.bodyModel)
      this.scene.add(this.bodyModel)

      // Auto-frame the model
      this.frameModel(this.bodyModel)
    } catch (error) {
      console.error('Failed to load body model:', error)
    }
  }

  /**
   * Load and position a garment on the body
   */
  async addGarment(garmentId: string, url: string): Promise<void> {
    try {
      // Check cache
      let garment: THREE.Group
      if (this.modelCache.has(url)) {
        garment = this.modelCache.get(url)!.clone()
      } else {
        const gltf = await this.loadGLTF(url)
        garment = gltf.scene
        this.modelCache.set(url, garment)
      }

      // Position garment relative to body
      // (Offsets pre-calculated in Blender during export)
      this.positionGarment(garment, garmentId)

      // Add to scene and tracking
      this.scene.add(garment)
      this.garments.set(garmentId, garment)
    } catch (error) {
      console.error(`Failed to load garment ${garmentId}:`, error)
    }
  }

  /**
   * Remove a garment from the scene
   */
  removeGarment(garmentId: string): void {
    const garment = this.garments.get(garmentId)
    if (garment) {
      this.scene.remove(garment)
      this.garments.delete(garmentId)
    }
  }

  /**
   * Update garments (add/remove based on current selection)
   */
  async updateGarments(selectedGarments: Garment[]): Promise<void> {
    const selectedIds = new Set(selectedGarments.map((g) => g.id))
    const currentIds = new Set(this.garments.keys())

    // Remove garments no longer selected
    for (const id of currentIds) {
      if (!selectedIds.has(id)) {
        this.removeGarment(id)
      }
    }

    // Add new garments
    for (const garment of selectedGarments) {
      if (!currentIds.has(garment.id)) {
        await this.addGarment(garment.id, garment.modelUrl)
      }
    }
  }

  /**
   * Play an animation
   */
  playAnimation(
    animationType: 'walk' | 'run' | 'idle',
    speed: number = 1.0
  ): void {
    if (!this.mixer) return

    // Stop current action
    if (this.currentAction) {
      this.currentAction.stop()
    }

    // Play new action
    const action = this.actions.get(animationType)
    if (action) {
      action.reset()
      action.clampWhenFinished = false
      action.loop = THREE.LoopRepeat
      action.speed = speed
      action.play()
      this.currentAction = action
    }
  }

  /**
   * Pause animation
   */
  pauseAnimation(): void {
    if (this.currentAction) {
      this.currentAction.paused = true
    }
  }

  /**
   * Resume animation
   */
  resumeAnimation(): void {
    if (this.currentAction) {
      this.currentAction.paused = false
    }
  }

  /**
   * Set camera to preset view
   */
  setCameraPreset(viewMode: 'front' | 'back' | '360'): void {
    const distance = 2.5

    switch (viewMode) {
      case 'front':
        this.camera.position.set(0, 0, distance)
        this.controls.autoRotate = false
        break
      case 'back':
        this.camera.position.set(0, 0, -distance)
        this.controls.autoRotate = false
        break
      case '360':
        this.controls.autoRotate = true
        break
    }

    this.controls.update()
  }

  /**
   * Automatically frame the camera to fit model in view
   */
  private frameModel(model: THREE.Object3D): void {
    const box = new THREE.Box3().setFromObject(model)
    const size = box.getSize(new THREE.Vector3())
    const maxDim = Math.max(size.x, size.y, size.z)
    const fov = this.camera instanceof THREE.OrthographicCamera ? 1.5 : 75
    const distance = maxDim / (2 * Math.tan((fov * Math.PI) / 180))

    this.camera.position.z = distance
    this.controls.target = box.getCenter(new THREE.Vector3())
    this.controls.update()
  }

  /**
   * Position garment relative to body (placeholder)
   * TODO: Implement garment-specific positioning logic
   */
  private positionGarment(garment: THREE.Group, garmentId: string): void {
    // Default: align to body origin
    garment.position.set(0, 0, 0)

    // In a real implementation, read offsets from garment metadata:
    // const offsets = getGarmentOffsets(garmentId)
    // garment.position.copy(offsets.position)
    // garment.rotation.copy(offsets.rotation)
  }

  /**
   * Load glTF model (helper)
   */
  private async loadGLTF(url: string): Promise<THREE.GLTF> {
    const loader = new GLTFLoader()
    return new Promise((resolve, reject) => {
      loader.load(url, resolve, undefined, reject)
    })
  }

  /**
   * Handle window resize
   */
  private onWindowResize(container: HTMLElement): void {
    const width = container.clientWidth
    const height = container.clientHeight
    const aspectRatio = width / height

    // Update orthographic camera
    if (this.camera instanceof THREE.OrthographicCamera) {
      this.camera.left = (-1.5 * aspectRatio)
      this.camera.right = 1.5 * aspectRatio
      this.camera.top = 1.5
      this.camera.bottom = -1.5
      this.camera.updateProjectionMatrix()
    }

    // Update renderer
    this.renderer.setSize(width, height)
    this.renderer.setPixelRatio(window.devicePixelRatio)
  }

  /**
   * Cleanup
   */
  dispose(): void {
    this.renderer.dispose()
    this.controls.dispose()
    window.removeEventListener('resize', () => this.onWindowResize)
  }
}
```

---

## Key Technical Decisions

### 1. **Orthographic vs. Perspective Camera**

**Decision:** Orthographic

**Rationale:**
- Fashion industry standard (no perspective distortion at edges)
- Makes garment fit assessment more accurate
- Easier to compare before/after
- Consistent across different screen sizes

### 2. **Three Point Lighting**

**Decision:** Key light + Fill light + Back light + Ambient

**Rationale:**
- Industry standard for product photography
- Key light defines form
- Fill light softens shadows
- Back light separates body from background
- Creates professional, retail-grade appearance

### 3. **Model Caching**

**Decision:** Cache loaded models in memory

**Rationale:**
- Garment swaps need to be <200ms
- Reloading from network is too slow
- Memory is cheap; latency is expensive
- Implement LRU (least-recently-used) cache if needed for large catalogues

### 4. **Animation Management**

**Decision:** Three.js AnimationMixer + Actions

**Rationale:**
- Built-in support for glTF animation clips
- Smooth blending between animations
- Easy speed control and looping
- No external animation library needed

---

## Performance Optimization

### 1. **Model Optimization**
```typescript
// Automatically optimize loaded models
function optimizeModel(gltf: THREE.GLTF): void {
  gltf.scene.traverse((node) => {
    if (node instanceof THREE.Mesh) {
      // Enable frustum culling
      node.frustumCulled = true

      // Merge geometries if possible
      if (node.geometry.attributes.position.count > 50000) {
        node.geometry = node.geometry.deleteAttribute('uv2')
      }

      // Optimize materials
      if (node.material instanceof THREE.MeshStandardMaterial) {
        node.material.envMapIntensity = 0.5
      }
    }
  })
}
```

### 2. **Garbage Collection**
```typescript
// Clean up unused models from cache periodically
function pruneCache(): void {
  const maxCacheSize = 100 * 1024 * 1024 // 100MB
  let totalSize = 0

  for (const [url, model] of this.modelCache) {
    totalSize += calculateModelSize(model)
  }

  if (totalSize > maxCacheSize) {
    // Remove oldest entries
    const entries = Array.from(this.modelCache.entries())
    entries.slice(0, Math.ceil(entries.length * 0.2)).forEach(([url]) => {
      this.modelCache.delete(url)
    })
  }
}
```

### 3. **Rendering Performance**
```typescript
// Monitor FPS
let frameCount = 0
let lastTime = performance.now()

const animate = () => {
  frameCount++
  const currentTime = performance.now()

  if (currentTime >= lastTime + 1000) {
    console.log(`FPS: ${frameCount}`)
    frameCount = 0
    lastTime = currentTime
  }

  requestAnimationFrame(animate)
  renderer.render(scene, camera)
}
```

---

## API & Data Structures

### Garment Loading

```typescript
interface Garment {
  id: string
  modelUrl: string // glTF/glb file
  offsets?: {
    position: [number, number, number]
    rotation: [number, number, number]
    scale: [number, number, number]
  }
}
```

### Animation Clips

Expected from glTF export (from Blender):
```
Animation Clips:
  - "walk" (30 frames, 2-second cycle)
  - "run" (24 frames, 1.5-second cycle)
  - "idle" (looped, breathing/weight shift)
```

---

## Future Enhancements

1. **Garment Physics Preview** — Real-time cloth simulation in viewport
2. **Material Variants** — Swap fabric textures without reloading model
3. **Screenshot / Sharing** — Export outfit renders
4. **Detail Zoom** — Inspect garment seams and textures up close
5. **Custom Backgrounds** — Choose backdrop (solid color, pattern, photo)
6. **Shadow Support** — Cast shadows for depth (requires shadow maps)

---

## Error Handling

```typescript
class ModelLoadError extends Error {
  constructor(public url: string, public originalError: Error) {
    super(`Failed to load model from ${url}: ${originalError.message}`)
  }
}

async function loadGLTFSafe(url: string): Promise<THREE.GLTF | null> {
  try {
    return await loadGLTF(url)
  } catch (error) {
    console.error(new ModelLoadError(url, error as Error))
    return null // Gracefully degrade
  }
}
```

---

## Testing Strategy

1. **Unit Tests** — SceneManager methods (loading, positioning, animations)
2. **Integration Tests** — Viewport3D + SceneManager interaction
3. **Performance Tests** — FPS monitoring, memory leaks
4. **Visual Regression** — Screenshot comparisons across browsers

---

**Document Version:** 1.0  
**Last Updated:** 2026-03-17
