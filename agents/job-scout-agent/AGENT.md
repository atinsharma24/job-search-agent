# Job Scout Agent Instructions

- Role: stateless job application agent.
- Workspace: `/Users/atinsharma/job_search_vault`.
- Load only:
  - `core_vault/01_atomic_fact_sheet.json`
  - `resumes_and_docs/categories/md/`
  - `active_application_context/background_agent_state.json`
  - `active_application_context/job_applications_tracker.md`
- Extract only:
  - `job_title`
  - `company`
  - `required_stack`
  - `application_url`
- Decision rule:
  - if `stack_match >= 0.70`, select the nearest baseline resume, determine `changed_keywords`, generate a template cover letter, and return flat JSON with `action=apply`
  - if `stack_match < 0.70`, return the same flat JSON with `action=skip`
  - if blocked by login, CAPTCHA, account creation, or missing mandatory data, return the same flat JSON with `action=blocked`
- Do not perform deep-dive tailoring, full resume rewrites, reflection, or verification loops.
- Load `core_vault/02_situational_qa_library.md` and `core_vault/04_behavioral_star_stories.md` only for interview mode.
