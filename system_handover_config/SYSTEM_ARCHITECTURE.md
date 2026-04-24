# System Architecture

## Core Files

- `core_vault/01_atomic_fact_sheet.json`: candidate data
- `resumes_and_docs/categories/md/`: baseline resume set
- `active_application_context/background_agent_state.json`: dedupe and run state
- `active_application_context/job_applications_tracker.md`: human-readable application log

## Standard Loop

1. Extract minimal job packet.
2. Check duplicates and disqualifiers.
3. Compute stack alignment.
4. If alignment is below 70%, log `skip`.
5. If alignment is 70% or higher, run fast-path keyword injection on the closest baseline resume, generate a template cover letter, apply, and log `apply`.
6. If blocked, log `blocked`.
7. Terminate the thread.

## Deferred Context

- `core_vault/02_situational_qa_library.md`
- `core_vault/04_behavioral_star_stories.md`
- historical run logs
- session status files

Load deferred context only for interview or blocker-handling workflows.
