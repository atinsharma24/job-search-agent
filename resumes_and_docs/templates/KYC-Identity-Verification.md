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
**Jul 2025 – Mar 2026 | Remote (Bangalore)**

**Document Intelligence & Verification:**
- Built an **AI document verification module** using **Google Gemini API** to automate data extraction and validation from unstructured SMB documents (invoices, GST forms, business licenses), eliminating manual review steps
- Architected **VyaparGPT** — a WhatsApp-native LLM assistant for Indian SMBs using **Node.js, OpenAI, and Gemini APIs**, handling full message lifecycle: webhook → LLM processing → response dispatch with provider-fallback logic
- Processed **1,000+ active users** with **conversation context managed per session** for personalized, stateful interactions

**System Performance & Reliability:**
- Diagnosed and resolved **N+1 query patterns** in **Supabase (PostgreSQL)**; implemented indexing and response caching, **cutting API response time by 40%** across critical endpoints
- Engineered **real-time bidirectional chat** using **Socket.IO** and integrated **VideoSDK** for live SMB-to-support workflows, ensuring zero third-party dependency for compliance-sensitive environments
- Owned **CI/CD pipeline** setup with **GitHub Actions and Vercel**, reducing deployment cycle time by 30% and eliminating environment drift

**Payment & Compliance Infrastructure:**
- Integrated **Razorpay** payment gateway for subscription billing, handling **webhook validation, payment state reconciliation, and failed-payment retry flows** in production

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

---

## EDUCATION

**B.Tech — Computer Science & Engineering**  
Vellore Institute of Technology (VIT), Vellore | Aug 2020 – Nov 2025  
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
