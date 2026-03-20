# PARTNER OUTREACH STRATEGY & CLO3D MATURITY ASSESSMENT
## Fashion Tech Week 1 Partnership Framework

**Document Owner:** Garment & Cloth Simulation Engineer  
**Date:** 2026-03-18  
**For:** Zara & H&M Outreach (starting Week 2)  
**Status:** Ready for CEO Approval  

---

## Executive Summary

This framework guides outreach to Zara and H&M with a focus on **CLO3D asset maturity assessment**. We've designed a discovery call structure that quickly identifies their 3D design capabilities, integration readiness, and pilot garment availability.

**Key Insight:** Both Zara and H&M likely use CLO3D already. Our job is to:
1. Confirm CLO3D files are production-quality (not just prototypes)
2. Understand their size scaling methodology (critical for fit accuracy)
3. Secure 5-10 pilot garments for Week 3-4 integration
4. Establish a repeatable B2B submission workflow

**Expected Outcome:** 5-10 validated garments live in catalogue within 4 weeks of first technical sync.

---

## PART 1: CLO3D MATURITY ASSESSMENT

### What is CLO3D?

**CLO3D** is industry-standard 3D garment design software used by:
- 80%+ of global fashion brands
- Design validation before physical sampling
- Digital pattern grading (size scaling)
- Fit simulation on digital dress forms
- Export to web/visualization tools (our integration point)

**For Fashion Tech:** CLO3D garments are ideal because:
- Design-validated (fit is proven on dress form)
- Parametric sizing available (XS-XL scaling rules built-in)
- Professional mesh quality (less cleanup needed)
- Textures typically included (color, patterns)

### Maturity Levels (Zara/H&M Assessment)

**Level 1: Basic** (Design-time only)
- ❌ CLO3D used for initial design
- ❌ No active use after design handoff
- ❌ No fit validation data captured
- ❌ Fit rules not documented
- **Effort to integrate:** High (manual fit calibration needed)
- **Timeline:** 3-4 weeks per garment

**Level 2: Production** (Design → Sampling)
- ✅ CLO3D used for design + pattern grading
- ✅ Size scaling documented (XS-XL rules)
- ✅ Fit validated on dress form before physical sampling
- ⚠️ Fit data exists but not structured for export
- **Effort to integrate:** Medium (extract & normalize fit rules)
- **Timeline:** 1-2 weeks per garment

**Level 3: Enterprise** (Design → Production → Reorder)
- ✅ Active CLO3D library maintained
- ✅ Parametric sizing fully documented
- ✅ Fit standards enforced (±tolerance rules)
- ✅ Fit validation automated (dress form simulation)
- ✅ Structured export pipeline
- **Effort to integrate:** Low (direct handoff possible)
- **Timeline:** <1 week per garment

**Most Likely:** Zara/H&M = **Level 2-3** (they invest heavily in 3D design)

---

## PART 2: DISCOVERY CALL SCRIPT (Week 2)

### Call Objective

**Goal:** Assess CLO3D maturity, understand their asset pipeline, secure pilot garments.

**Duration:** 30-45 minutes  
**Attendees:**
- Fashion Tech: Clothing Lead + Backend Lead
- Partner: Design Lead + Technical Lead (CTO/VP Engineering)

**Prep Before Call:**
- [ ] Review partner's recent collections (web, Instagram)
- [ ] Identify 3-5 garments from their store (use as reference examples)
- [ ] Prepare sample CLO3D file (to show what we can handle)

---

### Discovery Call Agenda

#### Section 1: Current 3D Workflow (5 min)

**Our Questions:**

1. "Walk us through your current 3D design workflow from concept to production."
   - *Why we ask:* Understand where CLO3D fits in their process
   - *Listen for:* Do they use CLO3D daily? Just for validation? For all garments or select categories?

2. "What % of your catalogue is designed in CLO3D vs. other tools?"
   - *Why we ask:* Size of addressable asset library
   - *Listen for:* "100% of new designs in CLO3D" (ideal) vs. "legacy patterns in CAD, new stuff in CLO3D" (mixed)

3. "Do you maintain an active CLO3D project library that's version-controlled?"
   - *Why we ask:* Assess maturity (enterprise CLO3D use = yes)
   - *Listen for:* "Yes, versioned in Dropbox/SharePoint/Git" (good) vs. "scattered across designer hard drives" (messy)

**Partner Likely Answers:**
- **Level 2:** "About 60-70% in CLO3D. New designs yes, heritage styles still in CAD. Designers have local projects, sync to shared drive weekly."
- **Level 3:** "100% of new designs in CLO3D since 2022. All projects live in our design management platform with version history."

---

#### Section 2: Size Scaling & Fit Validation (10 min)

**Our Questions:**

1. "How do you currently handle size grading in CLO3D? Do you use the built-in parametric grader or manual adjustments per size?"
   - *Why we ask:* This directly impacts our fitting algorithm (we need scale factors)
   - *Listen for:* "Parametric grader with master rules" (ideal) vs. "manual per-size tweaks" (acceptable but more work)

2. "Can you share your size chart? What's the reference size for your base pattern?"
   - *Why we ask:* We need to know base size (usually M) and scale factors (XS=0.85, L=1.08, etc.)
   - *Listen for:* "Sure, here's XS-XL scale factors" or "we don't have a single chart, varies by category"

3. "Do you do fit validation on dress forms in CLO3D? What dress form standards do you use?"
   - *Why we ask:* Assess if their fit data can calibrate our algorithm
   - *Listen for:* "Yes, standardized dress form set (XS, S, M, L, XL)" (great) or "only on size 8 female form" (limited)

4. "Have you tested any of your designs on human body scans? Do you have fit data from physical samples?"
   - *Why we ask:* We're introducing human body fitting (they may only use dress forms). This validates our approach.
   - *Listen for:* "We compare physical samples to dress form simulation to verify" (they understand fit validation complexity)

**Partner Likely Answers:**
- **Level 2:** "We use parametric grader with master % rules (e.g., chest +2%, sleeve +1% per size). Reference is size M. We validate on dress form set XS-XL, but we don't have body scan data."
- **Level 3:** "Full parametric system, documented in our design standards. We validate both on dress forms AND physical samples. We have proportional data for average, slim, curvy body types."

---

#### Section 3: File Export & Asset Quality (8 min)

**Our Questions:**

1. "When you export from CLO3D, what formats do you use? OBJ, FBX, or do you keep it in CLO3D?"
   - *Why we ask:* Affects integration complexity (if they already export to standard format, we're done. If not, we need to do it.)
   - *Listen for:* "We export to OBJ/FBX for vendor samples" (great) vs. "mostly stay in CLO3D, share .zprj files with vendors" (means we'll work with .zprj directly)

2. "Do your exports include textures and material definitions? What texture resolution?"
   - *Why we ask:* We need color, normals, roughness for web viewer
   - *Listen for:* "Yes, all exports have color + normal maps at 4K" (great) vs. "textures are applied in Photoshop post-export" (we handle)

3. "What polygon count do your garments typically have? Have you decimated for real-time?"
   - *Why we ask:* We need to optimize for web (target 5k-10k triangles)
   - *Listen for:* "Usually 30-50k triangles in design, we decimate for web" (they understand optimization) vs. "never thought about it, exports are heavy" (we'll handle)

4. "Can you export animations/rigged garments from CLO3D? Or are they static meshes?"
   - *Why we ask:* For Phase 2, animated garments are nice but not required
   - *Listen for:* "Static meshes only" (expected) vs. "We can export rigged with skeleton" (future feature)

**Partner Likely Answers:**
- **Level 2:** "We export to OBJ for samples. Textures are in the design but not always in exports. Polygon counts are high (40k+). Static meshes only."
- **Level 3:** "We export OBJ + FBX with full texture sets (2K resolution). Polygon counts are optimized (~15k typical). We're exploring rigging for animation."

---

#### Section 4: Pilot Program (7 min)

**Our Questions:**

1. "Would you be interested in a pilot program? 5-10 garments from your current collection to test virtual try-on?"
   - *Why we ask:* Lock in commitment
   - *Listen for:* "Absolutely, we're very interested" (success) vs. "we need exec approval first" (expected, introduce to CEO)

2. "Which garment categories would you prioritize? Tops, dresses, bottoms, outerwear?"
   - *Why we ask:* Get specific pilot garment list
   - *Listen for:* "White button-up shirt, black dress, blue jeans, blazer" (gives us real assets to work with)

3. "Can you provide CLO3D files (`.zprj`) or at least OBJ exports? What's your timeline?"
   - *Why we ask:* Confirms asset availability and timeline alignment
   - *Listen for:* "Yes, can deliver by EOW" (excellent, Week 3 fit testing) vs. "need 2-3 weeks to export from active projects" (delayed to Week 4)

4. "Who will be the technical point person for integration? Do they have experience with 3D file formats?"
   - *Why we ask:* Need a reliable technical contact for the 4-week pilot
   - *Listen for:* "[Name], our 3D design lead, they know CLO3D inside out" (ideal)

**Partner Likely Answers:**
- **Level 2:** "We'd love to try a pilot. Top choices: our bestselling white shirt, navy dress, denim jeans. We can get CLO3D files by end of next week. [Design lead name] will coordinate."
- **Level 3:** "Yes, very interested. We have 20+ candidates that would be good. We can start shipping CLO3D files within days. Our VP of Product will oversee the partnership."

---

#### Section 5: Expectations & SLA (5 min)

**Our Promises:**
1. "We'll convert your CLO3D files to web-ready models in <1 week per garment."
2. "We validate fit on multiple body types before launch (not just dress forms)."
3. "You'll see a preview in our viewer within 3-4 weeks of first file submission."
4. "We'll keep you updated weekly and incorporate your feedback on fit/appearance."

**We Ask:**
1. "Is there anything in this timeline that seems unrealistic for your team?"
2. "What's your approval process? Do files need design review before we publish?"
3. "Do you have any concerns about sharing CLO3D files with a new vendor?"

**Partner Likely Answers:**
- **Level 2:** "Timeline is great. Design lead approves, then it's my call. CLO3D files—we'll sign an NDA if needed."
- **Level 3:** "This fits our roadmap perfectly. Legal/IP will handle NDA. We have a quarterly review process; your pilot fits our Q2 innovation initiative."

---

### Call Exit: Maturity Assessment

**Immediately After Call, Score:**

| Capability | Level 1 | Level 2 | Level 3 |
|------------|---------|---------|---------|
| CLO3D daily use | ❌ | ✅ | ✅ |
| Parametric sizing | ❌ | ✅ | ✅ |
| Fit validation (dress form) | ⚠️ | ✅ | ✅ |
| Fit validation (human body) | ❌ | ❌ | ✅ |
| OBJ/FBX export capability | ❌ | ✅ | ✅ |
| Texture data available | ❌ | ⚠️ | ✅ |
| Optimized polygon counts | ❌ | ⚠️ | ✅ |
| Active asset library | ❌ | ✅ | ✅ |
| Pilot garments ready | ❌ | ✅ | ✅ |
| Technical point person | ⚠️ | ✅ | ✅ |

**Scoring:**
- 7-10 checkmarks = **Level 3 Enterprise** (1 week per garment, high confidence)
- 4-6 checkmarks = **Level 2 Production** (1-2 weeks per garment, standard path)
- 0-3 checkmarks = **Level 1 Basic** (3-4 weeks per garment, manual calibration)

---

## PART 3: POST-CALL ACTION PLAN

### If Level 3 Enterprise (Zara/H&M Most Likely)

**Immediate Actions (Same Week):**
1. ✅ Send NDA (Legal to handle)
2. ✅ Schedule weekly technical syncs (same time, recurring)
3. ✅ Send detailed asset submission template (Garment Intake Checklist)
4. ✅ Request first 5 pilot garments by EOW

**Week 2-3:**
1. ✅ Receive CLO3D files
2. ✅ Import + validate
3. ✅ Begin fitting algorithm testing
4. ✅ Generate preview meshes

**Week 4:**
1. ✅ QA review with partner
2. ✅ Partner approves fit appearance
3. ✅ Deploy to web viewer
4. ✅ Partner tests in viewer

### If Level 2 Production (Likely)

**Immediate Actions (Same Week):**
1. ✅ Send NDA
2. ✅ Set weekly syncs
3. ✅ Send Asset Intake Checklist
4. ✅ Request files + size scale factors document

**Week 2-3:**
1. ✅ Receive files + scale factors
2. ✅ Import + validate
3. ✅ Extract fit parameters from their data
4. ✅ Begin fitting algorithm calibration

**Week 4:**
1. ✅ Intensive fitting validation (may need iterations)
2. ✅ Partner provides feedback
3. ✅ Adjust scale factors if needed
4. ✅ Deploy to viewer

### If Level 1 Basic (Unlikely)

**Immediate Actions:**
1. ✅ Send NDA
2. ✅ Escalate to CEO (risk flag: more work than expected)
3. ✅ Reassess timeline with partner (may need 6-8 weeks instead of 4)

---

## PART 4: EMAIL TEMPLATES

### Email 1: Post-Call Summary (Send within 1 hour)

**Subject:** Fashion Tech Partnership — Call Summary & Next Steps

---

Hi [Partner Contact],

Thanks so much for taking time to chat about Fashion Tech. We loved learning about your CLO3D workflow and are excited about the pilot opportunity.

**What We Heard:**
- You use CLO3D for [X]% of designs, with full parametric sizing in place
- Your team maintains an active asset library with [X-Y size] dress form validation
- You can provide [#] sample garments starting [week X]

**What's Next:**
1. **NDA:** Legal will send standard partnership agreement by [date]
2. **Asset Submission:** Please use this template for garment files: [link]
3. **Weekly Sync:** Let's schedule [day/time] recurring
4. **First Batch:** Target [date] to receive initial 5 garments

**Your Pilot Timeline:**
```
Week 1 (Mar 22): You send files
Week 2 (Mar 29): We validate & begin fitting
Week 3 (Apr 5): QA review with you
Week 4 (Apr 12): Live in viewer
```

**Questions Before We Proceed?**
- Do you need an NDA from our side?
- What's the best cadence for check-ins (weekly, bi-weekly)?
- Any concerns on our end we should know about?

Looking forward to building this together!

Best regards,  
[Fashion Tech Partnerships]

---

### Email 2: Asset Submission Request (Send Week 1, Friday)

**Subject:** CLO3D Asset Submission — Week 1 Pilot Garments

---

Hi [Partner Contact],

Following up on our call — we're ready to receive your first batch of CLO3D files!

**What We Need:**

1. **CLO3D Files (`.zprj`)** for 5 pilot garments:
   - Sample garments: [whitelist garment names from discovery call]
   - File format: `.zprj` preferred, OBJ/FBX acceptable
   - One file per garment

2. **Metadata per garment:**
   ```json
   {
     "garment_name": "Classic White Button-Up Shirt",
     "sku": "ZARA-SHIRT-12345",
     "brand": "Zara",
     "category": "shirt",
     "color": "white",
     "base_size": "M",
     "size_chart": {
       "XS": 0.85,
       "S": 0.92,
       "M": 1.0,
       "L": 1.08,
       "XL": 1.16
     }
   }
   ```

3. **File Format:** ZIP package per attached template

**Submission Portal:**
- Use [SECURE LINK] or email to partnerships@fashion-tech.com
- Questions? Reply to this thread.

**Timeline:**
- Submit by: **[Date]** (EOW if possible)
- We validate: 24-48 hours
- You review fit preview: 3-4 days
- Live in viewer: EOW

**Questions?**
Call or Slack: [Contact Info]

Thanks!

---

### Email 3: Fit Validation Complete (Send Week 3-4)

**Subject:** Garment Fit Validation Complete — [Garment Name]

---

Hi [Partner Contact],

Great news! We've completed fit validation for your first batch of garments.

**Status:**
- ✅ [Garment 1] — APPROVED, ready for viewer
- ✅ [Garment 2] — APPROVED, ready for viewer
- ⚠️ [Garment 3] — MINOR REVISIONS needed (fit too snug at shoulders)
- 🔄 [Garment 4] — IN PROGRESS (testing on diverse body types)

**What This Means:**
- Approved garments are live in the viewer today
- Minor revision garments need your feedback (see details below)
- In-progress garments will be ready by [date]

**For the Minor Revision Garment [#3]:**

We noticed fit was tight at shoulders on size L. Two options:
1. **We adjust:** Increase shoulder width offset by 2cm, re-fit and re-validate
2. **You adjust:** Send updated CLO3D with adjusted shoulder seam, we re-import

Which works better for your team?

**Next Steps:**
1. Review garments in viewer: [LINK]
2. Send feedback by [DATE]
3. We iterate and finalize by [DATE]

Thanks!

---

## PART 5: CONTINGENCY PLANS

### If Partner Says "No CLO3D, Only Samples"

**Response:**
"No problem. We can work with physical samples too. Process:
1. Ship sample garment to us
2. We 3D scan it (photogrammetry)
3. Clean up mesh, extract fit parameters
4. Integrate into viewer

Timeline: 3-4 weeks instead of 1-2 (due to scanning + cleanup).

Can we do 2-3 samples as pilot to test workflow?"

**Effort:** High (manual mesh cleanup, no parametric sizing data)  
**Escalation:** Mention to CEO (slows timeline 2x)

---

### If Partner's CLO3D Files Are Messy

**Possible Issue:** High polygon counts, poor UV mapping, missing textures  
**Our Response:**
"No worries, this is common. Our import pipeline handles cleanup:
- Decimation (high-poly → web-friendly)
- Texture extraction
- UV validation

We may need 1-2 iterations with you for fit parameters, but we've got this."

**Escalation Trigger:** If >30% of files fail to import → technical review call

---

### If Partner Wants Revenue Share Before Pilot

**Response:**
"Let's prove the concept first. Pilot is no-cost to you, we absorb R&D.
Once we see traction (real user feedback), we can discuss partnership terms.

Most partners see 10-15% return lift with virtual try-on. We share that upside."

**Escalation:** Revenue discussion → CEO handles

---

## PART 6: SUCCESS CRITERIA (Week 1-4)

| Milestone | Target | Success |
|-----------|--------|---------|
| **Call Completed** | Week 2 | ✅ CLO3D maturity assessed, pilot secured |
| **Files Received** | Week 3 start | ✅ 5-10 garments submitted |
| **Import Validated** | Week 3 mid | ✅ 100% parse successfully |
| **Fit QA Complete** | Week 3 end | ✅ <10% require revisions |
| **Viewer Live** | Week 4 start | ✅ Garments appear in web viewer |
| **Partner Approval** | Week 4 mid | ✅ Partner signs off on appearance |
| **Repeat Submission** | Week 4+ | ✅ Partner can self-serve submit next batch |

---

## PART 7: ZARA & H&M SPECIFIC NOTES

### Zara Profile

**Company:** Spanish fast fashion (2,500+ stores globally)  
**3D Maturity:** Likely **Level 3 Enterprise** (they invest heavily in design tech)  
**Key Contacts:**
- Design Director
- CTO / VP Innovation
- Retail Partnerships Lead

**Angle:**
- Speed: "Your designs are already 3D-validated. We just convert to web."
- Scale: "From pilot to 10,000 garments in 6 months."
- First-Mover: "Be first global brand with Web3D try-on."

**Success Signal:** "Can we do a pilot? And scale to our full new collection?"

---

### H&M Profile

**Company:** Swedish fast-fashion, sustainability-focused (5,000+ stores globally)  
**3D Maturity:** Likely **Level 2-3** (strong design teams, variable maturity by studio)  
**Key Contacts:**
- Head of Digital / E-Commerce
- VP of Design
- Sustainability Lead (emphasize fit accuracy = fewer returns = less waste)

**Angle:**
- Sustainability: "Better fit = fewer returns = less waste (environmental impact)."
- Inclusivity: "Show garments on diverse body types, not just models."
- Speed-to-Market: "Parallel design + try-on testing speeds up cycles."

**Success Signal:** "Can we pilot? Does this support our sustainability goals?"

---

## Summary

**Week 1 Outcome:**
- ✅ Discovery call scripts prepared
- ✅ CLO3D maturity framework documented
- ✅ Contingency plans for common scenarios
- ✅ Email templates ready for Week 2 outreach
- ✅ Success criteria defined

**Week 2 Action:**
- 🚀 Schedule calls with Zara/H&M
- 🚀 Run discovery calls (30-45 min each)
- 🚀 Assess maturity, secure pilot garments
- 🚀 Send NDA + asset submission templates

**Week 3-4:**
- 🚀 Receive pilot garments
- 🚀 Import, validate, fit test
- 🚀 QA review with partners
- 🚀 Deploy to viewer, go live

---

**Document Version:** 1.0  
**Created:** 2026-03-18  
**Status:** Ready for CEO Review & Week 2 Execution  
**Next Update:** After first partner calls (Week 2)
