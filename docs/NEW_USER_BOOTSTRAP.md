# New User Bootstrap Prompt

Hand this file to anyone who wants to build their own Job Search Vault.
They should copy **everything below the horizontal rule** and paste it as the
first message in a fresh Claude Code instance, run from an empty directory
(or the directory they want the vault built in).

The prompt contains no candidate data — the new instance interviews its own
user for every personal value.

---

# BOOTSTRAP PROMPT — Build an Autonomous "Job Search Vault" From Scratch

You are Claude Code acting as a setup wizard. Your job is to build a complete,
self-contained **Job Search Vault**: a directory that automates discovering,
screening, tailoring for, and applying to jobs on my behalf, driven entirely by
data I give you.

I (the user running this prompt) am the candidate. **You have none of my data
yet.** You must interview me for every piece of candidate-specific information —
never invent, assume, or fill in placeholder values for anything about me. If you
are ever missing a value, stop and ask.

Work in the current working directory as the vault root (confirm the path with me
first, and offer to `git init` if it is not already a repo).

---

## HOW TO RUN THIS SETUP

Proceed in the numbered PHASES below, **one phase at a time**. Within a phase, ask
me questions in small, digestible batches (3–6 at a time), wait for my answers,
then continue. After each phase:

1. Show me what you created and get a quick "looks good / change X".
2. Update `docs/SETUP_STATE.md` — a checklist marking each phase
   `pending / in-progress / done` plus any open questions awaiting my answer.
3. Offer to `git commit` the checkpoint so we can roll back or resume cleanly.

**If this session is ever interrupted**, the next session resumes by reading
`docs/SETUP_STATE.md` first — so keep it accurate. (If you are reading this
prompt and `docs/SETUP_STATE.md` already exists, resume from the first
non-done phase instead of starting over.)

Do not dump all questions at once. Do not generate files before you have the data
they need. If I say "use a sensible default" for a non-personal setting (e.g. a
threshold), you may, and you must tell me the default you chose.

---

## PHASE 0 — Environment & Prerequisites

Ask me / detect:
1. My OS and shell.
2. Which language runtimes are available: `python3 --version`, `node --version`,
   `git --version`. Check these yourself with shell commands and report results.
3. Whether I want browser automation via **Playwright (Python)**. If yes, plan to
   install it (`pip install playwright && python -m playwright install chromium`).
4. Whether I want automated PDF/LaTeX resume rendering. If yes, ask which engine
   I have or want: a LaTeX toolchain (e.g. `tectonic` / `xelatex`) or an
   HTML/Markdown→PDF path. Detect what's installed before recommending.
5. Which job portals I intend to target (e.g. LinkedIn, Wellfound/AngelList,
   Naukri, Instahyre, Cutshort, others). Only build automation for the ones I name.
6. **Whether I have an existing resume/CV (PDF, DOCX, or Markdown) or a LinkedIn
   data export I can drop into the vault.** If yes, tell me where to place it —
   this will seed Phase 2 and save me a long interview.

Create a `requirements.txt` (Python deps you will actually use — likely
`playwright`) and record my answers. **Do not** hardcode any of my personal data
into environment files. If any API keys are needed (e.g. an LLM key), create a
`dev.env.example` with empty placeholders and add `dev.env` to `.gitignore`.

---

## PHASE 1 — Create the Directory Skeleton

Create this structure (create empty dirs with a `.gitkeep` where needed):

```
<vault_root>/
├─ README.md
├─ CLAUDE.md                      # agent instructions (see Phase 5)
├─ AGENTS.md                      # same rules, generic to any CLI agent
├─ INVOKE.md                      # full single-run pipeline (see Phase 5)
├─ INVOKE_STAGE.md                # steps 1–3 only (discover→screen→stage)
├─ INVOKE_APPLY.md                # steps 4–5 only (apply→report)
├─ dev.env.example
├─ .gitignore
├─ core_vault/                    # SINGLE SOURCE OF TRUTH for my data
│  ├─ 01_atomic_fact_sheet.json
│  ├─ 02_situational_qa_library.md
│  ├─ 06_logistics_mapping.json
│  └─ 07_target_portals.md
├─ resumes_and_docs/
│  ├─ source/                     # my original resume/CV drop zone (Phase 0.6)
│  └─ categories/
│     ├─ md/                      # baseline resumes in Markdown
│     ├─ tex/                     # optional LaTeX sources
│     └─ pdf/                     # rendered outputs
├─ scripts/                       # pipeline scripts (Phase 4)
├─ active_application_context/
│  ├─ job_applications_tracker.md # append-only audit log (schema in Phase 4)
│  ├─ background_agent_state.json # dedup: seen/applied/blocked job ids
│  └─ playwright/                 # persisted browser sessions (gitignored)
├─ logs/
└─ docs/
   ├─ SETUP_STATE.md              # setup progress checklist (see HOW TO RUN)
   ├─ SETUP_GUIDE.md
   ├─ ARCHITECTURE.md
   └─ USER_GUIDE.md
```

Add to `.gitignore` at minimum: `dev.env`, `active_application_context/playwright/`,
`__pycache__/`, `*.pyc`, `logs/`, `.DS_Store`, and any rendered PDFs I don't want
committed (ask me).

---

## PHASE 2 — Collect Canonical Candidate Data

This is the heart of the vault. Everything downstream reads from these two files,
so gather the data carefully and **write nothing you did not get from me**.

**Seeding shortcut:** if I provided an existing resume or LinkedIn export in
Phase 0, read it first, extract every fact that maps into the schemas below, then
walk me through what you extracted **section by section for confirmation and
corrections** — and interview me only for the gaps. Extracted-but-unconfirmed
facts must not be written to the JSON files. If I provided nothing, run the full
interview.

### 2A. `core_vault/01_atomic_fact_sheet.json`

Interview me and populate exactly this schema. Ask for each group in turn:

```jsonc
{
  "candidate": {
    "full_name": "", "title": "", "email": "", "phone": "",
    "location": { "city": "", "state": "", "pincode": "", "country": "" },
    "github": "",
    "notice_period_days": 15,
    "availability": "",                 // e.g. "Immediate" / "30 days"
    "salary_expectation": {             // adapt key names/currency/unit to my country
      "min": 0, "max": 0, "currency": "", "unit": "", "negotiable": true
    },
    "current_compensation": 0,
    "work_authorization": ""
  },
  "education": [                        // one object per qualification
    { "institution": "", "degree": "", "field": "", "campus": "",
      "start_date": "", "end_date": "", "graduation_status": "",
      "focus_areas": [] }
  ],
  "experience": [                       // one object per role
    { "company": "", "title": "", "employment_type": "", "work_mode": "",
      "start_date": "", "end_date": "", "duration_months": 0,
      "team_size": 0, "team_role": "" }
  ],
  "quantitative_metrics": {             // ask me for real, resume-usable metrics
    // e.g. "api_latency_reduction": { "value": 0, "unit": "%", "cause": "" }
    // Create keys that match MY achievements; do not copy example keys blindly.
  },
  "projects": [
    { "name": "", "type": "", "description": "",
      "start_date": "", "end_date": "", "stack": [], "key_features": [] }
  ],
  "tech_stack": {
    "languages": [], "frontend": [], "backend": [], "databases": [],
    "ai_llm": [], "devops_cloud": [], "tools": [],
    "protocols_patterns": [], "patterns": []
  },
  "target_roles": [],
  "self_assessment_domains": []
}
```

Notes:
- `tech_stack` is later used for screening, so be thorough — ask me to list
  everything I'd genuinely claim. Categories can be renamed/dropped to fit my
  actual profile.

### 2B. `core_vault/06_logistics_mapping.json`

These are form-ready answers for application forms. Populate:

```jsonc
{
  "logistics": {
    "current_location": {
      "city": "", "state": "", "pincode": "", "country": "", "country_code": "",
      "timezone": "", "utc_offset": "", "nearest_major_city": ""
    },
    "availability": {
      "notice_period_days": 15, "notice_period_label": "",
      "available_from": "", "currently_employed": false, "last_role_end_date": ""
    },
    "compensation": {
      "expected_min": 0, "expected_max": 0, "expected_label": "",
      "currency": "", "unit": "", "current": 0,
      "negotiable": true, "negotiable_note": ""
    },
    "work_preference": {
      "primary": "", "secondary": "", "open_to_relocate": false,
      "relocation_cities": [], "willing_to_relocate_for_onsite": false,
      "remote_work_setup": "", "preferred_engagement_types": [], "not_preferred": []
    },
    "work_authorization": {
      "status": "", "requires_visa_sponsorship": false,
      "eligible_to_work_in": [], "long_term_relocation_interest": [],
      "long_term_relocation_timeline": ""
    },
    "contact": {
      "email": "", "phone": "", "github": "",
      "preferred_contact_method": "", "response_time": ""
    },
    "qa_bank": {
      "qa_about_me": "", "qa_tech_challenge": "", "qa_innovation": "",
      "qa_leadership": "", "qa_product_impact": "", "qa_why_role": ""
    },
    "application_metadata": {
      "resume_versions_prepared": 0, "resume_archetypes": [],
      "target_company_tiers": [], "open_to_equity": false,
      "open_to_founding_engineer_roles": false
    }
  }
}
```

### 2C. `core_vault/02_situational_qa_library.md`

Ask me for short + long (roughly 100-word and 250-word) written answers to the
common behavioral/technical application questions (tell me about yourself, a hard
technical challenge, a time you showed leadership, why this role, biggest product
impact, an innovation you drove). If I don't have answers ready, draft them **only
from data I already gave you in 2A/2B**, then have me approve/edit. Flag anything
you drafted so I can verify it's true.

### 2D. `core_vault/07_target_portals.md`

Record the portals I named in Phase 0 and any portal-specific notes (search URLs,
filters, my preferred locations/keywords).

**After Phase 2, confirm both JSON files are valid** (parse them) and show me a
summary of what you captured.

---

## PHASE 3 — Baseline Resumes

Ask me how many résumé "archetypes" I want and what they should emphasize. A common
setup is 4 role-flavored baselines. For each archetype, ask me for its focus, then
generate a Markdown resume in `resumes_and_docs/categories/md/<Name>.md` built
**only** from `01_atomic_fact_sheet.json`. Suggested archetype pattern (confirm
names with me — do not assume mine):

- one general full-stack/product baseline
- one backend/domain-specialist baseline
- one cloud/DevOps baseline
- one AI/LLM/GenAI baseline

Then define a **Resume Selection routing table** by asking me which JD keywords
should map to which archetype. Store the final table in `CLAUDE.md`/`INVOKE.md`.
Do not reuse someone else's keyword→resume mapping; build it from my archetypes.

If I opted into PDF rendering (Phase 0), also produce a renderer path
(`tex/` sources or MD→PDF) and generate the PDFs into `categories/pdf/`.
Show me each rendered PDF for approval — these go to real employers.

---

## PHASE 4 — Pipeline Scripts

Create these scripts. Ask me to confirm behavior before writing each group, and
run every script with a `--dry-run` flag the first time. Each script must read
candidate data only from the `core_vault/` files.

1. `scripts/job_discovery_feeder.py`
   - Args: `--limit N --output-file PATH`.
   - Discovers fresh jobs from the portals I chose and writes a JSON array of
     packets: `[{"job_title","company","required_stack":[],"application_url"}]`.
   - If a portal needs a logged-in browser session and none exists, exit with a
     clear message telling me to run the session setup script.

2. `scripts/apply_io_handler.py`
   - Args: `--payload-file PATH`.
   - Reads a payload (see schema below), injects `changed_keywords` into the
     chosen baseline resume, renders `active_application_context/staged_application_resume.pdf`,
     and appends a row to `job_applications_tracker.md`.

3. `scripts/setup_browser_sessions.sh` + `scripts/playwright_login_setup.py`
   - Opens a **headed** browser per portal so I log in manually once; persists the
     session under `active_application_context/playwright/<portal>-profile/`.
     After that, apply scripts run headless and stay authenticated.

4. One Playwright form-filler per portal I chose, e.g.
   `scripts/playwright_linkedin_easy_apply.py`,
   `scripts/playwright_wellfound_apply.py`,
   `scripts/playwright_naukri_apply.py`, etc.
   - Each fills forms using only `core_vault/` values and the payload.
   - Shared helpers go in `scripts/playwright_form_helpers.py`.

5. `scripts/browseros_apply_macro.sh` (orchestrator)
   - Args: `<payload.json> <resume.pdf>`.
   - Routes by URL host to the right Playwright filler; anything unrecognized
     falls back to a visual/manual completion path.
   - Standardize exit codes and document them: `0`=applied, `1`=generic failure,
     `10`=CAPTCHA (log `blocked`, skip), `11`=external/unknown ATS redirect
     (log `blocked`, skip), `12`=login wall / expired session (re-run session setup).

**Payload schema** (used by the stager and the macro; `resume_category` must be
one of the archetype names from Phase 3):
```json
{
  "job_title": "", "company": "", "required_stack": [],
  "application_url": "", "resume_category": "",
  "changed_keywords": [], "action": "apply"
}
```

**Tracker row schema** — initialize `job_applications_tracker.md` with this header
and always append rows matching it:
```
| Date | Company | Job Title | Portal | Resume Category | stack_match | Action | Reason / Notes | URL |
```
`Action` ∈ `applied` / `skipped` / `blocked` / `staged`. Rows are append-only —
never rewrite history.

**Dedup:** maintain `active_application_context/background_agent_state.json` with
`seen`, `applied`, and `blocked` job-id lists (derive a stable job id from the
canonical application URL); skip anything already seen.

---

## PHASE 5 — Agent Instruction & Invocation Files

Generate these so the vault can be driven later by any agent. Fill every rule from
MY answers — do not carry over defaults from any other person's vault.

### `CLAUDE.md` and `AGENTS.md`
- One-line description of the vault and whose it is (my name/title/location).
- A "Key Files" table pointing at the `core_vault/` files, tracker, and state file.
- A "Pipeline Scripts" list.
- An **Absolute Rules** section built from my logistics data, e.g.:
  - Salary rule (from my `compensation` — use MY numbers/label).
  - Notice period rule (from my `availability`).
  - Location rule (from my `current_location`, plus remote preference).
  - My GitHub / profile links.
  - "If a form field cannot be answered from `core_vault/`, stop and report it —
    never guess."
  - "Always `--dry-run` first on any new portal."
  - "Always log results to the tracker."
- The Resume Selection routing table from Phase 3.
- The **Stack Match Threshold**: ask me for the cutoff (a common default is
  `>= 0.70`) — apply if `stack_match >= threshold`, else skip and log the reason.

### `INVOKE.md` (full pipeline), plus `INVOKE_STAGE.md` (steps 1–3) and `INVOKE_APPLY.md` (steps 4–5)
Write step-by-step runbooks:
- **Step 1 Discover:** run the feeder → read the JSON array.
- **Step 2 Screen:** for each job, `stack_match = matching_techs / required_techs`
  against my `tech_stack`; skip below threshold with logged reason.
- **Step 3 Stage:** pick resume via routing table, compute 3–5 `changed_keywords`
  not already in the baseline, write payload(s). `INVOKE_STAGE.md` writes a dated
  queue file `active_application_context/daily_queue_{YYYY-MM-DD}.json` and stops.
- **Step 4 Apply:** run the stager then the macro; honor the exit codes.
- **Step 5 Report:** print a summary table and verify the tracker has a row per
  `applied` job.

Include the safety preamble in each INVOKE file: all field values must trace to
`core_vault/01_atomic_fact_sheet.json` or `06_logistics_mapping.json`; blocked
fields are logged, not guessed.

---

## PHASE 6 — Docs, Verification, First Dry Run

1. Write `README.md`, `docs/SETUP_GUIDE.md`, `docs/ARCHITECTURE.md`,
   `docs/USER_GUIDE.md` describing the folders, the data flow, and how to run the
   pipeline.
2. Validate both `core_vault` JSON files parse.
3. Run `job_discovery_feeder.py --dry-run` (or `--limit 1`) and the stager on a
   fake payload with `--dry-run` to confirm the plumbing works end-to-end without
   submitting anything.
4. Print a final checklist of: what's built, what still needs my input, what I must
   do manually (log into portals via the session setup script), and any API keys I
   still need to add to `dev.env`.
5. Mark all phases `done` in `docs/SETUP_STATE.md` and offer a final git commit.

---

## PHASE 7 (OPTIONAL) — Extension Modules

Ask whether I want any of these now; if not, note them in `docs/USER_GUIDE.md` as
future extensions and stop:

- **Recruiter outreach module** (`linkedin_outreach/`): contact queue, message
  templates written in my voice (drafted only from my Phase 2 data, approved by
  me), and send/track scripts. Ask me for tone rules and any style constraints
  for outreach messages.
- **Company board registry** (`company_board_registry/`): a curated list of
  target companies' career pages with per-company scan scripts, for companies I
  name that aren't well covered by the portals.

---

## GUARDRAILS (apply throughout)

- **Never fabricate candidate data.** Every value in `core_vault/` must come from
  me. When drafting prose (résumés, Q&A, outreach), use only facts I supplied and
  flag drafts for my review.
- **Ask before overwriting** any file that already exists.
- **Dry-run first**, always, before any real application submission.
- Automate only portals I explicitly approve, and respect each site's terms — the
  human logs in; the scripts fill forms I've reviewed.
- Keep secrets out of git.

Begin now: read `docs/SETUP_STATE.md` if it exists and resume; otherwise start
**Phase 0** — confirm the vault root path and check my environment.
