# Cover Letter — Master Template (2026)

> **How to use.** Replace every `{{PLACEHOLDER}}`. Then do the three tailoring passes at the
> bottom before sending. Base version below is ~450 words — trims to ~300 by cutting one
> evidence block. House style matches `Sarvam-AI-Cover-Letter.md`.
>
> **NDA constraint:** never name AGI Ready clients, products, or commercial terms. Describe
> that work by stack, architecture pattern, and ownership scope only.

---

**Atin Sharma**
Agra 282007, Uttar Pradesh, India
atinsharma24@gmail.com | +91 82185 02886
[LinkedIn](https://www.linkedin.com/in/atinsharma24/) | [GitHub](https://github.com/atinsharma24/)

---

**Hiring Team**
{{COMPANY}}
{{COMPANY_CITY}}
{{DATE}}

Dear {{HIRING_MANAGER_OR_TEAM}},

I'm writing to apply for the **{{ROLE_TITLE}}** role at {{COMPANY}}. I'm a full-stack engineer
who has spent the last two years shipping production AI systems end-to-end — currently at
**AGI Ready Inc.**, an AI-native development studio, and before that as a **founding engineer
at OpenBiz Software**, where I was one of three engineers who took two products from zero to
**1,000+ active users**. {{ONE_SENTENCE_WHY_THIS_COMPANY}}

At OpenBiz I architected **VyaparGPT**, a WhatsApp-native LLM assistant in Node.js serving 40+
SMBs in closed pilot and scaling to 1,000+ platform users. I built the full message lifecycle
— webhook ingestion, HMAC-SHA256 validation, session context, LLM dispatch, response delivery
— with **stateless provider failover** (OpenAI → Gemini on 5xx, 429, or timeout) that kept
failures entirely off the user's screen. At **AGI Ready** I now build client products in
**Next.js, TypeScript, and Node.js**, architecting API and webhook integrations and async
workflows, and owning systems through to production.

**Why I'm a strong fit for {{COMPANY}}:**

**Production AI & RAG Pipelines**
- Built **provider-agnostic LLM layers** across OpenAI, Gemini, Groq, and Anthropic — switching inference providers is a single config flag, with no downstream retrieval or generation changes
- **Nimbus**, my RAG workspace on Next.js 14 + pgvector + Groq, delivers **sub-800ms semantic retrieval** with SSE streaming, async queue ingestion, and exponential-backoff 429 retry
- Engineered a **parallel Graph RAG pipeline** with LangGraph state machines and a dual-database ingestion router splitting unstructured data into Pinecone (hybrid dense/sparse) and structured compliance data into Supabase/pgvector
- Designed **hallucination guardrails** intercepting Cohere Re-rank v3 scores — a sub-0.4 confidence threshold rewrites the system prompt to enforce strict context-locking

**Backend Engineering That Holds Up**
- Cut **API latency by 40%** at 1,000+ user scale — N+1 chains rewritten as JOINs, composite indexes, TTL caching
- **Idempotent Razorpay billing** with HMAC-SHA256 webhook validation and out-of-order event handling: **100% payment-state consistency** across all paying customers
- Owned **CI/CD** (GitHub Actions + Vercel) with per-PR testing and approval-gated production — **30% faster deployments, zero broken-build incidents** over four months

**AI-Native Delivery**
- **Claude Code and Codex** are my primary development tools — I direct agentic tooling with architectural judgement and review its output against production standards, rather than iterating at the prompt level
- Built an **autonomous web agent** on MCP: a Claude 3.5 Sonnet Executor for DOM/form reasoning paired with a lightweight Groq Watcher for page-state validation, with WAF/CAPTCHA detection and human escalation

{{PARAGRAPH_ON_WHY_THIS_COMPANY_SPECIFICALLY}}

I'd welcome the chance to discuss how this maps to what {{TEAM_OR_PRODUCT}} is building. I'm
reachable at atinsharma24@gmail.com or +91 82185 02886.

Best regards,
**Atin Sharma**

---

## Tailoring Passes — do all three before sending

**1. Keyword pass.** Pull the 3 most-repeated technical terms from the JD and make sure each
appears verbatim in the opening paragraph or a bullet. Consult
`core_vault/JobApplyFiles/05_ats_keyword_dictionary.md`.

**2. Evidence pass.** Reorder the three evidence blocks so the most JD-relevant one is first,
and delete the least relevant block entirely if the letter runs past one page. Swap in
domain-specific bullets from
`resumes_and_docs/master_cv/Atin_Sharma_Professional_Experience_Dossier.md` §5 where a project
maps better than the default:

| If the role is… | Lead with |
|---|---|
| Conversational AI / chatbots / WhatsApp | VyaparGPT — session context, provider failover, Gemini Vision |
| RAG / vector search / document AI | Nimbus + DocGPT + the Graph RAG pipeline |
| Fintech / payments / billing | Razorpay idempotent billing, HMAC webhooks, 100% consistency |
| Compliance / KYC / legal-tech | Gemini Vision GST extraction, Supabase compliance partitioning |
| DevOps / platform / infra | CI/CD ownership, Dockerised microservices, N+1 and indexing work |
| Agents / MCP / AI tooling | Autonomous Web Agent, MCP orchestration, Claude Code practice |

**3. Specificity pass.** `{{PARAGRAPH_ON_WHY_THIS_COMPANY_SPECIFICALLY}}` must reference
something only findable by actually reading the company's site, docs, changelog, or
engineering blog. Generic mission-statement praise is worse than omitting the paragraph.

## Matching resume

Attach `resumes_and_docs/categories/pdf/Atin_Sharma_Resume_2026.pdf`, or a
category-tailored variant per the routing table in `CLAUDE.md` → *Resume Selection Logic*.

## Standing facts

| Field | Value |
|---|---|
| Expected CTC | **18–24 LPA**, negotiable. Never quote below 18 in writing. *(A private 15 LPA walk-away floor exists in the vault — it is never disclosed.)* |
| Current CTC | 11.2 LPA |
| Notice period | 15 days |
| Total experience | ~14 months, currently employed — never answer "fresher" |
| Work preference | Remote-first; open to Bangalore, Hyderabad, Pune, Delhi NCR, Mumbai |
| Work authorisation | Indian citizen — no sponsorship required |
