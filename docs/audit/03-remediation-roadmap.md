# Remediation Roadmap

Guiding principle: **a submitted application is irreversible; a skipped one is not.**
Correctness lands before throughput, and everything stays dry-run-gated until the pre-flight
check passes.

Strategy: **correctness first, then volume.** Throughput stays capped low until a run produces
zero defects.

---

## Phase 0 — Repo hygiene ✅ *done, commit `4126589`*

- `.gitignore` added; 2,139 files untracked (91% of the repo), local files retained.
- Chrome profiles with live session cookies removed from the index.

**Still outstanding — deferred by user decision:**

> Log out of all sessions on LinkedIn, Naukri and Wellfound, then re-run
> `bash scripts/setup_browser_sessions.sh`.
>
> This is the *only* action that revokes the cookies already published in `origin/main`.
> `.gitignore` stops future exposure; it cannot recall what is already public. Repo visibility
> does not affect this either way.

---

## Phase 1 — Foundations *(no behaviour change)*

Six new modules under `scripts/`. Nothing imports them yet, so the running system is
untouched and each is independently testable.

### `vault_config.py` — one source for every form answer

Loads `core_vault/JobApplyFiles/{01_atomic_fact_sheet,06_logistics_mapping}.json` and exposes
typed accessors. Replaces every hardcoded constant.

**Makes leaking the private 15 LPA floor structurally impossible**, via three independent
layers — any one of which suffices:

1. **Redact at load.** A recursive scrub deletes keys matching
   `negotiation_floor|_private|walk_?away` *before* the dict is memoised. The value is never
   in memory for a consumer to reach.
2. **No accessor exists.** There is deliberately no function that returns a floor. A future
   contributor cannot "just use the floor getter" because there isn't one.
3. **A compensation-scoped tripwire.** `assert_no_private_floor(text)` raises if a string
   states 15 *as money*.

> The tripwire must be salary-scoped, **not** a bare "contains 15" check — the notice period
> is legitimately 15 days. Gate on a salary token (`lpa|lakh|ctc|salary|package|₹|per annum`)
> co-occurring with a 15-token. `"15 days"` passes; `"15 LPA"`, `"₹15L"`, `"CTC 15"` raise.

`verify_bank()` runs the tripwire over every answer at startup, so a poisoned bank raises
**before a browser opens**.

**YOE must union calendar months, not sum durations.** Naive summing gives 25 by
double-counting the VIT research role; the correct algorithm excludes `employment_type`
matching `academic|part-time|intern` and unions month ranges. Correct value: **14**
(AGI Ready 2 + OpenBiz 12).

### `vault_state.py` — atomic, locked, set-backed

Replaces the list-backed store: `tmp` + `os.replace`, `fcntl.flock`, `.bak` rotation, and a
load that **raises rather than returning empty state** — failing open would re-apply to all
158 completed jobs.

The dedup fix is a **bounded attempt counter**, resolving both mirror bugs at once:

| Outcome | applied | seen | blocked | attempts++ | retried next run? |
|---|:--:|:--:|:--:|:--:|---|
| `APPLIED` / `ALREADY_APPLIED` | ✅ | ✅ | | | no |
| `SKIPPED_FILTER` | | ✅ | | | no |
| `BLOCKED_PERMANENT` | | ✅ | ✅ | | no |
| `FAILED_RETRYABLE` | | ❌ | | ✅ | yes — max 2, then auto-blocked |
| `CAPTCHA` | | ❌ | | ❌ | yes — run aborts, job untouched |

Naukri's 54 retries stop at 2. LinkedIn's transient CAPTCHA no longer blacklists a job
permanently. CAPTCHA is explicitly *not* counted, because it says nothing about the job.

Ships with `--migrate` to convert v1→v2 and seed `applied` from the tracker's 291 unique URLs.

### `vault_resume.py` — routing + the 0-char guard

JD → category per `CLAUDE.md`'s routing table, weighting the job title 3× (description
scraping is unreliable). Honours the per-job `"resume"` key that is currently logged but
ignored.

`validate_resume()` rejects any PDF under **800 extractable characters** — bad files measure
0, good ones 4,346–4,645 — and requires marker strings to catch garbled extraction.
Validation lives *inside* `safe_upload()`, so no code path can upload without it. This kills
the 424-uploads-of-an-image-PDF class permanently.

### `vault_answers.py` — question-aware screening

Replaces blind affirmation at `naukri:719-728` and the unconditional `"Yes"` at
`linkedin_easy_apply:110-116`. First-match rule table:

| Rule | Matches | Result |
|---|---|---|
| **0** | **empty / unrecognised question** | **`ABSTAIN`** ← the single most important rule |
| 1 | sponsorship · visa · felony · bond · pay-a-fee · 60/90-day notice | `NO` |
| 2 | legally authorised · eligible in India · willing to relocate · agree to terms | `YES` |
| 3 | ctc · salary · notice · joining · location · email · phone | `VALUE` from `vault_config` |
| 4 | *"years of experience **with X**"* | real YOE if X is in the stack, else `"0"` |
| 5 | total experience | `years_experience()` |
| 6 | matches a `qa_bank` key | long-form answer |
| 7 | *fallthrough* | `ABSTAIN` |

Rule 4 fixes a live defect in *both* files: `linkedin_easy_apply.py:74` maps anything
containing `experience` to total YOE, and `naukri:617` answers `"1"` to any question
mentioning `mysql`/`react`/`node`.

Adds the missing **`NO` branch** — its absence is why hard-negative questions stall until the
step budget dies, a large share of the 177 `step_limit` failures.

Rewrites the Naukri chatbot table at `609-624`, deleting `"10 LPA"`, `"Immediate"`,
`"OpenBiz Software"`, and the catch-all `else`. **Abstaining records `BLOCKED_PERMANENT` with
the question text** — converting silent wrong answers into visible human-review items. That is
the correctness-first trade: fewer submissions, none of them wrong.

### `vault_browser.py` — challenge detection and backoff

CAPTCHA/WAF detection (Pipeline B has none), `guarded_goto` with retry/backoff, `polite_sleep`
with jitter. Reuses the existing detector at `playwright_linkedin_easy_apply.py:50-56` and the
documented exit codes (0/1/10/11/12) so `INVOKE.md`'s contract still holds.

On detection: screenshot, then **abort the whole run** — a challenge on one portal means the
IP or profile is flagged, and continuing makes it worse.

### `preflight_check.py` — the gate

Asserts, before any live run: both JSONs parse and agree · no private-floor key survives
redaction · `assert_no_private_floor` passes over all 5 resume PDFs, staged artifacts, queue
notes and `qa_bank` · every resume has extractable text · no script references
`NewResDocPdf`/`2026New1` · state loads · CDP reachable · each portal session live.

Wired as a gate in `run_apply_all.sh`.

---

## Phase 2 — Artifact hygiene *(no code)*

Delete `active_application_context/staged_application_resume.pdf` — 30 June, leaks
`15L+ (negotiable)`, says "Immediate Joiner", omits AGI Ready, renders raw Markdown. Nothing
in Pipeline B reads it; its only consumers are retiring. Pre-flight check 4 then passes.

---

## Phase 3 — Wiring *(dry-run gated)*

In order: config → resume → answers → browser → exit codes. Run
`bash scripts/run_apply_all.sh --dry-run` after each sub-step.

Diffs stay minimal by **keeping the module-level constant names and rebinding them to
accessors**, so every downstream f-string keeps working:

```python
EXPECTED_CTC_LPA = vc.expected_ctc_numeric()    # was: 16
CURRENT_CTC_LPA  = vc.current_ctc_lpa()         # was: 11.2
```

| File | Change |
|---|---|
| `playwright_{instahyre,cutshort,linkedin_discover}_apply.py` ~L27-37, `naukri:36-37` | rebind constants |
| `playwright_linkedin_discover_apply.py:190-202` | delete the 7-line salary clobber |
| `playwright_form_helpers.py:27-81` | delegate to `vault_config` — fixes YOE=0 **and** drops the `fact_sheet`/`logistics` leak keys for all three consumers at once |
| `naukri:378-393` | `fill_notice_period` uses an unordered `any()`, so a dropdown listing "Immediate" first wins over "15 Days". Iterate preferences outer, options inner. |
| `cutshort:178`, `naukri:938/1019`, `linkedin:357` | honour the per-job `"resume"` key |
| `run_apply_all.sh` | capture `${PIPESTATUS[0]}` (tee masks the real code); abort on 10/12/13; exit non-zero if any step failed; fix the unassigned `${AUTO_CHROME_MSG:-}` at L41 |

Dry-run is genuinely safe — all four scripts short-circuit before submit (`cutshort:252`,
`instahyre:117`, `naukri:747`, `linkedin` via `EXIT_SUCCESS` at `289-291`).

---

## Phase 4 — State migration

Land `vault_state` wiring, then `python3 scripts/vault_state.py --migrate --yes`. Doing this
*after* dry-run validation means a bad migration can be reverted without having lost a real
application.

---

## Phase 5 — Retire Pipeline A

Only now, once Phases 3–4 have confirmed what is actually live.

**Safe to delete:** `job_discovery_feeder.py` · `apply_io_handler.py` ·
`browseros_apply_macro.sh` · `playwright_naukri_apply.py` *(disposes of its `NameError` — no
fix needed)* · `playwright_wellfound_apply.py` · `run_scout.sh` · the 9 dead
`linkedin_outreach*/batch*` scripts.

> ### ⚠ Must NOT be deleted
> `playwright_form_helpers.py` and `playwright_linkedin_easy_apply.py` are **Pipeline B
> infrastructure** despite living among Pipeline A files. Verified imports at `cutshort:19`,
> `linkedin_discover:192,209`, `naukri_discover:290`. LinkedIn's entire apply engine is
> `playwright_linkedin_easy_apply.py`. Deleting either breaks Pipeline B outright.

Then update the docs referencing deleted scripts: `CLAUDE.md`, `AGENTS.md`, `INVOKE.md`,
`INVOKE_STAGE.md`, `INVOKE_APPLY.md`, `docs/ARCHITECTURE.md`, `docs/USER_GUIDE.md`.

---

## Phase 6 — Throttled live run

Pre-flight gate on, `--max-apply 3`. **Manually verify each application against the portal's
own "applied" page** before raising the cap. Two clean runs before returning to 15.

---

## Phase 7+ — Deferred

| Item | Note |
|---|---|
| **Session rotation** | The only fix for already-public cookies. Deferred by user decision. |
| Tracker → JSONL/SQLite | 327 KB, 3 interleaved schemas, 61% duplicates; the existing parser recognises ~19 of ~1,300 rows |
| Recover `02_situational_qa_library.md` / `04_behavioral_star_stories.md` | Only copies are in `.claude/worktrees/festive-davinci-67abbc/` — lost if pruned |
| Fix canonical paths in all 5 instruction files | `core_vault/01_…` → `core_vault/JobApplyFiles/01_…` |
| Add `linkedin` to the fact sheet | Agents must otherwise halt on any form asking for it |
| Make `*_queue.md` authoritative | Currently decorative; jobs are hardcoded Python lists |
| **Wire `board_scan_feeder.py` + `company_board_registry/`** | API-based discovery — see [`02`](02-browser-automation.md#4-the-higher-leverage-change-dont-use-a-browser-for-discovery) |
| Reconcile `scratch/registry_probe/` vs `company_board_registry/` | scratch's `verified.json` is *larger* — may be newer |
| Rewrite `README.md`, `docs/ARCHITECTURE.md`, `docs/RESUME_WORKFLOW.md` | 7 dead path references between them |
| Move `atin-sharma-offer-letter.pdf` out of the repo | 3.27 MB, NDA-governed, sitting in the root |

---

## Verification

```bash
python3 scripts/preflight_check.py            # primary gate — must exit 0
bash    scripts/run_apply_all.sh --dry-run    # must exit 0; tracker rows read DRY_RUN
bash    scripts/run_apply_all.sh --dry-run    # run twice: 2nd must record 0 new applications
```

Targeted assertions:

| Assertion | Expected |
|---|---|
| `assert_no_private_floor("15 LPA")` | raises |
| `assert_no_private_floor("15 days")` | passes |
| `experience_months()` | `14` |
| `validate_resume("NewResDocPdf.pdf")` | raises `ResumeUnusable` |
| `select_category("RAG pipeline, pgvector, Groq")` | `GenAI_Prompt_Engineer` |

**Definition of done for P0:** a dry run across all four portals produces zero pre-flight
failures, zero duplicate state writes, and a tracker in which every row's recorded resume
matches the file actually uploaded.
