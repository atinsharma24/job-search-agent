# TECHNICAL DEEP-DIVE DOCUMENTATION
### Atin Sharma — Architecture Knowledge Base for Technical Screens
> Usage: Query by architecture name or technology keyword during live technical interviews  
> Source: Nimbus, DocGPT, VyaparGPT, Content Intelligence Pipeline

---

## Architecture A — Production RAG Pipeline (Nimbus + DocGPT)

### System Overview

Two implementations of RAG architecture:
- **Nimbus** — Next.js 14, pgvector, Groq — vector-native PostgreSQL implementation
- **DocGPT** — Django, ChromaDB — standalone vector DB implementation

Both share the same conceptual pipeline but differ in vector storage backend and generation model.

---

### Pipeline Stages

#### Stage 1 — Document Ingestion

| Implementation | Method |
|---|---|
| Nimbus | Async ingestion with per-document status tracking |
| DocGPT | PDF ingestion via PyPDF2 |

**Nimbus ingestion specifics:**
- Asynchronous queue-based processing to avoid blocking the request thread
- Status states: `pending → processing → indexed → error`
- 429 retry logic: on rate-limit responses from embedding APIs, backs off with exponential delay before marking failed

**DocGPT ingestion specifics:**
- PyPDF2 used for PDF text extraction
- Chunking strategy: fixed-size chunks with **overlap** (overlap prevents context loss at chunk boundaries; sentences spanning a chunk break are represented in both adjacent chunks)
- Typical chunk parameters: chunk size ~500–1000 tokens, overlap ~50–100 tokens (tuned for dense business documents)

---

#### Stage 2 — Embedding Generation

| Implementation | Model |
|---|---|
| Nimbus | OpenAI embeddings (via provider-agnostic layer) |
| DocGPT | `all-MiniLM-L6-v2` (Sentence Transformers, local) |

- `all-MiniLM-L6-v2` produces 384-dimensional dense vectors; chosen for speed and offline capability
- Nimbus embedding is provider-switchable — same abstraction layer used for generation also handles embedding routing

---

#### Stage 3 — Vector Storage & Retrieval

**Nimbus — pgvector (PostgreSQL extension):**
- Vectors stored as `vector(dimensions)` column type within an existing PostgreSQL table
- Similarity metric: **cosine similarity** — measures angle between query vector and document chunk vectors; range [−1, 1], where 1 = identical direction
- Query pattern: `SELECT ... ORDER BY embedding <=> query_vector LIMIT k`
  - pgvector `<=>` operator = cosine distance
- Advantage: no separate vector DB process; vectors co-located with relational metadata (`user_id`, `document_id`, `created_at`) enabling hybrid SQL + semantic filtering
- Index types supported: `IVFFlat` or `HNSW` (HNSW preferred for query speed at scale)

**DocGPT — ChromaDB:**
- In-process or client-server vector database
- Collection-based storage; each document set isolated in a named collection
- Similarity: cosine (configurable)
- Embedding function passed at collection creation time
- Retrieval: `collection.query(query_embeddings=[...], n_results=k)`

---

#### Stage 4 — Generation (RAG Synthesis)

**Nimbus — Provider-Agnostic LLM Layer:**

```
Config: { provider: "groq" | "openai" | "anthropic" }
         ↓
LLM Abstraction Layer
         ↓
  ┌──────────────┬──────────────┬──────────────┐
  │   Groq API   │  OpenAI API  │ Anthropic API│
  └──────────────┴──────────────┴──────────────┘
```

- Single interface exposes `generate(prompt, context)` regardless of underlying provider
- Provider credentials loaded from environment; switching providers requires only config change — zero code changes
- **Streaming:** Groq API used as primary for low-latency streaming responses; chunks sent to client via SSE or streaming fetch

**DocGPT — GPT-4o-mini:**
- Fixed provider (OpenAI)
- Django REST backend orchestrates: vector retrieval → prompt assembly → GPT-4o-mini API call → response return
- Prompt structure: system context + retrieved chunks + user query

---

### Key Design Decisions

| Decision | Rationale |
|---|---|
| pgvector over standalone vector DB | Leverages existing PostgreSQL infra; transactional consistency; JOIN-capable |
| Chunk overlap strategy | Prevents semantic loss at chunk boundaries |
| Cosine similarity over L2 | Direction-invariant; appropriate for normalized embeddings |
| Provider-agnostic layer | Avoids vendor lock-in; enables cost/latency optimization switching |
| Async ingestion | Prevents request timeout on large documents; decouples UX from processing |

---
---

## Architecture B — Conversational AI Infrastructure (VyaparGPT)

### System Overview

WhatsApp-native LLM assistant built on the WhatsApp Business API, deployed for Indian SMBs.  
Runtime: Node.js. Dual LLM provider integration (OpenAI + Google Gemini) with active failover.

---

### Webhook Lifecycle

```
WhatsApp Platform
      │
      ▼ HTTP POST (webhook event)
Webhook Ingestion Layer (Node.js Express endpoint)
      │
      ├─ Signature validation (HMAC-SHA256 against shared secret)
      ├─ Message type routing (text / media / document / status update)
      │
      ▼
Session Context Lookup
      │
      ├─ Key: phone_number_id + from_phone_number
      ├─ State: conversation_history[], user_metadata, session_created_at
      │
      ▼
Intent & Content Processing
      │
      ▼
LLM API Dispatch (with fallback — see below)
      │
      ▼
Response Construction
      │
      ▼
WhatsApp Send API (POST to graph.facebook.com/messages)
      │
      ▼
Delivery Status Webhook (read receipts / delivery confirmations)
```

---

### Provider-Fallback Logic (OpenAI ↔ Gemini)

```
Incoming Message
      │
      ▼
Primary Provider: OpenAI (GPT)
      │
      ├─ SUCCESS → return response
      │
      └─ FAILURE conditions:
            - HTTP 5xx (server error)
            - HTTP 429 (rate limit)
            - Timeout (configurable threshold)
            │
            ▼
      Secondary Provider: Google Gemini API
            │
            ├─ SUCCESS → return response
            │
            └─ FAILURE → return graceful degradation message to user
```

**Implementation details:**
- Both providers initialized at startup with their respective API clients
- Failover is transparent to the user — no error surface, no retry indication
- Provider response normalization layer: both APIs return different response shapes; normalizer extracts `content.text` uniformly regardless of provider
- Failover is stateless per-request — not sticky; next message can hit primary again if recovered

---

### Session-Based Context Management

- Session key: composite of `phone_number_id` + `user_phone_number`
- Context window: rolling `conversation_history[]` array of `{role, content}` objects passed to LLM on every turn
- State persistence: in-memory (fast) with optional database persistence for long-running sessions
- TTL: sessions expire after configurable idle period (e.g., 30 min) to prevent stale context injection
- Multi-turn handling: history prepended to each LLM call, enabling follow-up questions without re-stating context

---

### LLM-Powered Document Verification Module

- **Trigger:** user sends image/document via WhatsApp (media webhook event)
- **Media retrieval:** WhatsApp media ID → download via Graph API to temporary buffer
- **Extraction prompt:** structured prompt to Gemini Vision API specifying target fields (GST number, business name, date, amount, etc.)
- **Output:** JSON of extracted fields → stored to database / returned to business workflow
- **Document types handled:** GST certificates, Aadhaar (redacted), invoices, vendor agreements (photographed / scanned)

---
---

## Architecture C — Resilient Scraping Pipeline (Content Intelligence)

### System Overview

Autonomous content ingestion and rewriting pipeline.  
Microservices architecture on Docker. GitHub Actions cron for scheduling.  
Dual-model AI rewriting with failover. React 19 Diff View editorial frontend.

---

### Puppeteer-Based Client-Side Rendering Bypass

**Problem:** Target content sites render HTML via JavaScript (React/Vue SPAs or dynamically loaded content). Standard HTTP fetch (e.g., `axios.get(url)`) retrieves the pre-render HTML shell — content nodes are empty. CSS selectors return null.

**Solution — Puppeteer headless Chrome:**

```
Puppeteer.launch() → headless Chromium instance
      │
      ▼
page.goto(url, { waitUntil: 'networkidle2' })
      │         └─ waits until <2 network connections for 500ms
      │            ensures JS hydration and lazy-loads complete
      ▼
page.waitForSelector(targetSelector)  [optional — explicit wait for element]
      │
      ▼
page.evaluate(() => document.querySelector(...).innerText)
      │         └─ executes inside browser context, returns serialized result
      ▼
Extracted structured text → passed to TypeScript processing layer
```

**Key configurations:**
- `waitUntil: 'networkidle2'` — more reliable than `domcontentloaded` for SPA content
- `page.setUserAgent(...)` — mimic real browser UA to avoid bot detection
- `page.setExtraHTTPHeaders(...)` — language/accept headers for localized content
- Timeout: per-page configurable to avoid hanging on slow targets

---

### TypeScript Processing Layer

- Raw extracted HTML/text passed through TypeScript normalization step
- Operations: whitespace normalization, removal of navigation/footer boilerplate, sentence boundary detection
- Output: clean plaintext article body, structured as `{ title, body, source_url, scraped_at }`

---

### Dual-Model AI Rewriting with Failover

```
Clean Article Body
      │
      ▼
Primary Rewrite: Google Gemini API
      │
      ├─ SUCCESS → rewritten content
      │
      └─ FAILURE (5xx / rate limit / timeout)
            │
            ▼
      Secondary Rewrite: OpenAI API
            │
            ├─ SUCCESS → rewritten content
            │
            └─ FAILURE → flag article as "manual_review_required"
```

**Rewriting prompt design:**
- Instruction: rewrite for factual accuracy preservation, tone normalization, plagiarism avoidance
- Input: original scraped body
- Output: rewritten body in same structure

**Failover is per-article** — not per-session. Each article independently attempts primary then falls back; partial batch success is valid (some articles rewritten by Gemini, others by OpenAI).

---

### React 19 Diff View (Editorial Frontend)

- Split-screen interface: left pane = original scraped content, right pane = AI-rewritten content
- Real-time diff highlighting: word-level or line-level change markers (similar to Git diff visual)
- Editorial actions: approve / reject / manual-edit per article
- State machine per article: `pending_review → approved → published / rejected`
- Purpose: human-in-the-loop checkpoint before any AI-rewritten content is published

---

### Docker Microservices + GitHub Actions Cron

```
┌─────────────────────────────────────┐
│           Docker Compose            │
│  ┌─────────────┐ ┌───────────────┐  │
│  │  Scraper    │ │  AI Rewriter  │  │
│  │  Service    │ │  Service      │  │
│  │ (Puppeteer) │ │ (Gemini+OAI)  │  │
│  └─────────────┘ └───────────────┘  │
│  ┌─────────────┐ ┌───────────────┐  │
│  │   React 19  │ │   Laravel     │  │
│  │   Frontend  │ │   API         │  │
│  └─────────────┘ └───────────────┘  │
└─────────────────────────────────────┘
         ▲
         │ Triggered by
┌─────────────────┐
│  GitHub Actions │
│  cron schedule  │
│  (e.g., */6hrs) │
└─────────────────┘
```

**Self-healing mechanism:**
- GitHub Actions cron re-triggers pipeline on schedule regardless of prior run state
- Failed scrape targets logged but do not block the batch; pipeline continues to next URL
- Docker container restart policy: `unless-stopped` — recovers from process crashes automatically

---

> **MCP Agent Usage Note:**  
> Query this document by architecture letter (A / B / C) or by technology keyword  
> (e.g., "pgvector", "webhook", "Puppeteer") to retrieve the relevant technical block  
> for answering deep technical screening questions.
