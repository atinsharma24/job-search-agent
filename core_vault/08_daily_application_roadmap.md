# Daily Application Roadmap

Updated: 2026-04-08

Purpose: define the exact daily workflow for sourcing, screening, tailoring, and applying to India-compatible remote software engineering roles.

## Daily Objective

- Find and apply to the highest-signal remote roles that allow working from India
- Prioritize backend, full-stack, software engineer, and founding engineer roles
- Prioritize conversational AI, document intelligence, fintech, compliance automation, and developer tooling
- Avoid wasting time on jobs that are geo-restricted to US, UK, Canada, or EU only

## Non-Negotiable Rules

- Never claim a location or work authorization not supported by the vault
- Never enter salary, notice period, or experience values that contradict `06_logistics_mapping.json` and `01_atomic_fact_sheet.json`
- Never answer behavioral or technical free-text questions from memory if the answer should come from the vault
- Skip any application that requires details not available with certainty
- Prefer direct ATS applications over crowded aggregator reposts
- Close redundant browser tabs continuously to keep the workspace manageable

## Source Priority

1. Cutshort
2. Arc
3. Ashby-hosted company boards
4. Himalayas
5. Y Combinator Work at a Startup
6. UnseenRoles
7. Remotive

## Daily Time Blocks

### Block 1 — India-Remote First Pass

Duration: 45-60 minutes

Targets:
- Cutshort
- Arc
- Himalayas

Actions:
- Open remote software engineer, backend engineer, and full-stack searches
- Filter for India-compatible remote roles first
- Open only strong-fit jobs with relevant stack overlap
- Skip internships, contract-only roles, and clearly geo-restricted roles

Output:
- 5-10 shortlisted roles

### Block 2 — Startup ATS Discovery

Duration: 30-45 minutes

Targets:
- Ashby boards
- Y Combinator Work at a Startup
- UnseenRoles

Actions:
- Search for `backend engineer`, `software engineer`, `full stack engineer`, `founding engineer`, `AI engineer`, `LLM`, and `RAG`
- Prioritize roles with India-remote eligibility or globally remote wording that does not exclude India
- Prefer direct ATS applications when possible

Output:
- 3-6 additional high-signal targets

### Block 3 — Application Execution

Duration: 60-90 minutes

Actions:
- Read the JD fully
- Check geography eligibility first
- Route resume by JD content:
  - `LLM`, `Conversational`, `RAG` -> `ResumesTailored/resume_templates/Conversational-AI.md`
  - `Compliance`, `Legal` -> `ResumesTailored/resume_templates/Legal-Tech-Compliance.md`
  - default -> `FinalResApr1.pdf`
- Map all fields from the vault
- Submit only when all answers are exact and defensible

Output:
- 5-10 completed applications on a strong day
- 2-5 completed applications on a weaker day

## Portal-by-Portal Tactics

## 1. Cutshort

Primary role searches:
- Remote software engineer
- Remote backend developer
- Remote full-stack developer

What to prioritize:
- India-based startups
- Remote-friendly NCR, Bangalore, Hyderabad roles
- Node.js, TypeScript, React, Next.js, PostgreSQL, AI integration

What to avoid:
- Service-company mass hiring with irrelevant stacks
- Contract-only roles
- Roles heavily centered on Java/.NET/PHP unless clearly adaptable and strong fit

## 2. Arc

Primary role searches:
- Software engineer
- Backend developer
- Full-stack developer

What to prioritize:
- Explicit `India` or `remote from India`
- Global remote companies with clear location eligibility
- AI, fintech, platform, and developer tooling roles

What to avoid:
- US-only or timezone-locked roles that implicitly exclude India
- Senior-only roles requiring 4+ years

## 3. Ashby Boards

Search patterns:
- `site:jobs.ashbyhq.com "India" "Remote" "Software Engineer"`
- `site:jobs.ashbyhq.com "India" "Remote" "Backend Engineer"`
- `site:jobs.ashbyhq.com "India" "Remote" "Full Stack Engineer"`
- `site:jobs.ashbyhq.com "India" "Remote" "Founding Engineer"`

What to prioritize:
- AI startups
- Fintech or compliance automation startups
- Smaller teams with product ownership

## 4. Himalayas

Use:
- Country-specific India remote filters
- Clean eligibility checking

What to prioritize:
- Explicitly India-compatible remote roles
- Software, backend, or full-stack roles with direct application paths

## 5. YC Work at a Startup

Search manually for:
- Founding engineer
- Backend engineer
- Full stack engineer
- AI engineer

What to prioritize:
- Teams with strong product ownership
- Startups where broad engineering scope is expected
- Roles where 0-day notice and startup-style execution are an advantage

## 6. UnseenRoles

Use for:
- Discovery only
- Early-signal roles before they flood mainstream boards

What to do:
- Validate each discovered role on the actual ATS or company site before applying

## 7. Remotive

Use only if accessible without account restrictions or via public job pages.

What to prioritize:
- Curated software development jobs with visible location eligibility

## Daily Screening Checklist

For each job, verify in this order:

1. Is it remote?
2. Does it explicitly allow India or avoid excluding India?
3. Is the title in-scope?
4. Is the stack reasonably aligned?
5. Is the seniority realistic for 8-9 months of experience?
6. Can every required field be answered from the vault?
7. Does the JD warrant a specific resume variant?

If any of 1, 2, 5, or 6 fails, skip immediately.

## Resume Routing Rules

### Conversational AI / RAG

Use:
- `ResumesTailored/resume_templates/Conversational-AI.md`

Trigger words:
- LLM
- RAG
- conversational
- chatbot
- WhatsApp
- AI agent
- retrieval
- vector database

### Legal / Compliance

Use:
- `ResumesTailored/resume_templates/Legal-Tech-Compliance.md`

Trigger words:
- compliance
- legal
- KYC
- identity verification
- AML
- workflow automation for regulated domains

### Default

Use:
- `FinalResApr1.pdf`

## Vault Mapping Rules

### Standard Logistics

Source:
- `06_logistics_mapping.json`
- `01_atomic_fact_sheet.json`

Use:
- Location: Agra, Uttar Pradesh, India
- Notice period: 0 days / Immediate Joiner
- Expected CTC: 15L+ (negotiable, no hard ceiling)
- Work authorization: Indian citizen, no sponsorship required for India

### Behavioral Questions

Source:
- `04_behavioral_star_stories.md`

Map:
- Conflict -> Story 1
- Ambiguity / changing priorities -> Story 2
- Failure / mistake -> Story 3
- Leadership / coordination -> Story 4
- Prioritization / trade-offs -> Story 5

### Technology Proficiency

Source:
- `05_ats_keyword_dictionary.md`

Use:
- Exact sentence for the technology asked

### Technical Deep Dives

Source:
- `03_technical_deep_dive.md`

Use for:
- RAG architecture
- WhatsApp conversational infrastructure
- LLM failover
- vector storage choices
- ingestion pipelines

## Daily Metrics To Track

- Roles screened
- Roles skipped for geo mismatch
- Roles skipped for seniority mismatch
- Roles applied
- Portal-wise conversion
- Companies worth revisiting

## End-of-Day Cleanup

1. Close redundant browser tabs
2. Keep one useful search tab per portal at most
3. Save notable companies or roles worth revisiting
4. Note recurring blockers:
- geography restrictions
- current CTC requirements
- experience-floor disqualification
- ATS fields requiring unverifiable details

## Weekly Review

At the end of each week:
- Identify which portals generated the most India-compatible responses
- Increase time spent on the top two portals
- Reduce time on portals dominated by UK/US/EU-only remote roles
- Update search strings for any domain showing traction: AI, fintech, compliance, document intelligence
