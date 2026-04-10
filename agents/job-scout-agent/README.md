# How to Use the Job-Scout Agent

The `job-scout-agent` is a specialized sub-agent designed to handle the heavy lifting of your job search with high accuracy and low token cost.

### 1. How to Invoke
In your Gemini CLI, you can now delegate tasks directly to this agent. 

**Example Commands:**
- `"@job-scout run an hourly scout of Cutshort and Arc."`
- `"@job-scout check for new LinkedIn jobs and apply to Easy-Apply ones."`
- `"@job-scout summarize my pending_review list and draft the cover letters."`

### 2. File Structure
- `agents/job-scout-agent/AGENT.md`: The "brain" of the agent. You can edit this file to change its behavior (e.g., if you want to target 3-5 year roles later).
- `active_application_context/background_agent_state.json`: Where the agent stores its memory of seen/applied jobs.

### 3. Best Practices
- **Login First:** Make sure you are logged into your job portals in your main browser. The agent uses your active session.
- **Review Regularly:** Use the `STATUS_CHECK_PROMPT.md` I created earlier to see what the agent has found while you were away.
- **Update the Vault:** If the agent says it couldn't answer a specific question (marked as `pending_review`), update your `01_atomic_fact_sheet.json` with that info, and it will know it for next time.
