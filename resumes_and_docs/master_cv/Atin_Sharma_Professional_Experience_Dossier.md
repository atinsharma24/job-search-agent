# ATIN SHARMA — PROFESSIONAL EXPERIENCE DOSSIER

**Full-Stack Engineer | AI Systems · RAG Pipelines · LLM Agents · AI-Native Development**

atinsharma24@gmail.com | +91 82185 02886
[github.com/atinsharma24](https://github.com/atinsharma24/) | [linkedin.com/in/atinsharma24](https://www.linkedin.com/in/atinsharma24/)
Agra, Uttar Pradesh, India — Remote-first, open to relocation

> **Private working document.** Long-form reference for interview preparation, detailed
> application forms, and cover-letter assembly. Not for direct submission — the one-page
> submission artifact is `resumes_and_docs/categories/pdf/Atin_Sharma_Resume_2026.pdf`.
>
> **Confidentiality note:** The AGI Ready engagement is governed by a one-way NDA and a
> 12-month non-compete/non-solicitation clause. Client names, product specifics, codebase
> details, and commercial terms must **not** be disclosed in applications, interviews, or
> public writing. Describe the work generically — stack, architecture patterns, and
> ownership scope only.

---

## 1. POSITIONING SUMMARY

Full-stack engineer with production ownership across two startups back-to-back: founding
engineer at OpenBiz Software India (Jun 2025 – May 2026), where I was one of three technical
leads shipping two commercial AI products from zero to 1,000+ active Indian SMB users, and
currently full-stack developer at AGI Ready Inc. (Jun 2026 – present), a Delaware-incorporated
AI-native development studio, building client products in Next.js/TypeScript/Node.js.

My depth is in the seam between application engineering and applied AI: production RAG
pipelines (pgvector, ChromaDB, Pinecone), provider-agnostic LLM layers with failover
(OpenAI ↔ Gemini ↔ Groq ↔ Anthropic), agentic orchestration over MCP, and the unglamorous
reliability work that makes them survive real traffic — idempotent webhook processing,
N+1 elimination, composite indexing, TTL caching, and approval-gated CI/CD.

I work AI-natively: Claude Code and Codex are my primary development tools, used with
architectural judgement rather than prompt-level iteration.

**VIT Vellore, B.Tech Computer Science & Engineering** — coursework completed Nov 2025,
degree conferred May 2026.

---

## 2. CURRENT ENGAGEMENT FACTS

Sourced from `atin-sharma-offer-letter.pdf` (AGI Ready Inc. Independent Contractor
Engagement Letter, dated 3 July 2026).

| Field | Value |
|---|---|
| Company | AGI Ready Inc. — Delaware C-Corporation, AI-Native Development Studio |
| Role (as contracted) | Full-Stack Developer — Pathways Program |
| Role (as presented on resume) | Full-Stack Developer |
| Engagement type | Independent Contractor |
| Work arrangement | Full-time, Remote |
| Reporting to | Amardeep Singh Pal, CEO |
| Contract start date | 2 July 2026 |
| Date presented on resume | June 2026 *(per candidate instruction)* |
| Probation | 3 months — 2 Jul 2026 to 1 Oct 2026 |
| Compensation — months 1–3 | ₹50,000/month (₹6.00 LPA annualised) |
| Compensation — month 4 onward | ₹70,000/month (₹8.40 LPA annualised), from 2 Oct 2026 |
| Performance bonus | Up to 20% of annual compensation, discretionary |
| Notice period owed by candidate | **30 days'** written notice per §9.2 (waivable at AGI Ready's discretion) |
| Notice period quoted on applications | **15 days** *(candidate decision — see note below)* |
| Post-probation upside | Possible conversion to full-time employment + ESOP eligibility (statement of intent only, not a grant) |
| Restrictive covenants | One-way NDA; 12-month non-compete limited to AGI Ready clients and directly competing AI dev studios; 12-month non-solicitation |

### Figures quoted on applications — candidate decisions

These are now synced across every file in the vault (`CLAUDE.md`, `AGENTS.md`, `INVOKE*.md`,
both canonical JSONs, all comet-context prompts, all resume templates).

| Field | Value quoted | Reconciliation against the contract |
|---|---|---|
| Notice period | **15 days** | Contract §9.2 requires 30 days. 15 is achievable only if AGI Ready waives part of the notice, which §9.2 permits at their discretion. Treat as a negotiating position, not a guarantee. |
| Current CTC | **11.2 LPA** | The letter gives ₹8.4 LPA base post-probation + up to 20% discretionary bonus = **₹10.08 LPA at maximum**. 11.2 is above what the letter supports; be ready to substantiate if a payslip or offer letter is requested during background verification. |
| Expected CTC | **18–24 LPA**, 18 stated as the floor | Roughly a 1.6× step on stated current CTC — a normal ask. |
| Walk-away minimum | **15 LPA — PRIVATE** | Never disclose, never write down in a form or message. This exists so you know when to stop negotiating, not as a number anyone else sees. Quoting it converts your floor into their ceiling. |

> The non-compete is narrow — it explicitly does **not** prevent you working as a software
> developer generally or freelancing for non-competing clients — so the job search itself is
> unaffected.

**Also accurate:** remote-first with relocation openness to Bangalore / Hyderabad / Pune /
Delhi NCR / Mumbai; Indian citizen — no sponsorship required; ~14 months total professional
experience, currently employed (**never answer "fresher"** — the vault previously instructed
exactly that, now corrected).

---

## 3. KEY METRICS

| Metric | Value | Metric | Value |
|---|---|---|---|
| API latency reduction | **40%** | Platform active users | **1,000+** |
| Deployment cycle reduction | **30%** | VyaparGPT SMB pilot | **40 businesses** |
| Shared infra reuse (Website Builder) | **~60%** | LeetCode problems solved | **347** |
| Founding team size | **3 engineers** | Broken-build incidents post-CI/CD | **0 over 4 months** |
| Payment-state consistency | **100%** | Nimbus semantic retrieval | **sub-800ms** |

---

## 4. PROFESSIONAL EXPERIENCE

### 4.1 AGI Ready Inc. — Full-Stack Developer
**Jun 2026 – Present · Remote · Delaware, US**

AI-native development studio building custom AI products, automation, and agent systems for
clients. Small team reporting directly to the founder/CEO.

> **Scope of engagement** — the following is drawn from the contracted Scope of Work. It
> describes owned responsibilities, not retrospective achievement claims. Replace with
> specific shipped outcomes and metrics as the engagement matures; that is the single
> highest-value upgrade available to this document.

- **Full-stack feature delivery.** Build and ship product features end-to-end in
  **Next.js, TypeScript, and Node.js** across multiple concurrent client products, working
  directly with the founder and a tight delivery team.
- **API and integration architecture.** Design and integrate service APIs spanning
  third-party platforms, AI/LLM provider APIs, webhook receivers, and asynchronous
  background workflows — the same integration surface I owned at OpenBiz (WhatsApp Business
  API, Razorpay webhooks, dual-provider LLM dispatch), applied across a client portfolio.
- **AI-native development practice.** Operate with **Claude Code and Codex** as primary
  development tools — decomposing problems, directing agentic tooling with architectural
  judgement, and reviewing generated code against production standards, rather than
  prompt-level iteration.
- **Production ownership.** Debug, deploy, and own production systems end-to-end.
- **Ambiguity-to-delivery.** Break complex, loosely-specified client problems into scoped
  deliverables and ship iteratively. Per the engagement letter: *"You will not be handed
  perfect tickets. You will be handed problems and trusted to solve them."*

**Interview framing:** this role is the deliberate next step after founding-engineer work —
same end-to-end ownership, but across a portfolio of client problems rather than a single
product, with AI-native tooling as a first-class part of the engineering practice.

---

### 4.2 OpenBiz Software India Pvt Ltd — Founding Engineer
**Jun 2025 – May 2026 · Remote / Bangalore**

One of three founding technical leads responsible for architecting and shipping two
AI-powered SaaS products for the Indian SMB market.

- **Architected VyaparGPT**, a WhatsApp-native LLM assistant in Node.js: designed the full
  message lifecycle (WhatsApp Business API webhook ingestion → HMAC signature validation →
  session context lookup → LLM dispatch → response delivery), serving 40+ businesses in a
  closed SMB pilot and scaling to 1,000+ active platform users. Implemented multi-turn
  conversational context via a rolling `conversation_history[]` window, enabling natural
  follow-up queries without context re-statement.
- **Engineered LLM provider-failover** (OpenAI → Google Gemini) at the API layer: on HTTP
  5xx, 429 rate-limit, or configurable timeout, requests reroute transparently to the
  secondary provider with response-shape normalisation — no failure surface exposed to users.
- **Built an LLM-powered document verification module** using the Gemini Vision API to
  extract structured fields (GST number, business name, invoice amount, dates) from
  photographs of GST certificates and vendor agreements sent through WhatsApp — eliminating
  a manual, agent-driven data-entry step in SMB onboarding.
- **Engineered a parallel Graph RAG pipeline** with LangGraph state machines, routing user
  queries into asynchronous multi-threaded retrieval paths to reduce end-to-end token latency.
- **Built a dual-database ingestion router** (Drizzle ORM) streaming large-scale business
  datasets into **Pinecone** (hybrid dense/sparse search) for unstructured content and
  **Supabase/pgvector** for structured compliance data — partitioning by data shape rather
  than forcing a single store.
- **Designed runtime evaluation guardrails** intercepting Cohere Re-rank v3 cross-encoder
  scores: an absolute `< 0.4` confidence threshold hook dynamically overrides system prompts
  to enforce strict context-locking and suppress hallucination.
- **Resolved critical N+1 query patterns** in the Supabase (PostgreSQL) layer: rewrote ORM
  calls to JOIN-based queries, introduced composite indexes on high-frequency WHERE/JOIN
  columns, and added TTL-based response caching for read-heavy stable endpoints — a verified
  **40% reduction in API latency** at 1,000+ user scale.
- **Built and owned the GitHub Actions + Vercel CI/CD pipeline** from scratch: automated
  testing on every PR, environment-consistent staging deploys on merge to main, production
  gated behind explicit approval. Introduced branch protection, PR description standards,
  and a shared deployment checklist — **30% reduction in deployment cycle time** and
  **zero direct-to-main broken-build incidents** over four subsequent months.
- **Implemented idempotent Razorpay subscription billing**: HMAC webhook validation,
  payment-state reconciliation, and out-of-order event handling via a re-entrant idempotency
  check that re-queries the Razorpay API on every `payment.captured` regardless of prior
  subscription state — **100% payment-state consistency** across all paying customers.
- **Delivered the Automated Content Intelligence Pipeline**: Puppeteer scraping, TypeScript
  normalisation, dual-model AI rewriting with failover, React 19 diff-view editorial
  approval, and Dockerised microservices on a GitHub Actions cron.
- **Shipped a parallel Website Builder product** in a 6-week window alongside active
  VyaparGPT development with zero additional engineers, by auditing and reusing **~60%** of
  shared infrastructure (auth, Supabase layer, Razorpay billing, CI/CD) and restructuring
  sprint cadence to separate greenfield work from maintenance load.
- **Engineered real-time bidirectional chat** with Socket.IO for live messaging between SMB
  users and business owners.

---

### 4.3 Vellore Institute of Technology — Research Contributor
**Jan 2025 – Nov 2025 · Vellore (on-campus)**

- Contributed to research on **Blockchain-Based LLM Models Using Fully Homomorphic
  Encryption (FHE) for Academic Records** — investigating how FHE enables inference over
  encrypted student academic data without decryption, with blockchain providing an immutable
  audit trail for credential issuance and verification.
- Evaluated architectural trade-offs between on-chain data storage and off-chain encrypted
  record pointers, weighing gas-cost constraints against privacy guarantees in a credential
  provenance system.
- Applied cryptographic primitives in an LLM context — exploring inference over
  privacy-preserving representations of sensitive data without plaintext exposure.

---

## 5. PROJECTS

### 5.1 Nimbus — AI-First RAG Document Workspace *(in development)*
**[github.com/atinsharma24/nimbus](https://github.com/atinsharma24/nimbus)**
**Stack:** Next.js 14 · TypeScript · PostgreSQL · pgvector · Prisma · NextAuth.js · Groq API · OpenAI

- Production-grade RAG pipeline: documents ingested asynchronously into a queue-based
  processor with explicit status states (`pending → processing → indexed → error`), chunked
  with overlap to prevent semantic loss at boundaries, embedded, and stored in a pgvector
  column inside PostgreSQL.
- **Cosine similarity search** (`embedding <=> query_vector`) co-locating vector data with
  relational metadata (`user_id`, `document_id`, `created_at`) for hybrid SQL + semantic
  filtering — **sub-800ms retrieval** over multi-format corpora.
- **Provider-agnostic LLM abstraction**: a single config flag
  (`provider: "groq" | "openai" | "anthropic"`) routes generation calls — switching inference
  providers requires zero code changes.
- Streaming responses via Groq delivered as **server-sent events (SSE)** for token-by-token
  document Q&A.
- Ingestion resilience: **exponential-backoff 429 retry** on embedding rate limits and
  per-document status tracking.

### 5.2 Autonomous Web Agent — Claude 3.5 Sonnet + MCP Orchestration
**[github.com/atinsharma24/auto-agent](https://github.com/atinsharma24/auto-agent)**
**Stack:** Python · Groq API · OpenClaw · BrowserOS (MCP) · Claude 3.5 Sonnet · Anthropic API

- **Dual-agent architecture**: an Executor (Claude 3.5 Sonnet) handles multi-step reasoning
  over DOM and form logic; a Watcher (Groq, fast inference) runs cheap page-state validation
  between every state transition — separating cost-intensive reasoning from high-frequency
  polling.
- **MCP (Model Context Protocol)** integration via BrowserOS gives the Executor structured
  tool-level access to DOM inspection, form-fill operations, and navigation — intent-driven
  traversal without brittle CSS selectors.
- Persistent **local queue manager** (`pending → in_progress → applied / failed / escalated`)
  with URL deduplication, session-spanning persistence, and graceful WAF/CAPTCHA handling:
  the Watcher fingerprints challenge pages (CAPTCHA iframe src, Cloudflare challenge text),
  pauses the Executor, and escalates to a human — resuming from the last checkpoint once
  cleared.

### 5.3 DocGPT — RAG Document Assistant
**[github.com/atinsharma24/docgpt](https://github.com/atinsharma24/docgpt)**
**Stack:** React 19 · Python (Django) · ChromaDB · OpenAI GPT-4o-mini · all-MiniLM-L6-v2 · PyPDF2 · Docker

- Full Django RAG pipeline: PyPDF2 text extraction with fixed-size overlap chunking
  (~500–1000 tokens, ~50–100 token overlap), local `all-MiniLM-L6-v2` embeddings
  (384-dimensional, offline — **zero API cost**), ChromaDB cosine retrieval, GPT-4o-mini
  generation.
- Django backend and ChromaDB store containerised as independent Docker services for
  portable, reproducible deployment with no external database dependency.
- RAG prompt structure — system context + retrieved k-nearest chunks + user query — ensuring
  generation is grounded in retrieved content rather than model priors.

### 5.4 VyaparGPT — WhatsApp AI Business Assistant *(OpenBiz product)*
**Stack:** Node.js · OpenAI API · Google Gemini API · WhatsApp Business API

- Complete WhatsApp message lifecycle: webhook ingestion → **HMAC-SHA256** signature
  validation → message-type routing (text / media / document / status) → session context
  lookup → LLM dispatch → response delivery → delivery-status webhook.
- **Stateless per-request provider failover** (OpenAI primary → Gemini secondary) — not
  sticky, transparent to users, with normalisation extracting `content.text` uniformly from
  both APIs' differing response shapes.
- **Session-based context management**: composite session key
  (`phone_number_id` + `user_phone_number`), rolling `conversation_history[]` passed on every
  turn, configurable TTL expiry preventing stale context injection into resumed conversations.
- **Gemini Vision document extraction**: media retrieved from the WhatsApp Graph API →
  structured extraction prompt → JSON output of key fields persisted to the database.

### 5.5 Automated Content Intelligence Pipeline *(OpenBiz product)*
**Stack:** React 19 · TypeScript · Laravel · Node.js · OpenAI · Google Gemini · Docker · GitHub Actions · Puppeteer

- **Puppeteer scraping layer**: headless Chromium with `waitUntil: 'networkidle2'` to ensure
  SPA hydration and lazy-loads complete; `page.setUserAgent()` and custom headers to mimic
  real browser behaviour; per-page configurable timeouts preventing hangs on slow targets.
- **Dual-model AI rewriting**: Gemini primary → OpenAI fallback **per article** (not
  per-batch — partial batch success is valid); articles failing both providers flagged
  `manual_review_required`.
- **React 19 diff-view editorial frontend**: split-screen word-level diff highlighting,
  per-article state machine (`pending_review → approved → published / rejected`),
  human-in-the-loop checkpoint before publication.
- **Dockerised microservices** (Scraper, AI Rewriter, Laravel API, React Frontend) with
  `unless-stopped` restart policy, triggered on a GitHub Actions cron — self-healing across
  process crashes and partial scrape failures.

---

## 6. TECHNICAL SKILLS

| Category | Technologies |
|---|---|
| **Languages** | JavaScript, TypeScript, Python, SQL, Java |
| **Frontend** | React (v18/19), Next.js, React Native, Redux Toolkit, TailwindCSS |
| **Backend** | Node.js, Express.js, NestJS, FastAPI, Django, Laravel |
| **Databases** | PostgreSQL, Supabase, MongoDB, Redis, pgvector, ChromaDB, Pinecone, AWS DynamoDB |
| **AI / LLM** | OpenAI API, Google Gemini API, Groq API, Anthropic Claude API, RAG pipelines, LangChain.js, LangGraph, Cohere Re-rank v3, Sentence Transformers (all-MiniLM-L6-v2), Vercel AI SDK, MCP, prompt engineering, PyPDF2 |
| **AI-Native Tooling** | Claude Code, Codex, BrowserOS / OpenClaw |
| **DevOps / Cloud** | Docker, GitHub Actions, Vercel, AWS (S3, SNS, DynamoDB) |
| **Tools** | Git, Postman, Socket.IO, Razorpay SDK, VideoSDK, Puppeteer, Drizzle ORM, Prisma |
| **Patterns** | WebSockets (Socket.IO), REST, HMAC-SHA256 webhook validation, idempotent event processing, N+1 query optimisation, cosine vector similarity search, provider-agnostic LLM layers, hybrid dense/sparse retrieval |

---

## 7. EDUCATION

**Vellore Institute of Technology, Vellore**
B.Tech in Computer Science and Engineering
Coursework completed Nov 2025 · Degree conferred May 2026
Focus: Full-Stack Development, AI Systems

**Delhi Public School, Agra** — Secondary & Senior Secondary

---

## 8. INTERVIEW TALKING POINTS

**"Tell me about yourself."**
Full-stack engineer, currently at AGI Ready Inc. building client products in
Next.js/TypeScript/Node.js as part of a small AI-native studio team. Before that, founding
engineer at OpenBiz for a year — one of three engineers who took two AI products from zero to
1,000+ active Indian SMB users. My strength is owning the whole path: designing the API
surface, wiring the LLM layer with real failover, and then doing the reliability work that
keeps it up — idempotent webhooks, query optimisation, gated CI/CD.

**"Hardest technical problem you've solved."**
At OpenBiz, API latency degraded badly as we crossed 1,000 users. I traced it to an N+1
pattern in our Supabase PostgreSQL layer — single parent fetches spawning N child queries per
request. I rewrote the ORM calls as JOIN-based queries, added composite indexes on the
high-frequency WHERE/JOIN columns, and introduced TTL response caching on stable read-heavy
endpoints. Verified 40% latency reduction. The interesting part wasn't the fix — it was that
the ORM made the problem invisible until we had enough traffic to feel it.

**"Something you built that you're proud of."**
Nimbus — an open-source RAG workspace on Next.js 14, pgvector, and Groq. Async ingestion with
explicit per-document status states, overlap chunking, cosine similarity search co-located
with relational metadata so I can filter semantically and relationally in one query, SSE
streaming, and a provider-agnostic LLM layer where switching between Groq, OpenAI, and
Anthropic is a single config flag. Sub-800ms retrieval.

**"Leadership / influence without authority."**
Environment drift across three engineers' local setups was producing non-reproducible bugs at
OpenBiz. I built the GitHub Actions + Vercel pipeline from scratch — PR-triggered tests,
consistent staging deploys, approval-gated production — and introduced branch protection and
PR description standards that became team defaults. 30% faster deployment cycles, zero
broken-build incidents over the next four months.

**"Product judgement."**
Indian SMBs run on WhatsApp and paper, not SaaS dashboards. VyaparGPT met them there: a
WhatsApp-native assistant with real multi-turn session context, plus a Gemini Vision module
that read GST certificates and vendor agreements straight from photographs — deleting a
manual agent-driven data-entry step from onboarding entirely.

**"Why are you looking?"**
I want a role with founding-level ownership over a product I can go deep on — shipping
AI-powered features fast with a small team and real users. My work sits exactly at the
intersection roles like this need: production RAG and LLM orchestration on one side,
dependable TypeScript/Node backend engineering on the other.

**"How do you use AI in your work?"**
Claude Code and Codex are my primary development tools at AGI Ready. The discipline is
treating it as delegation, not autocomplete — I decide the architecture and decomposition,
direct the tooling against that plan, and review output against production standards. It
changes throughput significantly; it doesn't change who is accountable for the design.

---

## 9. PROVENANCE

| Claim set | Source |
|---|---|
| AGI Ready role, dates, terms, scope | `atin-sharma-offer-letter.pdf` (3 Jul 2026) |
| OpenBiz experience, projects, metrics | `resumes_and_docs/master_cv/Atin_Sharma_Master_CV.md`, `core_vault/JobApplyFiles/01_atomic_fact_sheet.json` |
| Logistics, compensation, Q&A bank | `core_vault/JobApplyFiles/06_logistics_mapping.json` |
| Resume layout / build | `resumes_and_docs/categories/tex/Atin_Sharma_Resume_2026.tex` → `tectonic` |

**Last updated:** 1 August 2026
