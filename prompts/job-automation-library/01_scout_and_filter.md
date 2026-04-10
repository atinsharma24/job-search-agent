# Prompt: Scout and Initial Filter

**Target:** Broad discovery of new roles across all primary portals.

**Prompt:**
"@job-scout Execute a scouting run on the following platforms based on the Three-Tier strategy:
- **Tier 2 (Auto-Apply):** Cutshort, Instahyre, and LinkedIn (strictly 'Easy Apply' filtered).
- **Tier 1 (Scout & Draft):** YC Work at a Startup, Wellfound (AngelList), and direct ATS links (Ashby, Lever, Greenhouse).
- **Tier 3 (Background Scrape):** Arc.dev, Himalayas.app, and Remotive.

**Logic:**
1. Filter for 1-3 years experience and 'Full Stack AI Engineer' / 'MERN Developer' roles in India.
2. For **Tier 2** roles: If it matches my tech stack, APPLY immediately using the fact sheet.
3. For **Tier 1** roles: Do NOT apply yet. Add to `pending_review`, draft a cover letter, and notify me for manual review.
4. For **Tier 3** roles: Log to `seen_job_ids` and apply only if it's an exact stack match.
5. Log all new IDs to `active_application_context/background_agent_state.json`."
