# GenAI / Prompt Engineer

**Profile:**
Specialized Generative AI Engineer focused on LLM orchestration, agentic workflows, and high-fidelity RAG pipelines. Expert in prompt engineering, dual-model failover architectures (Gemini + OpenAI), and semantic search optimization using pgvector and ChromaDB. Experienced in designing resilient AI infrastructures with sub-800ms retrieval times and fault-tolerant message lifecycles.

**OpenBiz (Jun 2025 – May 2026) | Founding Engineer | Remote / Bangalore**

**Key Experience Highlights:**
- LLM provider-fallback: OpenAI → Google Gemini on HTTP 5xx, 429 rate-limit, or configurable timeout — response-shape normalisation ensures zero failure surface exposed to users.
- VyaparGPT: full WhatsApp message lifecycle with HMAC-SHA256 webhook validation, multi-turn conversational context via rolling `conversation_history[]`, Gemini Vision API document extraction from GST certificates and vendor agreements.
- Serving 40+ SMBs in closed pilot, scaling to 1,000+ active platform users.
- Automated Content Intelligence Pipeline: dual-model AI rewriting (Gemini primary → OpenAI fallback per article); React 19 Diff View with per-article state machine (pending_review → approved → published).
- VIT Research Contributor (Jan–Nov 2025): Blockchain-Based LLM Using Fully Homomorphic Encryption (FHE) — investigating computation on encrypted academic data without decryption; explored FHE-compatible cryptographic primitives for privacy-preserving model inference.

**Projects:**
- **Nimbus** (In Dev 2026): Provider-agnostic LLM abstraction layer (Groq/OpenAI/Anthropic via single config flag), pgvector cosine search, SSE streaming, 429 retry with exponential backoff.
- **DocGPT**: Django RAG pipeline — local all-MiniLM-L6-v2 embeddings (384-dim, zero API cost), ChromaDB cosine retrieval, GPT-4o-mini generation, overlap chunking.
- **Autonomous Web Agent**: Dual-agent (Claude 3.5 Sonnet Executor + Groq Watcher), MCP via BrowserOS for DOM-level form interaction, persistent queue with WAF/CAPTCHA detection.

**Tech Focus:**
Python, LangChain, Groq API, pgvector, ChromaDB, OpenAI, Google Gemini, Prompt Engineering, Agentic Workflows.

**Patterns:** WebSocket (Socket.IO), REST, Webhook Validation (HMAC-SHA256), N+1 Query Optimization, Vector Similarity Search (cosine), Provider-Agnostic LLM Layers, Idempotent Event Processing.

**Profile Snapshot:** Immediate Joiner · Remote-first · 15L+ (negotiable) · Indian Citizen · github.com/atinsharma24
