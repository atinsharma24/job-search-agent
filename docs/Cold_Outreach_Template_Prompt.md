# Cold Outreach Template Suite

---

## PERSONA 1 — FOUNDERS / C-SUITE (CEO/CTO)

**Angle:** Business impact, shipping velocity, LangGraph/RAG aligned to their product roadmap.

---

### 1A · LinkedIn Connection Request (≤300 chars)

> Building compliance/conversational AI at [Company]? I shipped a WhatsApp-native LLM assistant + RAG pipeline at a fintech startup. LangGraph, pgvector, MERN. Would value connecting.

---

### 1B · Cold Email

**Subject:** LangGraph + RAG engineer — relevant to [Company]'s [Specific Feature/Product]

Atin here — full-stack engineer who spent the last year as a founding engineer at an AI-first startup building production LLM systems for Indian SMBs.

The work that's directly relevant to [Company Name]:

- Architected a WhatsApp-native AI assistant using LangGraph state machines — multi-turn context, provider fallback (OpenAI → Gemini), webhook-to-response lifecycle
- Built a production RAG pipeline on pgvector with sub-800ms retrieval and async ingestion with rate-limit handling
- Resolved N+1 patterns in Supabase that cut API latency 40% — the kind of fix that matters once your pipeline is under real load

I noticed [Specific Feature/News — e.g., "you're expanding your KYC document intelligence layer" / "your recent raise is going toward agentic automation"]. That's the exact intersection I've been building in.

Not looking for a pitch meeting — happy to share a relevant code sample or a two-paragraph breakdown of how I'd approach a specific problem on your roadmap. Worth a 15-minute call?

**Atin Sharma**
github.com/atinsharma24 | linkedin.com/in/atinsharma24

---

### 1C · Follow-Up (Send 6–8 days after 1B, no reply)

**Subject:** Re: LangGraph + RAG engineer — relevant to [Company]'s [Specific Feature/Product]

Quick follow-up in case this got buried.

One concrete thing I can offer: I've already built the core loop you'd need for a document intelligence or conversational AI feature — ingestion, chunking, vector retrieval, LLM orchestration, fallback handling. The scaffolding exists, it's been tested in production, and I can adapt it.

If the timing isn't right, no issue at all. But if [Company Name] has an AI/backend opening coming up, I'd genuinely like to be in that conversation.

**Atin**

---

## PERSONA 2 — VP OF ENGINEERING / HEAD OF AI

**Angle:** Architecture decisions, LLM integration without technical debt, scalability.

---

### 2A · LinkedIn Connection Request (≤300 chars)

> Shipping LLM features into MERN backends without accumulating debt is a specific skill. I've done it — LangGraph orchestration, pgvector RAG, Docker. Building at [Company] looks like the right next problem.

---

### 2B · Cold Email

**Subject:** Backend + LLM integration engineer — no "AI wrapper" experience

The most common failure mode when teams add AI to an existing backend: it becomes a bolted-on API call with no state management, no fallback, and no observability. I've specifically avoided that pattern.

At my last role I owned the LLM integration layer end-to-end:

- **Orchestration:** LangGraph for multi-step, stateful workflows — not a linear chain, an actual state machine with conditional routing and retry handling
- **Retrieval:** pgvector RAG pipeline with cosine similarity, async ingestion, per-document status tracking, and 429 retry logic — built to survive production rate limits
- **Backend contract:** Clean separation between the AI layer and the core MERN API so LLM providers can be swapped (and were — OpenAI to Gemini fallback in production) without touching business logic

I'm targeting roles at [Company Name] specifically because [Specific Reason — e.g., "your compliance automation stack is the exact domain I've been building for" / "the way your platform handles document verification maps closely to problems I've already solved"].

Happy to walk through the architecture on a short call, or send over the relevant code if that's more useful.

**Atin Sharma**
github.com/atinsharma24 | linkedin.com/in/atinsharma24

---

### 2C · Follow-Up

**Subject:** Re: Backend + LLM integration engineer — no "AI wrapper" experience

Still interested in connecting if you're building out your AI engineering capacity.

One specific thing worth noting: I've already solved the provider-agnosticism problem — the abstraction layer I built lets you switch between Groq, OpenAI, and Anthropic at config level with zero downstream changes to retrieval or generation logic. For a team making long-term LLM vendor decisions, that's worth having in-house.

If there's a relevant opening at [Company Name] or if timing is off right now, I'd still value being on your radar. Either way, happy to share the architecture doc.

**Atin**

---

## PERSONA 3 — ENGINEERING MANAGERS

**Angle:** Immediate ticket-taking capacity, ownership, MERN + Docker proficiency, no hand-holding required.

---

### 3A · LinkedIn Connection Request (≤300 chars)

> Managing a team shipping AI-adjacent backend features? I own the full loop — MERN, LangGraph, Docker, RAG pipelines. Founding engineer background means I don't wait for specs. Would like to connect.

---

### 3B · Cold Email

**Subject:** Full-stack + AI engineer — can take AI backend tickets from day one

Straight to the point: I'm an engineer who can sit down on day one and contribute to an AI-integrated backend without a ramp-up period.

What that looks like concretely:

- **MERN + TypeScript** across the full stack, strict typing, production CI/CD via GitHub Actions + Vercel
- **LLM orchestration** with LangGraph — I've built stateful multi-step agents, not just prompt wrappers
- **RAG pipelines** — pgvector, chunking strategies, retrieval tuning, async ingestion with error handling
- **Docker** — containerised deployments, environment parity, no "works on my machine" issues
- **Founding engineer instinct** — I've owned features from zero, not just executed tickets

I'm targeting [Company Name] because [Specific Reason]. If you have backend or AI-adjacent capacity needs, I'd like to understand what the team is working on and whether there's a fit.

No pressure on timeline — even a 20-minute intro call would be useful.

**Atin Sharma**
github.com/atinsharma24 | linkedin.com/in/atinsharma24

---

### 3C · Follow-Up

**Subject:** Re: Full-stack + AI engineer — can take AI backend tickets from day one

Following up briefly — I know your inbox moves fast.

If it helps to have a one-line summary: full-stack engineer with a year of production LLM systems (LangGraph, RAG, provider fallback), MERN + Docker, available immediately, targeting [Company Name] specifically.

If there's an open role or if headcount is coming up, I'd genuinely like to be considered. Happy to do a technical screen at any point.

**Atin**

---

## PERSONA 4 — SENIOR / STAFF ENGINEERS

**Angle:** Peer-to-peer technical curiosity, specific stack questions, referral pathway.

---

### 4A · LinkedIn Connection Request (≤300 chars)

> Fellow engineer building LLM-integrated backends. Curious how [Company] handles context window management at scale — LangGraph or something custom? Would value a quick exchange.

---

### 4B · Conversation-Starter Message (LinkedIn DM, not a job ask)

Hey [Name] — came across your profile while looking into [Company Name]'s engineering work.

Quick genuine question: when you're orchestrating multi-step LLM workflows at [Company], do you use something like LangGraph for the state machine, or did the team roll a custom solution? I've been using LangGraph in production and ran into some interesting edge cases around conditional routing and memory persistence — curious whether you hit similar issues at your scale.

Not trying to pitch anything — just find this problem space genuinely interesting and your team seems to be doing some of the more thoughtful work in this area.

**Atin**

---

### 4C · Follow-Up / Referral Ask (Only after they've replied to 4B)

Thanks for the context on [their answer] — that's actually a cleaner approach than what I implemented.

Relevant to share: I'm actively looking at [Company Name] for my next role. Backend/AI engineering, targeting the [specific team/role if known] side of things. My background is LangGraph, RAG pipelines on pgvector, MERN, Docker — about a year of production LLM systems at a fintech startup.

If you think there's a fit worth exploring, I'd genuinely appreciate an internal nudge or even just knowing who the right person to reach is. No pressure at all if it's not the right time — I just figured a direct ask was more respectful of your time than dancing around it.

---

### 4D · Alternative — Specific Technical Observation (Cold, no prior interaction)

Hey [Name] — noticed your post/talk/PR about [Specific Technical Thing at Company].

The retrieval architecture you described maps closely to something I wrestled with building a RAG pipeline on pgvector — specifically around [specific problem, e.g., "cosine similarity thresholds producing low-confidence chunks under domain-specific jargon"]. Curious how [Company] handles that at your document volume.

I'm also keeping an eye on [Company Name] for backend/AI roles if that's ever relevant context. But genuinely asking the question either way.

**Atin** — github.com/atinsharma24

---

## PERSONA 5 — TECHNICAL RECRUITERS / TALENT ACQUISITION

**Angle:** Scannable, stack-precise, role-aligned, interview-ready signal.

---

### 5A · LinkedIn Connection Request (≤300 chars)

> Full-stack + AI engineer, open to roles at [Company]. Stack: MERN, LangGraph, RAG/pgvector, Docker, TypeScript. Targeting backend or AI engineering. Would like to connect.

---

### 5B · Cold Email / InMail

**Subject:** Backend + AI Engineer — [Company Name] roles — immediate availability

Hi [Name],

I'll keep this structured so it's easy to route.

**Who I am:**
Full-stack product engineer, founding-team background at an AI-first startup. One year of production systems in the conversational AI / document intelligence space.

**Core stack:**
`TypeScript` · `Node.js` · `React/Next.js` · `Python` · `FastAPI` · `LangGraph` · `pgvector` · `RAG pipelines` · `Docker` · `PostgreSQL` · `GitHub Actions`

**What I've shipped:**
- WhatsApp-native LLM assistant (LangGraph state machine, multi-provider fallback, ~40 pilot SMBs)
- Production RAG pipeline (pgvector, sub-800ms retrieval, async ingestion)
- 40% API latency reduction via N+1 query resolution in Supabase

**What I'm targeting:**
Mid-level Backend, Full-Stack, or AI Engineering role — conversational AI, document intelligence, or compliance automation domain — at [Company Name] specifically.

**Compensation:** ₹15L–₹18L
**Availability:** Immediate
**Location:** Open to Bangalore; remote-first preferred

If any of your open roles match this profile, I'd like to be in the process. Happy to do a technical screen at short notice.

**Atin Sharma**
atinsharma24@gmail.com | github.com/atinsharma24 | linkedin.com/in/atinsharma24

---

### 5C · Follow-Up

**Subject:** Re: Backend + AI Engineer — [Company Name] roles — immediate availability

Hi [Name] — quick follow-up on my previous message.

If the timing on open roles has changed or a relevant position has come up, I'm still very interested in [Company Name]. I'm actively interviewing and moving fast — won't be available indefinitely.

Single line summary for easy routing: **LangGraph + RAG + MERN, 1 year production AI systems, immediate joiner, ₹15–18L band.**

Happy to clear any technical bar quickly.

**Atin**

---

## QUICK REFERENCE — TEMPLATE SELECTION GUIDE

| Situation | Use |
|---|---|
| Found the CTO/CEO on LinkedIn, no mutual connection | 1A → wait 3 days → 1B if connected |
| Found a VP Eng job posting, want to bypass HR | 2B directly to their work email |
| Referral is the goal, found a senior engineer | 4A → wait for accept → 4B → 4C only after reply |
| Recruiter reached out first | Skip 5A/5B — respond with 5B structure inline |
| Sent cold email, no reply after 7 days | One follow-up only (1C / 2C / 3C) then move on |
| Engineer posted something technical | 4D — best conversion rate of all templates |

- [ ] **One rule above all:** Personalise the `[Specific Feature/News]` placeholder every single time. A template sent as a template converts at near zero. The same template with one sentence of genuine company-specific observation converts at 3–5x.