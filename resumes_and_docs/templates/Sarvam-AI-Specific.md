# Atin Sharma
**Backend AI Engineer | LLM Systems & Conversational AI**

📧 atinsharma24@gmail.com | 📱 +91 82185 02886  
🔗 [LinkedIn](linkedin-url) | [GitHub](https://github.com/atinsharma24/) | 📍 Agra 282007, India

---

## PROFILE

Backend engineer with founding experience building **production LLM systems and conversational AI** for Indian SMBs. At OpenBiz, architected **VyaparGPT** — a WhatsApp-native AI assistant processing **1,000+ active users** using **Node.js, OpenAI, and Gemini APIs** with **provider-fallback logic, conversation context per session, and full message lifecycle orchestration**. Built **AI document verification pipelines** (Gemini API) and reduced API latency by **40% through PostgreSQL optimization**. Currently building **Nimbus**, an open-source RAG document workspace on **pgvector and Groq**, enabling **semantic search and streaming LLM responses**. Expert in **Python, Node.js, RAG pipelines, vector search, and LLM API integration** (OpenAI, Gemini, Groq, Anthropic). Targeting roles in **backend AI engineering and LLM infrastructure** for India's AI stack.

---

## PROFESSIONAL EXPERIENCE

### Founding Engineer | OpenBiz Software India Pvt Ltd
**Jun 2025 – May 2026 | Remote (Bangalore)**

**LLM Systems & Conversational AI:**
- Architected **VyaparGPT** — a **WhatsApp-native AI business assistant** for Indian SMBs using **Node.js, OpenAI, and Gemini APIs**
  - Handled **full message lifecycle**: webhook receipt → LLM processing → response dispatch
  - Implemented **provider-fallback logic** (OpenAI ↔ Gemini) for high availability and cost optimization
  - Managed **conversation context per session** for stateful, personalized interactions across 1,000+ active users
  - Built with **TypeScript** for type-safe architecture and maintainability
- Built an **AI document verification module** using **Google Gemini API** to automate data extraction from unstructured business documents (invoices, GST forms, licenses)

**Backend Performance & Infrastructure:**
- Diagnosed and resolved **N+1 query patterns** in **Supabase (PostgreSQL)**; implemented indexing and response caching, **cutting API response time by 40%** across critical endpoints
- Engineered **real-time bidirectional chat** using **Socket.IO** and integrated **VideoSDK** for live SMB-to-support workflows
- Architected the core **MERN platform** from scratch; scaled to 1,000+ active users with **TypeScript** throughout the stack
- Owned **CI/CD pipeline** setup with **GitHub Actions and Vercel**, reducing deployment cycle time by 30%

**Platform Engineering:**
- **Razorpay**: HMAC webhook validation, payment-state reconciliation, re-entrant idempotency check — **100% payment-state consistency**.
- **CI/CD**: GitHub Actions + Vercel — **30% reduction in deployment cycle time**, zero broken-build incidents over four months.
- Website Builder: shipped within 6-week window by reusing ~60% of shared infrastructure.

---

### Research Contributor | Vellore Institute of Technology
**Jan 2025 – Nov 2025 | Vellore (On-campus)**

- Contributed to research on **Blockchain-Based LLM Model Using Fully Homomorphic Encryption (FHE) for Academic Records** — investigating how FHE enables computation on encrypted student data without decryption.
- Explored how model inference could operate on **privacy-preserving representations of sensitive data** using FHE-compatible cryptographic primitives, without exposing plaintext records.

---

## KEY PROJECTS

### Nimbus — AI Document Workspace (In Development, 2026)
**Stack:** **Next.js 14**, **TypeScript**, **PostgreSQL**, **pgvector**, **Prisma**, **NextAuth.js**, **Groq API**, **OpenAI**

- Building a **production RAG pipeline** with **streaming LLM responses** via **Groq API** and **semantic search** over user documents using **pgvector (cosine similarity)** for precise retrieval
- Designed a **provider-agnostic LLM layer** supporting **Groq, OpenAI, and Anthropic** — **one-config switching** without downstream changes to retrieval or generation logic
- Implemented **async document ingestion** with **429 retry logic and per-document status tracking** to handle API rate limits gracefully in production
- Built with **Prisma ORM** for type-safe database access and **NextAuth.js** for authentication

### DocGPT — RAG Document Assistant
**Stack:** **React 19**, **Python (Django)**, **ChromaDB**, **Sentence Transformers**, **OpenAI**, **Docker**

- Built a **Retrieval-Augmented Generation (RAG) system** enabling natural language querying of PDF documents via semantic search
- Implemented **semantic vector search** using **ChromaDB and Sentence Transformers (all-MiniLM-L6-v2)** for cost-efficient local embeddings
- Engineered a **text chunking pipeline** using **PyPDF2 with overlap strategies** to preserve context across chunk boundaries
- Developed **Django REST API backend** to orchestrate: retrieval → context injection → **GPT-4o-mini response pipeline**

### Automated Content Intelligence Pipeline
**Stack:** **React 19**, **TypeScript**, **Node.js**, **OpenAI**, **Gemini**, **Docker**, **GitHub Actions**

- Designed a **multi-stage TypeScript content pipeline** that scrapes, analyzes, and AI-rewrites content at scale
- Integrated **Google Gemini and OpenAI models with failover logic** for content rewriting with factual accuracy via custom prompt engineering
- Deployed **microservices architecture** using Docker and **GitHub Actions cron jobs** for self-healing automated ingestion

---

## TECHNICAL SKILLS

**Backend:** **Node.js · Python (Django / DRF) · Express.js · NestJS**  
**Languages:** **JavaScript/TypeScript · Python · SQL · Java**  
**Databases:** **PostgreSQL (Supabase) · MongoDB · pgvector · ChromaDB · Redis**  
**AI/LLM:** **OpenAI API · Google Gemini API · Groq API · Anthropic API · RAG Pipelines · Vector Search (pgvector, ChromaDB) · LangChain.js · Vercel AI SDK · Prompt Engineering · Streaming LLM Responses**  
**DevOps:** **Docker · GitHub Actions · Vercel · CI/CD Pipelines · Git · Prisma ORM**  
**Tools:** **Socket.IO · Razorpay API · Puppeteer · Postman · VideoSDK**  
**Frontend:** React.js (v18/19) · Next.js (App Router) · Redux Toolkit · TailwindCSS  
**Patterns:** WebSocket (Socket.IO) · REST · Webhook Validation (HMAC-SHA256) · N+1 Query Optimization · Vector Similarity Search (cosine) · Provider-Agnostic LLM Layers · Idempotent Event Processing  

---

## EDUCATION

**B.Tech — Computer Science & Engineering**  
Vellore Institute of Technology (VIT), Vellore | Expected Graduation: May 2026  
Focus: Full Stack Development, AI Systems, Information Security Management

---

## AREAS OF EXPERTISE

✓ **LLM Integration (OpenAI, Gemini, Groq, Anthropic) with Provider Fallback**  
✓ **RAG Pipelines & Vector Search (pgvector, ChromaDB)**  
✓ **Backend AI Infrastructure & API Performance Optimization**  
✓ **Conversational AI & WhatsApp Automation**  
✓ **Real-Time Systems (Socket.IO) & Streaming LLM Responses**  
✓ **PostgreSQL Query Optimization & Indexing**  
✓ **CI/CD Automation & Production Deployment**  
✓ **Prompt Engineering & LLM Response Optimization**  

---

**Target Roles at Sarvam AI:**
- Backend Engineer
- Backend AI Engineer
- ML Engineer
- Frontend Engineer (Full-Stack Capability)

**GitHub:** [github.com/atinsharma24](https://github.com/atinsharma24/)

---

**Availability:** Immediate Joiner — 0-day notice period | **Work Mode:** Remote-first; open to Bangalore, Hyderabad, Pune, Delhi NCR, Mumbai | **Expected CTC:** 15–18 LPA (INR) | **Work Authorization:** Indian Citizen — no sponsorship required
