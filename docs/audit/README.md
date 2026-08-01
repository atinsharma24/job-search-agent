# Vault Audit — 1 August 2026

A full read-only audit of every subsystem in `job_search_vault`: the automation layer, the
data layer, the content assets, and repository hygiene.

| Document | Contents |
|---|---|
| [`01-findings.md`](01-findings.md) | Every finding, with `file:line` evidence and severity |
| [`02-browser-automation.md`](02-browser-automation.md) | CDP vs Claude-in-Chrome vs alternatives — the recommendation |
| [`03-remediation-roadmap.md`](03-remediation-roadmap.md) | Phased fix plan, P0 → P3 |
| [`04-live-run-findings.md`](04-live-run-findings.md) | Defects found by actually running the pipeline — including that LinkedIn was applying to nothing |
| [`../design/screening_question_agent.md`](../design/screening_question_agent.md) | Design for the autonomous screening-question agent |

**Method.** Findings were produced by two parallel exploration passes and then
independently re-verified by direct measurement — reading the cited lines, running
`pdftotext`, parsing the tracker, querying `gh`, and checking git history. Claims that could
not be reproduced were dropped. Every number below is measured, not estimated.

---

## The one-sentence version

The automation works mechanically but **submits wrong data and records outcomes that never
happened**; fixing browser technology would not move a single one of the numbers below.

---

## Measured reality

| Metric | Value | Source |
|---|---|---|
| Confirmed applications | **65** | tracker status histogram |
| Failures | **554** | 207 `no_apply_button` · 177 `step_limit` · 89 `no URL found` · 81 `error:1` |
| Applications naming an **unreadable** resume | **424** | `NewResDocPdf.pdf` = **0** extractable chars |
| Duplicate tracker rows | **503 of 855** URLs | worst single URL logged **54×** |
| Expected CTC actually submitted | **16 LPA** (Naukri chatbot: **10 LPA**) | vs. documented floor of 18 |
| Years of experience submitted | **0 — "Fresher"** | vs. actual ~14 months |
| Tracked files that are junk | **2,139 of 2,327 (91%)** | Chrome profiles + `node_modules` |

A ~10% success rate is not a tuning problem. Roughly half the submitted applications were
unreadable by any ATS that parses PDFs, and effectively all of them understated experience
and compensation.

---

## Severity summary

### P0 — actively damaging every run

| # | Finding | Evidence |
|---|---|---|
| 1 | Session cookies for LinkedIn/Naukri/Wellfound committed to a **public** repo | `origin/main`, 1,356 files, [`01`](01-findings.md#s1) |
| 2 | Naukri types **`"10 LPA"`** into any salary question — below current CTC | `playwright_naukri_discover_apply.py:616` |
| 3 | Naukri types a **skills list into any unrecognised question** | `playwright_naukri_discover_apply.py:624` |
| 4 | Naukri clicks **"Yes" without reading the question** | `playwright_naukri_discover_apply.py:719-728` |
| 5 | Resume with **0 extractable characters** uploaded 424× | `NewResDocPdf.pdf` |
| 6 | `EXPECTED_CTC_LPA = 16` hardcoded, bypassing canonical JSONs | 4 scripts |
| 7 | `years_experience = 0  # Fresher` | `playwright_form_helpers.py:36` |
| 8 | Staged upload PDF leaks the **private 15L floor** | `staged_application_resume.pdf` |
| 9 | Dedup broken both ways → 503 duplicate rows | `naukri:1035` / `linkedin:371` |

### P1 — structural

State store has no locking or atomic write and fails open · tracker has 3 interleaved schemas
and is unparseable · no CAPTCHA detection in the live pipeline · no retries or backoff
anywhere · `run_apply_all.sh` always exits 0 · queue `.md` files are decorative.

### P2 — correctness of record

Canonical paths wrong in all 5 instruction files · 2 broken symlinks for files declared
canonical · `linkedin` field missing from the fact sheet · 23 hand-maintained copies of the
candidate profile · `README.md` and `docs/ARCHITECTURE.md` describe a vault that no longer
exists.

---

## What is genuinely good

Worth stating, because the audit is otherwise unrelenting:

- **`company_board_registry/`** — 204 *verified* Greenhouse/Lever/Ashby JSON endpoints, built
  with real methodology (live-200 + non-empty-array checks, no guessed slugs). The
  highest-quality asset in the vault. Zero consumers.
- **`scripts/board_scan_feeder.py`** — the best-engineered script here: per-host crawl delays,
  a real `--dry-run`, first-run seeding, its own state file. Completely unwired.
- **`scripts/playwright_login_setup.py`** — the only browser code that does fingerprint
  hygiene (`--disable-blink-features=AutomationControlled`, `navigator.webdriver` shim).
- **The `--headless=new` + CDP design** (commit `1b7c23c`) — correctly solves background
  execution without stealing macOS focus. Keep it; see [`02`](02-browser-automation.md).

The pattern: the best work in this repo is disconnected from the path that actually runs.
