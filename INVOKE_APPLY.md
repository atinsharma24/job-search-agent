# Job Search — Apply Run (Steps 4–5)

> **Requires local Playwright sessions. Run after INVOKE_STAGE.**
> Browser sessions must exist at `active_application_context/playwright/`.
> If they don't, run `bash scripts/setup_browser_sessions.sh` first.

Vault root: `/Users/atinsharma/job_search_vault`

---

## Step 4 — Apply

Determine today's date (YYYY-MM-DD format). The queue file is:
```
active_application_context/daily_queue_{date}.json
```

**Before proceeding**, check that this file exists. If it does not:
```
No staged queue found for {date}. Run INVOKE_STAGE first.
```
Stop immediately. Do not proceed.

For each payload in the array:

1. Run the stager to produce the tailored PDF:
```bash
python3 scripts/apply_io_handler.py --payload-file active_application_context/daily_queue_{date}.json
```
This produces `active_application_context/staged_application_resume.pdf` and appends a row to the tracker.

2. Run the apply macro:
```bash
bash scripts/browseros_apply_macro.sh \
  active_application_context/daily_queue_{date}.json \
  active_application_context/staged_application_resume.pdf
```

The macro auto-routes by URL:
- `linkedin.com` → `playwright_linkedin_easy_apply.py`
- `wellfound.com` / `angel.co` → `playwright_wellfound_apply.py`
- `naukri.com` → `playwright_naukri_apply.py`
- Anything else → `claude` CLI visual fallback (you will be prompted to complete it)

Exit codes:
- `0` = applied successfully
- `1` = generic failure
- `10` = CAPTCHA detected — log `blocked`, skip
- `11` = external redirect / non-standard ATS — log `blocked`, skip
- `12` = login wall — session expired, run `setup_browser_sessions.sh`

---

## Step 5 — Report

After processing all jobs, output a summary table:

| Company | Job Title | Action | Reason |
|---|---|---|---|
| ... | ... | applied / skipped / blocked | ... |

Then verify `active_application_context/job_applications_tracker.md` has a row for every `applied` entry.
