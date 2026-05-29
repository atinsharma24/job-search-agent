# Atin Sharma
**Full-Stack Engineer | AI Document Verification & Identity Systems**

📧 atinsharma24@gmail.com | 📱 +91 82185 02886  
🔗 [LinkedIn](linkedin-url) | [GitHub](https://github.com/atinsharma24/) | 📍 Agra 282007, India

---

## PROFILE

Full-stack engineer with founding experience building **AI-powered document verification and WhatsApp automation systems** for Indian SMBs. At OpenBiz, engineered an **LLM-based document verification module using Google Gemini API** that automated data extraction from unstructured business documents, replacing manual review workflows. Built **VyaparGPT**, a WhatsApp-native AI assistant processing 1,000+ active users with **40% API latency reduction** through query optimization. Experienced in **real-time data pipelines, PostgreSQL optimization, RAG systems (pgvector, ChromaDB), and production API integrations** (OpenAI, Gemini, Groq). Targeting roles in **KYC automation, identity verification, and compliance-tech** where document intelligence and system reliability are critical.

---

## PROFESSIONAL EXPERIENCE

### Founding Engineer | OpenBiz Software India Pvt Ltd
**Jun 2025 – May 2026 | Remote (Bangalore)**

**Document Intelligence & Verification:**
- **Gemini Vision API document verification module**: extracting structured fields (GST number, business name, invoice amount, dates) from **WhatsApp photographs of GST certificates and vendor agreements** — eliminating a manual data-entry step in SMB onboarding. Direct applicability to KYC document extraction workflows.
- **VyaparGPT**: built full WhatsApp message lifecycle — webhook ingestion → **HMAC-SHA256 validation** → session context → LLM dispatch → response delivery — serving **40+ SMBs in closed pilot**, scaling to **1,000+ active platform users**.
- **LLM provider-fallback**: OpenAI → Google Gemini on HTTP 5xx, 429 rate-limit, or configurable timeout — zero failure surface exposed to users.

**System Performance & Reliability:**
- **N+1 fix**: rewrote ORM calls to JOIN-based queries, composite indexes on high-frequency WHERE/JOIN columns, TTL-based response caching — **40% API latency reduction** at 1,000+ user scale.
- **Razorpay**: HMAC webhook validation, payment-state reconciliation, out-of-order event handling via re-entrant idempotency check — **100% payment-state consistency**.
- **CI/CD**: GitHub Actions + Vercel — **30% reduction in deployment cycle time**, zero broken-build incidents over four months.

---

### Research Contributor | Vellore Institute of Technology
**Jan 2025 – Nov 2025 | Vellore (On-campus)**

- Contributed to research on **Blockchain-Based LLM Model Using Fully Homomorphic Encryption (FHE) for Academic Records** — directly relevant to KYC/identity: FHE enables computation on encrypted personal data without decryption, with blockchain providing an immutable audit trail for credential issuance and verification.
- Evaluated architectural trade-offs between on-chain data storage and off-chain encrypted record pointers, assessing gas cost constraints versus **data privacy guarantees** in an academic credential provenance system — applicable to identity verification infrastructure design.
- Explored how model inference could operate on **privacy-preserving representations of sensitive data** using FHE-compatible cryptographic primitives, without exposing plaintext records.

---

## KEY PROJECTS

### Nimbus — AI Document Workspace (In Development, 2026)
**Stack:** Next.js 14, TypeScript, PostgreSQL, **pgvector**, Prisma, NextAuth.js, Groq API, OpenAI

- Building a **production RAG pipeline** with **streaming LLM responses** via Groq API and **semantic search** over user documents using **pgvector (cosine similarity)** for precise retrieval
- Designed a **provider-agnostic LLM layer** supporting Groq, OpenAI, and Anthropic — **one-config switching** without downstream changes to retrieval or generation logic
- Implemented **async document ingestion** with **429 retry logic and per-document status tracking** to handle API rate limits gracefully in production

### DocGPT — RAG Document Assistant
**Stack:** React 19, Python (Django), **ChromaDB**, Sentence Transformers, OpenAI, Docker

- Built a **Retrieval-Augmented Generation (RAG) system** enabling natural language querying of PDF documents via semantic search
- Implemented **semantic vector search** using **ChromaDB and Sentence Transformers (all-MiniLM-L6-v2)** for cost-efficient local embeddings
- Engineered a **text chunking pipeline** using **PyPDF2 with overlap strategies** to preserve context across chunk boundaries, ensuring accurate document understanding
- Developed **Django REST API backend** to orchestrate: retrieval → context injection → GPT-4o-mini response pipeline

### Automated Content Intelligence Pipeline
**Stack:** React 19, TypeScript, Node.js, OpenAI, Gemini, Docker, GitHub Actions

- Designed a **multi-stage TypeScript content pipeline** that scrapes, analyzes, and AI-rewrites news articles at scale
- Engineered a **Puppeteer-based scraper** to bypass client-side rendering and extract structured article metadata
- Integrated **Google Gemini and OpenAI models with failover logic** for content rewriting with factual accuracy via custom prompt engineering
- Deployed **microservices architecture** using Docker and **GitHub Actions cron jobs** for self-healing automated ingestion

---

## TECHNICAL SKILLS

**Languages:** JavaScript/TypeScript · Python · SQL · Java  
**Frontend:** React.js (v18/19) · Next.js (App Router) · Redux Toolkit · TailwindCSS · shadcn/ui  
**Backend:** Node.js · Express.js · NestJS · Django / DRF  
**Databases:** **PostgreSQL (Supabase)** · MongoDB · **pgvector** · **ChromaDB** · Redis  
**AI/LLM:** **OpenAI API · Google Gemini API · Groq API** · RAG Pipelines · **Vector Search** · LangChain.js · Vercel AI SDK · Prompt Engineering  
**DevOps:** Docker · GitHub Actions · Vercel · CI/CD Pipelines · Git · Prisma ORM  
**Tools:** Socket.IO · **Razorpay API** · Puppeteer · Postman · VideoSDK  
**Patterns:** WebSocket (Socket.IO) · REST · Webhook Validation (HMAC-SHA256) · N+1 Query Optimization · Vector Similarity Search (cosine) · Provider-Agnostic LLM Layers · Idempotent Event Processing  

---

## EDUCATION

**B.Tech — Computer Science & Engineering**  
Vellore Institute of Technology (VIT), Vellore | Expected Graduation: May 2026  
Focus: Full Stack Development, AI Systems, Information Security Management, Image Processing (CNNs), Cyber Security

---

## AREAS OF EXPERTISE

✓ AI Document Verification & Data Extraction  
✓ Real-time API & Webhook Processing  
✓ PostgreSQL Query Optimization & Indexing  
✓ RAG Pipelines & Vector Search (pgvector, ChromaDB)  
✓ WhatsApp Automation & Conversational AI  
✓ Payment Gateway Integration & Compliance Workflows  
✓ CI/CD Automation & Production Deployment  

---

**Target Companies:** Signzy, Bureau, Digio  
**GitHub:** [github.com/atinsharma24](https://github.com/atinsharma24/)

---

**Availability:** Immediate Joiner — 0-day notice period | **Work Mode:** Remote-first; open to Bangalore, Hyderabad, Pune, Delhi NCR, Mumbai | **Expected CTC:** 15–18 LPA (INR) | **Work Authorization:** Indian Citizen — no sponsorship required
