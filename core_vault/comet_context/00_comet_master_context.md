# COMET AGENT MASTER CONTEXT
### Atin Sharma — Single Source of Truth for Job Application Automation
> Load this file first. It contains every fact needed to fill any application form field.
> For behavioral free-text or technical deep-dives, also load the referenced specialist files.
> Never invent, guess, or extrapolate values not present in this document.

---

## 1. PERSONAL DETAILS

| Field | Value |
|---|---|
| Full Name | Atin Sharma |
| Email | atinsharma24@gmail.com |
| Phone | +91 82185 02886 |
| Location (City) | Agra |
| Location (State) | Uttar Pradesh |
| Location (Pincode) | 282007 |
| Location (Country) | India |
| LinkedIn | https://www.linkedin.com/in/atinsharma24 |
| GitHub | https://github.com/atinsharma24 |

---

## 2. LOGISTICS & ELIGIBILITY

| Field | Value |
|---|---|
| Notice Period | 0 days — Immediate Joiner |
| Work Authorization | Indian Citizen — no visa sponsorship required |
| Currently Employed | Yes (OpenBiz, ending 20 May 2026) |
| Available From | Immediately / 20 May 2026 |
| Expected CTC | 15L+ (negotiable, no hard ceiling) — INR |
| Current CTC | Not applicable / fresher rate |
| Work Mode Preference | Remote (primary) · Bangalore hybrid (secondary) |
| Open to Relocation | Yes — Bangalore, Hyderabad, Pune, Delhi NCR, Mumbai |
| Remote Setup | MacBook Air M4 — fully equipped home office |
| Preferred Role Types | Full-time · Founding / early-stage |
| Not Preferred | Contract-only · Internship |
| Total Experience | ~12 months (OpenBiz Founding Engineer + VIT Research Contributor) |
| Years of Experience | 1 |

---

## 3. PROFESSIONAL EXPERIENCE

### Role 1 — OpenBiz Software India Pvt Ltd
| Field | Value |
|---|---|
| Title | Founding Engineer |
| Employment Type | Full-time |
| Start Date | June 2025 |
| End Date | May 2026 |
| Duration | ~12 months |
| Work Mode | Remote / Bangalore |
| Team Size | 3 founding engineers |

**Key achievements (use verbatim in free-text fields):**
- Architected zero-to-one MERN platform with strict TypeScript across the stack
- Built VyaparGPT — WhatsApp-native AI assistant deployed to ~40 SMB pilot businesses; handled full webhook → LLM → response delivery with provider fallback and session-aware context
- Built AI document verification module (Google Gemini API) automating extraction from unstructured SMB documents
- Diagnosed and resolved N+1 query patterns in Supabase (PostgreSQL) → **40% reduction in API latency** via indexing and response caching
- Engineered fault-tolerant Razorpay subscription billing with idempotent webhook validation → **100% payment-state consistency**, zero manual reconciliation
- Owned CI/CD pipeline (GitHub Actions + Vercel) → **30% reduction in deployment cycle time**, zero environment-mismatch incidents

---

### Role 2 — Vellore Institute of Technology (Research Contributor)
| Field | Value |
|---|---|
| Title | Research Contributor |
| Type | Academic / Part-time |
| Start Date | January 2025 |
| End Date | November 2025 |
| Duration | 11 months |
| Location | On-campus, Vellore |

**Research topics & contributions:**
- Contributed to research on **Blockchain-Based LLM Model Using Fully Homomorphic Encryption (FHE) for Academic Records** — investigating how FHE enables computation on encrypted student data without decryption, with blockchain providing an immutable audit trail for credential issuance and verification.
- Evaluated architectural trade-offs between on-chain data storage and off-chain encrypted record pointers, assessing gas cost constraints versus data privacy guarantees in an academic credential provenance system.
- Explored how model inference could operate on privacy-preserving representations of sensitive academic data using FHE-compatible cryptographic primitives, without exposing plaintext records.

---

## 4. EDUCATION

### Vellore Institute of Technology
| Field | Value |
|---|---|
| Degree | B.Tech — Computer Science and Engineering |
| Campus | Vellore |
| Start | 2021 |
| End / Graduation | Expecting May 2026 |
| Focus | Full Stack Development, AI Systems |

### Delhi Public School
| Field | Value |
|---|---|
| Level | Secondary / Senior Secondary (Class X & XII) |
| Campus | Agra |

---

## 5. KEY METRICS (use these numbers in application forms)

| Metric | Value | Context |
|---|---|---|
| Platform user scale | 1,000+ active users | MERN platform built at OpenBiz |
| VyaparGPT pilot | ~40 SMB businesses | Initial closed pilot cohort |
| API latency reduction | 40% | N+1 fix + indexing + caching in Supabase |
| Deployment cycle reduction | 30% | GitHub Actions + Vercel CI/CD pipeline |
| Payment consistency | 100% | Razorpay idempotent webhook system |
| Shared infra reuse (Website Builder) | ~60% | Reused auth, Supabase layer, Razorpay billing, CI/CD |
| Zero broken-build incidents | 4 months | Post CI/CD pipeline setup with GitHub Actions + Vercel |
| LeetCode problems | 347+ | Data structures & algorithms practice |
| Team size (OpenBiz) | 3 | Founding technical leads |

---

## 6. PROJECTS

### Nimbus — AI RAG Workspace *(In Development, 2026)*
**Stack:** Next.js, pgvector, Groq API, Prisma, TypeScript  
**GitHub:** github.com/atinsharma24/nimbus  
- Production RAG pipeline: sub-800ms semantic retrieval over multi-format document corpora with streaming LLM responses
- Provider-agnostic LLM layer: one-config switch between Groq, OpenAI, and Anthropic
- Async ingestion with 429 retry logic and per-document status tracking

---

### Autonomous Web Agent *(Open-source side project)*
**Stack:** Python, Claude 3.5 Sonnet, Groq API, OpenClaw, BrowserOS (MCP)  
**GitHub:** github.com/atinsharma24/auto-agent  
- Claude 3.5 Sonnet + MCP orchestration layer translating structured local context schemas into DOM-level form interactions
- Dual-agent: lightweight Groq-based "Watcher" for cost-efficient state-parsing + heavy "Executor" agent for complex interactions
- Local queue management with WAF/CAPTCHA detection and graceful human-escalation

---

### DocGPT — RAG Document Assistant *(Side project)*
**Stack:** React 19, Python (Django), ChromaDB, OpenAI (GPT-4o-mini), Docker  
- Full RAG pipeline: PDF ingestion (PyPDF2) → chunking with overlap → embedding (all-MiniLM-L6-v2) → ChromaDB retrieval → GPT-4o-mini generation

---

### VyaparGPT *(OpenBiz professional product)*
**Stack:** Node.js, OpenAI API, Google Gemini API  
- WhatsApp-native AI business assistant for Indian SMBs
- Full WhatsApp message lifecycle management
- LLM provider-fallback logic (OpenAI → Gemini on 5xx / rate-limit)
- Document verification: Gemini Vision API extracting structured fields from GST certs, invoices, Aadhaar photos

---

### Automated Content Intelligence Pipeline *(OpenBiz professional product)*
**Stack:** React 19, TypeScript, Laravel, Node.js, OpenAI, Gemini, Docker, GitHub Actions, Puppeteer  
- Puppeteer-based scraping bypassing client-side rendering on JS-heavy SPAs
- Dual-model AI rewriting (Gemini primary, OpenAI fallback) per article
- React 19 Diff View for human-in-the-loop editorial review
- Microservices on Docker with GitHub Actions cron scheduling

---

## 7. SKILLS

### Languages
JavaScript/TypeScript · Python · SQL · Java

### Frontend
React.js (v18/v19) · Next.js · React Native · Redux Toolkit · TailwindCSS

### Backend
Node.js · Express.js · NestJS · Django · Laravel

### Databases
PostgreSQL · Supabase · MongoDB · pgvector · ChromaDB · AWS DynamoDB

### AI / LLM
OpenAI API · Google Gemini API · Groq API · Anthropic Claude · RAG Pipelines · LangChain.js · Sentence Transformers (all-MiniLM-L6-v2) · pgvector · ChromaDB · Vercel AI SDK · Prompt Engineering · MCP (Model Context Protocol) · PyPDF2

### DevOps / Cloud
Docker · GitHub Actions · Vercel · AWS S3 · AWS SNS

### Tools
Git · Postman · Socket.IO · Razorpay SDK · VideoSDK · Puppeteer · BrowserOS · OpenClaw

### Patterns
WebSocket (Socket.IO) · REST · Webhook Validation (HMAC-SHA256) · N+1 Query Optimization · Vector Similarity Search (cosine) · Provider-Agnostic LLM Layers · Idempotent Event Processing

---

## 8. STANDARD FORM-FILL ANSWERS

### "Where are you located?"
Agra, Uttar Pradesh, India

### "Are you authorized to work in India?"
Yes — Indian Citizen, no visa sponsorship required.

### "What is your notice period?"
Immediate / 0 days.

### "What is your expected salary / CTC?"
15L+ (negotiable, no hard ceiling).

### "How many years of experience do you have?"
~1 year (12 months as Founding Engineer at OpenBiz Software India Pvt Ltd).

### "Are you open to relocation?"
Yes — open to Bangalore, Hyderabad, Pune, Delhi NCR, Mumbai. Currently based in Agra.

### "Are you currently employed?"
Yes, transitioning — current role ends 20 May 2026.

### "What is your current CTC?"
Fresher-equivalent / not applicable in the traditional sense.

### "LinkedIn URL"
https://www.linkedin.com/in/atinsharma24

### "GitHub URL"
https://github.com/atinsharma24

### "Tell us about yourself" (50–100 words)
I'm a Full-Stack Product Engineer with ~12 months of founding-team experience at OpenBiz, where I built VyaparGPT (a WhatsApp-native AI assistant for Indian SMBs) and a production MERN platform serving 1,000+ active users. I specialize in AI systems — RAG pipelines, LLM orchestration, and conversational AI — alongside strong backend fundamentals: PostgreSQL optimization, CI/CD infrastructure, and billing system design. I'm currently building Nimbus, an open-source RAG document workspace, and have a deep interest in developer tooling and document intelligence.

---

## 9. SPECIALIST FILES (load when needed)

| Use case | File |
|---|---|
| Behavioral / STAR stories (conflict, failure, leadership, etc.) | `../JobApplyFiles/04_behavioral_star_stories.md` |
| Technical architecture deep-dives (RAG, WhatsApp, Puppeteer, MCP agent) | `../JobApplyFiles/03_technical_deep_dive.md` |
| ATS keyword sentences (one sentence per tech for skills fields) | `../JobApplyFiles/05_ats_keyword_dictionary.md` |
| Short-answer / situational Q&A (250-word & 100-word versions) | `../JobApplyFiles/02_situational_qa_library.md` |
| Full logistics & compensation detail | `../JobApplyFiles/06_logistics_mapping.json` |
| Resume routing rules & daily application workflow | `../JobApplyFiles/08_daily_application_roadmap.md` |

---

## 10. PROFILE SNAPSHOT

| Field | Value |
|---|---|
| Availability | Immediate Joiner — 0-day notice period |
| Work Mode | Remote-first; open to Bangalore, Hyderabad, Pune, Delhi NCR, Mumbai |
| Expected CTC | 15–18 LPA (INR) — negotiable for high-ownership roles with equity |
| Work Authorization | Indian Citizen — no sponsorship required |
| GitHub | github.com/atinsharma24 |
| LinkedIn | linkedin.com/in/atinsharma24 |

---

> **COMET USAGE RULES:**
> 1. Never enter values not present in this document or the specialist files.
> 2. For salary fields: always use 15L+ (negotiable, no hard ceiling) unless the form forces a single number → use 1500000 (INR/year) or 15 (LPA).
> 3. For experience in years: use 1.
> 4. For graduation year: 2026.
> 5. For "current employer": OpenBiz Software India Pvt Ltd.
> 6. Skip any application requiring unverifiable details (current CTC in exact rupees, official transcripts, etc.).
> 7. Prefer "Founding Engineer" as title — not "Software Engineer" unless the form forces a generic title.
