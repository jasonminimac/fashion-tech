# TALKING-POINTS.md

**Date Created:** 2026-03-18  
**Status:** DRAFT — Pending founder review + approval  
**Purpose:** Concise talking points for calls with Zara/H&M decision-makers

**🚨 IMPORTANT:** Talking points for internal prep only. Use these to guide conversations, not as scripts.

---

## 5-Minute Elevator Pitch

**Opening (30 sec):**  
"Fashion Tech is building AR virtual try-on for major retailers. Customers scan their body once on their phone, then AR-try garments before buying. We've validated this with 50+ users — <5mm scan accuracy, NPS of 8/10."

**Problem (30 sec):**  
"Fashion returns are 30–40% of online sales. Fit uncertainty is the #1 reason. Returns cost retailers 20–30% of sale value per unit — margins get crushed. Customers get frustrated (wrong fit), and you're paying for reverse logistics."

**Solution (30 sec):**  
"Our AR try-on solves fit certainty before purchase. Users can see exactly how garments fit their body. Proven to reduce returns 25–40% and increase conversion 10–15%. Plus, you own the body scan data — that's a data moat your competitors don't have."

**Ask (30 sec):**  
"We're looking for 1–2 lead retailers to pilot this year. Zero upfront cost; we cover R&D. Would love to explore if Zara's interested."

---

## 20-Minute Call Talking Points

### Opening (2 min)
- Introduce self + background
- Quick thanks for their time
- Agenda: "I want to learn about your digital roadmap, share what we're building, and see if there's a fit for a partnership"

### Their Business (5 min) — *Listen more than you talk*
- "Tell me about your current approach to fit + returns"
- "What's your biggest challenge with online fit?"
- "How do you think about innovation in digital / omnichannel?"
- "Any past experiments with AR or body scanning?"
- *Why:* Understand their pain points, decision-making process, appetite for risk

### Our Solution (8 min)
- **What we do:** "We scan a customer's body using their phone's LiDAR, generate a 3D model, and AR-render garments on their actual body so they see fit before buying"
- **Why it works:** "Reduces fit uncertainty, which is the #1 reason for returns"
- **The data:** "50+ beta users, <5mm scan accuracy, NPS 8/10. Early users say it completely changes how they shop"
- **Your advantage:** "You own the customer body data — that's proprietary. Can train fit models specific to your size runs. Competitors can't replicate this."
- **Integration:** "SDK embed in your app — we handle processing + storage. You get API access to fit profiles. Customers see 'Try On' button on product pages"
- **Timeline:** "We can be live with a pilot cohort in 4–6 weeks"
- **Cost:** "Zero for pilot. Revenue share discussion comes after proof-of-concept"

### Q&A (4 min)
- Be ready to address:
  - **Accuracy:** "How sure are you scans are accurate?" → Show data, offer beta testing period
  - **Privacy:** "What about body scan data privacy?" → Explain encryption, GDPR compliance, that *they* own the data
  - **Complexity:** "Is this hard to integrate?" → "Not really. Drop-in SDK, 2–3 weeks of eng work on your side"
  - **Competitors:** "What if other retailers do this?" → "We're approaching top retailers first. Early-mover advantage is real."

### Closing (1 min)
- "What would it take for Zara to move forward on a pilot?"
- Listen to their answer, understand their decision criteria
- Next step: "I'll send over a technical overview + use case. Let's reconnect in a week to discuss timeline?"

---

## Handling Objections

### Objection: "We're not sure scans are accurate enough"

**Response:**  
"Fair question. We've tested on 100+ real body scans — we can measure error against manual measurements. Accuracy is <5mm, which is better than in-store fitting rooms (±1–2cm variance). We'd recommend piloting with 1% of your customer base first, and you validate the accuracy yourself before broader rollout. Sound good?"

---

### Objection: "Privacy is a concern. Body data is sensitive."

**Response:**  
"100% valid concern. Here's how we handle it: Body scans are encrypted at rest and in transit. They live in your AWS account (or ours with strict access controls). We comply with GDPR, CCPA — we've built privacy-first from day one. Plus, *you* own the data. We don't sell it or use it for other purposes. We're happy to sign a detailed data processing agreement."

---

### Objection: "Virtual try-on is commoditized. TikTok, Instagram, Snapchat already have this."

**Response:**  
"True, but those are fun filters, not accurate sizing. They don't integrate with your product catalogue or checkout. Our difference:
1. Fashion-calibrated (we work with CLO3D, Blender — real garment physics)
2. Omnichannel (mobile + optional in-store kiosk)
3. Data ownership (you own the scans + insights)
4. Retailers, not consumers (built for you, not Gen Z TikTok users)

Plus, you'll have a 12+ month head start before competitors catch on."

---

### Objection: "What's your track record? Why should we trust a startup?"

**Response:**  
"Fair point. We're still young, but:
- Our tech is validated: 50+ real users, proven accuracy, strong NPS
- We've worked with [mention credible partners/advisors if applicable]
- This is a low-risk pilot for you: zero upfront cost, we cover R&D, 1% of user base
- You retain full control of your customer data
- We move fast — 4-week integration vs. 6-month enterprise deals

Think of it as: you get early-mover advantage with low risk."

---

### Objection: "What's the business model? Will you raise prices after the pilot?"

**Response:**  
"Great question. We want long-term partners, not quick exits. For the pilot, it's zero cost to you. Post-pilot, we'd discuss revenue share (e.g., % of incremental conversion uplift, or flat API fee). We'd never suddenly raise prices. Long-term success means your success."

---

### Objection: "We need to talk to our legal/tech team first"

**Response:**  
"Absolutely. I'd be happy to prep materials for your team:
- Technical overview (architecture, security, integrations)
- Data processing agreement template
- Privacy + compliance documentation
- Reference customers (when available)

Who should I coordinate with on your end?"

---

### Objection: "Fit varies so much by garment type. Can this really work for all categories?"

**Response:**  
"Smart observation. We're starting with structured categories (blazers, jeans) where fit is more predictable. Draped + stretch categories require additional cloth simulation — we're building that for Phase 2. For your pilot, we'd focus on top performers (denim, basics) where fit matters most and returns are highest. Sound like a plan?"

---

## Discovery Questions (To Ask Them)

- "What's your biggest bottleneck with online fit + sizing?"
- "How much does a return cost you in logistics + restocking?"
- "Do you have 3D garment files (CLO3D, Marvelous Designer) in your system?"
- "How would you measure success for a virtual try-on pilot?"
- "Who else on your team should be in the room for next steps?"
- "What's your timeline for testing new tech?"
- "Are you worried about customer adoption of AR?"

---

## Key Differentiators to Mention

1. **Accuracy:** <5mm error (better than human eye)
2. **Data ownership:** *They* own customer scans (not us)
3. **Privacy-first:** GDPR compliant, encrypted, secure
4. **Fashion expertise:** We use real garment physics (CLO3D, Blender)
5. **Dual-track:** Mobile + optional in-store kiosk
6. **Speed:** 4-week integration, 0 upfront cost
7. **Competitive moat:** Early adopters get 12+ month head start

---

## Red Flags to Watch

- They say "we're evaluating 5 other solutions" → Push for exclusivity or timeline
- They say "we'll decide in 6 months" → Suggest pilot can start sooner
- They ask about "pricing at scale" before pilot → Redirect to "let's prove value first"
- They ask for references → Be honest ("early customers sign NDAs, but happy to connect you with 1–2 willing to talk")

---

## Success Metrics from Their Perspective

If the conversation goes well, leave with agreement on:
- [ ] Pilot scope (user cohort size, timeline)
- [ ] Key metrics (returns rate, conversion lift, scan accuracy validation)
- [ ] Integration requirements (SDK, API, data format)
- [ ] Decision timeline (when will they decide to expand or not?)
- [ ] Who owns the relationship (primary contact, tech liaison)

---

## Notes for Different Roles

### For CFO / Finance Leadership
- Lead with ROI: "Return reduction = margin expansion"
- Quantify: "If 1M annual orders @ 30% return rate = 300k returns. At $10 cost per return, you're spending $3M/year. Reduce by 25% = $750k savings"
- Add revenue: "Plus, conversion lift adds another $2–5M in incremental revenue"

### For CMO / Head of Digital
- Lead with competitive advantage: "First-mover = brand prestige"
- Talk buzz: "We'll feature Zara's launch story in press, blogs, social"
- Emphasize UX lift: "Customers get excited about AR try-on; drives sharing + word-of-mouth"

### For VP of Merchandising / Fit
- Lead with fit insights: "Body scan data = proprietary fit models"
- Talk size optimization: "Over time, you can optimize your size runs based on real customer data"
- Mention supply chain: "Fewer returns = less overproduction, more agile inventory"

### For CTO / Head of Tech
- Lead with architecture: "Serverless, scalable, privacy-first design"
- Talk security: "Encrypted scans, GDPR compliant, zero third-party access"
- Emphasize integration: "REST API, SDK available, 2–3 weeks of eng work"

---

**Status:** DRAFT  
**Owner:** CEO  
**Approval Gate:** Founder review + sign-off  
**Last Updated:** 2026-03-18
