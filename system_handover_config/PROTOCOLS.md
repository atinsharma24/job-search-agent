# Background Execution Protocol for Shared Agents

To ensure multiple agents (Codex, OpenClaw, Gemini CLI) do not collide when running background tasks:

## 1. Token/Turn Efficiency
- **Surgical Reads**: Do not read full job descriptions if the summary shows `5+ years` or `US Only`.
- **Parallelism**: Use parallel tool calls for searching multiple portals at once.

## 2. Multi-Agent Collision Avoidance
- **Locking**: Before starting a browser-heavy run, check the `last_run_timestamp` in `active_application_context/background_agent_state.json`. 
- **Wait Period**: Do not start a new run if the last run was within the last 45 minutes, unless explicitly requested by the user.

## 3. Navigation Rules
- **Direct Access**: Use search URLs from `07_remote_job_portals_india.md` to skip landing page navigation.
- **Hidden Tabs**: Always run in background/hidden tabs using the `local-server` integration to avoid interrupting the user's work.

## 4. Verification
- After clicking 'Apply', verify the success message or redirect before updating the `job_applications_tracker.md`.
