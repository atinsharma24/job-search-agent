# ☁️ Automation & Scheduling

This guide explains how to make your job search run 24/7.

## 1. BrowserOS Native Scheduling (Recommended)
This uses the **Local-Server MCP** to schedule tasks directly in your browser. This is the most reliable way to maintain logged-in sessions on LinkedIn/Cutshort.

**To trigger a schedule:**
Use the **@job-scout** to suggest a new schedule:
> "@job-scout suggest a schedule to run prompt #01 every 4 hours. Call it 'Background Job Scout'."

**How it works:**
- BrowserOS creates a **hidden background tab**.
- It opens the portals, scans for new jobs, and auto-applies.
- It will NOT pop up or interrupt your work.
- It updates `job_applications_tracker.md` after every successful run.

---

## 2. Using System Cron (Local Machine)
If you want to run the **Gemini CLI** from your terminal on a fixed schedule (e.g., while you are away from the computer).

1.  **Create a script (`run_scout.sh`):**
    ```bash
    #!/bin/bash
    cd /Users/atinsharma/job_search_vault
    gemini-cli "@job-scout Execute prompt #01 from /prompts/job-automation-library/01_scout_and_filter.md"
    ```
2.  **Add to Crontab:**
    `crontab -e`
3.  **Add this line (to run every 4 hours):**
    `0 */4 * * * /Users/atinsharma/job_search_vault/run_scout.sh`


