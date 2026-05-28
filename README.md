# 🚀 Autonomous Job Search Vault v2.0

Welcome to your AI-powered job search command center. This vault is a modular, high-performance architecture designed to automate the heavy lifting of your job search—from scouting roles on LinkedIn and Cutshort to generating tailored LaTeX resumes and submitting applications.

## 🌟 Key Features
- **@job-scout Agent:** A specialized AI persona that understands your tech stack and experience.
- **Auto-Tailoring Resumes:** Automated LaTeX generation using `tectonic` for single-page, professional PDFs.
- **Intelligent Scouting:** Hourly background scans of top India-remote job portals.
- **Modular Vault:** A clean "Source of Truth" architecture compatible with Gemini, Codex, and OpenClaw.
- **Portability:** Use the **Master Bootloader Prompt** to instantly spin up this system on any LLM.

---

## 📂 Quick Start
1.  **Read the Setup Guide:** [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) (Install Tectonic, etc.)
2.  **Initialize the Agent:** Open your CLI and paste the prompt from `system_handover_config/MASTER_BOOTLOADER_PROMPT.md`.
3.  **Run Your First Scout:** Paste the prompt from `prompts/job-automation-library/01_scout_and_filter.md`.
4.  **Check Progress:** Paste the prompt from `system_handover_config/STATUS_CHECK_PROMPT.md`.

---

## 📖 Table of Contents
| Guide | Description |
| :--- | :--- |
| [Architecture Map](docs/ARCHITECTURE.md) | How the folders and files work together. |
| [Setup Guide](docs/SETUP_GUIDE.md) | How to install dependencies and configure your environment. |
| [User Guide](docs/USER_GUIDE.md) | Commands and prompts for daily scouting and applying. |
| [Resume Workflow](docs/RESUME_WORKFLOW.md) | How the LaTeX tailoring and PDF generation works. |
| [Automation & Scheduling](docs/AUTOMATION_AND_SCHEDULING.md) | Setting up cron jobs and local browser scheduling. |

---

## 🛠️ Requirements
- **Gemini** (or any LLM agent with browser/shell access)
- **Local-Server MCP** (for browser interactions)
- **Tectonic CLI** (for LaTeX $\rightarrow$ PDF compilation)
- **Active Browser Session:** Stay logged into your job portals!

---

**Developed for Atin Sharma**  
*Full-Stack & AI Engineer | 2026 Strategy*
