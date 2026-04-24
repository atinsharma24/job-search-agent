# MASTER BOOTLOADER PROMPT

Boot target: `@job-scout`

- Load only:
  - `core_vault/01_atomic_fact_sheet.json`
  - `resumes_and_docs/categories/md/`
  - `active_application_context/background_agent_state.json`
  - `active_application_context/job_applications_tracker.md`
- Active input packet:

```json
[
  {
    "job_title": "",
    "company": "",
    "required_stack": [],
    "application_url": ""
  }
]
```

- Do not load Mem0, `packed_context.txt`, session logs, STAR libraries, or situational QA unless `interview_state=true`.
- Use fast-path tailoring only.
- Apply when `stack_match >= 0.70`.
- Log and terminate after `apply`, `skip`, or `blocked`.
