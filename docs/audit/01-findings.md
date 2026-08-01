# Findings

Every claim carries a `file:line` reference and was verified by direct measurement.
Severity: **P0** actively damaging · **P1** structural · **P2** correctness of record.

---

## A. Security

### <a name="s1"></a>A1 · Live session cookies in a public repository — **P0**

```
$ gh repo view atinsharma24/job-search-agent --json visibility
{"isPrivate":false,"visibility":"PUBLIC"}

$ git ls-files | grep -c "playwright/.*-profile/"
1356

$ git ls-files | grep -i "Cookies"
active_application_context/playwright/linkedin-profile/Default/Cookies
active_application_context/playwright/linkedin-profile/Default/Cookies-journal
...
$ git branch -r --contains 42ddca0
origin/main
```

Chrome profile directories for LinkedIn, Naukri and Wellfound are committed — including
`Cookies`, `Local Storage/leveldb/`, `IndexedDB/`, and `Account Web Data`. They are reachable
in `origin/main` of a public repo.

**Two independent remediations, both required:**

| Action | Fixes |
|---|---|
| `.gitignore` + `git rm -r --cached` *(done — commit `4126589`)* | Future exposure |
| **Log out of all sessions on all three portals**, then re-run `setup_browser_sessions.sh` | Past exposure |

Repository visibility does not affect the second. Cookies already published remain valid
until the sessions behind them are revoked, and clones/forks/caches persist independently of
the repo's current state. **Deferred by user decision.**

### A2 · `dev.env` holds a plaintext API key — P1

`dev.env` contains `GEMINI_API_KEY="AIza…"`. It was untracked but *un-ignored*, one
`git add -A` from being published. Now covered by `.gitignore`.

---

## B. What actually gets submitted

This section is the core of the audit. Everything here is live in the running pipeline.

### B1 · Naukri answers salary questions with `"10 LPA"` — **P0**

`scripts/playwright_naukri_discover_apply.py:609-624`:

```python
if "skill" in question or "tech" in question or ...:
    val = "TypeScript, Node.js, React, Next.js, Python, RAG, LangChain, PostgreSQL"
elif "notice" in question or "join" in question:
    val = "Immediate"
elif "ctc" in question or "salary" in question or "lpa" in question:
    val = "10 LPA"                    # ← below current CTC of 11.2, 8L below the floor
elif "experience" in question or "mysql" in question or "react" in question:
    val = "1"
elif "company" in question or "employer" in question:
    val = "OpenBiz Software"          # ← stale; current employer is AGI Ready Inc.
else:
    val = "TypeScript, Node.js, React, ..."   # ← ANY unrecognised question
```

Four distinct defects in fifteen lines:

1. **`"10 LPA"`** — the single most damaging line in the vault. Lower than the candidate's own
   current CTC, and 8 LPA below the documented floor.
2. **The `else` branch** types a skills list into *any* question the table doesn't recognise —
   "Why do you want this role?", "Notice period in days?", anything.
3. **`"Immediate"`** contradicts the canonical 15-day notice.
4. **`"OpenBiz Software"`** names a former employer as current.

### B2 · Screening questions answered "Yes" without being read — **P0**

`scripts/playwright_naukri_discover_apply.py:719-728`:

```python
if txt_lower in ("yes", "y", "i agree", "agree", "confirm"):
    log(f"  Clicking yes/confirmation option: {txt}")
    el.click()
    last_clicked_question = question      # ← captured, but never inspected
```

The `question` variable is in scope and is stored *after* the click. Only the option's own
text drives the decision. "Do you have 5+ years of experience?", "Are you willing to sign a
2-year bond?", "Do you require visa sponsorship?" all receive an unconditional **Yes**.

The mirror defect on LinkedIn is `playwright_linkedin_easy_apply.py:110-116`, where any
yes/no field defaults to `"Yes"`.

There is also no `No` branch anywhere. A question requiring a negative answer simply stalls
until the step budget is exhausted — a large share of the **177 `step_limit` failures**.

### B3 · An unreadable resume was uploaded 424 times — **P0**

```
$ pdftotext NewResDocPdf.pdf - | tr -d '[:space:]' | wc -c
0
$ grep -c "NewResDocPdf.pdf" job_applications_tracker.md
424
```

| PDF | Extractable chars |
|---|---|
| `NewResDocPdf.pdf`, `NewResDocPdf2.pdf`, `LatestCV.pdf` | **0** |
| `2026New1.pdf` *(what the scripts actually upload)* | 3,501 — but garbled, no word spacing |
| `Atin_Sharma_Resume_2026.pdf` and the 4 category PDFs | 4,346 – 4,645 |

Two separate problems. The tracker *names* a 0-char file 424 times; the scripts *upload*
`2026New1.pdf`, whose text extracts as `EngineeredaparallelGraphRAGpipeline…`. An ATS
tokenising that gets one enormous nonsense token.

**The record and reality also diverge.** `playwright_cutshort_apply.py:325` logs
`f"Resume: {job['resume']}"` — a per-job category like `AI_Integrated_FullStack` — while
`:178` uploads the fixed `RESUME_PATH`. The `"resume"` key has been logged-but-ignored since
the file was written. `naukri:1022` hardcodes the note `"NewResDocPdf.pdf"` regardless.

### B4 · Compensation hardcoded, bypassing the canonical JSONs — **P0**

```
scripts/playwright_instahyre_apply.py:28        EXPECTED_CTC_LPA = 16
scripts/playwright_cutshort_apply.py:37         EXPECTED_CTC_LPA = 16
scripts/playwright_linkedin_discover_apply.py:31 EXPECTED_CTC_LPA = 16
```

`playwright_linkedin_discover_apply.py:194-201` goes further — it builds the answer bank from
the fact sheet, then overwrites all seven salary keys:

```python
bank["current_ctc"]        = str(CURRENT_CTC_LPA)
bank["expected_ctc_min"]   = str(EXPECTED_CTC_LPA)
bank["expected_ctc_max"]   = str(EXPECTED_CTC_LPA)
bank["expected_ctc_label"] = f"{EXPECTED_CTC_LPA} LPA"
```

`CLAUDE.md` states *"Never invent candidate data — all field values must trace to
`01_atomic_fact_sheet.json`."* The scripts do precisely the opposite.

### B5 · Every application declares 0 years of experience — **P0**

`scripts/playwright_form_helpers.py:33-36`:

```python
months = 0
for experience in fact_sheet.get("experience", []):
    months = max(months, int(experience.get("duration_months", 0) or 0))
years_experience = 0  # Fresher — always submit as 0 YOE
```

`months` is computed and then discarded. Every portal form receives `"0"` while the attached
resume claims founding-engineer experience — an internal contradiction visible to any
recruiter who reads both.

**This file is Pipeline B infrastructure, not a retiring artifact.** Verified imports:

```
playwright_cutshort_apply.py:19          from playwright_form_helpers import maybe_upload_file
playwright_linkedin_discover_apply.py:192 from playwright_form_helpers import build_base_answer_bank
playwright_linkedin_discover_apply.py:209 from playwright_linkedin_easy_apply import execute_easy_apply
playwright_naukri_discover_apply.py:290   from playwright_form_helpers import build_base_answer_bank
```

LinkedIn's entire apply engine is `playwright_linkedin_easy_apply.py`. Neither file may be
deleted when Pipeline A is retired.

### B6 · The staged upload artifact leaks the private floor — **P0**

```
$ pdftotext active_application_context/staged_application_resume.pdf -
**Profile Snapshot:** Immediate Joiner ´• Remote-first ´• 15L+ (negotiable) ´• Indian Citizen
```

The file uploaded by the documented pipeline publishes the **private 15 LPA walk-away floor**
and the wrong notice period. It also renders raw Markdown (`**Profile:**`, `- VyaparGPT:`),
truncates lines mid-word, and mangles Unicode (`´•`).

Its `.md` sibling is correct as of 1 Aug (`15-day notice · 18L+`). The `.pdf` was last built
**30 June** and never regenerated. Both also carry an injected keyword `ServiceNow` — a
technology absent from the fact sheet, left over from an earlier run.

### B7 · Structural leak path for the private floor — P1

`playwright_form_helpers.py:42-43` embeds the *entire* un-redacted fact sheet and logistics
dict into the answer bank under keys `fact_sheet` and `logistics`. Both contain
`negotiation_floor_private: 15`. Nothing reads those keys — but any future code that iterates
the bank would surface the floor.

---

## C. State and record-keeping

### C1 · Dedup is broken in both directions — **P0**

`background_agent_state.json` stores plain **lists**, not sets.

**Naukri never marks failures seen** (`playwright_naukri_discover_apply.py:1035-1037`):
```python
else:
    append_tracker(company, title, url, f"FAILED ({status})", note_str)
save_state(state)            # ← no seen_job_ids.append
```
So every failure is retried on every one of the 62 search URLs in a run, and on every future
run. Measured consequence:

```
total URL rows: 855 | distinct: 352 | duplicates: 503
54× naukri.com/job-listings-fullstack-developer-nxtwave-...
25× naukri.com/job-listings-junior-react-developer-nxtwave-...
24× naukri.com/job-listings-react-node-js-developer-mern-...
```

**LinkedIn has the mirror bug** (`:371`) — it appends to `seen_job_ids` on *every* outcome, so
a single transient CAPTCHA permanently blacklists a job that was never actually attempted.

Neither "always mark seen" nor "never mark seen on failure" is correct. A **bounded attempt
counter** fixes both with one mechanism.

### C2 · State store has no locking and fails open — P1

```python
def save_state(state: dict):
    STATE_PATH.write_text(json.dumps(state, indent=2))
```

Called after *every* job (`naukri:992, 998, 1004, 1012, 1037`). 67 KB, truncate-then-write, no
temp file, no lock, no backup. Ctrl-C mid-write truncates it. `load_state` is a bare
`json.loads` with no `try/except` → the next run dies with `JSONDecodeError` and the entire
dedup history is unrecoverable without git.

The third reader is worse: `job_discovery_feeder.py:86-90` catches `JSONDecodeError` and
returns `set()` — **failing open**, re-surfacing every already-applied job.

`applied_job_ids` already contains a duplicate: 158 entries, 157 unique.

### C3 · The tracker is unparseable — P1

327 KB, 1,374 lines, **three interleaved schemas** from four writers:

| Writer | Format |
|---|---|
| `apply_io_handler.py:208` | 5-column markdown table |
| `playwright_cutshort_apply.py:100` | 8-column markdown table |
| `playwright_naukri_discover_apply.py:261` | `- [date] **Company:** …` bullet |
| `playwright_linkedin_discover_apply.py:181` | bullet variant |

Measured shapes: 1,020 bullets · 118 nine-pipe · 54 six-pipe · 19 five-pipe · 156 other.

**The only parser is broken by this.** `job_discovery_feeder.py:98-111` skips any line not
starting with `|` — discarding 94% of the file — then reads `columns[4]` as status, which for
8-column rows is the URL. Net: **it recognises ~19 of ~1,300 applications.** Tracker-based
dedup does not function.

Compounding: the bullet writers do no `|`-sanitisation while using a `|`-delimited format, and
`cutshort:340` injects raw Python exception reprs — newlines and pipes included — into cells.

### C4 · The tracker records intent, not outcome — P1

`apply_io_handler.py:358` calls `append_tracker_row()` immediately after staging the PDF,
hardcoding `"Applied |"` at `:213`. The actual apply runs *afterwards* and may CAPTCHA out,
hit a login wall, or crash. There is no post-hoc status update path anywhere in the repo.

---

## D. Pipeline architecture

Three pipelines exist. One runs.

### D1 · Pipeline A is documented but broken at four points — P1

`INVOKE.md` / `CLAUDE.md` / `README.md` all describe
`job_discovery_feeder.py → apply_io_handler.py → browseros_apply_macro.sh`.

- **`playwright_naukri_apply.py:380` is a guaranteed `NameError`.** `profile_dir` and
  `headless` are referenced in `main()` and defined nowhere in the file (verified by AST walk
  of the enclosing function). Sibling files define them at `wellfound:282-289`; this file's
  copy was dropped.
- **The LLM fallback is designed to always stop.** `browseros_apply_macro.sh:64-70` instructs
  Claude to read `core_vault/01_atomic_fact_sheet.json`,
  `core_vault/06_logistics_mapping.json` and `core_vault/02_situational_qa_library.md` — all
  three missing — then says *"If any field cannot be answered from the vault files, STOP."*
- **Exit codes are discarded.** `INVOKE.md:97-101` documents `10 = CAPTCHA`, `12 = login wall`.
  The macro only tests `-eq 0`, so a CAPTCHA escalates to the LLM fallback, which retries the
  same blocked page.
- **`run_scout.sh` cannot run** — `gemini-cli`, `scripts/notify_user.sh`, and `prompts/` are
  all absent.

### D2 · Pipeline B runs but is undocumented — P1

`run_apply_all.sh` → 4 `*_discover_apply.py` scripts over CDP. **Zero documentation
references.** The documented-vs-actual relationship is exactly inverted.

Gaps versus Pipeline A: **no CAPTCHA/WAF detection at all** (`grep -i "captcha\|challenge\|429"`
returns nothing across the four scripts), no exit-code contract, no structured logging.

### D3 · No retries or backoff anywhere — P1

`grep -rn "retry\|backoff" scripts/*.py` returns one unrelated print. Rate limiting is a flat
`time.sleep(2)` with no jitter at 6 sites. The only file with per-host crawl delays is
`board_scan_feeder.py` — the orphan.

### D4 · `run_apply_all.sh` always exits 0 — P1

All four `main()` functions fall off the end returning `None`. Combined with `| tee` masking
`$?`, the orchestrator prints `ALL PORTALS COMPLETE` even if every application failed.
`${AUTO_CHROME_MSG:-}` at `:41` is never assigned.

### D5 · Queue files are decorative — P1

`playwright_cutshort_apply.py:28` defines `QUEUE_PATH` pointing at `cutshort_queue.md` — and
never reads it. Jobs are a hardcoded Python list at `:42-83` (5 jobs, from June). The queue
file was edited 1 Aug and holds 7. Same for `instahyre_queue.md` and `naukri_queue.md`.
**Editing a queue file has no effect on what gets applied to.**

### D6 · Nine dead outreach scripts — P2

`scripts/linkedin_outreach{,_batch4,_batch5,_batch6}.py` plus five batch helpers, ~150 KB,
zero inbound references. `diff batch5 batch6` is **3 lines** — two path constants and a log
string. Superseded by `linkedin_outreach/scripts/`.

---

## E. Data layer

### E1 · Canonical paths are wrong in all five instruction files — P2

```
CLAUDE.md:14 · AGENTS.md:14 · INVOKE.md:8,38 · INVOKE_STAGE.md:8,38
  → core_vault/01_atomic_fact_sheet.json        *** MISSING ***
  → core_vault/06_logistics_mapping.json        *** MISSING ***
  → core_vault/02_situational_qa_library.md     *** MISSING ***
```
Real location is `core_vault/JobApplyFiles/`. Broken since the `99dfefa` consolidation.

### E2 · Two broken symlinks for files declared canonical — P2

```
core_vault/comet_context/02_situational_qa_library.md  → BROKEN
core_vault/comet_context/04_behavioral_star_stories.md → BROKEN
```
Targets deleted in `7c44ef5`. **The only surviving copies are in
`.claude/worktrees/festive-davinci-67abbc/core_vault/JobApplyFiles/`** — recover them before
that worktree is pruned, or the STAR stories are gone permanently.

`CLAUDE.md` lists the first as the source for behavioural form answers. The nearest live
substitute is the `qa_bank` object in `06_logistics_mapping.json`; nothing points there.

### E3 · Agents must halt on any form asking for LinkedIn — P2

Neither canonical JSON contains a `linkedin` field. `INVOKE.md:8` says all values must come
from those two files and *"never guess"*. An agent obeying literally cannot fill a LinkedIn
URL field, despite the URL being an Absolute Rule in `CLAUDE.md`.

### E4 · 23 hand-maintained copies of the candidate profile — P2

Independent narrative copies requiring manual edit on any fact change:
`comet_context/` (4) · `JobApplyFiles/` (4) · `categories/md/` (4) · `categories/tex/` (5) ·
`templates/` (6) · `master_cv/` (2) · `cover-letters/` (4) · `docs/` + `persona_*.md` (6) ·
`active_application_context/` (6).

Residual drift after the 1 Aug sync: `~12 months` still in 4 comet files — two of which
(`00_comet_master_context.md`, `comet_browser_agent_prompt.md`) contradict *themselves*
between lines. `core_vault/08_daily_application_roadmap.md:183` says `8-9 months`.

### E5 · Two mutually exclusive profile-mutation prompts, both live — P2

`comet_python_pivot_prompt.md` ("Python/FastAPI-First Repositioning") and
`comet_typescript_revert_prompt.md` ("Restore MERN/TypeScript-First Identity") are opposing
one-time missions rewriting the same public profiles. Both mtime 1 Aug. Nothing records which
ran last — **the live state of the public profiles is unknowable from the vault.**

### E6 · 55 resume files, five conflicting "canonical" declarations — P2

| Source | Declares canonical |
|---|---|
| `CLAUDE.md` / `AGENTS.md` / `INVOKE*.md` | the 4 in `categories/md/` |
| `categories/pdf/resume_mapping.md` | 5 variants headed by `LatestResume.pdf` *(obsolete)* |
| `docs/RESUME_WORKFLOW.md` | *"`LatestResume.pdf` is your master copy"* *(obsolete)* |
| `master_cv/…Dossier.md:11` | `Atin_Sharma_Resume_2026.pdf` *(in no routing table)* |
| the tracker, all of 29 Jul | `NewResDocPdf.pdf` *(0 chars)* |

`AI_Integrated_FullStack.pdf` exists at **six paths with five distinct sizes**. A glob-based
picker cannot disambiguate.

### E7 · Documentation describes a vault that no longer exists — P2

`README.md`: 3 of 4 Quick Start paths missing (`system_handover_config/`, `prompts/`).
`docs/ARCHITECTURE.md`: 4 of 7 documented layers do not exist.
`docs/RESUME_WORKFLOW.md`: fully obsolete.
`INVOKE_STAGE.md`: routing table missing the fintech row present in the other three files —
so a fintech JD routes differently depending on which invoke file was used.
`AGENTS.md` carries two rules absent from `CLAUDE.md`, so Claude sessions never see them.

---

## F. Repository hygiene — *fixed in commit `4126589`*

2,139 of 2,327 tracked files (91%) were junk: 1,356 Chrome profile files (113 MB) and 762
`node_modules` files (72 MB), which is why `.git` was 470 MB of a 698 MB repo. There was no
`.gitignore` at all; `.git/info/exclude` held one line.

Also present: `atin-sharma-offer-letter.pdf` (3.27 MB, NDA-governed) in the repo root, and
`scratch/registry_probe/` duplicating `company_board_registry/` with a *larger* `verified.json`
— the scratch copy may be the newer one. Reconcile before deleting either.
