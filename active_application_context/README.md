# Active Application Context

Purpose: live session state, workflow notes, and execution history for ongoing job applications.

Files in this directory should be updated as the application process evolves so the current operating context is separated from the base source vault.

---

## Background Automation Protocol (v1.0)

**Goal:** Maximize accuracy and minimize token/context usage during hourly background runs.

### 1. Pre-Run (Context Prep)
- Read `background_agent_state.json` to load `seen_job_ids`.
- Identify the current portal target (rotate through Cutshort, Arc, LinkedIn, Himalayas).

### 2. Search & Filter (Low Context)
- Navigate directly to the search URLs defined in `07_remote_job_portals_india.md`.
- Use `mcp_local-server_take_snapshot` to identify job listings.
- For each listing, extract Job ID and Title. Skip if in `seen_job_ids`.

### 3. Evaluation (Surgical Read)
- Open job details.
- Search for "Disqualifiers" first: `5+ years`, `7+ years`, `US Only`, `Europe Only`, `Citizen required`.
- If disqualified, add ID to `seen_job_ids` and close tab.
- If qualified (1-3 years, MERN/Python/AI focus), proceed to Apply.

### 4. Application
- **Tier 2 (Auto-Apply):** Use `01_atomic_fact_sheet.json` to fill forms on Cutshort, Instahyre, and LinkedIn (Easy Apply). Submit immediately.
- **Tier 1 (Scout & Draft):** For YC, Wellfound, and direct ATS (Ashby/Lever/Greenhouse), draft a tailored cover letter in `resumes_and_docs/tailored/cover-letters/` and a tailored resume. Move to `pending_review` and PAUSE for operator review before submission.
- **Tier 3 (Opportunistic):** Auto-apply only if 100% stack match is confirmed.

### 5. Post-Run (State Sync)
- Update `background_agent_state.json` with new seen/applied IDs.
- Append successful applications to `job_applications_tracker.md`.
- Log the run outcome to `session_status_latest.md`.

