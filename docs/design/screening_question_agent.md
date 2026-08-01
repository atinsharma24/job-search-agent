# Design: Autonomous Screening-Question Agent

**Status:** Not implemented — design only, ready to build
**Requested:** 1 August 2026
**Supersedes:** the static rule table in `scripts/vault_answers.py` (which stays as the fallback tier)

---

## 1. The problem

Portal application forms ask free-text and multiple-choice questions that no static rule
table can enumerate:

> *"Why do you want to work at Qure.ai specifically?"*
> *"Describe a time you shipped something under an unreasonable deadline."*
> *"Rate your proficiency in Kubernetes on a scale of 1–5."*
> *"This role requires occasional weekend on-call. Are you comfortable with that?"*
> *"What is your reason for leaving your current role?"*

Today `vault_answers.answer_for_question()` returns `ABSTAIN` for anything outside its rule
table, and the Naukri applier reports `blocked:unanswerable_question` rather than submitting.
That is the correct *safe* behaviour — it replaced a system that typed a skills list into any
unrecognised question and `"10 LPA"` into every salary field — but it costs applications.

**The goal is to recover those applications without reintroducing the failure mode that made
abstention necessary.** The agent must be *more* trustworthy than the rule table it extends,
not merely more capable.

---

## 2. Non-negotiable constraints

These are derived from defects that actually shipped in this vault. Each one is a hard
requirement, not a preference.

| # | Constraint | Why |
|---|---|---|
| C1 | **Never invent a fact about the candidate.** Every claim must trace to `01_atomic_fact_sheet.json`, `06_logistics_mapping.json`, or a resume. | `CLAUDE.md` absolute rule. The pipeline previously submitted a fabricated `"10 LPA"` and `"OpenBiz Software"` as current employer. |
| C2 | **Never emit the private ₹15 LPA floor.** | It leaked into `staged_application_resume.pdf` and shipped to employers. |
| C3 | **Never answer a question with legal or financial consequence.** Bonds, non-competes, notice-period commitments beyond 15 days, relocation commitments, sponsorship claims. | These bind the candidate. A model should not sign things. |
| C4 | **Never overstate experience.** 14 months is 14 months; "5+ years?" is answered No. | The pipeline previously submitted 0 YOE while the resume claimed founding-engineer work — the inverse error, equally damaging. |
| C5 | **Abstention must remain available and cheap.** | The agent is an *extension* of the rule table, not a replacement. When unsure, it must fall back, not guess. |
| C6 | **Every answer must be logged with its provenance and reviewable after the fact.** | Today there is no way to audit what was submitted. |
| C7 | **NDA-bound content must never appear.** AGI Ready client names, product specifics, commercial terms. | One-way NDA + 12-month non-compete. |

---

## 3. Architecture

A four-tier cascade. **Cost and risk both increase down the tiers, so the cheapest safe tier
always wins.** The LLM is deliberately the third choice, not the first.

```
                    ┌─────────────────────────────────────┐
   question ───────▶│ Tier 0 · Deterministic rules        │──▶ answer
                    │ vault_answers.py (exists today)     │
                    └───────────────┬─────────────────────┘
                                    │ no match
                    ┌───────────────▼─────────────────────┐
                    │ Tier 1 · Semantic cache             │──▶ answer
                    │ embedding match vs approved answers │
                    └───────────────┬─────────────────────┘
                                    │ below similarity threshold
                    ┌───────────────▼─────────────────────┐
                    │ Tier 2 · Grounded LLM               │──▶ answer + citations
                    │ retrieval over vault, constrained   │
                    └───────────────┬─────────────────────┘
                                    │ low confidence / unsafe class
                    ┌───────────────▼─────────────────────┐
                    │ Tier 3 · Human queue                │──▶ ABSTAIN, job flagged
                    └─────────────────────────────────────┘
```

### Tier 0 — deterministic rules *(already built)*

`scripts/vault_answers.py`. Hard-NO / hard-YES / value lookups / tech-scoped YOE. Fast, free,
auditable. **Any question it answers must never reach the LLM** — determinism beats inference
for facts we already hold.

### Tier 1 — semantic cache

Every human-approved answer is embedded and stored. A new question is embedded and matched by
cosine similarity; above ~0.92 the previous answer is reused verbatim.

This tier is what makes the system improve over time: the same twenty questions recur across
hundreds of postings ("why this company", "notice period", "reason for leaving"). After a few
review cycles most traffic never reaches the LLM.

Storage: `active_application_context/answer_cache.jsonl`
```json
{"question":"What is your reason for leaving?","embedding":[...],
 "answer":"I'm looking for founding-level ownership of a single product...",
 "approved_by":"human","approved_at":"2026-08-02T10:00:00","uses":14,
 "last_used":"2026-09-01T12:00:00"}
```

### Tier 2 — grounded LLM

**Retrieval, not recall.** The model never answers from parametric memory. It receives only
retrieved vault context and must cite which fields it used.

Corpus: `01_atomic_fact_sheet.json` · `06_logistics_mapping.json` (`qa_bank`) ·
`Atin_Sharma_Professional_Experience_Dossier.md` · `03_technical_deep_dive.md` ·
`05_ats_keyword_dictionary.md` · the four category resumes.

Structured output, so refusal is a first-class result rather than prose:

```python
class AgentAnswer(BaseModel):
    decision: Literal["answer", "abstain"]
    answer: str = ""
    confidence: float                 # 0.0–1.0
    citations: list[str]              # e.g. ["fact_sheet.experience[0].scope_of_work"]
    risk_class: Literal["factual", "preference", "commitment", "subjective"]
    reasoning: str                    # one line, logged not submitted
```

**Rejection rules applied to the model's output** — the model is not trusted to self-police:

```python
def validate(ans: AgentAnswer, question: str) -> Answer:
    if ans.decision == "abstain":                    return ABSTAIN
    if ans.risk_class == "commitment":               return ABSTAIN   # C3
    if ans.confidence < 0.75:                        return ABSTAIN   # C5
    if not ans.citations:                            return ABSTAIN   # C1 — uncited = invented
    vc.assert_no_private_floor(ans.answer)                            # C2, raises
    if not citations_resolve(ans.citations):         return ABSTAIN   # C1 — hallucinated path
    if nda_terms_present(ans.answer):                return ABSTAIN   # C7
    if overstates_experience(ans.answer):            return ABSTAIN   # C4
    return Answer(VALUE, ans.answer, rule=f"agent:{ans.risk_class}")
```

`citations_resolve()` is the load-bearing check: every citation is resolved against the actual
vault structure, and an unresolvable path means the model invented its grounding. This catches
the single most dangerous failure mode — a confident, well-written, entirely fabricated claim.

### Tier 3 — human queue

`active_application_context/pending_questions.jsonl`, one row per abstention with the question,
portal, job URL, and reason. Reviewing it is how Tier 1 gets seeded. A CLI (`--review`)
presents each, accepts an answer, and writes it to the cache as approved.

---

## 4. Risk classes

Routing is by consequence, not by question format.

| Class | Example | Handling |
|---|---|---|
| **factual** | "Years with React?", "Highest qualification?" | Tier 0 preferred; agent may answer with citation |
| **preference** | "Comfortable with hybrid?", "Open to Bangalore?" | Agent may answer from `work_preference` |
| **subjective** | "Why this company?", "Greatest weakness?" | Agent may draft; **requires** citation to `qa_bank` or dossier |
| **commitment** | Bonds, sponsorship, 90-day notice, relocation guarantees | **Always** Tier 3. Never auto-answered. |

The commitment class is why a naive "just let the LLM answer everything" approach is wrong:
these questions are cheap to answer and expensive to answer incorrectly.

---

## 5. Integration

Drop-in behind the existing interface, so no call site changes:

```python
# scripts/vault_answers.py
def answer_for_question(question: str, *, bank=None, context=None) -> Answer:
    ans = _rule_table_answer(question, bank)          # Tier 0
    if ans.decision is not Decision.ABSTAIN:
        return ans
    if not AGENT_ENABLED:                              # env flag, default OFF
        return ans
    from vault_answer_agent import resolve
    return resolve(question, bank=bank, context=context)
```

`context` carries company, role and JD text so "why this company" can be answered specifically
rather than generically.

**Rollout must be staged**, because this is the component most able to cause harm:

1. **Shadow mode** — agent runs, logs what it *would* answer, submits nothing. Compare against
   human review for ~200 questions.
2. **Assisted** — agent answers only `factual`; everything else queues.
3. **Supervised** — adds `preference` and `subjective`, still with a review pass afterward.
4. **Autonomous** — steady state. `commitment` still always queues.

Do not skip shadow mode. The whole reason this design is conservative is that the previous
"just answer it" implementation shipped `"10 LPA"` into hundreds of real applications.

---

## 6. Files to create

| Path | Purpose |
|---|---|
| `scripts/vault_answer_agent.py` | Tiers 1–3, validation, cache |
| `scripts/vault_answer_review.py` | `--review` CLI for the human queue |
| `active_application_context/answer_cache.jsonl` | Approved answers + embeddings |
| `active_application_context/pending_questions.jsonl` | Human queue |
| `active_application_context/answer_audit.jsonl` | Every answer submitted, with tier + citations |
| `docs/design/screening_question_agent.md` | This document |

**Model choice:** Claude Sonnet 4.5+ for Tier 2 — the task is constrained extraction and short
generation with a hard refusal path, not open-ended reasoning. Embeddings can be local
(`all-MiniLM-L6-v2`, already used in DocGPT) to keep Tier 1 free and offline.

---

## 7. Verification

Before enabling beyond shadow mode:

- **Red-team set** — 50 adversarial questions covering every constraint: bonds, sponsorship,
  salary floor probes ("what's the lowest you'd accept?"), experience inflation ("do you have
  8 years?"), NDA probes ("name a client you built for"). **Target: 100% abstention or
  correct refusal. Any single failure blocks rollout.**
- **Citation integrity** — every citation in the audit log resolves to a real vault path.
- **Floor containment** — `assert_no_private_floor` over the entire audit log returns clean.
- **Regression** — Tier 0 answers are byte-identical before and after the agent is enabled;
  the agent must never change a deterministic answer.
- **Cache hit rate** — should exceed 60% after ~200 questions, or Tier 1 is not earning its
  complexity.

---

## 8. Explicit non-goals

- **Not** a resume tailorer. Resume selection is `vault_resume.py` and stays deterministic.
- **Not** a cover-letter generator. That is a separate, human-reviewed artifact.
- **Not** a negotiation agent. It never discusses compensation beyond the stated 18–24 LPA band.
- **Not** a substitute for the rule table. Tier 0 must keep growing; every question the agent
  answers twice with the same result is a candidate for promotion to a deterministic rule.
