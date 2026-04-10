# System Architecture: Autonomous Job Search Vault

This document is the "Source of Truth" for any AI agent (Gemini CLI, Codex, OpenClaw, BrowserOS) interacting with this vault.

## 1. Directory Structure & File Roles
- **`/01_atomic_fact_sheet.json`**: Core candidate data (DO NOT HALLUCINATE).
- **`/04_behavioral_star_stories.md`**: Approved narratives for STAR-based questions.
- **`/active_application_context/`**: 
    - `background_agent_state.json`: Critical state file to prevent duplicate applications.
    - `README.md`: Contains the current "Background Automation Protocol."
- **`/agents/job-scout-agent/`**: 
    - `AGENT.md`: Logic for the `@job-scout` persona.
- **`/prompts/job-automation-library/`**: Standardized prompts for various job-search tasks.

## 2. Shared Agent Architecture
We use a **Scout -> Filter -> Apply** loop. 
- All agents MUST check `active_application_context/background_agent_state.json` before performing any browser action.
- All agents MUST update `job_applications_tracker.md` upon successful submission.

## 3. Tool Requirements
- **Browser Interaction**: Use `local-server` or equivalent to interact with the user's active browser session.
- **Persistence**: Log Job IDs in `seen_job_ids` immediately after extraction from the portal search results.
- **Security**: Never commit or log API keys or plaintext credentials.

## 4. Portability Protocol
To "re-instantiate" this agent in a new CLI or LLM:
1. Load `01_atomic_fact_sheet.json` as the system context.
2. Read `agents/job-scout-agent/AGENT.md` to set the persona.
3. Synchronize state from `active_application_context/background_agent_state.json`.
