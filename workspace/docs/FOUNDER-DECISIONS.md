# FOUNDER DECISIONS — 2026-03-18

**Date:** 2026-03-18  
**Recorded by:** CEO (Subagent)  
**Status:** LOCKED IN — Implementation begins immediately

---

## Overview

The founder has resolved three critical open items. These decisions define the product roadmap for Weeks 2–6 and beyond. **All decisions are final and ready for implementation.**

---

## Decision #1: Scanning Approach — DUAL TRACK

### Summary

The platform will pursue **DUAL TRACK body scanning** to maximize accuracy and user experience:
- **Consumer path:** iPhone LiDAR/ARKit (at-home scanning)
- **In-store path:** High-quality depth camera kiosk (retail locations)
- **AI enhancement:** Apply AI-powered 3D reconstruction tools to improve scan quality on both tracks

### Details

#### Consumer Path (iPhone LiDAR/ARKit)
- **Method:** Users scan themselves at home using iPhone 12 Pro+ LiDAR sensor with ARKit
- **Timeline:** Primary path for MVP (Weeks 1–4)
- **Quality bar:** <5mm reconstruction error vs. manual measurement
- **Fallback:** Photogrammetry for non-LiDAR iPhones

**Why this:**
- Immediate access (most users have iPhones)
- High friction entry (instant gratification)
- Social sharing potential (AR selfies)

#### In-Store Path (Depth Camera Kiosk)
- **Method:** Structured light or depth camera kiosk installed in retail stores (Zara, H&M, boutiques)
- **Timeline:** Parallel workstream starting Week 3–4
- **Quality target:** **Exceed iPhone accuracy** if feasible (e.g., <3mm error, better fabric texture capture)
- **Scope:** If in-store accuracy can materially outperform iPhone, pursue it. Otherwise, defer to Phase 2.
- **Location:** Start with flagship stores (NYC, London, LA)
- **User journey:** Scan in-store → instant recommendations → try on at home via app → purchase

**Why this:**
- Solves the "chicken & egg" problem (users need scan to try on → can get one in-store)
- Premium experience for fashion-forward customers
- B2B credibility with retailers (we're invested in their locations)
- Data richness (full-body + texture + posture)

#### AI Enhancement (Both Tracks)
- **Tools:** Apply AI-powered 3D reconstruction and mesh refinement
  - NeRF-style reconstruction (novel view synthesis to improve scan from sparse angles)
  - AI mesh enhancement (super-resolution, texture upsampling, artifact removal)
  - Reference: Founder mentioned "nanobabana" — interpret as AI mesh refinement tools
- **Application:** Post-process both iPhone and in-store scans to improve realism
- **Timeline:** Integration begins Week 4–5 (after initial scans generated)
- **Success metric:** Measurable improvement in user fit satisfaction (NPS +1–2 points)

### Implementation Notes

- **3D Scanning Lead brief update** (see Action Items below): Dual track explicitly documented
- **iPhone path:** Primary MVP; in-store path parallel
- **Quality comparison:** Week 4 checkpoint to evaluate in-store accuracy vs. iPhone
- **Decision point:** If in-store accuracy doesn't exceed iPhone by ≥2mm, defer to Phase 2

---

## Decision #2: Zara/H&M Outreach — PREPARE ONLY, DO NOT SEND

### Summary

Develop a **complete go-to-market communications plan** for Zara and H&M **without sending anything yet**. All materials prepared for founder review and approval before any external outreach.

### Details

#### What to Prepare (No External Action Yet)

**Communications Plan Components:**

1. **Contact List**
   - Identify primary targets: Zara sustainability/digital innovation + H&M digital partnerships
   - Secondary: Zara/H&M procurement, product teams
   - Format: Names, titles, emails, LinkedIn profiles, decision-making insights

2. **Messaging Strategy**
   - Core value prop: "Reduce returns by 30%, increase conversion by 15%, own rich body scan data"
   - Tailored angles:
     - **For procurement:** Cost savings via returns reduction
     - **For digital:** Innovation, competitive advantage
     - **For sustainability:** Extended fit reduces waste (overproduction of sizes)
   - Tone: Respectful, data-driven, partner-oriented (not sales-y)

3. **Email Templates** (3 variations)
   - Warm intro via founder/mutual contact
   - Cold outreach (respectful, specific)
   - Follow-up sequence (3 touchpoints, 1 week apart)
   - Each template: <150 words, clear CTA, deck link

4. **Talking Points**
   - 5–7 bullets addressing their known pain points (fit/returns, speed-to-market, data)
   - Competitive context ("Nobody else has done this yet in fashion")
   - Partnership models (API access, garment data sharing, revenue share options)
   - Differentiation from competitors (why us, why now)

5. **Pitch Deck Outline** (30–40 slides)
   - Exec summary (problem, solution, traction)
   - Market size + opportunity
   - How it works (user journey + technical stack)
   - Why Zara/H&M win (data moat, brand partnership, competitive advantage)
   - Financial model (ROI for retailer)
   - Team + vision
   - Ask (partnership terms, investment, support)

6. **Supporting Assets**
   - Case study template (for future pilots)
   - Demo video script (showing AR try-on, body scanning)
   - One-pager (1 page, printable)

#### Constraints

- ✅ **Prepare:** All materials in `/workspace/docs/brand-outreach/` 
- ✅ **Review:** CEO/founder approval gate before any send
- ❌ **DO NOT SEND:** No emails, LinkedIn messages, or outreach until founder says go
- ❌ **DO NOT CALL:** No phone calls or meetings scheduled without explicit approval

#### Why This Approach

- Maximizes impact (quality preparation beats reactive outreach)
- Reduces risk of fumbled first impression
- Gives founder control over timing (may align with product milestone or funding)
- Shows professionalism (we're thoughtful, not desperate)

### Timeline for Preparation

| Task | Owner | Due | Status |
|------|-------|-----|--------|
| Contact list research | Marketing/Ops | 2026-03-20 | Pending |
| Messaging strategy draft | CEO | 2026-03-20 | Pending |
| Email templates | Marketing | 2026-03-22 | Pending |
| Talking points | Product/CEO | 2026-03-22 | Pending |
| Pitch deck outline | CEO | 2026-03-23 | Pending |
| Founder review gate | Founder | 2026-03-25 | Pending |

---

## Decision #3: Test User Recruitment — DUAL APPROACH

### Summary

Test user recruitment combines **founder personal network** + **online community outreach** + **paid advertising** to hit 10–15 qualified beta testers by Week 3.

### Details

#### Channel 1: Founder TikTok Influencer Network (Founder-Led)
- **What:** Founder personally reaches out to fashion influencer contacts on TikTok
- **Target:** 10–20k follower micro-influencers they know
- **Messaging:** Personal intro from founder, early access, launch feature opportunity
- **Timeline:** Week 1–2 (parallel with online outreach)
- **Expected yield:** 3–5 committed testers (high quality, warm referral)

**Why this:**
- Highest NPS potential (founder vetting, trusted intro)
- Best social amplification (influencer + platform default)
- Fastest recruitment (no friction, personal relationship)

#### Channel 2: Online Community Outreach
- **Platforms:** Reddit (r/fashion, r/wardrobe), Discord fashion servers, Twitter/X fashion community
- **Format:** Announcement posts + recruiting threads (organic, not ads)
- **Messaging:** "Beta testing AR body scanning + virtual try-on, join 10 early adopters, free premium + featured on launch"
- **Timeline:** Week 1–2
- **Expected yield:** 5–10 committed testers (good engagement, high opt-in)

**Why this:**
- Large reach (10k–100k potential viewers per post)
- Self-selection (people who comment are already interested)
- Low cost (organic posts only at this stage)
- Rich feedback (Reddit/Discord are more discussion-friendly)

#### Channel 3: Paid Advertising (Contingent)
- **Platforms:** Instagram + TikTok ads (if Channels 1–2 underperform)
- **Budget:** $1,000–2,000 (contingent spend)
- **Target:** Fashion hashtags, lookalike audiences (Instagram fashion followers 22–35)
- **Timing:** Week 2 if organic yield is <5 testers
- **Expected yield:** 5–10 testers (variable quality, requires screening)

**Why this:**
- Backup if organic recruitment slow
- Demographic targeting precision
- Speed to volume

### Success Metrics

| Metric | Target | Timeline |
|--------|--------|----------|
| Recruitment outreach | Founder reaches out to 10+ influencers | Week 1–2 |
| Online posts published | Reddit + Discord + Twitter | Week 1 |
| Applications received | 15–20 applications | Week 2 |
| Qualified testers | 10–15 committed beta testers | Week 3 |
| Geographic mix | 60% US, 40% UK | Week 3 |
| Diversity | XS–L sizes, age 22–35 | Week 3 |
| Retention | 9/10 complete full 3-week beta | Week 6 |

### Implementation

- **CEO/Ops:** Execute online recruitment (Reddit, Discord, Twitter)
- **Founder:** Personal outreach to TikTok influencer contacts
- **Marketing:** Prepare paid ads as contingency
- **Ops:** Track applications, screen, and select final 10 testers

---

## Action Items (Implementation Checklist)

### Immediate (by 2026-03-19)

- [ ] **3D Scanning Lead:** Update brief to include in-store scanning as parallel workstream
  - Include: Founder preference for dual-track, success criteria for in-store (accuracy > iPhone)
  - File: `/workspace/docs/3d-scanning-lead/README.md` + `ROADMAP_AND_DEPENDENCIES.md`
  
- [ ] **Update DISCOVERY.md** to reflect dual-track approach
  - Add in-store kiosk detail to Section 2.1 (Body Scanning Pipeline)
  - Add AI enhancement detail to Section 3 (Tooling Assessment)
  
- [ ] **Update USER-RECRUITMENT.md** to reflect dual-channel strategy
  - Add founder TikTok influencer outreach
  - Clarify Channels 1–3 (founder network + online + ads)
  - Update timeline/expected yield

- [ ] **Create `/workspace/docs/brand-outreach/` structure**
  - Create folder if not exists
  - Placeholder files: `CONTACT-LIST-RESEARCH.md`, `MESSAGING-STRATEGY.md`, `EMAIL-TEMPLATES.md`, `TALKING-POINTS.md`, `PITCH-DECK-OUTLINE.md`

### Week 1–2 (2026-03-20 through 2026-03-27)

- [ ] **CEO:** Finalize messaging strategy for Zara/H&M
- [ ] **Marketing:** Complete contact list research
- [ ] **Marketing:** Draft email templates + talking points
- [ ] **CEO:** Outline pitch deck
- [ ] **CEO/Ops:** Execute online recruitment (Reddit, Discord, Twitter)
- [ ] **Founder:** Reach out to TikTok influencer contacts
- [ ] **Founder:** Review all brand outreach materials for approval before any send

### Week 3+ (Post-Founder Approval)

- [ ] **Founder:** Approve brand outreach materials
- [ ] **Marketing:** Execute approved outreach (email, LinkedIn, calls) per founder authorization
- [ ] **Ops:** Finalize 10 beta testers, send onboarding packages

---

## Cross-Document Updates Required

This decision impacts:

1. **DISCOVERY.md**
   - Section 2.1: Dual-track scanning pipeline
   - Section 3: AI enhancement tooling

2. **USER-RECRUITMENT.md**
   - Section: Recruitment channels (add founder + online + ads strategy)
   - Timeline: Adjust to reflect founder involvement

3. **3D Scanning Lead Brief** (README.md, ROADMAP_AND_DEPENDENCIES.md)
   - Include in-store kiosk as parallel workstream
   - Week 3–4 checkpoint: Compare in-store vs. iPhone accuracy

4. **New: brand-outreach/** folder structure
   - `/workspace/docs/brand-outreach/`
   - Prepare (don't send) all materials

---

## Notes for CEO

- **Dual-track scanning:** Signals founder's confidence in the market + budget for hardware investment. Make sure in-store partner conversations happen in parallel with iPhone MVP.
- **Zara/H&M outreach preparation:** This is smart risk management. A sloppy first impression kills deals. Prepare thoroughly, then wait for green light.
- **Recruitment dual-channel:** Leverages founder's network (credibility) + organic channels (scale) + ads (backup). Best of all three worlds.

---

## Sign-Off

**Decision Made By:** Founder  
**Recorded By:** CEO (Subagent)  
**Date Recorded:** 2026-03-18 17:05 GMT  
**Status:** FINAL — Ready for implementation

---

**Next Review:** End of Week 1 (2026-03-24) to assess progress on all three initiatives.

## GitHub Repository
- Repo: git@github.com:jasonminimac/fashion-tech.git
- Remote: origin (configured 2026-03-18)
- Auth: SSH key ~/.ssh/id_ed25519
- For Phase 1: personal account repo is sufficient; migrate to org if needed later


## Phase 1 Gate — Updated (2026-03-19)

**Principle:** Development does not stop waiting for users. Gate is a quality bar, not a headcount.

### Diabetic AI Phase 1 Gate
- MVP working end-to-end (glucose logging → spike detection → dashboard)
- Founder (Seb) has used it with real CGM data for a meaningful period
- No critical bugs or security holes
- Sandbox Dexcom integration stable (production upgrade deferred)
- Legal review: deferred, not a Phase 1 blocker

### Fashion Tech Phase 1 Gate  
- iPhone scan error <5mm consistently
- Core try-on flow working end-to-end
- Founder (Seb) has tested it and fit accuracy is broadly correct
- If working well, extended to friends/contacts — but dev does NOT wait for this
- Brand partnerships: Phase 2, not a Phase 1 gate
- 20+ external users: nice to have, not a hard gate

