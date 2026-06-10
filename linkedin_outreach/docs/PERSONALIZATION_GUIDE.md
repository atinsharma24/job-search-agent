# LinkedIn Outreach Personalization Guide

> Every connection request message must score >= 2 on the personalization rubric below
> before it is added to the send queue.

---

## The Rule

**No message may be sent with personalization_score < 2.**

Scores are calculated at queue-preparation time by `scripts/prepare_queue.ts`.
Messages below the threshold are flagged `needs_personalization` in pending.json
and will not advance to the approved queue.

---

## Personalization Rubric (max 3 points)

| Check | Points |
|---|---|
| Message contains the contact's company name | +1 |
| Message references something specific about what the company builds (product, domain, layer) | +1 |
| Message references a specific Atin project or metric that maps to that company's domain | +1 |
| Message contains the phrase "I like what [Company] is building" | -1 (deduction) |

**Passing threshold: >= 2 points**

---

## LinkedIn Character Limit

**300 characters hard limit** for connection request notes.

Write all messages under **280 characters** (20-char buffer for safety).
The `prepare_queue.ts` scorer will flag anything over 280 chars as a warning
and over 300 chars as a hard block.

---

## Bad vs Good Example

### BAD — score 0 (uses template phrase, no specific asset, deduction applied)

```
Hey Raghu I work on Full Stack and GenAI and have been building RAG systems as a
Founding Engineer. I like what Yellow.ai is building and would love to connect and
share ideas on product and AI execution.
```

Score breakdown:
- Company name present: +1
- Specific about what Yellow.ai builds: 0 (no)
- Specific Atin project/metric: 0 (no)
- Contains "I like what Yellow.ai is building": -1
= **Score: 0 — BLOCKED**

---

### GOOD — score 3

```
Hey Raghu — built VyaparGPT, a WhatsApp-native AI for 40+ SMBs using LangChain
and provider fallback. Yellow.ai's orchestration layer is exactly the kind of
infra I want to work on. Would value connecting.
```
[208 chars ✓]

Score breakdown:
- Company name (Yellow.ai): +1
- Specific about what they build (orchestration layer): +1
- Specific Atin project/metric (VyaparGPT, 40+ SMBs, LangChain): +1
= **Score: 3 — PASSES**

---

## Atin's Project → Company Domain Mapping

| Atin's Asset | Use For |
|---|---|
| VyaparGPT (WhatsApp AI, RAG, LangChain, 40 SMBs) | Conversational AI companies (Yellow.ai, Haptik, Gupshup, Observe.AI, Uniphore, Rezo.ai, Skit.ai) |
| Nimbus (pgvector RAG, sub-800ms retrieval, Groq) | RAG/search infrastructure, developer tools (Hasura, Appsmith, Postman, BrowserStack) |
| N+1 fix → 40% latency reduction at 1000+ users | Any backend/infra role, fintech (Razorpay, Signzy, Hasura) |
| Razorpay billing (idempotent webhooks, 100% consistency) | Fintech/payments companies (Razorpay directly, Signzy) |
| Gemini Vision document extraction (GST, invoices, Aadhaar) | KYC/document intelligence (Signzy, Nanonets) |
| Autonomous Web Agent (Claude + MCP orchestration) | Dev tooling, agentic AI (BrowserStack, LambdaTest, DevRev, Postman) |
| LangGraph stateful agents, AI CRM | Agentic AI, CRM-adjacent (Yellow.ai, Observe.AI, Rezo.ai, DevRev) |
| Dual-model fallback architecture (OpenAI → Gemini) | Any LLM infra company (Sarvam AI, Krutrim) |

---

## Reusable Template Fragments (each under 60 chars)

These are building blocks — combine them into full messages:

```
shipped VyaparGPT — WhatsApp AI for 40+ SMBs
built RAG pipeline, sub-800ms on pgvector
cut API latency 40% via N+1 fix in Postgres
Gemini Vision doc extraction pipeline in prod
autonomous web agent on Claude + MCP
LangGraph stateful agents, prod AI CRM
dual-model fallback (OpenAI → Gemini on 5xx)
idempotent Razorpay webhooks, 100% consistency
```

---

## Per-Persona Writing Rules

| Persona | Lead With | Avoid |
|---|---|---|
| persona_1_founders | Product/technical match to their domain | Compliments, vague "love your work" |
| persona_2_vp_eng | Architecture decisions, no tech debt, LLM integration | Overly casual tone |
| persona_3_eng_managers | What you can ship on day one, no ramp needed | Long intros, soft asks |
| persona_4_senior_engineers | Genuine technical question about their stack | Pitching a job ask too early |
| persona_5_recruiters | Scannable: stack + availability + salary in first two lines | Dense paragraphs |

---

## Hard Rules (non-negotiable)

1. NEVER use "I like what [Company] is building" — instant -1 and template flag
2. ALWAYS name a specific Atin asset that maps to the company's domain
3. ALWAYS include an outcome metric where available (40 SMBs, sub-800ms, 40%)
4. Stay under 280 characters (20-char buffer before LinkedIn's 300 limit)
5. No markdown, asterisks, or line breaks — LinkedIn renders plain text only
6. First phrase must be "Hey [FirstName]" — keeps it conversational
7. Never use "I am actively exploring" as an opener for founder/VP personas
