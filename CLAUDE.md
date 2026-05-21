# Job Search Vault — Claude Code Instructions

This vault automates job applications for Atin Sharma (Full-Stack + AI Engineer, Agra, India).

## How to Invoke the Full Pipeline

Paste the contents of `INVOKE.md` as your first message, or run:

```
Read INVOKE.md and execute every step from top to bottom.
Stop on the first hard error and report it.
Never invent candidate data — all field values must trace to
core_vault/01_atomic_fact_sheet.json or core_vault/06_logistics_mapping.json.
```

## Key Files

| File | Purpose |
|---|---|
| `core_vault/01_atomic_fact_sheet.json` | Canonical candidate data — single source of truth |
| `core_vault/06_logistics_mapping.json` | Form-ready answers (salary labels, notice period, relocation, Q&A bank) |
| `core_vault/02_situational_qa_library.md` | Pre-written 100/250-word answers for behavioral/technical form questions |
| `resumes_and_docs/categories/md/` | 4 baseline resumes: AI_Integrated_FullStack, Backend_AI_Specialist, Cloud_Native_FullStack, GenAI_Prompt_Engineer |
| `active_application_context/job_applications_tracker.md` | Audit log — append after every apply |
| `active_application_context/background_agent_state.json` | Dedup state — seen/applied/blocked job IDs |

## Pipeline Scripts

```
scripts/job_discovery_feeder.py     # Discovers jobs on LinkedIn + Wellfound
scripts/apply_io_handler.py         # Keywords-injects resume, renders PDF, appends tracker
scripts/browseros_apply_macro.sh    # Orchestrator: Playwright fast-path → claude fallback
scripts/playwright_linkedin_easy_apply.py   # LinkedIn Easy Apply form filler
scripts/playwright_wellfound_apply.py       # Wellfound form filler
scripts/playwright_naukri_apply.py          # Naukri form filler
scripts/setup_browser_sessions.sh   # One-time login helper
```

## Absolute Rules

- Salary: always 15–18 LPA. Never outside this range. Current CTC = 0.
- Notice period: always 0 days / Immediate Joiner.
- Location: Agra, Uttar Pradesh, India — unless the form asks for preferred work location (Remote).
- GitHub: https://github.com/atinsharma24/
- LinkedIn: https://www.linkedin.com/in/atinsharma24/
- If a form field cannot be answered from the vault files, stop and report it — never guess.
- Always run `--dry-run` on the first attempt at any new portal.
- Always log results to `active_application_context/job_applications_tracker.md`.

## Browser Sessions (First-Time Setup)

Run `bash scripts/setup_browser_sessions.sh` once. It opens headed browsers for LinkedIn, Wellfound, and Naukri so you can log in manually. Sessions persist automatically after that.

## Resume Selection Logic

| JD contains | Use resume |
|---|---|
| LLM, RAG, conversational, chatbot, vector, embedding, Groq, pgvector | `GenAI_Prompt_Engineer` |
| compliance, KYC, legal, identity, AML, document verification | `Backend_AI_Specialist` |
| cloud, DevOps, Docker, Kubernetes, AWS, infra | `Cloud_Native_FullStack` |
| full-stack, MERN, React, Next.js, product, founding | `AI_Integrated_FullStack` |

## Stack Match Threshold

Apply if `stack_match >= 0.70`. Skip if below. Log reason in tracker.
