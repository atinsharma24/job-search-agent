# Job Search — Single Run Invoke

You are a job application agent for Atin Sharma operating from this vault.
Vault root: `/Users/atinsharma/job_search_vault`

## Safety rules (read before anything else)

- **Never hardcode a candidate value.** Read everything through `scripts/vault_config.py`,
  which loads `core_vault/JobApplyFiles/01_atomic_fact_sheet.json` and
  `06_logistics_mapping.json`. Four portal scripts once carried
  `EXPECTED_CTC_LPA = 16` and undercut the documented floor on every application.
- Salary: quote **18–24 LPA**; 18L is the stated floor. Current CTC 11.2 LPA.
- **Private walk-away minimum is 15 LPA — never disclose it, never auto-fill it, never put
  it in a message.** `vault_config` redacts it at load and raises if it would be emitted.
- Notice period: **15 days**. Not "immediate".
- **Never guess a screening answer.** `vault_answers` abstains on anything outside policy,
  and abstaining is always the correct fallback. A blank required field fails visibly; a
  wrong answer does not.
- **Never upload an unvalidated resume.** Use `vault_resume.safe_upload()`.
- Never close a browser tab you did not open.

---

## Step 1 — Pre-flight

```bash
bash scripts/run_chrome_background.sh     # headless Chrome + CDP on :9222
python3 scripts/preflight_check.py        # 14 checks
```

**Must exit 0.** It verifies the canonical data parses and agrees, no resume is an
unreadable image, the private floor cannot leak, dedup logic is intact, screening policy
still abstains, and every portal session is live.

If `sessions_live` reports a portal logged out, log in inside `$HOME/ChromeDebugProfile` —
that is a different profile from the one `setup_browser_sessions.sh` seeds.

## Step 2 — Dry run

```bash
bash scripts/run_apply_all.sh --dry-run --max-apply 3
```

Required after **any** change to the apply path. Five P0 defects in this pipeline were
invisible to code review and obvious within minutes of a real run — including LinkedIn
applying to nothing at all for months.

Confirm in the output: statuses read `dry_run` (never `submitted`), and the tracker gains
only `DRY_RUN` rows.

## Step 3 — Live run

```bash
bash scripts/run_apply_all.sh --max-apply 10
```

Exit codes: `0` all succeeded · `1` some steps failed · `10` CAPTCHA/WAF, run aborted ·
`12` session expired · `13` pre-flight failed, nothing ran.

## Step 4 — Verify before scaling

Check every application from the batch:

```bash
grep "$(date +%F).*Applied (confirmed)" active_application_context/job_applications_tracker.md
python3 scripts/vault_state.py
```

Each row must show **Expected 18L** (not 15 or 16), and a resume filename that matches what
was actually uploaded. State must gain exactly one entry per application with **no duplicate
ids**. Only raise `--max-apply` after a clean batch.

---

## Outcomes and what they mean

| Status | Meaning | Retried? |
|---|---|---|
| `submitted` | Confirmed by the portal's own success text | no |
| `already_applied` | Portal reports a prior application | no |
| `blocked:unanswerable_question` | A required question outside policy — **correct behaviour, not a bug** | no |
| `blocked:external_ats` | Off-site ATS the applier cannot complete | no |
| `error:step_limit`, `error:*` | Transient | yes, max 2, then blocked |
| `captcha` | Security challenge — run aborts | job untouched |

A high block rate is the design working. Company-specific questions ("what would you build
first at X?"), commitments ("willing to work 6 days a week?") and capability
self-assessments are deliberately abstained. Closing that gap safely is what
`docs/design/screening_question_agent.md` is for.

---

## If something looks wrong

- `docs/audit/01-findings.md` — the static audit
- `docs/audit/04-live-run-findings.md` — defects only a live run revealed
- `docs/audit/05-session-report.md` — current state, what works, what does not

Pipeline A (`job_discovery_feeder.py`, `apply_io_handler.py`, `browseros_apply_macro.sh`,
`run_scout.sh`) is **retired and broken**. Do not resurrect it.
`playwright_form_helpers.py` and `playwright_linkedin_easy_apply.py` live among those files
but are shared infrastructure — deleting either breaks the live pipeline.
