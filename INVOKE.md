# Job Search — Single Run Invoke

You are a job application agent for Atin Sharma operating from this vault.
Vault root: `/Users/atinsharma/job_search_vault`

## Safety Rules (read before anything else)

- All field values MUST come from `core_vault/01_atomic_fact_sheet.json` or `core_vault/06_logistics_mapping.json`.
- Salary: 15–18 LPA only. Current CTC = 0. Never deviate.
- Notice period: 0 days / Immediate Joiner. Always.
- If a required form field cannot be answered from the vault, log it as `blocked` and move to the next job.
- Never submit without confirming the exit code from the Playwright script is 0.
- Run with `--dry-run` first when testing a new portal or script version.

---

## Step 1 — Discover Fresh Jobs

```bash
python3 scripts/job_discovery_feeder.py --limit 10 --output-file /tmp/discovered_jobs.json
```

Read `/tmp/discovered_jobs.json`. It is a JSON array of job packets:
```json
[{"job_title":"","company":"","required_stack":[],"application_url":""}]
```

If the file is empty or the script errors, check if the LinkedIn browser session exists:
`active_application_context/playwright/linkedin-profile/`
If it does not exist, stop and tell the user to run `bash scripts/setup_browser_sessions.sh` first.

---

## Step 2 — Screen Each Job

For each job in the array:

1. Read `core_vault/01_atomic_fact_sheet.json` (your stack is in `tech_stack`).
2. Compare the job's `required_stack` against your stack. Compute `stack_match` = (matching technologies) / (total required technologies).
3. If `stack_match < 0.70`: log skip with reason and move to next.
4. If `stack_match >= 0.70`: proceed to Step 3.

---

## Step 3 — Stage the Resume

Pick the best baseline resume using this routing table:

| JD signals | Resume category |
|---|---|
| LLM, RAG, vector, embedding, Groq, pgvector, conversational, chatbot | `GenAI_Prompt_Engineer` |
| compliance, KYC, legal, identity, AML, document verification | `Backend_AI_Specialist` |
| cloud, DevOps, Docker, Kubernetes, AWS, infra | `Cloud_Native_FullStack` |
| full-stack, MERN, React, Next.js, product, founding | `AI_Integrated_FullStack` |

Identify 3–5 keywords from the JD that are NOT already in the baseline resume's skills/profile section. These are `changed_keywords`.

Write a payload JSON to `/tmp/payload_<company>.json`:
```json
{
  "job_title": "...",
  "company": "...",
  "required_stack": [...],
  "application_url": "...",
  "resume_category": "...",
  "changed_keywords": [...],
  "action": "apply"
}
```

Run the stager:
```bash
python3 scripts/apply_io_handler.py --payload-file /tmp/payload_<company>.json
```

This produces `active_application_context/staged_application_resume.pdf` and appends a row to the tracker.

---

## Step 4 — Apply

```bash
bash scripts/browseros_apply_macro.sh \
  /tmp/payload_<company>.json \
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

---

## Supplemental: Apply to a Specific Job (Skip Discovery)

If you already have a job URL and want to apply directly, provide this input:

```
Apply to this job on my behalf:
  Job title: [title]
  Company: [company]
  URL: [url]
  Required stack: [comma-separated techs from the JD]

Run Steps 2–5 from INVOKE.md.
```
