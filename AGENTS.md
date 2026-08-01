# Job Search Vault — Codex Instructions

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

## Pipeline

**Always run pre-flight first. It is the gate, not a formality.**

```bash
bash scripts/run_chrome_background.sh          # headless Chrome + CDP on :9222
python3 scripts/preflight_check.py             # MUST exit 0 — 13 checks
bash scripts/run_apply_all.sh --dry-run        # verify before any live run
bash scripts/run_apply_all.sh --max-apply 10   # live
```

### Shared modules — use these, do not reimplement

| Module | Responsibility |
|---|---|
| `scripts/vault_config.py` | Every value submitted to a form. Makes emitting the private 15L floor structurally impossible. |
| `scripts/vault_answers.py` | Screening-question policy. Abstains rather than guessing. |
| `scripts/vault_resume.py` | JD → resume routing; rejects any PDF under 800 extractable chars. |
| `scripts/vault_state.py` | Atomic, locked dedup state. Bounded retry (2 attempts). |
| `scripts/vault_browser.py` | CAPTCHA/WAF detection, guarded navigation, tab ownership. |
| `scripts/preflight_check.py` | Regression gate for every defect below. |

### Portal scripts (Pipeline B — the one that runs)

```
scripts/run_apply_all.sh                      # orchestrator, gates on pre-flight
scripts/playwright_linkedin_discover_apply.py # LinkedIn discover + Easy Apply
scripts/playwright_naukri_discover_apply.py   # Naukri discover + apply
scripts/playwright_cutshort_apply.py          # Cutshort
scripts/playwright_instahyre_apply.py         # Instahyre (uses PROFILE resume, not upload)
scripts/playwright_linkedin_easy_apply.py     # LinkedIn form engine (shared infra — do NOT delete)
scripts/playwright_form_helpers.py            # shared field fillers (shared infra — do NOT delete)
scripts/setup_browser_sessions.sh             # one-time login helper
```

> Pipeline A (`job_discovery_feeder.py`, `apply_io_handler.py`,
> `browseros_apply_macro.sh`, `playwright_{naukri,wellfound}_apply.py`, `run_scout.sh`) is
> **retired** — documented but broken. See `docs/audit/01-findings.md` §D1.

## Hard-won rules

These each correspond to a defect that shipped. Do not undo them.

- **Never hardcode a candidate value in a portal script.** Four scripts carried
  `EXPECTED_CTC_LPA = 16`, undercutting the documented floor on every application.
- **Never blanket-answer "Yes".** Both LinkedIn and Naukri defaulted every yes/no question
  to Yes, affirming sponsorship, bonds and inflated experience. Abstaining is always safe.
- **Never upload an unvalidated PDF.** An image-only resume with zero extractable text went
  out 424 times. `vault_resume.safe_upload()` is the only correct upload path.
- **Never take `context.pages[0]`.** It hijacks the user's tabs. Use `vault_browser.named_page()`.
- **Prefer `id^=` / `data-*` / ARIA over CSS classes.** LinkedIn ships hashed class names.
- **A dry run must never write an "Applied" row.** It did once; see `docs/audit/04-live-run-findings.md` §L4.

## Absolute Rules

- Salary: quote 18-24 LPA on all forms; 18L is the stated floor. Current CTC = 11.2 LPA.
- Private walk-away minimum is 15 LPA — NEVER disclose it, never auto-fill it, never put it in a message. Human-led negotiation only.
- Notice period: always 15 days.
- Location: Agra, Uttar Pradesh, India — unless the form asks for preferred work location (Remote).
- GitHub: https://github.com/atinsharma24/
- LinkedIn: https://www.linkedin.com/in/atinsharma24/
- If a form field cannot be answered from the vault files, stop and report it — never guess.
- Always run `--dry-run` on the first attempt at any new portal.
- Always log results to `active_application_context/job_applications_tracker.md`.
- For LinkedIn outreach notes: always remove all hyphens ("-" or "--") and any mentions of salary so the messages do not look AI-written.
- Strictly do not apply to any internships or intern roles, except in FAANG-level companies (Google, Apple, Meta, Amazon, Microsoft, Netflix).

## Browser Sessions (First-Time Setup)

Run `bash scripts/setup_browser_sessions.sh` once. It opens headed browsers for LinkedIn, Wellfound, and Naukri so you can log in manually. Sessions persist automatically after that.

## Resume Selection Logic

| JD contains | Use resume |
|---|---|
| LLM, RAG, conversational, chatbot, vector, embedding, Groq, pgvector | `GenAI_Prompt_Engineer` |
| compliance, KYC, legal, identity, AML, document verification | `Backend_AI_Specialist` |
| cloud, DevOps, Docker, Kubernetes, AWS, infra | `Cloud_Native_FullStack` |
| full-stack, MERN, React, Next.js, product, founding | `AI_Integrated_FullStack` |
| payments, payout, wallet, banking, fintech, Razorpay, billing | `AI_Integrated_FullStack` |

## Stack Match Threshold

Apply if `stack_match >= 0.70`. Skip if below. Log reason in tracker.
