# Job Search Vault

Automated job applications for Atin Sharma across LinkedIn, Naukri, Cutshort and Instahyre,
plus the canonical candidate data every application is built from.

---

## Quick start

```bash
bash scripts/run_chrome_background.sh        # headless Chrome + CDP on :9222
python3 scripts/preflight_check.py           # 13 checks — MUST exit 0
bash scripts/run_apply_all.sh --dry-run      # verify before going live
bash scripts/run_apply_all.sh --max-apply 10 # live
```

**Pre-flight is a gate, not a formality.** It asserts the canonical data parses and agrees,
no resume is an unreadable image, the private salary floor cannot leak, dedup logic is
intact, and every portal session is live. `run_apply_all.sh` refuses to proceed without it.

First-time browser setup: log in to each portal once inside `$HOME/ChromeDebugProfile`, or
run `bash scripts/setup_browser_sessions.sh`.

---

## Where things live

| Path | What |
|---|---|
| `core_vault/JobApplyFiles/01_atomic_fact_sheet.json` | Canonical candidate data — single source of truth |
| `core_vault/JobApplyFiles/06_logistics_mapping.json` | Compensation, availability, `qa_bank` answers |
| `scripts/vault_*.py` | Shared modules — config, answers, resume, state, browser |
| `scripts/playwright_*_apply.py` | Per-portal apply scripts |
| `resumes_and_docs/categories/` | 4 category resumes + the master, in `tex`/`pdf`/`md`/`docx` |
| `active_application_context/` | Tracker, dedup state, per-portal queues |
| `docs/audit/` | Full engineering audit and remediation roadmap |
| `docs/design/` | Designs for work not yet built |

Resumes build from LaTeX via `tectonic`; `scripts/tex_resume_to_docx.py` derives the `.docx`
from the same source, so the two cannot drift.

---

## Architecture

Discovery and submission are separate problems and deserve different tools.

**Submission** drives real Chrome over CDP (`--headless=new`, so it never steals macOS
focus). Every value submitted comes from `vault_config`, which reads the canonical JSONs and
makes emitting the private negotiation floor structurally impossible. Screening questions go
through `vault_answers`, which **abstains rather than guessing** — a job with an unanswerable
required question is reported for human review, not answered wrongly.

**Discovery** currently scrapes portal search pages. It should not:
`company_board_registry/` already holds 204 verified Greenhouse/Lever/Ashby JSON endpoints
and `scripts/board_scan_feeder.py` already consumes them. Public ATS APIs have no bot
detection, no CAPTCHA and no session expiry. Wiring that up is the highest-value open item —
see [`docs/audit/02-browser-automation.md`](docs/audit/02-browser-automation.md).

---

## Read this before changing the apply path

This pipeline previously submitted hundreds of applications with the wrong salary, zero years
of experience, and a resume containing no extractable text. Those defects and their fixes are
documented in [`docs/audit/`](docs/audit/). The short version:

- Never hardcode a candidate value in a portal script — read `vault_config`.
- Never blanket-answer "Yes". Abstaining is always safe; guessing never is.
- Never upload a PDF without `vault_resume.safe_upload()`.
- Never take `context.pages[0]` — it hijacks the user's own tabs.
- Prefer `id^=` / `data-*` / ARIA selectors; portals ship hashed CSS class names.
- Always dry-run after touching the apply path. Five P0 defects were invisible to code
  review and obvious within minutes of a real run.

Each has a `preflight_check.py` regression guard. If one fails, it is telling you something
real.

---

## Requirements

- Python 3 with `playwright` (`pip install playwright && playwright install chromium`)
- Google Chrome
- `tectonic` for LaTeX → PDF; `pandoc` for `.docx`
- `pypdf` or `pdftotext` for resume text validation
