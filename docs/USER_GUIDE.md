# 📖 User Guide: Daily Scouting & Applying

This guide explains how to use your **@job-scout** agent for daily tasks.

## 🏁 Starting the Day
1.  **Check Status:** Open your CLI and paste the prompt from `system_handover_config/STATUS_CHECK_PROMPT.md`. This will give you a report on background runs.
2.  **Scout New Roles:** Run the **Scout & Filter** prompt from `prompts/job-automation-library/01_scout_and_filter.md`.
    - It will auto-apply to "Easy Apply" roles.
    - It will save more complex roles to the `pending_review` list.

## 📝 Handling "Pending Review" Roles
If the agent found a high-value role but couldn't auto-apply (e.g., it needs a custom cover letter):
1.  Run the **Draft Pending Letters** prompt from `prompts/job-automation-library/02_draft_pending_letters.md`.
2.  The agent will research the company and draft a tailored cover letter in `resumes_and_docs/tailored/cover-letters/`.
3.  **Review & Submit:** Review the draft, then manually click "Submit" on the job portal tab.

## 🎯 Tailoring for a "Dream Job"
If you find a role you *really* want:
1.  Use the **Deep Dive Tailoring** prompt from `prompts/job-automation-library/04_deep_dive_tailoring.md`.
2.  The agent will:
    - Extract the 3 most important keywords from the JD.
    - Tailor your **LaTeX resume** (using `res2.tex` / `master_resume_alt.tex`).
    - Compile a **single-page PDF** in `resumes_and_docs/tailored/resumes/`.

## ✅ Tracking Progress
- All successful applications are automatically logged to `active_application_context/job_applications_tracker.md`.
- Use the **Tracker Sync & Audit** prompt (`prompts/job-automation-library/03_tracker_sync_audit.md`) once a week to ensure your stats are accurate.
