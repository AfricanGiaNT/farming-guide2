---
title: "Mlangizi wa Ulimi – Business Plan (Final)"
author: "Solo Founder"
date: "October 2025"
subject: "Business Plan"
keywords: [Agriculture, AI, Malawi, Weather, Farmers, Partnerships]
geometry: margin=1in
fontsize: 11pt
linkcolor: blue
toc: true
toc-depth: 2
css: business_plan_theme.css
header-includes:
  - \usepackage{xcolor}
  - \definecolor{Primary}{HTML}{1A936F}
  - \definecolor{Secondary}{HTML}{114B5F}
  - \setlength{\parskip}{6pt}
  - \hypersetup{colorlinks=true, linkcolor=Secondary, urlcolor=Secondary}
---

# Cover

# Mlangizi wa Ulimi

### AI‑Powered Farming Guide for Malawi

**Tagline:** "Your AI‑Powered Farming Partner for Eastern Africa"  
**Funding Request:** MWK 7,200,000 ($4,000)  
**Contact:** trevorchimtengo2@gmail.com • +2650990845264 • Lilongwe, Malawi

\newpage

# Executive Summary

## Opportunity
- 20–30% of maize production is lost annually due to storage, handling, and pests.
- 70% of reported crop damage is attributed to climate variability.
- Farmers lack localized, timely, and actionable guidance for weather, varieties, and timing.

## Solution
Mlangizi wa Ulimi is a free, web‑based platform that combines AI + real‑time weather with a Malawi‑specific knowledge base to deliver practical, localized farming guidance.

## Market Potential
- Target: 750 users by Year 2; 1,500 by Year 3.
- Model: Traffic‑based B2B partnerships (seed companies, cooperatives, inputs) – farmers pay nothing.

## Funding Impact (requested MWK 7,200,000 / $4,000)
- Complete infrastructure, optimize APIs, and harden the platform.
- Execute initial marketing setup and partnership acquisition.
- Achieve break‑even by Month 12 (first partnership).

## Headline Financials (consistent and finalized)
- Year 1 revenue: MWK 315,000 (Q4 start, 300 users, 1 partnership).
- Year 2 revenue: MWK 11,677,500 (scaling to 3 partnerships and 750 users by Q4).
- Year 2 profit: MWK 8,977,500 (76.9% margin), given annual costs about MWK 2,700,000.
- Break‑even: Month 12 (with 1 partnership at 300+ users).

\newpage

# 1. Market Analysis

## 1.1 Size & Segments
- Malawi population ~20.4M; ~3.1M smallholder farmers.
- Initial target: 750+ users by Year 2 (~0.024% of smallholder farmers).
- Primary users: smallholder farmers with smartphones; secondary: extension workers; tertiary: cooperatives.

## 1.2 Competitive Landscape (Malawi/Region)
- Ulangizi (WhatsApp chatbot), PlantVillage (disease focus), SeedCo App (static info), WeFarm (SMS). Most lack combined AI + weather + Malawi‑specific variety matching via a free web experience.

## 1.3 Trends & Constraints
- Growing smartphone adoption; climate variability; strong interest in digital ag.
- Constraints: intermittent internet, limited digital literacy; addressed through mobile‑first UI and concise outputs.

\newpage

# 2. Product & Technology

## 2.1 Core Features
- Weather‑integrated recommendations (current + forecast + historical).
- AI‑powered crop and variety guidance (Malawi‑specific, cached for cost control).
- Knowledge base search (FAISS + embeddings) from local agronomic sources.
- Mobile‑first web app; no installation needed; PWA‑ready.

## 2.2 Architecture
- Frontend: React 18 + TypeScript, Tailwind, Chart.js.
- Backend: Python (Flask), REST APIs.
- Data: PostgreSQL (prod), SQLite (dev), FAISS vectors for semantic search.
- Integrations: OpenWeather, OpenAI, Google (location).
- Cost controls: response caching; 6‑hour variety cache; local vector search.

## 2.3 Differentiators (practical, not hype)
- Free for farmers; Malawi‑specific guidance; AI + weather in one place; web‑first.

\newpage

# 3. Business Model

## 3.1 Traffic‑Based Partnership Fees (B2B)
- Seed Companies: MWK 180,000 base + MWK 18,000 per 100 active users.
- Cooperatives: MWK 90,000 base + MWK 9,000 per 100 active users.
- Input Suppliers: MWK 112,500 base + MWK 11,250 per 100 active users.

Farmers pay MWK 0. Partners pay to reach engaged traffic via contextual placements.

## 3.2 Go‑to‑Market (free channels first)
- Facebook and WhatsApp groups; extension‑worker advocacy; cooperative partnerships.
- One‑time setup budget for assets/tools; ongoing activities rely on free channels.

\newpage

# 4. Financials (Final, consistent)

## 4.1 User Growth Targets
- Year 1 Q4: 300 users (first partnership).
- Year 2 Q4: 750 users (3 partnerships).
- Year 3 Q4: 1,500 users (5 partnerships).

## 4.2 Revenue Projections (by quarter, Year 2)
- Q1: 1 partnership, 400 users → MWK 1,080,000
- Q2: 2 partnerships, 550 users → MWK 2,835,000
- Q3: 2 partnerships, 650 users → MWK 3,510,000
- Q4: 3 partnerships, 750 users → MWK 4,252,500
- Year 2 Total: MWK 11,677,500

## 4.3 Cost Structure
- Fixed infrastructure + APIs: ~MWK 2,400,000/year.
- Ongoing marketing: MWK 0/month (free channels only).
- Legal (Y1 one‑time): MWK 300,000.

## 4.4 P&L Snapshot
| Metric | Year 1 | Year 2 | Year 3 |
|---|---:|---:|---:|
| Users (Q4) | 300 | 750 | 1,500 |
| Partnerships (Q4) | 1 | 3 | 5 |
| Revenue | 315,000 | 11,677,500 | 22,680,000 |
| Costs | 2,700,000 | 2,700,000 | 3,000,000 |
| Net Profit | -2,385,000 | 8,977,500 | 19,680,000 |
| Profit Margin | n/a | 76.9% | 86.8% |

Notes: Year 1 reflects Q4 start; Year 2 uses quarterly ramp; Year 3 scales users/partners.

## 4.5 Break‑Even & Sensitivity
- Break‑even: Month 12 with 1 partnership (~300+ users).
- Ultra‑Conservative (Y2): 400 users, 1 partnership → Revenue 3,024,000; Profit 324,000; BE achieved.
- Conservative (Y2): 750 users, 2 partnerships → Revenue 5,670,000; Profit 2,970,000.

\newpage

# 5. Implementation Plan (Solo‑friendly)

## Phase 1–3 (Months 1–8): Stabilize & Launch
- Harden API integrations, vector search, and caching; mobile UX polish.
- Soft launch via free channels; gather farmer feedback; iterate.

## Phase 4 (Months 9–12): Partnership & Break‑Even
- Scale to 300+ users; secure first seed‑company partnership; reach break‑even.

## Phase 5 (Months 13–18): Growth & Optimization
- Add second partnership; improve recommendation quality and data ergonomics.

## Phase 6 (Months 19–24): Sustainability & Planning
- Reach ~750 users; expand to 3 partnerships; prepare for Year‑3 scale.

\newpage

# 6. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Intermittent internet | High | Caching, concise payloads, PWA patterns |
| Solo‑founder load | High | Focus on core scope; automate; defer non‑essential features |
| API cost drift | Medium | Aggressive caching; prompt/token discipline; usage monitoring |
| Competition | Medium | Local focus; partnerships; UX speed; credible results |
| Regulatory changes | Medium | Minimal PII; transparent data handling; legal updates |

\newpage

# 7. Partnerships

## Targets & Pricing (summary)
- Seed companies: MWK 180,000 base + MWK 18,000 per 100 users.
- Cooperatives: MWK 90,000 base + MWK 9,000 per 100 users.
- Inputs: MWK 112,500 base + MWK 11,250 per 100 users.

## Roadmap (18–24 months)
- Month 12: 1 seed company active (BE achieved).
- Month 18: 2 partnerships active.
- Month 24: 3 partnerships active (seed + coop + inputs).

\newpage

# 8. Technology Differentiation (Realistic)

- AI where it counts (retrieval + summarization), not hype.
- Weather‑aware guidance embedded into flows.
- Local knowledge base (Malawi‑specific) with semantic search.
- Free web access; mobile‑first; zero‑install; optimized responses.

\newpage

# 9. Marketing Approach (Clarified)

## Initial Setup (one‑time, funded)
- MWK 1,200,000 for content assets, group tools, partnership collateral, and community seeding.

## Ongoing Operations (month‑to‑month)
- MWK 0 using free Facebook/WhatsApp channels, referrals, and extension‑worker advocacy.

\newpage

# 10. Social Impact

- 750+ farmers supported by Year 2; 1,500+ by Year 3.
- Potential 5–10% yield improvement for engaged users.
- Economic impact via improved timing/variety decisions and reduced losses.

\newpage

# 11. Conclusion

Mlangizi wa Ulimi is a pragmatic, Malawi‑focused, AI + weather farming guide. The model is free for farmers and funded by traffic‑based partnerships. With a modest setup budget and disciplined operations, the plan reaches break‑even by Month 12 and scales sustainably to 750 users and 3 partnerships by Year 2.

\newpage

# Appendix A – Financial Tables (Detail)

## A.1 Year 2 Quarterly Detail (Revenue)
| Quarter | Partnerships | Users | Revenue (MWK) |
|---|---:|---:|---:|
| Q1 | 1 | 400 | 1,080,000 |
| Q2 | 2 | 550 | 2,835,000 |
| Q3 | 2 | 650 | 3,510,000 |
| Q4 | 3 | 750 | 4,252,500 |
| Total | – | – | 11,677,500 |

## A.2 Yearly Summary
| Year | Users (Q4) | Partnerships (Q4) | Revenue | Costs | Net Profit |
|---|---:|---:|---:|---:|---:|
| 1 | 300 | 1 | 315,000 | 2,700,000 | -2,385,000 |
| 2 | 750 | 3 | 11,677,500 | 2,700,000 | 8,977,500 |
| 3 | 1,500 | 5 | 22,680,000 | 3,000,000 | 19,680,000 |

\newpage

# Appendix B – References (Selected)

- FAISS: Efficient Similarity Search (Facebook AI Research).
- OpenAI Embeddings & GPT API documentation.
- Malawi agriculture and climate articles (IFPRI, World Bank, peer‑reviewed).


