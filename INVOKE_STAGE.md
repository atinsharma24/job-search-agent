# Job Search — Stage Run (Steps 1–3)

You are a job application agent for Atin Sharma operating from this vault.
Vault root: `/Users/atinsharma/job_search_vault`

## Safety Rules (read before anything else)

- All field values MUST come from `core_vault/01_atomic_fact_sheet.json` or `core_vault/06_logistics_mapping.json`.
- Salary: 15L+ (negotiable, no hard ceiling). Current CTC = 0.
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

## Step 3 — Stage All Payloads

Pick the best baseline resume for each qualifying job using this routing table:

| JD signals | Resume category |
|---|---|
| LLM, RAG, vector, embedding, Groq, pgvector, conversational, chatbot | `GenAI_Prompt_Engineer` |
| compliance, KYC, legal, identity, AML, document verification | `Backend_AI_Specialist` |
| cloud, DevOps, Docker, Kubernetes, AWS, infra | `Cloud_Native_FullStack` |
| full-stack, MERN, React, Next.js, product, founding | `AI_Integrated_FullStack` |

Identify 3–5 keywords from the JD that are NOT already in the baseline resume's skills/profile section. These are `changed_keywords`.

Build a payload object for each qualifying job:
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

Determine today's date (YYYY-MM-DD format). Write **all** qualifying payloads as a JSON array to:
```
active_application_context/daily_queue_{date}.json
```

Example for 2026-06-02:
```
active_application_context/daily_queue_2026-06-02.json
```

Do **not** run `apply_io_handler.py`. Do **not** launch any browser. Stop here.

Output a staging summary table:

| Company | Job Title | Resume Category | stack_match | Queued / Skipped |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

---

> **Run INVOKE_APPLY.md locally to execute Steps 4–5.**
