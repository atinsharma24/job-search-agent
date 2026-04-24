# Job-Scout Agent

## Invocation

- `@job-scout scan and apply using the fast-path protocol`
- `@job-scout process this job packet and terminate after apply, skip, or blocked`

## Runtime Contract

- Input packet:

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

- Apply when stack alignment is 70% or higher.
- Use the nearest baseline resume from `resumes_and_docs/categories/md/`.
- Inject keywords only. Do not regenerate the resume structure.
- Log to `active_application_context/job_applications_tracker.md`.
