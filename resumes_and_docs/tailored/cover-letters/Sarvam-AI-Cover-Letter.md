# Cover Letter: Sarvam AI - Backend Engineer / Backend AI Engineer

**Atin Sharma**  
Agra 282007, India  
atinsharma24@gmail.com | +91 82185 02886  
[LinkedIn](linkedin-url) | [GitHub](https://github.com/atinsharma24/)

---

**Hiring Team**  
Sarvam AI  
Bengaluru, Karnataka  
[Date]

Dear Hiring Manager,

I'm writing to express my strong interest in the **Backend Engineer** and **Backend AI Engineer** positions at Sarvam AI. As a backend engineer with founding experience building **production LLM systems and conversational AI** for Indian SMBs, I'm deeply aligned with Sarvam's mission to build India's sovereign AI stack.

At OpenBiz Software, I architected **VyaparGPT** — a WhatsApp-native AI assistant processing **1,000+ active users** using **Node.js, OpenAI, and Gemini APIs**. I built the full message lifecycle (webhook → LLM processing → response dispatch) with **provider-fallback logic** (OpenAI ↔ Gemini) for high availability and cost optimization, managing **conversation context per session** for stateful interactions.

**Why I'm a strong fit for Sarvam AI:**

**LLM Infrastructure & Backend AI:**
- Built **provider-agnostic LLM layers** supporting **OpenAI, Gemini, Groq, and Anthropic** with one-config switching — no downstream changes to retrieval or generation logic
- Currently building **Nimbus**, a RAG document workspace on **pgvector and Groq**, with **streaming LLM responses** and **semantic search** using **cosine similarity** for precise retrieval
- Implemented **async document ingestion with 429 retry logic** and per-document status tracking to handle API rate limits gracefully in production

**Production Backend Engineering:**
- Reduced API latency by **40% through PostgreSQL optimization** (N+1 query resolution, indexing, response caching)
- Architected the core **MERN platform** from scratch at OpenBiz, scaling to 1,000+ users with **TypeScript** throughout
- Built **real-time bidirectional chat** using **Socket.IO** for low-latency conversational interfaces
- Owned **CI/CD pipelines** (GitHub Actions, Vercel), reducing deployment time by 30%

**RAG Pipelines & Vector Search:**
- Built **DocGPT**, a RAG system using **ChromaDB and Sentence Transformers (all-MiniLM-L6-v2)** for cost-efficient local embeddings
- Engineered **text chunking pipelines with PyPDF2** preserving context across boundaries for accurate document understanding
- Developed **Django REST backends** orchestrating retrieval → context injection → GPT-4o-mini response pipelines

**AI Document Verification:**
- Built an **AI document verification module** using **Google Gemini API** to automate data extraction from unstructured business documents (invoices, GST forms, licenses)

I'm particularly excited about Sarvam's work on **building LLM infrastructure for India** — from models to products to enterprise security. Your focus on **sovereign AI** and **India-first solutions** resonates deeply with my experience building AI systems tailored for Indian SMBs and compliance workflows.

I'd love to discuss how my backend AI engineering experience, LLM integration expertise, and production RAG pipeline work can contribute to Sarvam's mission of building India's AI stack.

Thank you for considering my application. I look forward to the opportunity to speak with you.

Best regards,  
**Atin Sharma**

---

**Portfolio Highlights:**
- **VyaparGPT** (WhatsApp AI Assistant): Node.js + OpenAI/Gemini + 1,000+ users
- **Nimbus** (RAG Document Workspace): pgvector + Groq + streaming LLM responses
- **DocGPT** (RAG System): Python + ChromaDB + OpenAI
