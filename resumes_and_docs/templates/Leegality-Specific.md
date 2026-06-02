# Atin Sharma
**Full-Stack Engineer | React + Python | Legal-Tech Document Automation**

📧 atinsharma24@gmail.com | 📱 +91 82185 02886  
🔗 [LinkedIn](linkedin-url) | [GitHub](https://github.com/atinsharma24/) | 📍 Agra 282007, India

---

## PROFILE

Full-stack engineer with founding experience building **AI-powered document automation systems** for Indian SMBs. At OpenBiz, engineered an **LLM-based document verification module using Google Gemini API** that automated data extraction from unstructured business documents (invoices, GST forms, licenses), eliminating manual compliance workflows. Architected **VyaparGPT**, a WhatsApp-native AI assistant processing 1,000+ active users with **40% API latency reduction** through PostgreSQL optimization. Built **production RAG pipelines** (pgvector, ChromaDB) enabling semantic search over legal and business documents. Expert in **React.js (v18/19), Next.js, Python (Django), Node.js**, with deep experience in document intelligence, compliance automation, and LLM integration. Targeting roles in **legal-tech document infrastructure** where React + Python expertise and AI-driven automation converge.

---

## PROFESSIONAL EXPERIENCE

### Founding Engineer | OpenBiz Software India Pvt Ltd
**Jun 2025 – May 2026 | Remote (Bangalore)**

**Document Automation & Legal-Tech Workflows:**
- Built an **AI document verification module** using **Google Gemini API** to automate data extraction and validation from unstructured SMB documents (invoices, GST certificates, business licenses), replacing fully manual compliance review workflows
- Architected **VyaparGPT** — a **WhatsApp-native LLM assistant** for Indian SMBs using **Node.js, React.js, OpenAI, and Gemini APIs**
  - Processed **1,000+ active users** with **conversation context per session** for stateful, personalized interactions
  - Implemented **provider-fallback logic** (OpenAI ↔ Gemini) for high availability
  - Handled full message lifecycle: webhook → LLM processing → response dispatch

**React + Full-Stack Development:**
- Architected the core **MERN platform** from scratch; scaled to 1,000+ active users with **TypeScript throughout the stack**
- Built **React.js frontends** with **Redux Toolkit for state management** and **TailwindCSS** for responsive design
- Engineered **real-time bidirectional chat** using **Socket.IO** and integrated **VideoSDK** for live SMB-to-support workflows

**Backend & Performance Optimization:**
- Diagnosed and resolved **N+1 query patterns** in **Supabase (PostgreSQL)**; implemented indexing and response caching, **cutting API response time by 40%**
- Developed **Django REST API backends** to orchestrate document processing and LLM response pipelines
- Integrated **Razorpay** payment gateway for subscription billing, handling **webhook validation, payment state reconciliation, and retry flows**

**DevOps & CI/CD:**
- **CI/CD**: GitHub Actions + Vercel — **30% reduction in deployment cycle time**, zero broken-build incidents over four months.
- **Razorpay**: HMAC webhook validation, payment-state reconciliation, re-entrant idempotency check — **100% payment-state consistency**.

---

### Research Contributor | Vellore Institute of Technology
**Jan 2025 – Nov 2025 | Vellore (On-campus)**

- Contributed to research on **Blockchain-Based LLM Model Using Fully Homomorphic Encryption (FHE) for Academic Records** — FHE enables computation on encrypted data without decryption; applicable to **privacy-preserving legal document processing** and digital signature audit trails.
- Evaluated architectural trade-offs between on-chain data storage and off-chain encrypted record pointers — relevant to **Leegality-style legal-tech infrastructure** design.
- Explored how model inference could operate on privacy-preserving representations of sensitive academic data using FHE-compatible cryptographic primitives.

---

## KEY PROJECTS

### Nimbus — AI Document Workspace (In Development, 2026)
**Stack:** **Next.js 14**, **TypeScript**, **PostgreSQL**, **pgvector**, **Prisma**, **NextAuth.js**, **Groq API**, **OpenAI**

- Building a **production RAG pipeline** with **streaming LLM responses** via Groq API and **semantic search** over user documents using **pgvector (cosine similarity)** — ideal for legal research and compliance document analysis
- Designed a **provider-agnostic LLM layer** supporting **Groq, OpenAI, and Anthropic** — **one-config switching** without downstream changes
- Implemented **async document ingestion** with **429 retry logic and per-document status tracking** to handle API rate limits gracefully
- Built with **Next.js 14 App Router**, **Prisma ORM**, and **NextAuth.js** for enterprise-grade authentication

### DocGPT — RAG Document Assistant
**Stack:** **React 19**, **Python (Django)**, **ChromaDB**, **Sentence Transformers**, **OpenAI**, **Docker**

- Built a **Retrieval-Augmented Generation (RAG) system** enabling natural language querying of PDF documents via semantic search — **directly applicable to legal research and compliance document analysis**
- Implemented **semantic vector search** using **ChromaDB and Sentence Transformers (all-MiniLM-L6-v2)** for cost-efficient local embeddings
- Engineered a **text chunking pipeline** using **PyPDF2 with overlap strategies** to preserve context across chunk boundaries, ensuring accurate document understanding
- Developed **Django REST API backend** to orchestrate: retrieval → context injection → GPT-4o-mini response pipeline

### Automated Content Intelligence Pipeline
**Stack:** **React 19**, **TypeScript**, **Node.js**, **OpenAI**, **Gemini**, **Docker**, **GitHub Actions**

- Designed a **multi-stage TypeScript content pipeline** that scrapes, analyzes, and AI-rewrites content at scale
- Built **React 19 frontend** with **split-screen Diff View** comparing original vs. AI-rewritten content in real-time
- Integrated **Google Gemini and OpenAI models with failover logic** for content rewriting with factual accuracy
- Deployed **microservices architecture** using Docker and **GitHub Actions cron jobs** for self-healing automated ingestion

---

## TECHNICAL SKILLS

**Frontend:** **React.js (v18/19) · Next.js (App Router) · Redux Toolkit · TailwindCSS · shadcn/ui**  
**Backend:** **Python (Django / DRF) · Node.js · Express.js · NestJS**  
**Languages:** **JavaScript/TypeScript · Python · SQL · Java**  
**Databases:** **PostgreSQL (Supabase) · MongoDB · pgvector · ChromaDB · Redis**  
**AI/LLM:** **OpenAI API · Google Gemini API · Groq API · RAG Pipelines · Vector Search · LangChain.js · Vercel AI SDK · Prompt Engineering**  
**DevOps:** **Docker · GitHub Actions · Vercel · CI/CD Pipelines · Git · Prisma ORM**  
**Tools:** **Socket.IO · Razorpay API · Puppeteer · Postman · VideoSDK**  
**Patterns:** WebSocket (Socket.IO) · REST · Webhook Validation (HMAC-SHA256) · N+1 Query Optimization · Vector Similarity Search (cosine) · Provider-Agnostic LLM Layers · Idempotent Event Processing  

---

## EDUCATION

**B.Tech — Computer Science & Engineering**  
Vellore Institute of Technology (VIT), Vellore | Expected Graduation: May 2026  
Focus: Full Stack Development, AI Systems, Information Security Management, Cyber Security

---

## AREAS OF EXPERTISE

✓ **React.js + Next.js Frontend Development**  
✓ **Python (Django) Backend Development**  
✓ AI-Powered Document Automation & Legal-Tech Workflows  
✓ RAG Pipelines & Semantic Search (pgvector, ChromaDB)  
✓ PostgreSQL Query Optimization & API Performance  
✓ LLM Integration (OpenAI, Gemini, Groq) with Provider Fallback  
✓ CI/CD Automation & Production Deployment  

---

**Target Roles at Leegality:**
- Front End Developer - ReactJS
- Senior FrontEnd Developer - ReactJS
- Software Engineer/Sr Software Engineer - Python

**GitHub:** [github.com/atinsharma24](https://github.com/atinsharma24/)

---

**Availability:** Immediate Joiner — 0-day notice period | **Work Mode:** Remote-first; open to Bangalore, Hyderabad, Pune, Delhi NCR, Mumbai | **Expected CTC:** 15L+ (negotiable, no hard ceiling) | **Work Authorization:** Indian Citizen — no sponsorship required
