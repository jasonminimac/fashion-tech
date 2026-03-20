# Cloth Simulation Strategy & Implementation Plan

**Document Owner:** Clothing & Physics Lead  
**Date:** 2026-03-17  
**Phase Focus:** Phase 1 (Static) → Phase 2 (Dynamic)  

---

## Executive Summary

Cloth simulation is the most technically challenging aspect of Fashion Tech's MVP. This document outlines:

1. **Why cloth sim is hard** (physics complexity, performance, accuracy tradeoffs)
2. **Phase 1 strategy** (avoid full simulation, use static fitting + baked poses)
3. **Phase 2 upgrade path** (introduce Blender cloth sim with performance optimization)
4. **Long-term vision** (learning-based model for real-time inference)

**Key Decision:** Phase 1 launches WITHOUT real-time cloth simulation. We use pre-fitted garments + pose-space blending. Phase 2 adds cloth simulation for improved realism.

---

## The Cloth Simulation Problem

### Why It's Hard

#### 1. Physics Complexity

A cloth simulation must solve:
- **Collision detection:** Prevent garment mesh from penetrating body/ground
- **Constraints:** Maintain edge lengths, prevent stretching beyond fabric limits
- **Gravity:** Fabric hangs and drapes realistically
- **Aerodynamics:** Wind and air pressure affect fabric
- **Friction:** Body surfaces and internal cloth-to-cloth friction
- **Damping:** Energy dissipation (stiffness, creases)

**Computational cost:** O(n³) for n vertices, tens of thousands per garment.

#### 2. Parameter Tuning

Every fabric is different:
- **Cotton:** Heavy, drapey, settles quickly
- **Silk:** Light, flowing, glides over skin
- **Denim:** Stiff, resists wrinkles, defined folds
- **Spandex:** Stretchy, hugs body, snappy recovery
- **Blends:** Complex behavior, non-linear parameters

**No universal parameters.** Each garment needs individual calibration.

#### 3. Performance vs. Quality Tradeoff

| Approach | Speed | Quality | Real-Time? |
|----------|-------|---------|-----------|
| Static mesh | ⚡ instant | ⚠️ poor | ✅ Yes |
| Pose-space blend | ⚡ <10ms | ✅ good | ✅ Yes |
| Pre-baked cloth sim | 🐢 <500ms | ✅✅ excellent | ❌ No (but cached) |
| Real-time cloth sim | 🐢 1-5s per frame | ✅✅ perfect | ❌ No |
| Learning-based (GPU) | ⚡ <20ms | ✅✅ very good | ✅ Yes |

#### 4. Validation Difficulty

How do we know if a garment looks "correct"?
- No ground truth (different fabrics drape differently)
- Visual quality is subjective
- Requires expert judgment (fashion designer, QA)
- Expensive to validate across 50+ garments

---

## Phase 1 Strategy: Static Fitting + Pose Blending

### Why Phase 1 Avoids Full Cloth Sim

**Rationale:**

1. **Time Constraint:** Building, tuning, validating cloth sim for 50+ garments = 3+ weeks
2. **MVP Goal:** Prove the core loop (scan → try-on → buy), not perfect physics
3. **User Expectations:** Early users tolerate static garments if fit is good and animations are smooth
4. **Risk Reduction:** One less complex system to debug

### Phase 1 Architecture

```
User Body + Animation
       ↓
[Load Pre-Fitted Garment]
       ↓
[Identify Current Animation Pose]
       ↓
[Select Pre-Baked Mesh Variant]
       ↓
[Apply Pose-Space Blending (Optional)]
       ↓
[Render in Viewer]
```

**Detail:**

#### Step 1: Pre-Fitted Garment Storage

When a garment is imported:
1. Static fit to reference body (T-pose, size M)
2. Apply size scaling (shrinkwrap) for each size (XS, S, L, XL)
3. Store 5 fitted variants in S3:
   ```
   s3://garments/{garment_id}/
     ├─ fitted_XS.glb
     ├─ fitted_S.glb
     ├─ fitted_M.glb    ← reference
     ├─ fitted_L.glb
     └─ fitted_XL.glb
   ```

#### Step 2: Animation Pose Blending

When user animation plays (e.g., walk cycle):

1. User body animation is 60fps (from Blender Lead)
2. Garment follows body via **skeleton binding** (weighted to same bones)
   - Garment vertices inherit body bone transformations
   - No additional simulation, just mesh deformation
3. Wrinkles/secondary motion: Optional lattice deformer
   - Light, procedural deformation on top of skeleton binding
   - Adds visual interest without full sim cost

**Result:** Garment "sticks" to body, animates naturally, no cloth sim overhead.

#### Step 3: User-Specific Fit

When user scans their body:
1. Capture scanned body geometry (from 3D Scanning Lead)
2. For each garment size:
   - Fit pre-made garment to user body (same shrinkwrap algorithm)
   - Cache result in user session (S3 or ephemeral storage)
3. Display fitted variant in viewer
4. User sees garment at their size, on their body

**Assumption:** Fitting algorithm works across diverse body types (validated in weeks 1-4).

### Phase 1 Expected Visual Quality

- ✅ Garment positioned correctly on body (no clipping)
- ✅ Correct size (M garment looks M on user)
- ✅ Natural animation (garment moves with body)
- ⚠️ Limited drape realism (no heavy fabric sag, wrinkles)
- ⚠️ No secondary motion (sleeves don't wave in wind)
- ⚠️ Stiff appearance (real silk is more flowing)

**User Feedback Expectation:** "It looks like a 3D model wearing a garment, not like a person in real clothes."

**Is This OK for MVP?** Yes. Users understand it's a prototype. Focus on fit accuracy, not photorealism.

---

## Phase 2 Strategy: Cloth Simulation Integration

### When to Introduce Cloth Sim

**Trigger:** After Phase 1 launch, collect user feedback:
- "Garments look too stiff"
- "Why doesn't silk hang differently than denim?"
- "This doesn't look like real cloth"

**Timeline:** Weeks 5-8 (or later, if Phase 1 succeeds)

### Phase 2 Architecture: Blender Cloth Sim

#### Option A: Pre-Baked Simulation (Recommended)

**Workflow:**

```
[Garment Ready for Sim]
       ↓
[Select Key Animation Frames]
   (e.g., frames 0, 10, 20, 30 of 60-frame walk cycle)
       ↓
[Run Cloth Sim for Each Frame]
   (Blender headless, ~30s per frame)
       ↓
[Blend Between Simmed Poses]
   (real-time interpolation on GPU)
       ↓
[Cache Results in S3]
   (one set per garment/body type)
       ↓
[User Playback]
   (load cached poses, blend at 60fps)
```

**Pros:**
- Realistic cloth drape (full physics simulation)
- Real-time playback (poses are pre-computed)
- Works on all devices (no GPU required)
- Deterministic, reproducible

**Cons:**
- Heavy preprocessing (30s per frame × many poses × many garments)
- Blending between poses can show seams/artifacts
- New animation type → must re-bake

**Implementation:**

```python
def bake_cloth_sim(garment_obj, body_obj, animation_frames, fabric_params):
    """
    Pre-compute cloth sim for key animation frames.
    
    Args:
        garment_obj: Blender garment mesh
        body_obj: Blender animated body
        animation_frames: [0, 10, 20, 30, ...]
        fabric_params: {"mass": 5.0, "damping": 0.1, ...}
    
    Returns:
        baked_poses: {frame_idx: fitted_mesh}
    """
    
    baked_poses = {}
    
    for frame_idx in animation_frames:
        # Set animation frame
        bpy.context.scene.frame_set(frame_idx)
        
        # Apply cloth sim with fabric params
        cloth_modifier = garment_obj.modifiers.new("Cloth", "CLOTH")
        set_cloth_properties(cloth_modifier, fabric_params)
        
        # Simulate 30 frames from this starting pose
        # (convergence to stable state)
        for sim_frame in range(30):
            bpy.context.scene.frame_set(frame_idx + sim_frame)
            # Physics step (automatic)
        
        # Store result
        final_frame = frame_idx + 30
        baked_mesh = capture_mesh_state(garment_obj, final_frame)
        baked_poses[frame_idx] = baked_mesh
    
    return baked_poses
```

**Runtime blending (on GPU, real-time):**

```python
def blend_baked_poses(pose_frames, weights, animation_frame):
    """
    Interpolate between pre-baked cloth sim poses.
    
    Args:
        pose_frames: [(0, mesh_0), (10, mesh_10), (20, mesh_20), ...]
        weights: [0.3, 0.7] (for frames 10 and 20)
        animation_frame: 17 (current frame)
    
    Returns:
        interpolated_mesh: Blended result
    """
    
    lower_idx, upper_idx = find_surrounding_frames(animation_frame, pose_frames)
    lower_mesh, upper_mesh = pose_frames[lower_idx], pose_frames[upper_idx]
    
    # Linear blend between vertex positions
    t = (animation_frame - lower_idx) / (upper_idx - lower_idx)
    blended_verts = lerp(lower_mesh.vertices, upper_mesh.vertices, t)
    
    return Mesh(verts=blended_verts)
```

#### Option B: Real-Time Cloth Sim (Advanced, Phase 2.5+)

**Workflow:**

```
[Garment Ready]
       ↓
[Assign Cloth Properties]
       ↓
[Play Animation]
       ↓
[For Each Frame:]
   - Run cloth sim step
   - Render
       ↓
[Display Result (60fps target, may be slower)]
```

**Pros:**
- Highest quality and realism
- Adaptable to any animation
- No preprocessing needed

**Cons:**
- Very slow (5-10+ seconds per animation frame on CPU)
- Requires GPU acceleration for real-time (expensive)
- Debugging cloth instability is hard
- May not work on low-end hardware

**When to Use:** Desktop/high-end viewer, not MVP.

#### Option C: Learning-Based Model (Phase 3+)

**Concept:** Train a neural network to predict cloth deformation.

**Workflow:**

```
[Generate Training Data]
  (simulate 10,000 garment-pose pairs)
       ↓
[Train ML Model]
  (input: garment params + body pose → output: cloth deformation)
       ↓
[Deploy on GPU]
  (inference <20ms, real-time)
       ↓
[User Try-On]
  (model predicts cloth shape in real-time)
```

**Pros:**
- Real-time quality rivaling full simulation
- Works on GPU and CPU
- Generalizes to new garments/bodies

**Cons:**
- Requires significant training data generation
- Model quality depends on training diversity
- Harder to debug (black box)
- Research-level complexity

**Candidates:**
- **NVIDIA GARNet:** Learning-based garment deformation
- **TensorFlow Lite:** Deploy on mobile/web
- **Custom PyTorch model:** If GARNet unavailable

---

## Fabric Parameter Calibration

### Challenge: Every Garment Needs Tuning

**Problem:** Blender's cloth sim has 15+ parameters, and optimal values vary per fabric.

**Solution:** Build a **fabric lookup table** and **auto-tuning algorithm**.

### Fabric Lookup Table

```python
FABRIC_PARAMS = {
    "cotton": {
        "mass": 5.0,  # g per m²
        "damping": 0.08,
        "elasticity": 0.15,
        "bending_stiffness": 0.5,
        "air_damping": 0.02,
        "friction": 0.3,
        "wrinkle_intensity": 0.8,
        "notes": "Heavy, settles quickly, distinct wrinkles"
    },
    "silk": {
        "mass": 2.0,
        "damping": 0.02,
        "elasticity": 0.05,
        "bending_stiffness": 0.1,
        "air_damping": 0.01,
        "friction": 0.15,
        "wrinkle_intensity": 0.3,
        "notes": "Light, flows smoothly, minimal wrinkles"
    },
    "denim": {
        "mass": 8.0,
        "damping": 0.12,
        "elasticity": 0.08,
        "bending_stiffness": 0.8,
        "air_damping": 0.03,
        "friction": 0.4,
        "wrinkle_intensity": 0.6,
        "notes": "Stiff, defined creases, resists stretching"
    },
    "spandex": {
        "mass": 1.5,
        "damping": 0.25,  # High damping = snappy recovery
        "elasticity": 0.85,  # Highly elastic
        "bending_stiffness": 0.2,
        "air_damping": 0.02,
        "friction": 0.5,
        "wrinkle_intensity": 0.1,
        "notes": "Stretchy, hugs body, snaps back"
    },
    # ... more fabrics
}
```

### Auto-Tuning Algorithm

**Goal:** Given a garment and reference cloth appearance, optimize parameters.

**Process:**

```python
def auto_tune_fabric_params(garment_obj, body_obj, reference_sim_video, fabric_type):
    """
    Auto-tune cloth sim parameters by comparing to reference video.
    
    Args:
        garment_obj: Blender garment mesh
        body_obj: Blender body in T-pose
        reference_sim_video: Ground truth cloth appearance (video or sequence)
        fabric_type: "cotton", "silk", etc.
    
    Returns:
        tuned_params: Optimized parameter dict
    """
    
    # Start with lookup table params
    params = FABRIC_PARAMS[fabric_type].copy()
    
    # Run sim with initial params
    sim_result_1 = run_cloth_sim(garment_obj, body_obj, params, frames=100)
    
    # Compare to reference (visual similarity metric)
    error_1 = compare_meshes(sim_result_1, reference_sim_video)
    
    # Gradient descent on key parameters
    # Adjust damping, mass, elasticity
    for iteration in range(10):
        # Perturb each param slightly
        for param_name in ["damping", "mass", "elasticity"]:
            params_up = params.copy()
            params_up[param_name] *= 1.05  # +5%
            
            sim_up = run_cloth_sim(garment_obj, body_obj, params_up, frames=100)
            error_up = compare_meshes(sim_up, reference_sim_video)
            
            # Update if error decreased
            if error_up < error_1:
                params[param_name] *= 1.05
                error_1 = error_up
    
    return params
```

**Validation:**
- Run sim with tuned parameters
- Visually inspect for artifacts (excessive bunching, unrealistic stretching)
- Store final parameters in database
- Log: original lookup → tuned adjustments

---

## Validation & Quality Assurance

### QA Checklist for Cloth Sim

Before a garment with cloth sim ships:

- [ ] **Stability:** Sim runs 100 frames without crashing/exploding
- [ ] **No Clipping:** Garment doesn't penetrate body in key poses
- [ ] **Drape Quality:** Fabric settles naturally (no bizarre folds)
- [ ] **Wrinkles:** Match fabric type (silk: smooth, denim: creased)
- [ ] **Animation:** Garment responds smoothly to body movement
- [ ] **Performance:** Sim + rendering <500ms for 60 frames (if baked)
- [ ] **Consistency:** Same garment on different body types looks proportional
- [ ] **Partner Sign-Off:** Brand approves final appearance

### Automated Validation

```python
def validate_cloth_sim(garment_obj, sim_result, fabric_type):
    """
    Auto-check cloth sim quality.
    
    Returns:
        report: Dict of pass/fail checks
    """
    
    report = {
        "clipping": check_mesh_penetration(sim_result, body),
        "stability": check_for_nan_inf(sim_result),
        "bunching": detect_excessive_folding(sim_result),
        "wrinkle_count": count_surface_wrinkles(sim_result),
        "expected_wrinkle_count": FABRIC_PARAMS[fabric_type]["wrinkle_intensity"],
        "drape_quality": measure_smoothness(sim_result),
    }
    
    # Pass if all checks OK
    return all(report.values())
```

---

## Cloth Simulation Integration with Blender Lead

### Dependencies

**What Clothing Lead Needs from Blender Lead:**

1. **Rigged Reference Body**
   - T-pose with skeleton/armature
   - Weight-painted so deformations look natural
   - Export to `.blend` for cloth sim setup

2. **Animation Data**
   - Walk cycle (60 frames)
   - Idle pose with weight shifts
   - Frame metadata (which frames are key poses)

3. **Blender Export Pipeline**
   - Can Blender headless CLI run cloth sim? (bpy module available?)
   - How to export simmed results? (GLB, FBX, or raw mesh data?)

**What Blender Lead Can Expect from Clothing Lead:**

1. **Fitted Garments**
   - Pre-fitted meshes (shrinkwrapped, sized for S/M/L/XL)
   - Ready to bind to body skeleton

2. **Cloth Sim Requests**
   - "Run cloth sim on this garment, these params, this animation"
   - Batch requests (5-10 garments at once)

3. **Feedback**
   - "Cloth looks unrealistic here" → tweak parameters
   - Visual QA on rendered output

---

## Timeline & Milestones

### Phase 1: Static Fitting (Weeks 1-8)

- Week 1-2: Garment data model, import pipeline
- Week 2-3: Static fitting algorithm (shrinkwrap)
- Week 3-4: Fit validation on diverse bodies
- Week 4-5: Integration with animation skeleton (no cloth sim)
- Week 5-6: B2B onboarding, 10+ garments ready
- Week 6-8: Polish, testing, 50+ garment target

**Cloth Sim Status:** None yet. Use skeleton-based deformation only.

### Phase 2: Cloth Sim (Weeks 9-12, optional)

- Week 9: Fabric parameter lookup table
- Week 10: Auto-tune algorithm, test on 5 garments
- Week 11: Pre-bake cloth sim for key poses, blending interpolation
- Week 12: QA on 50 garments, partner feedback

**Cloth Sim Status:** Pre-baked sim, pose-space blending. Real-time playback.

### Phase 3+: Advanced (Months 4+, future)

- Learning-based model (NVIDIA GARNet)
- Real-time cloth sim on GPU
- Advanced animations (running, dancing, dynamic poses)

---

## Performance Benchmarks (Targets)

| Metric | Phase 1 | Phase 2 | Phase 3 |
|--------|---------|---------|---------|
| **Garment loading** | <100ms | <100ms | <100ms |
| **Fitting latency** | <1s | <1s | <1s |
| **Animation playback** | 60fps | 60fps | 60fps |
| **Memory per garment** | 50MB | 100MB | 50MB* |
| **Cloth sim time per frame** | N/A | 30s (offline) | 20ms (GPU) |
| **Viewer FPS** | 60 | 60 | 60 |

*With model compression / LOD variants

---

## Known Challenges & Workarounds

### Challenge 1: Cloth Sim Artifacts

**Problem:** Simulation produces weird folds, tears, or stretching.

**Workarounds:**
- Adjust mass (heavier = settles faster)
- Increase damping (stiffer = fewer oscillations)
- Add collision buffer (margin increases)
- Smooth fabric seams (remove sharp edges)
- Increase sub-steps (more iterations, more stable)

### Challenge 2: Different Poses, Different Fit

**Problem:** Garment fitted in T-pose may look bad when sitting/running.

**Workaround (Phase 1):**
- Fit in multiple poses if critical (T-pose + one animation frame)
- Use skeleton binding (garment follows body bones naturally)

**Workaround (Phase 2):**
- Pre-bake cloth sim for multiple poses
- Blend between them

### Challenge 3: Scaling Garment for Different Body Sizes

**Problem:** Fitted garment at size M doesn't scale cleanly to L.

**Workaround:**
- Store scale factors per size (uniform + per-dimension tweaks)
- Test extensively on diverse bodies
- Manual intervention for edge cases

### Challenge 4: Partner Expectations

**Problem:** Manufacturers want photorealistic results, not stylized cloth.

**Expectation Setting:**
- Show Phase 1 preview (static + animation)
- Explain cloth sim roadmap (coming in Phase 2)
- Set clear quality bar (good enough for e-commerce try-on, not film VFX)

---

## Comparison: Blender Cloth vs. Marvelous Designer vs. Learning-Based

| Aspect | Blender | Marvelous Designer | Learning-Based |
|--------|---------|-------------------|-----------------|
| **Cost** | Free | $300-600 license | Custom R&D |
| **Quality** | Good | Excellent | Excellent |
| **Speed** | Medium | Fast | Very Fast |
| **Real-Time?** | No (pre-baked) | No | Yes |
| **Integration** | Easy (Python) | Medium (API) | Hard (ML ops) |
| **Parameter Tuning** | Manual | Automated | Automatic |
| **Generalization** | Per-garment | Per-garment | Across garments |
| **Maturity** | Stable | Industry standard | Research |

**Recommendation for Phase 1-2:** Blender cloth sim (free, good quality, easy integration).  
**Recommendation for Phase 3:** Explore learning-based model if real-time becomes critical.

---

## Summary

### Phase 1: What We're NOT Doing

- ❌ Real-time cloth simulation
- ❌ Complex fabric interactions
- ❌ Wind, aerodynamics, extreme poses
- ❌ Photorealistic drape

### Phase 1: What We ARE Doing

- ✅ Static fitting with proper sizing
- ✅ Skeleton-based animation
- ✅ Garment loads fast, looks decent
- ✅ Proves MVP loop works

### Phase 2+: Upgrade Path

- Add pre-baked cloth sim
- Pose-space blending for smooth transitions
- Fabric parameter tuning
- Learning-based model (if needed)

**Success Criterion:** Users see garments fit correctly on their body, animated naturally, with acceptable visual quality for an MVP.

---

**Version:** 1.0  
**Last Updated:** 2026-03-17  
**Next Review:** After Phase 1 MVP launch (Week 8)
