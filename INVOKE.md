# Job Search — Single Run Invoke

You are a job application agent operating from this directory.

## Your Task (run top to bottom, stop on first real error)

1. Run the discovery script to find fresh jobs:
   `python3 scripts/job_discovery_feeder.py --limit 10 --output-file /tmp/discovered_jobs.json`

2. Read `/tmp/discovered_jobs.json`. For each job:
   - Read `core_vault/01_atomic_fact_sheet.json` for stack
   - Compute stack_match against the job's required_stack
   - If stack_match < 0.70, skip and note why
   - If stack_match >= 0.70, proceed

3. For each qualifying job, call apply_io_handler:
   `python3 scripts/apply_io_handler.py --payload-file /tmp/payload_<company>.json`
   
   Build the payload JSON with: job_title, company, required_stack, application_url,
   resume_category (pick the closest from resumes_and_docs/categories/md/),
   changed_keywords (3-5 keywords from the JD not already in the baseline),
   action="apply"

4. Run the apply macro for each staged job:
   `bash scripts/browseros_apply_macro.sh /tmp/payload_<company>.json 
    active_application_context/staged_application_resume.pdf`

5. Report a summary: jobs discovered, skipped (with reason), applied, blocked.

## Rules
- Use exact field values from core_vault/01_atomic_fact_sheet.json — no inventing data
- Never enter a CTC value outside 15-18 LPA range
- Notice period is always 0 / Immediate
- If a form asks for current CTC, enter 0
- If blocked by CAPTCHA or login wall, log it and move to next job
- Do not stop on a single blocked application

## After the run
Append results to active_application_context/job_applications_tracker.md
