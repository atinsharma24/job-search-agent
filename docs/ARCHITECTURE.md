# 🏢 Vault Architecture

The Job Search Vault is structured into 7 distinct layers. This modular design ensures any agent (Gemini, Codex, OpenClaw) can find information instantly and with minimal context token usage.

## 1. Core Vault (`/core_vault/`)
This is the **Source of Truth**. It contains static data that defines who you are and what you've built.
- `01_atomic_fact_sheet.json`: Your profile, stack, metrics, and project details.
- `04_behavioral_star_stories.md`: Approved STAR narratives for complex form questions.
- `07_remote_job_portals_india.md`: Search URLs for India-remote job boards.

## 2. Active Context (`/active_application_context/`)
The **Short-Term Memory** of the agent.
- `background_agent_state.json`: Critical state file! Tracks `seen_job_ids`, `applied_job_ids`, and `pending_review`.
- `job_applications_tracker.md`: High-level log of all applications submitted.
- `README.md`: Current "Background Automation Protocol."

## 3. Agents & Logic (`/agents/`)
The **"Brain"** of the system.
- `job-scout-agent/AGENT.md`: Detailed persona and execution logic.

## 4. Prompt Library (`/prompts/`)
The **"Toolbox"**.
- `job-automation-library/`: Predefined prompts for scouting, drafting, and resume generation.

## 5. Resumes & Documents (`/resumes_and_docs/`)
The **"Assets"** layer.
- `templates/`: Master LaTeX files (`.tex`).
- `tailored/`: Output folder for job-specific resumes and cover letters.
- `categories/`: High-signal resumes (AI Engineer, Backend Specialist, etc.).

## 6. Logs & Scripts (`/logs/`, `/scripts/`)
- `/logs/run_reports/`: Daily logs of what the agent discovered and did.
- `/scripts/`: Automated Python tools (e.g., batch resume generator).

## 7. Handover Configuration (`/system_handover_config/`)
Used to move this vault between different LLMs (e.g., from Gemini CLI to Codex).
- `MASTER_BOOTLOADER_PROMPT.md`: One-click setup for any new agent.
- `STATUS_CHECK_PROMPT.md`: Quick health check of the automation.
- `tool_specific_configs/`: 
    - `openclaw/SYSTEM.md`: System instructions for OpenClaw TUI.
    - `codex/instructions.md`: Custom instructions for Codex CLI.
