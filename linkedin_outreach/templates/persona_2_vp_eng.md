---
persona_id:   2
persona_name: VP OF ENGINEERING / HEAD OF AI
angle:        Architecture decisions, LLM integration without technical debt, scalability.
variants:     3
---

## VARIANT 2A — linkedin_connection — 167 chars

SUBJECT: N/A

PLACEHOLDERS: [Company]

---
Shipping LLM features into MERN backends without accumulating debt is a specific skill. I've done it — LangGraph orchestration, pgvector RAG, Docker. Building at [Company] looks like the right next problem.
---

## VARIANT 2B — cold_email

SUBJECT: Backend + LLM integration engineer — no "AI wrapper" experience

PLACEHOLDERS: [Company Name], [Specific Reason]

---
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

## VARIANT 2C — followup

SUBJECT: Re: Backend + LLM integration engineer — no "AI wrapper" experience

PLACEHOLDERS: [Company Name]

---
Still interested in connecting if you're building out your AI engineering capacity.

One specific thing worth noting: I've already solved the provider-agnosticism problem — the abstraction layer I built lets you switch between Groq, OpenAI, and Anthropic at config level with zero downstream changes to retrieval or generation logic. For a team making long-term LLM vendor decisions, that's worth having in-house.

If there's a relevant opening at [Company Name] or if timing is off right now, I'd still value being on your radar. Either way, happy to share the architecture doc.

**Atin**
---