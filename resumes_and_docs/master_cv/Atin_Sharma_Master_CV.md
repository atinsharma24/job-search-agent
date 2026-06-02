# ATIN SHARMA
**Full-Stack Product Engineer | AI Systems | RAG Pipelines | WhatsApp Automation**

atinsharma24@gmail.com | +91 82185 02886 | [github.com/atinsharma24](https://github.com/atinsharma24/) | [linkedin.com/in/atinsharma24](https://www.linkedin.com/in/atinsharma24/)
Agra, Uttar Pradesh, India — Open to Remote & Relocation

---

## PROFESSIONAL SUMMARY

Founding engineer with 12 months of production experience building AI-powered full-stack systems at OpenBiz Software India Pvt Ltd, where I was one of three engineers who shipped two commercial products from zero to 1,000+ active Indian SMB users. I specialize in MERN + AI stacks — TypeScript, Node.js, Python, PostgreSQL — with hands-on production delivery across conversational AI (VyaparGPT, a WhatsApp-native LLM assistant for 40+ SMB pilot businesses), RAG pipelines (Nimbus on pgvector + Groq; DocGPT on ChromaDB), and resilient DevOps (GitHub Actions + Vercel CI/CD reducing deployment cycle time by 30%). My technical scope spans full-stack web, LLM orchestration with dual-model provider-fallback (OpenAI ↔ Gemini), idempotent payment billing, and autonomous multi-agent web automation. I am an immediate joiner (0-day notice) targeting 15L+ (negotiable, no hard ceiling) in founding-stage or early-product roles where I can own the stack end-to-end. VIT Vellore, B.Tech Computer Science Engineering (Coursework Completed: Nov 2025, Degree Conferred: May 2026).

---

## KEY METRICS

| Metric | Value | Metric | Value |
|---|---|---|---|
| API Latency Reduction | **40%** | Platform Active Users | **1,000+** |
| Deployment Cycle Faster | **30%** | VyaparGPT SMB Pilot | **40 businesses** |
| Shared Infra Reuse (Website Builder) | **~60%** | LeetCode Problems Solved | **347** |
| Founding Team Size | **3 engineers** | Zero Broken-Build Incidents | **4 months post CI/CD** |

---

## PROFESSIONAL EXPERIENCE

### OpenBiz Software India Pvt Ltd | Founding Engineer | Jun 2025 – May 2026 | Remote / Bangalore

One of three founding technical leads responsible for architecting and shipping two AI-powered SaaS products for the Indian SMB market on the MERN stack.

- **Architected VyaparGPT**, a WhatsApp-native LLM assistant built in Node.js: designed the full message lifecycle (WhatsApp Business API webhook ingestion → HMAC signature validation → session context lookup → LLM dispatch → response delivery), serving 40+ businesses in a closed SMB pilot and scaling to 1,000+ active platform users. Implemented multi-turn conversational context (rolling `conversation_history[]`) enabling natural follow-up queries without re-stating context.
- **Engineered LLM provider-fallback** (OpenAI → Google Gemini) at the API layer: on HTTP 5xx, 429 rate-limit, or configurable timeout, requests are transparently rerouted to the secondary provider with response-shape normalization — no failure surface exposed to users.
- **Built an LLM-powered document verification module** using the Gemini Vision API to extract structured fields (GST number, business name, invoice amount, dates) from photographs of GST certificates and vendor agreements sent directly through WhatsApp, eliminating a manual, agent-driven data-entry step in the SMB onboarding workflow.
- **Resolved critical N+1 query patterns** in the Supabase (PostgreSQL) layer: rewrote ORM calls to JOIN-based queries, introduced composite indexes on high-frequency WHERE/JOIN columns, and added TTL-based response caching for read-heavy stable endpoints — achieving a verified **40% reduction in API latency** at 1,000+ user scale.
- **Built and owned the GitHub Actions + Vercel CI/CD pipeline** from scratch: automated testing on every PR, environment-consistent staging deploys on merge to main, and production gated behind explicit approval. Introduced branch protection rules, PR description standards, and a shared deployment checklist — driving a **30% reduction in deployment cycle time** and **zero direct-to-main broken-build incidents** over the subsequent four months.
- **Delivered the Automated Content Intelligence Pipeline**: Puppeteer-based scraping (headless Chromium, `waitUntil: 'networkidle2'` to handle SPA hydration), TypeScript normalization layer, dual-model AI rewriting (Gemini primary → OpenAI failover per article), React 19 split-screen Diff View for human-in-the-loop editorial approval, and Dockerized microservices triggered by GitHub Actions cron — fully automated content ingestion and review cycle.
- **Shipped a parallel Website Builder product** within a 6-week window alongside active VyaparGPT development, with zero additional engineers, by auditing and reusing ~60% of shared infrastructure (auth, Supabase layer, Razorpay billing, CI/CD) and restructuring sprint cadence to separate greenfield work from maintenance load.
- **Implemented idempotent Razorpay subscription billing**: webhook validation (HMAC), payment-state reconciliation, out-of-order event handling (re-entrant idempotency check re-querying Razorpay API on every `payment.captured` regardless of prior subscription state), achieving 100% payment-state consistency across all paying customers.
- **Engineered real-time bidirectional chat** using Socket.IO enabling live messaging between SMB users and business owners within the platform.

---

### Vellore Institute of Technology | Research Contributor | Jan 2025 – Nov 2025 | Vellore (On-campus)

- Contributed to academic research on **Blockchain-Based LLM Model Using Fully Homomorphic Encryption (FHE) for Academic Records** — investigating how FHE enables computation on encrypted student academic data without decryption, with blockchain providing an immutable audit trail for credential issuance and verification.
- Evaluated architectural trade-offs between on-chain data storage and off-chain encrypted record pointers, assessing gas cost constraints versus data privacy guarantees in an academic credential provenance system.
- Applied cryptographic primitives in an LLM context — exploring how model inference could operate on privacy-preserving representations of sensitive academic data without exposing plaintext records.

---

## PROJECTS

### Nimbus — AI-First RAG Document Workspace *(in progress)*
**Stack:** Next.js 14 · TypeScript · PostgreSQL · pgvector · Prisma · NextAuth.js · Groq API · OpenAI

- Designed a production-grade RAG pipeline: documents are ingested asynchronously into a queue-based processor with status states (`pending → processing → indexed → error`), chunked with overlap to prevent semantic loss at chunk boundaries, embedded, and stored in a pgvector extension column within PostgreSQL.
- Implemented **cosine similarity search** (`embedding <=> query_vector`) via pgvector, co-locating vector data with relational metadata (`user_id`, `document_id`, `created_at`) for hybrid SQL + semantic filtering — targeting sub-800ms retrieval.
- Built a **provider-agnostic LLM abstraction layer**: a single config flag (`provider: "groq" | "openai" | "anthropic"`) routes generation calls to Groq, OpenAI, or Anthropic — switching inference providers requires zero code changes.
- Streaming LLM responses via Groq API delivered as server-sent events (SSE), providing real-time token-by-token document Q&A with visible streaming in the UI.
- Ingestion pipeline includes **429 retry logic** (exponential backoff on embedding API rate limits) and per-document status tracking, making the system resilient to upstream API transience at scale.

---

### Autonomous Web Agent — Claude 3.5 Sonnet + MCP Orchestration
**GitHub:** [github.com/atinsharma24/auto-agent](https://github.com/atinsharma24/auto-agent)
**Stack:** Python · Groq API · OpenClaw · BrowserOS (MCP) · Claude 3.5 Sonnet · Anthropic API

- Designed a **dual-agent architecture**: Executor (Claude 3.5 Sonnet) handles complex multi-step reasoning over DOM + form logic; Watcher (Groq, fast inference) runs cheap page-state validation between every state transition — separating cost-intensive reasoning from high-frequency polling.
- Integrated **MCP (Model Context Protocol)** via BrowserOS to give the Executor agent structured tool-level access to browser DOM (inspect field labels, types, values), form-fill operations, and navigation — enabling intent-driven form traversal without brittle CSS selectors.
- Built a persistent **local queue manager** (per-job status: `pending → in_progress → applied / failed / escalated`) with URL deduplication, session-spanning persistence, and graceful WAF/CAPTCHA detection: Watcher identifies challenge pages by DOM fingerprint (CAPTCHA iframe src, Cloudflare challenge text), pauses Executor, and escalates to human — Executor resumes from last checkpoint after challenge is cleared.

---

### DocGPT — RAG Document Assistant
**Stack:** React 19 · Python (Django) · ChromaDB · OpenAI GPT-4o-mini · all-MiniLM-L6-v2 · PyPDF2 · Docker

- Built a full RAG pipeline in Django: PDF text extraction via PyPDF2 with fixed-size overlap chunking (~500–1000 tokens, ~50–100 token overlap), local embedding generation using `all-MiniLM-L6-v2` (384-dimensional dense vectors, offline — no API cost), vector storage in ChromaDB with cosine similarity retrieval, and GPT-4o-mini generation.
- Containerized the Django backend and ChromaDB store as Docker services for portable, reproducible deployment with no external database dependency.
- Designed the RAG prompt structure: system context + retrieved k-nearest chunks + user query, ensuring generation is grounded in retrieved document content rather than model priors.
- Implemented the React 19 frontend with multi-format document upload, query interface, and streamed answer display.

---

### VyaparGPT — WhatsApp AI Business Assistant *(OpenBiz product)*
**Stack:** Node.js · OpenAI API · Google Gemini API · WhatsApp Business API

- Managed the complete WhatsApp message lifecycle: webhook ingestion → HMAC-SHA256 signature validation → message type routing (text / media / document / status) → session context lookup → LLM dispatch → response delivery → delivery status webhook.
- Implemented **LLM provider-fallback** (OpenAI primary → Gemini secondary): failover is stateless per-request (not sticky), transparent to users, with provider response normalization extracting `content.text` uniformly from both APIs' differing response shapes.
- Built **session-based context management**: composite session key (`phone_number_id` + `user_phone_number`), rolling `conversation_history[]` window passed to the LLM on every turn, configurable TTL expiry to prevent stale context injection in resumed conversations.
- Powered **Gemini Vision API document extraction**: media retrieved from WhatsApp Graph API → structured extraction prompt → JSON output of key fields (GST number, invoice amount, vendor name, dates) stored to database.

---

### Automated Content Intelligence Pipeline *(OpenBiz product)*
**Stack:** React 19 · TypeScript · Laravel · Node.js · OpenAI · Google Gemini · Docker · GitHub Actions · Puppeteer

- **Puppeteer scraping layer**: headless Chromium launched with `waitUntil: 'networkidle2'` to ensure SPA JS hydration and lazy-loads complete; `page.setUserAgent()` and custom HTTP headers to mimic real browser behavior; per-page configurable timeout to prevent hanging on slow targets.
- **Dual-model AI rewriting**: Gemini primary → OpenAI fallback per article (failover is per-article, not per-batch; partial batch success is valid); articles failing both providers flagged as `manual_review_required`.
- **React 19 Diff View editorial frontend**: split-screen with word-level diff highlighting, per-article state machine (`pending_review → approved → published / rejected`), human-in-the-loop checkpoint before publication.
- **Dockerized microservices** (Scraper, AI Rewriter, Laravel API, React Frontend) with `unless-stopped` restart policy; GitHub Actions cron schedule triggers the full pipeline automatically — self-healing across process crashes and partial scrape failures.

---

## TECHNICAL SKILLS

| Category | Technologies |
|---|---|
| **Languages** | JavaScript, TypeScript, Python, SQL, Java |
| **Frontend** | React.js (v18, v19), Next.js, React Native, Redux Toolkit, TailwindCSS |
| **Backend** | Node.js, Express.js, NestJS, Django, Laravel |
| **Databases** | PostgreSQL, Supabase, MongoDB, ChromaDB, pgvector, AWS DynamoDB |
| **AI / LLM** | OpenAI API, Google Gemini API, Groq API, RAG Pipelines, pgvector, ChromaDB, Sentence Transformers (all-MiniLM-L6-v2), Vercel AI SDK, LangChain.js, Prompt Engineering, PyPDF2, Claude 3.5 Sonnet (Anthropic API), MCP |
| **DevOps / Cloud** | Docker, GitHub Actions, Vercel, AWS S3, AWS SNS |
| **Tools** | Git, Postman, Socket.IO, Razorpay SDK, VideoSDK, Puppeteer, BrowserOS / OpenClaw |
| **Patterns** | WebSocket (Socket.IO), REST, Webhook Validation (HMAC-SHA256), N+1 Query Optimization, Vector Similarity Search (cosine), Provider-Agnostic LLM Layers, Idempotent Event Processing |

---

## EDUCATION

**Vellore Institute of Technology, Vellore**
B.Tech in Computer Science and Engineering | Coursework Completed: Nov 2025 | Degree Conferred: May 2026
Focus: Full Stack Development, AI Systems

**Delhi Public School, Agra**
Secondary & Senior Secondary

---

## PROFILE SNAPSHOT

| | |
|---|---|
| **Availability** | Immediate Joiner — 0-day notice period |
| **Work Mode** | Remote-first; open to Bangalore, Hyderabad, Pune, Delhi NCR, Mumbai |
| **Expected CTC** | 15L+ (negotiable, no hard ceiling) — INR |
| **Work Authorization** | Indian Citizen — no sponsorship required |
| **GitHub** | [github.com/atinsharma24](https://github.com/atinsharma24/) |
| **LinkedIn** | [linkedin.com/in/atinsharma24](https://www.linkedin.com/in/atinsharma24/) |
