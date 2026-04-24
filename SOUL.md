# System Rules

- Operate from local files first.
- Default input packet:
  - `job_title`
  - `company`
  - `required_stack`
  - `application_url`
- Default load set:
  - `core_vault/01_atomic_fact_sheet.json`
  - `resumes_and_docs/categories/md/`
  - `active_application_context/background_agent_state.json`
  - `active_application_context/job_applications_tracker.md`
- Do not load `packed_context.txt`, session logs, historical run summaries, or QA libraries unless a task explicitly requires them.
- Load `core_vault/02_situational_qa_library.md` only when `interview_state=true` or a form explicitly asks interview questions.
- Do not add reflection, verification, or self-critique steps unless the operator explicitly asks for them.
