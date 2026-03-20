# ZARA-HM-STRATEGY.md — Brand Partnership Outreach

**Document:** Brand Outreach Strategy  
**Targets:** Zara (Inditex) + H&M  
**Objective:** Secure CLO3D assets + partnership agreement for MVP  
**Timeline:** Week 1 outreach → Week 2 discovery calls → Week 3-4 pilot  
**Owner:** CEO + Garments Lead  
**Status:** Ready to execute Monday AM

---

## 🎯 Strategic Objective

Establish early partnerships with **Zara** and **H&M** to:

1. **Validate their 3D asset maturity** — Do they already have CLO3D files? Or photogrammetry scans?
2. **Secure garment data** — Get permission to scan/import their garments into our platform
3. **Build B2B credibility** — Position ourselves as the infrastructure layer for their virtual try-on
4. **Pilot B2B integration** — Run a 4-week pilot with 20-50 garments by Week 5

**Success Definition:**
- ✅ Discovery calls scheduled (Weeks 2)
- ✅ CLO3D/3D asset pipeline understood
- ✅ Pilot garments identified (20-50 items)
- ✅ Framework NDA + data sharing agreement signed

---

## 🏢 Why Zara & H&M First?

| Brand | Why | Advantages | Risk |
|-------|-----|-----------|------|
| **Zara** | Inditex: most digitally mature fast-fashion | Already use 3D tools, global scale, prestige | Complex org, slow decisions |
| **H&M** | Pioneer of sustainability + digital retail | Digital-first culture, fast iteration, friendly | Smaller PLT, lower budgets |

**Both:** Mature enough to have 3D pipelines. Large enough to justify partnership resources. Fashion-forward enough to care about innovation.

---

## 📋 Outreach Materials (Ready to Send Monday AM)

### Email Template 1: Discovery Outreach

**Subject:** Virtual Try-On Infrastructure — Fashion Tech Partnership Opportunity

```
Hi [Name],

We're building the infrastructure layer for virtual fashion try-on powered by 3D body 
scanning + AI. We're talking to forward-thinking retailers who are ready to reduce returns 
and delight customers with perfect fit.

You likely already have:
- 3D garment assets (CLO3D, Marvelous Designer, or photogrammetry)
- A vision for omnichannel virtual try-on
- Pressure to reduce return rates

We have:
- Body scanning (iPhone LiDAR + photogrammetry)
- AR try-on (iOS + web)
- API for your app/site integration
- Data ownership model you'll love (you never own the scan, we manage privacy)

Would you be open to a 30-45 min call next week to explore?

Best,
[CEO Name]
Fashion Tech
```

### Email Template 2: Follow-Up (After Discovery Call)

**Subject:** Summary — Zara + Fashion Tech Virtual Try-On Partnership

```
Hi [Name],

Thanks for the great call. Here's what we agreed:

1. CLO3D asset sharing: You'll provide [X] garments in .zprj format
2. Pilot timeline: 4 weeks, 20-50 garments, web + iOS
3. Data governance: We own scans; you get fit-profile API only
4. Success metrics: [defined on call]

Next steps:
- [You]: Legal review of data sharing agreement (attached template)
- [Us]: Set up import pipeline for your garment formats
- Schedule: Follow-up sync in 1 week (Mar 25)

Looking forward!
Best,
[CEO Name]
```

### Email Template 3: Asset Submission Request

**Subject:** Garment Submission — Fashion Tech Virtual Try-On Pilot

```
Hi [Name],

We're ready to import your garments. Here's the submission process:

FORMAT OPTIONS (pick one):
1. CLO3D .zprj + .zpac files (ideal — we have native import)
2. FBX + textures (fallback — we'll set up CLO3D internally)
3. Photogrammetry scans (we'll convert to 3D)

SUBMISSION CHECKLIST:
□ Garment files (format: [selected above])
□ Size range (XXS-XL and size variants)
□ Fabric type (silk, cotton, denim, stretch, etc.)
□ Fit notes (slim fit, regular, relaxed, oversized)
□ Care/maintenance (we need this for VR rendering)

Upload to: [S3 presigned URL]

Questions? Reply or book a call.
Best,
[Garments Lead]
```

### Email Template 4: Pilot Results (Week 5)

**Subject:** Pilot Complete — Virtual Try-On Results + Partnership Proposal

```
Hi [Name],

We completed the 4-week pilot with your garments. Results:

METRICS:
- 25 garments live in our platform
- Average upload → live time: 2 days
- Fit accuracy (vs. in-store try-on): 87%
- Return rate projection: -15% (internal modeling)

NEXT PHASE:
- Scale to 500+ garments by Q2
- SDK integration into your app (3-week dev)
- Revenue share model (we split return savings)

Can we schedule a call to discuss Phase 2?
Best,
[CEO Name]
```

### Email Template 5: Contingency (If Partner Hesitates)

**Subject:** Quick Question — Virtual Try-On Feasibility Study

```
Hi [Name],

I know you're cautious about new partners. We get it. 

Quick asks to move forward:
1. 30-min call with your 3D/product team (I'll share tech spec first)
2. 5 sample garments to test our pipeline (no commitment)
3. Legal to review our standard data-sharing template

This gives you zero risk to evaluate.

Available [dates]?

Best,
[CEO Name]
```

---

## 📞 Discovery Call Script (30-45 min)

**Pre-Call Prep (send 48h before):**
- Tech summary one-pager
- Data governance doc
- Reference customer quote (or use competitor pressure angle)

**Call Structure:**

### Part 1: Context Setting (5 min)
*"Hi [Name]. Thanks for taking time. Quick context: we're building the consumer-facing infrastructure for virtual try-on. The key insight is **you already have the hard part solved — the 3D garments and fit algorithms. We're the distribution layer.**"*

### Part 2: Discovery Questions (20 min)

**Q1-3: Current State**
- Q1: "What's your current 3D asset status? Do you have CLO3D, Marvelous, or photogrammetry in-house?"
- Q2: "Which teams own those assets? (Design, Sourcing, Digital?)"
- Q3: "Have you tried virtual try-on before? What happened?"

**Q4-6: Pain Points**
- Q4: "What's your top priority right now? (Returns? Fit? International sizing?)"
- Q5: "If you could reduce returns by X%, what would that be worth?"
- Q6: "What's blocking you from launching virtual try-on today?"

**Q7-9: Our Fit**
- Q7: "Are you open to an outside partner handling the scanning/AR layer?"
- Q8: "How do you think about data ownership? (i.e., do you need to own customer scans?)"
- Q9: "What's your timeline? (weeks? months?)"

**Q10-12: Partnership Terms**
- Q10: "Would you be interested in a pilot? (4 weeks, 20-50 garments, zero cost to you?)"
- Q11: "What would success look like for you? (metrics, timelines?)"
- Q12: "Who else should we talk to in your org? (Legal, Digital, Merchant?)"

### Part 3: Proposal (10 min)
*"Based on this, here's what we propose: **4-week pilot with 20 of your bestselling items. We'll handle the scanning/import; you validate fit accuracy. If it works, we scale to 500+ SKUs and integrate into your app.**"*

**Timeline:**
- Week 1 (now): Asset submission
- Week 2: Upload + QA
- Week 3: Fit testing
- Week 4: Results + decision

**Cost to You:** Zero (we cover everything)

**Our Ask:** 
- 20 garments in CLO3D or FBX
- Access to your fit data (anonymized)
- Permission to use results in marketing (redacted)

### Part 4: Next Steps (5 min)
- ✅ If interested: Schedule kick-off call with [Garments Lead] + [their 3D/Digital lead]
- ✅ Send data-sharing agreement template
- ✅ Get legal/procurement intro

---

## 🎯 CLO3D Maturity Assessment

**After discovery call, score each brand on 3 dimensions:**

### Dimension 1: Asset Readiness (Score: 1-5)

| Level | Description | Zara Signal | H&M Signal |
|-------|-------------|-------------|-----------|
| **1: None** | No 3D assets | Not expected | Not expected |
| **2: Exploratory** | <20% of catalogue; experimental | Possible (legacy) | Possible (legacy) |
| **3: Production** | 30-60% of catalogue; CLO3D active | **Most likely** | Likely |
| **4: Mature** | 80%+ of catalogue; CLO3D native | Possible (luxury line) | Unlikely |
| **5: Enterprise** | 100% + real-time physics sims | Unlikely (complexity) | Unlikely |

**Scoring Question:** "Which % of your product catalogue already exists as a 3D file?"

### Dimension 2: Organizational Readiness (Score: 1-5)

| Level | Description | Signal |
|-------|-------------|--------|
| **1: No** | No 3D team; CAD is foreign | "We don't have anyone who knows this stuff" |
| **2: Silos** | 3D team exists but isolated (design only) | "Our design team uses CLO3D but procurement doesn't" |
| **3: Connected** | 3D team + partnerships (1-2 retailers) | "We've done virtual try-on pilots before" |
| **4: Integrated** | 3D assets flow across org; used by retail | "Our apps already show 3D models" |
| **5: API-Native** | 3D data exported + accessed via API | "We have a 3D asset management system" |

**Scoring Question:** "How integrated are your 3D assets across teams?"

### Dimension 3: Speed of Execution (Score: 1-5)

| Level | Description | Signal |
|-------|-------------|--------|
| **1: Slow** | Procurement-heavy; >6 months for pilots | Zara size + legacy processes |
| **2: Cautious** | Legal + data concerns; 3-4 month pilots | Large org, privacy-first |
| **3: Balanced** | Pilot possible in 4-6 weeks | H&M typical; digital-forward |
| **4: Fast** | Fast-track pilots; <2 weeks setup | Startup-like mentality |
| **5: Agile** | Realtime iteration; daily deployments | Tech/DTC brands only |

**Scoring Question:** "How quickly can you move on a pilot project?"

---

## 📊 Post-Call Assessment Matrix

**Score each brand (1-5 per dimension):**

| Brand | Asset Readiness | Org Readiness | Speed | **Total** | Recommendation |
|-------|-----------------|---------------|----|----------|-----------------|
| Zara | 4 | 3 | 1 | **8** | Pursue (assets ✅, slow org ⚠️) |
| H&M | 3 | 4 | 3 | **10** | Pursue hard (balanced + fast) |

**Scoring Guide:**
- **10+:** High-value partner — prioritize
- **7-9:** Worth pursuing but manage expectations
- **<7:** Low fit — defer or pass

---

## 🤝 Partnership Framework (Post-Pilot)

**If pilot succeeds, propose:**

### Deal Structure
```
Technology: We handle body scanning + AR
You handle: Garment assets + marketing
Revenue: [TBD] split of reduce-return savings
Term: 12 months exclusive pilot, then exclusive partner discussion
```

### API Access
- Retailers get `/fit-recommendations` endpoint (fit profile + size suggestions)
- **They never see:** Raw mesh, point cloud, or unprocessed scan data
- **They get:** Derived insights only (fit profile, size preference, etc.)

### SLA
- Garment upload → live: 2 business days
- Fit accuracy: 85%+ vs. in-store
- Uptime: 99.5%

### Data Governance
- **We own:** Body scan data (encrypted, GDPR/CCPA compliant)
- **They own:** Their garment specifications + fit feedback
- **Both:** Anonymized aggregate insights (trend data, fit patterns)

---

## 📅 Outreach Timeline

**Week 1 (Now):**
- Monday AM: Send discovery emails (Zara + H&M)
- Tuesday-Wed: Follow-ups (phone/LinkedIn)
- Thursday: Confirm 1-2 calls booked for Week 2

**Week 2:**
- Mon-Tue: Discovery calls
- Wed-Fri: Assessment + pilot proposal sent

**Week 3:**
- Mon: Legal review (NDA, data sharing)
- Tue-Wed: Asset submission from partners
- Thu-Fri: Import pipeline testing

**Week 4-5:**
- Weeks 4: Pilot execution (fitting, testing)
- Week 5: Results + Phase 2 proposal

**Week 6+:**
- Ongoing: Partner support + scale

---

## 🎯 Success Metrics

**Week 2 (Discovery):**
- ✅ 1-2 calls completed
- ✅ CLO3D maturity assessed
- ✅ Pilot interest confirmed

**Week 4 (Pilot Kickoff):**
- ✅ 20-50 garments submitted
- ✅ Import pipeline tested
- ✅ Legal agreement signed

**Week 5 (Pilot Results):**
- ✅ Fit accuracy: 85%+
- ✅ Upload time: <2 days per garment
- ✅ Partner satisfaction: >8/10 (NPS)

**Week 6+ (Phase 2):**
- ✅ Scale to 500+ garments
- ✅ SDK integration underway
- ✅ Revenue share agreement finalized

---

## 🚀 Go/No-Go Decision (Week 4)

**GO if:**
- ✅ Both brands submitted pilot garments
- ✅ Legal agreements signed
- ✅ Import pipeline handles their file formats

**NO-GO if:**
- ❌ Either brand declines or slow-walks (>8 weeks to pilot)
- ❌ Data governance dead-end (they won't accept our terms)
- ❌ Asset quality issues (CLO3D files corrupt or incompatible)

**Pivot Plan (if no-go):**
- Use photogrammetry to scan garments internally
- Seek smaller/startup brands (DTC, marketplace sellers)
- Launch MVP with internal test garments only (still viable, less impressive at launch)

---

## 📁 Artifacts

**Send to Zara/H&M (attached to email):**
- `PARTNER_OUTREACH_STRATEGY.md` (this file)
- `DATA_GOVERNANCE_TEMPLATE.md` (legal framework)
- `TECH_SPEC_ONE_PAGER.md` (what we build)
- `PILOT_SLA.md` (commitments)

**Internal Tracking:**
- `partner_calls_log.md` (call notes + scores)
- `partner_status.md` (real-time tracker)

---

**Outreach Owner:** CEO + Garments Lead  
**Status:** Ready to execute Monday 09:00 AM GMT  
**Last Updated:** 2026-03-18 16:53 GMT
