# Job Search Playbook

- Standard input packet:

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

- Standard decision rule:
  - `stack_match >= 0.70` -> fast-path tailor, apply, log, terminate
  - `stack_match < 0.70` -> log skip, terminate
  - blocked flow -> log blocked, terminate

- Fast-path tailoring:
  - select the nearest baseline resume from `resumes_and_docs/categories/md/`
  - swap target keywords only
  - generate a template cover letter

- Deferred files:
  - `core_vault/02_situational_qa_library.md`
  - `core_vault/04_behavioral_star_stories.md`
  - session status logs

Load deferred files only for interview mode or explicit blocker handling.
