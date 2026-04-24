# Current Session Action Plan

## Standard Packet

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

## Execution Rule

1. Read one job packet.
2. Compute stack alignment.
3. If `stack_match >= 0.70`, run fast-path keyword injection on the nearest baseline resume, generate a template cover letter, apply, log, and terminate.
4. If `stack_match < 0.70`, log `skip` and terminate.
5. If blocked by login, CAPTCHA, account creation, or missing mandatory data, log `blocked` and terminate.

## Deferred Context

- interview libraries
- historical logs
- session summaries

Do not load deferred context during standard application runs.
