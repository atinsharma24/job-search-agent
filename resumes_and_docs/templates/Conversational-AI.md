# Atin Sharma
**Full-Stack Engineer | Conversational AI & LLM Systems**

📧 atinsharma24@gmail.com | 📱 +91 82185 02886  
🔗 [LinkedIn](linkedin-url) | [GitHub](https://github.com/atinsharma24/) | 📍 Agra 282007, India

---

## PROFILE

Full-stack engineer with founding experience building **production conversational AI systems for Indian SMBs**. At OpenBiz, architected **VyaparGPT** — a **WhatsApp-native LLM assistant** using **Node.js, OpenAI, and Gemini APIs**, processing 1,000+ active users with **provider-fallback logic, conversation context per session, and full message lifecycle orchestration** (webhook → LLM processing → response dispatch). Reduced API latency by 40% through PostgreSQL optimization. Built **real-time chat infrastructure** (Socket.IO) and **AI document verification pipelines** (Gemini API). Currently building **Nimbus**, an open-source RAG document workspace on **pgvector and Groq**, enabling semantic search and streaming LLM responses. Targeting roles in **conversational AI, LLM-powered products, and voice/chat automation** where system depth and AI integration are valued.

---

## PROFESSIONAL EXPERIENCE

### Founding Engineer | OpenBiz Software India Pvt Ltd
**Jul 2025 – Mar 2026 | Remote (Bangalore)**

**Conversational AI & LLM Systems:**
- Architected **VyaparGPT** — a **WhatsApp-native AI business assistant** for Indian SMBs using **Node.js, OpenAI, and Gemini APIs**
  - Handled **full message lifecycle**: webhook receipt → LLM processing → response dispatch
  - Implemented **provider-fallback logic** (OpenAI ↔ Gemini) for high availability
  - Managed **conversation context per session** for stateful, personalized interactions
  - Processed **1,000+ active users** with TypeScript-based type-safe architecture
- Built an **AI document verification module** using **Google Gemini API** to automate data extraction from unstructured business documents

**Real-Time Infrastructure & Performance:**
- Engineered **real-time bidirectional chat** using **Socket.IO** and integrated **VideoSDK** for in-app conferencing — supporting live SMB-to-support workflows
- Diagnosed and resolved **N+1 query patterns** in **Supabase (PostgreSQL)**; implemented indexing and response caching, **cutting API response time by 40%**
- Owned **CI/CD pipeline** setup with **GitHub Actions and Vercel**, reducing deployment cycle time by 30%

**Platform Engineering:**
- Integrated **Razorpay** payment gateway for subscription billing, handling **webhook validation, payment state reconciliation, and retry flows**
- Architected the core MERN platform from scratch, scaling to 1,000+ active users with TypeScript throughout the stack

---

## KEY PROJECTS

### Nimbus — AI Document Workspace (In Development, 2026)
**Stack:** Next.js 14, TypeScript, PostgreSQL, **pgvector**, Prisma, NextAuth.js, **Groq API**, OpenAI

- Building a **production RAG pipeline** with **streaming LLM responses** via **Groq API** and **semantic search** over user documents using **pgvector (cosine similarity)** for precise retrieval
- Designed a **provider-agnostic LLM layer** supporting **Groq, OpenAI, and Anthropic** — **one-config switching** without downstream changes to retrieval or generation logic
- Implemented **async document ingestion** with **429 retry logic and per-document status tracking** to handle API rate limits gracefully

### DocGPT — RAG Document Assistant
**Stack:** React 19, Python (Django), **ChromaDB**, Sentence Transformers, **OpenAI**, Docker

- Built a **Retrieval-Augmented Generation (RAG) system** enabling natural language querying of PDF documents via semantic search
- Implemented **semantic vector search** using **ChromaDB and Sentence Transformers (all-MiniLM-L6-v2)** for cost-efficient local embeddings
- Engineered a **text chunking pipeline** using **PyPDF2 with overlap strategies** to preserve context across chunk boundaries
- Developed **Django REST API backend** to orchestrate: retrieval → context injection → **GPT-4o-mini response pipeline**

### Automated Content Intelligence Pipeline
**Stack:** React 19, TypeScript, Node.js, **OpenAI, Gemini**, Docker, GitHub Actions

- Designed a **multi-stage TypeScript content pipeline** that scrapes, analyzes, and AI-rewrites news articles at scale
- Integrated **Google Gemini and OpenAI models with failover logic** for content rewriting with factual accuracy via custom prompt engineering
- Deployed **microservices architecture** using Docker and **GitHub Actions cron jobs** for self-healing automated ingestion

---

## TECHNICAL SKILLS

**Languages:** JavaScript/TypeScript · Python · SQL · Java  
**Frontend:** React.js (v18/19) · Next.js (App Router) · Redux Toolkit · TailwindCSS · shadcn/ui  
**Backend:** Node.js · Express.js · NestJS · Django / DRF  
**Databases:** **PostgreSQL (Supabase)** · MongoDB · **pgvector** · **ChromaDB** · Redis  
**AI/LLM:** **OpenAI API · Google Gemini API · Groq API** · **RAG Pipelines** · **Vector Search** · **LangChain.js** · **Vercel AI SDK** · **Prompt Engineering**  
**DevOps:** Docker · GitHub Actions · Vercel · CI/CD Pipelines · Git · Prisma ORM  
**Tools:** **Socket.IO** · Razorpay API · Puppeteer · Postman · VideoSDK  

---

## EDUCATION

**B.Tech — Computer Science & Engineering**  
Vellore Institute of Technology (VIT), Vellore | Aug 2020 – Nov 2025  
Focus: Full Stack Development, AI Systems, Information Security Management

---

## AREAS OF EXPERTISE

✓ Conversational AI & WhatsApp Automation  
✓ LLM Integration (OpenAI, Gemini, Groq) with Provider Fallback  
✓ RAG Pipelines & Vector Search (pgvector, ChromaDB)  
✓ Real-Time Chat Infrastructure (Socket.IO)  
✓ PostgreSQL Query Optimization & API Performance  
✓ CI/CD Automation & Production Deployment  
✓ Prompt Engineering & LLM Response Optimization  

---

**Target Companies:** Sarvam AI, Yellow.ai  
**GitHub:** [github.com/atinsharma24](https://github.com/atinsharma24/)
