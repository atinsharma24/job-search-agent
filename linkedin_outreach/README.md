# LinkedIn Outreach — Supervised Automation Scaffold

This repository is a human-in-the-loop outreach scaffold designed to prepare, review, and send personalized LinkedIn messages and emails safely. Everything is intentionally supervised — no messages are sent without explicit human approval. The system lives under `/Users/atinsharma/job_search_vault/linkedin_outreach/` and contains templates, contact lists, queue management, sending scripts (BrowserOS executor), and a manual Gmail-trigger invoker.

Quick links
- Root: /Users/atinsharma/job_search_vault/linkedin_outreach/
- Detailed runbook: docs/WORKFLOW.md
- Agent config: agent/agent_config.json

Table of contents
- Overview
- Directory map
- Key concepts
- Getting started (install & initial run)
- End-to-end workflow (detailed)
- Safety rules & limits
- Scripts & package.json
- Troubleshooting & common errors
- How to extend

Overview

The system separates responsibilities into three phases:
1. Prepare: read contacts (CSV), resolve templates and placeholders, build pending queue entries.
2. Review: interactive CLI for a human reviewer to approve, edit, skip, or blacklist entries.
3. Send: BrowserOS-driven executor that opens LinkedIn profiles and sends connection requests or messages — requires one-keystroke confirmation per message and enforces delays and daily limits.

Directory map

linkedin_outreach/
├── agent/
│   └── agent_config.json        ← agent settings, run commands, notification config
├── contacts/
│   └── targets.csv             ← contact list (single-sample row provided)
├── templates/
│   ├── persona_1_founders.md
│   ├── persona_2_vp_eng.md
│   ├── persona_3_eng_managers.md
│   ├── persona_4_senior_engineers.md
│   └── persona_5_recruiters.md
├── queue/
│   ├── pending.json            ← pending queue entries (built by prepare)
│   ├── approved.json           ← human-approved entries (for send_agent)
│   ├── sent.json               ← archive of sent entries
│   └── blacklist.json          ← contact_ids never to message (created by reviewer)
├── logs/
│   ├── outreach.log            ← audit log for approvals and sends
│   └── errors.log              ← error and halt conditions
├── scripts/
│   ├── prepare_queue.ts        ← builds pending.json from targets.csv
│   ├── review_queue.ts         ← interactive reviewer (enquirer)
│   ├── send_agent.ts           ← BrowserOS executor (must be run when browser logged in)
│   ├── agent_runner.ts         ← convenience script: runs prepare → review
│   └── gmail_invoker.ts        ← one-shot Gmail invoker (searches for trigger email)
├── package.json                ← npm scripts & deps
├── README.md                   ← this file (high-level)
└── docs/
    └── WORKFLOW.md             ← extensive runbook (detailed)

Key concepts

- Templates: Markdown files per persona. Each contains variants (e.g., 1A, 1B) and placeholders like [Company], [Specific Feature/News]. Do NOT send templates as-is — always resolve placeholders.
- Contacts CSV: canonical list of targets. Column names must match the schema (see below).
- Queue files: pending.json → approved.json → sent.json. Always operate on approved.json for sending.
- Human-in-the-loop: review_queue.ts is mandatory to move pending → approved.
- Agent runner & invoker: agent_runner orchestrates local prepare+review. gmail_invoker is an optional one-shot script that checks Gmail for a trigger email and runs agent_runner; it sends start/finish notifications via Gmail.

CSV schema (contacts/targets.csv)

The CSV must have exactly these columns (order preserved):

contact_id, full_name, title, company, linkedin_url, email, persona_id, variant_id, status, placeholder_company, placeholder_feature_or_news, placeholder_specific_reason, placeholder_technical_thing, notes, priority, added_date, approved_date, sent_date

Example sample row (already present):
- contact_id: c001
- full_name: Ankit Verma
- title: VP of Engineering
- company: Signzy
- linkedin_url: https://www.linkedin.com/in/[placeholder]
- persona_id: 2
- variant_id: 2B
- status: pending
- placeholder_company: Signzy
- placeholder_feature_or_news: KYC document intelligence layer
- placeholder_specific_reason: compliance automation stack alignment
- priority: HIGH
- added_date: 2026-04-11

Status values allowed: pending → approved → sending → sent → failed | skipped

Queue entry schema (queue/pending.json)

Each entry in pending.json must follow this schema (fields present in created entries):
- queue_id: uuid-v4
- contact_id: matches targets.csv contact_id
- full_name
- company
- linkedin_url
- persona_id: integer 1–5
- variant_id: string (e.g., "2B")
- message_type: linkedin_connection | dm | inmail | email
- subject: string | null
- body_raw: template body with placeholders unfilled
- body_compiled: template with ALL placeholders replaced (never send body_raw)
- placeholders_used: map of placeholder -> resolved value
- status: pending | approved | sending | sent | failed | skipped
- priority: HIGH | MEDIUM | LOW
- created_at, approved_at, sent_at: ISO-8601 timestamps
- error: nullable string

Files that were created for you
- Templates for 5 personas (persona_*.md)
- Sample contacts/targets.csv (one row)
- queue/pending.json with sample compiled entry
- scripts (prepare_queue.ts, review_queue.ts, send_agent.ts, agent_runner.ts, gmail_invoker.ts)
- agent/agent_config.json
- package.json

Getting started — install

1. From linkedin_outreach directory run:

   npm install

2. (Optional dev tools) If you don't have ts-node installed globally, the package.json contains it as a devDependency and npm scripts call ts-node.
3. Verify you have access to Gmail through Strata (this environment already has Gmail connected). The gmail_invoker uses the connected Gmail actions via Strata.

End-to-end workflow (recommended manual-trigger)

1. Add contacts to contacts/targets.csv (status should be pending). Ensure placeholders are populated for each contact.
2. Run the prepare step (resolves templates → queue/pending.json):

   npm run prepare

   - Output: processed/queued/skipped counts. Errors are appended to logs/errors.log.

3. Run the interactive review:

   npm run review

   - For each pending entry you can Approve (moves to queue/approved.json), Edit message, Skip (this session), Blacklist (never send), or Exit.
   - Approved entries get approved_at timestamp and an entry in logs/outreach.log.

4. When you're ready to send approved items, run the send agent (requires a logged-in LinkedIn browser session):

   npm run send

   - For each approved entry, the script prints the message and requires a single keystroke confirmation (Y to send).
   - The script enforces safety: daily cap (15), randomized delay (45–90s), CAPTCHA/security halts, and will log / exit if problems occur.

5. Sent entries are moved to queue/sent.json and outreach.log receives a SENT entry. Errors are appended to logs/errors.log.

Optional: use the Gmail invoker (one-shot) to trigger prepare+review automatically when you receive an email with subject "RUN OUTREACH":

1. Send yourself an email with subject: RUN OUTREACH (or change agent/agent_config.json notification.trigger_subject).
2. Run:

   npm run gmail:invoke

3. The invoker will search for unread messages matching the trigger, send a "start" notification to the configured notification_email (agent/agent_config.json), run agent_runner (prepare → review), and send a "finished" notification when complete.

Notes on the Gmail invoker:
- It uses the connected Gmail integration via Strata actions (gmail_search_emails and gmail_send_email).
- It is a one-shot script (not a long-running poller). Re-run it manually or from cron when needed.
- The invoker marks trigger emails as processed in its internal logic (not yet implemented to modify message labels) — currently it searches for unread messages; to avoid duplicates, archive or mark trigger emails as read after testing.

Safety rules (must read)

- NEVER send messages without human approval. The review step is mandatory to move items into approved.json.
- The send_agent enforces a hard daily cap of 15 LinkedIn messages. If the cap is reached it exits with a message.
- The send_agent waits between 45–90 seconds between sends (randomized) to avoid detection.
- If LinkedIn shows CAPTCHA, suspicious activity, or rate-limit responses, the send_agent logs HUMAN_INTERVENTION_REQUIRED to logs/errors.log and exits immediately.
- Do not store LinkedIn credentials in files. Ensure your LinkedIn session is already logged in in your browser before running the send step.

Template authoring and placeholders

- Templates live in `templates/` and are structured with variant sections. Each variant must include placeholders in square brackets: e.g., [Company], [Specific Feature/News].
- The prepare script maps common placeholder names to CSV columns. If any placeholder remains unresolved (bracketed text remains) the row will be skipped and an UNRESOLVED_PLACEHOLDER entry will be written to logs/errors.log.
- Connection-request variants are validated to be ≤ 300 characters after placeholder resolution. If they exceed 300 chars they will be skipped and logged.

Common logs & error codes

- UNRESOLVED_PLACEHOLDER — prepare skipped an entry due to unresolved placeholder(s).
- CONNECTION_EXCEEDS_LIMIT — connection message too long (>300 chars).
- BUTTON_NOT_FOUND — send_agent could not find Connect or Message button on profile.
- ADD_NOTE_NOT_FOUND, TEXTAREA_NOT_FOUND, SEND_BUTTON_NOT_FOUND — UI element not found during send flow.
- HUMAN_INTERVENTION_REQUIRED — CAPTCHA or security challenge detected; stop and investigate.
- SEND_ERROR — other send-time exception; entry is marked failed for retry.

Troubleshooting

- If prepare skips rows: check contacts/targets.csv placeholders and ensure required columns are populated.
- If review shows unexpected text: edit templates in templates/ and re-run prepare.
- If send_agent fails to find buttons: LinkedIn UI changed — inspect the DOM manually or update send_agent.ts snapshot/selector logic.
- If Gmail invoker finds no emails: confirm the trigger subject and that the trigger email is unread.

Extending and automation

- To add more personas: create templates/persona_N_name.md following existing format and update agent_config persona_scope if needed.
- To automate invocation via cron: add `npm run gmail:invoke` to your crontab at a safe frequency (e.g., hourly) but prefer manual runs for safety.

Security & privacy

- Sensitive data (LinkedIn credentials) must never be written to disk. The system assumes your browser session is already logged in for send operations.
- Logs contain limited PII for auditing. If you need stricter privacy, rotate logs and secure the folder with OS file permissions.

If anything is unclear or you want a deeper walkthrough (video screencast-style steps or a smaller excerpt for a README on another repo), tell me which part to expand. For full operational checks I can also run a dry-run of the invoker that only searches Gmail and reports matches (no emails sent).