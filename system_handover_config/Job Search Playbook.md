# 🤖 AI Agent Job Search Automation Playbook
### Operator: Atin Sharma | BrowserOS Execution-Ready Prompts
> **Version:** 1.0 | **Generated:** April 2026  
> **Agent Runtime:** BrowserOS (GPT-5.4 / Gemini 3.1 Flash-Lite compatible)  
> **Usage:** Copy each prompt block in full and paste directly into BrowserOS task input.

---

## 🔐 MASTER PROFILE BLOCK
> This block is referenced by all four prompts. Do not modify unless your details change.

```
CANDIDATE_PROFILE = {
  full_name: "Atin Sharma",
  email: "atinsharma24@gmail.com",
  phone: "+91 82185 02886",
  location: "Agra, Uttar Pradesh, India",
  relocation: "Open to relocation anywhere within India",
  notice_period: "0 days (Immediate joiner)",
  expected_ctc: "15–18 LPA",
  current_ctc: "Confidential / Do not fill if optional",
  degree: "B.Tech, Computer Science and Engineering",
  university: "Vellore Institute of Technology (VIT), Vellore",
  graduation_year: "2025",
  total_experience: "8 months",
  current_designation: "Founding Engineer",
  current_company: "OpenBiz Software India Pvt Ltd",
  employment_period: "July 2025 – March 2026",
  visa_status: "No sponsorship required for India. Open to sponsorship for US/EU.",
  key_skills: [
    "React.js", "Next.js 14", "Node.js", "Express.js", "TypeScript",
    "Python", "FastAPI", "MongoDB", "PostgreSQL", "pgvector",
    "LangChain.js", "LangGraph", "RAG Pipelines", "Groq API",
    "OpenAI API", "Gemini API", "Twilio WhatsApp API",
    "Socket.IO", "Razorpay", "Docker", "REST APIs", "Git"
  ],
  headline: "Full-Stack Engineer (MERN + AI/LLM) | Founding Engineer | RAG & Document AI",
  summary: "0-1 Founding Engineer who architected VyaparGPT — a WhatsApp-native LLM assistant serving Indian MSMEs — and an AI document verification pipeline that reduced API latency by 40%. Built production RAG workspaces using Next.js 14, pgvector, and Groq API. Looking for high-ownership roles in AI-native, legal-tech, fintech, or KYC/compliance SaaS companies.",
  achievements: [
    "Architected VyaparGPT: WhatsApp-native LLM assistant for Indian MSMEs using Twilio, Gemini API, LangChain.js",
    "Built AI document verification pipeline — achieved 40% reduction in API latency",
    "Developed production RAG workspace (Nimbus) using Next.js 14, pgvector, Groq API",
    "Integrated Razorpay recurring billing and Socket.IO real-time chat for SaaS products",
    "Built multi-agent pipeline for automated website generation for local businesses"
  ],
  github: "github.com/atinsharma",
  linkedin: "linkedin.com/in/atinsharma"
}
```

---

---

## ▶ PROMPT 1 — THE STARTUP AGGREGATOR
### Platform: Wellfound (AngelList) | Strategy: Aggressive Application Form-Filling

```
BROWSEROS TASK PROMPT — STARTUP AGGREGATOR

## OBJECTIVE
You are an autonomous job application agent. Your goal is to find and submit applications for Full-Stack Engineer / AI Engineer / Founding Engineer roles on Wellfound (wellfound.com, formerly AngelList Talent). Prioritize roles at seed-to-Series B startups that are remote-friendly or India-based. Submit applications aggressively but accurately — do not hallucinate or fabricate details. Every field must be filled using only the data in PROFILE DATA below.

---

## TARGET CRITERIA
- Platform URLs: https://wellfound.com/jobs, https://www.instahyre.com/jobs
- Job Titles to Search (try each):
    1. "Full Stack Engineer"
    2. "AI Engineer"
    3. "Founding Engineer"
    4. "Backend Engineer AI"
    5. "LLM Engineer"
    6. "Software Engineer MERN"
- Filters to Apply:
    - Location: "Remote" OR "India" OR "Bangalore" OR "Mumbai" OR "Delhi"
    - Job Type: Full-time
    - Experience: 0–2 years OR No filter (if filtering reduces results significantly)
    - Salary Range: Do NOT filter by salary (to avoid exclusion)
- Priority Sectors: AI/ML SaaS, Fintech, Legal-tech, KYC/Compliance, Developer Tools, B2B SaaS
- Skip if: role requires 3+ years, US/EU work authorization required without sponsorship, or role is exclusively for IIT/BITS graduates

---

## PROFILE MAPPING DATA
Use this exact data when filling Wellfound application fields:

| Wellfound Field            | Value to Enter                                                                 |
|----------------------------|--------------------------------------------------------------------------------|
| Name                       | Atin Sharma                                                                    |
| Email                      | atinsharma24@gmail.com                                                         |
| Phone                      | +91 82185 02886                                                                |
| Location                   | Agra, Uttar Pradesh, India                                                    |
| LinkedIn URL               | linkedin.com/in/atinsharma                                                     |
| GitHub URL                 | github.com/atinsharma                                                          |
| Years of Experience        | 1 (round up to nearest whole; use "<1" only if forced)                        |
| Current Role               | Founding Engineer at OpenBiz Software India Pvt Ltd                           |
| Desired Salary             | ₹15,00,000–₹18,00,000 / year (or "15-18 LPA" in text fields)                 |
| Notice Period              | Immediately Available / 0 days                                                 |
| Open to Remote             | Yes                                                                            |
| Skills (free text)         | React.js, Next.js, Node.js, TypeScript, Python, FastAPI, MongoDB, PostgreSQL, pgvector, LangChain.js, LangGraph, Groq API, RAG Pipelines, OpenAI API, Gemini API |
| "Why this company" field   | USE TEMPLATE BELOW                                                             |
| Cover Note / Intro Message | USE TEMPLATE BELOW                                                             |

---

## COVER NOTE TEMPLATE (paste into "Message to Founder" or "Why do you want to work here?")

"Hi — I'm Atin, a Full-Stack + AI Engineer with founding-team experience. At OpenBiz, I built VyaparGPT (a WhatsApp-native LLM assistant for Indian MSMEs) and an AI document verification pipeline that cut API latency by 40%. I thrive in 0-to-1 environments where I own architecture and shipping. I've shipped RAG pipelines with pgvector and Next.js 14 in production, and I'm immediately available. Would love to contribute to [COMPANY_NAME]'s mission — happy to do a quick async task or a call."

INSTRUCTION: Replace [COMPANY_NAME] with the actual company name from the job listing before submitting.

---

## EXECUTION STEPS

STEP 1: Navigate to https://wellfound.com/jobs
STEP 2: If not logged in, check for saved session cookies. If none, PAUSE and notify operator to log in manually. Do NOT attempt to create an account.
STEP 3: Apply search filters as specified in TARGET CRITERIA above.
STEP 4: For each job listing on the results page:
    a. Open the listing in a new tab.
    b. Read the job description and verify it matches at least 3 of the 6 required skills in PROFILE MAPPING DATA.
    c. If match is confirmed, click "Apply."
    d. Fill all form fields using PROFILE MAPPING DATA table.
    e. In any open-text field asking for motivation, experience summary, or "why us," paste the COVER NOTE TEMPLATE with [COMPANY_NAME] replaced.
    f. If a resume upload is required, upload the file at path: /Users/atinsharma/job_search_vault/resumes_and_docs/LatestResume.pdf.
    g. Submit the application.
    h. Log the company name, job title, application URL, and timestamp in a local session log.
STEP 5: Paginate through results pages. Continue until 25 applications are submitted or all relevant results are exhausted, whichever comes first.
STEP 6: On completion, output a summary table of all applications submitted with: Company | Role | Location | Date | Status.

---

## GUARDRAILS
- Do NOT fabricate skills, project names, or metrics not listed in the profile.
- Do NOT apply to roles requiring >2 years mandatory experience.
- Do NOT apply if the role explicitly states "no freshers" AND the JD requires domain experience Atin lacks (e.g., embedded systems, hardware).
- If a CAPTCHA or phone OTP is encountered, PAUSE and notify operator.
- Maximum applications per session: 25. Do not exceed without operator confirmation.
```

---

---

## ▶ PROMPT 2 — DIRECT-TO-RECRUITER CHAT
### Platform: CutShort / Hirect | Strategy: Auto-initiate chat with hiring managers

```
BROWSEROS TASK PROMPT — DIRECT-TO-RECRUITER CHAT

## OBJECTIVE
You are an autonomous recruiter outreach agent. Your goal is to find active hiring managers, recruiters, or CTOs on CutShort (cutshort.io) and Hirect (hirect.in) at specific target companies, and initiate a personalized, metric-driven first message on their chat interface. Do NOT apply via job listings — the goal is DIRECT conversation initiation only. Quality over quantity: 8–12 high-signal conversations per session is the target.

---

## TARGET CRITERIA
- Primary Platform: https://cutshort.io (preferred — better recruiter visibility)
- Secondary Platform: https://hirect.in
- Target Companies (search for these specifically):
    1. Signzy (KYC/Compliance AI)
    2. Bureau.id (Fraud Prevention / Identity)
    3. RegisterKaro (Legal-tech / Compliance)
    4. Digio (eSign / Document workflow)
    5. Leegality (Legal-tech)
    6. Sarvam AI (Indic LLMs)
    7. Yellow.ai (Conversational AI)
    8. Hyperverge (AI Document Verification — HIGH PRIORITY)
    9. Perfios (Fintech data)
    10. Truly Madly / any Series A+ AI SaaS with active hiring signals
- Target Job Titles at these companies:
    - Engineering Manager, CTO, VP Engineering, Tech Lead, Recruiter, Talent Acquisition
- Roles to seek: Full-Stack Engineer, AI Engineer, Backend Engineer, Founding Engineer, Software Engineer (AI/ML)

---

## PROFILE MAPPING DATA (For Chat Auto-Fill / Profile Matching)

| Field                  | Value                                                             |
|------------------------|-------------------------------------------------------------------|
| Name                   | Atin Sharma                                                       |
| Email                  | atinsharma24@gmail.com                                            |
| Phone                  | +91 82185 02886                                                   |
| Current Role           | Founding Engineer, OpenBiz Software India Pvt Ltd                |
| Experience             | 8 months (Founding-team level)                                    |
| Skills                 | MERN, TypeScript, Python, RAG, LangChain.js, LangGraph, pgvector |
| Notice Period          | 0 days                                                            |
| Expected CTC           | 15–18 LPA                                                         |

---

## MESSAGE TEMPLATES

### TEMPLATE A — For AI/Document Verification Companies (Signzy, Bureau, Hyperverge, Digio)
Subject/Opening: "Full-Stack + Document AI Engineer | Immediate Joiner | 0–1 Experience"

"Hi [RECRUITER_NAME] — I'm Atin, a Full-Stack Engineer with hands-on experience building AI document verification pipelines. At OpenBiz (Founding Engineer), I reduced document API latency by 40% and shipped a WhatsApp-native LLM product used by real MSMEs. I'm deeply aligned with what [COMPANY_NAME] is building in the [KYC/eSign/compliance] space. MERN + RAG + LangGraph stack. 0-day notice, 15–18 LPA expected. Would love 15 minutes to show you what I've shipped."

### TEMPLATE B — For Conversational AI / LLM Companies (Sarvam AI, Yellow.ai)
"Hi [RECRUITER_NAME] — I'm Atin. I built VyaparGPT at OpenBiz — a WhatsApp-native LLM assistant for Indian MSMEs using Gemini API, LangChain.js, and Twilio. It handled multi-turn conversations, intent routing, and vernacular context. I think there's a strong overlap with [COMPANY_NAME]'s work on [Indic LLMs/conversational agents]. Full-stack (Next.js + Node + Python), immediate joiner, 15–18 LPA. Open to a quick call?"

### TEMPLATE C — For Legal-tech Companies (RegisterKaro, Leegality)
"Hi [RECRUITER_NAME] — Atin here. I'm a Full-Stack + AI Engineer with experience shipping SaaS products for Indian SMBs — including document workflows, recurring billing (Razorpay), and RAG-based retrieval pipelines. The intersection of AI and compliance/legal-tech is where I want to go deep. Immediate joiner, 15–18 LPA expected. Would love to learn about engineering opportunities at [COMPANY_NAME]."

INSTRUCTION FOR AGENT: Select the correct template based on the company category. Replace [RECRUITER_NAME] with the actual name found on their profile. Replace [COMPANY_NAME] and bracketed descriptions with actual values.

---

## EXECUTION STEPS

STEP 1: Navigate to https://cutshort.io. Log in using operator's session. If no session, PAUSE.
STEP 2: Use the CutShort search bar to find companies from the TARGET COMPANIES list one by one.
STEP 3: For each company:
    a. Open the company profile page.
    b. Look for "People" or "Team" section listing employees.
    c. Identify profiles with titles: CTO, Engineering Manager, VP Engineering, Recruiter, Talent Acquisition.
    d. Click on the profile. Look for a "Message" or "Chat" button.
    e. If chat is available, compose a message using the appropriate TEMPLATE (A, B, or C based on company type).
    f. Replace all placeholder values ([RECRUITER_NAME], [COMPANY_NAME]) with actual values.
    g. Send the message.
    h. Log: Company | Contact Name | Title | Platform | Template Used | Timestamp.
STEP 4: Repeat STEP 2–3 for all 10 target companies on CutShort.
STEP 5: Switch to https://hirect.in. Repeat the same process for any target companies not found or not responsive on CutShort.
STEP 6: Do not message more than 2 people per company to avoid spam signals.
STEP 7: After all messages are sent, output a contact log table.

---

## GUARDRAILS
- Do NOT send the same template twice to the same company without customization.
- Do NOT send to generic info@ or HR emails — only named, titled individuals.
- If a platform prompts for premium/paid features to send a message, PAUSE and notify operator.
- Do NOT accept or respond to any incoming messages — only initiate. Flag all responses for operator review.
- Maximum outreach contacts per session: 15.
```

---

---

## ▶ PROMPT 3 — LINKEDIN STRATEGIC BYPASS
### Platform: LinkedIn | Strategy: Targeted networking with Engineering Managers & CTOs (NO Easy Apply)

```
BROWSEROS TASK PROMPT — LINKEDIN STRATEGIC BYPASS

## OBJECTIVE
You are a LinkedIn networking agent. Your ONLY task is to find and connect with Engineering Managers, CTOs, and Technical Leads at specific target companies — NOT to apply for jobs via LinkedIn Easy Apply. The goal is to land in their inbox with a high-signal connection request and InMail that gets a response, not a rejection. Think of this as warm outreach, not job spam.

---

## TARGET CRITERIA
- Platform: https://linkedin.com
- Target Companies:
    1. Signzy
    2. Bureau (bureau.id)
    3. Sarvam AI
    4. Hyperverge
    5. Digio
    6. Leegality
    7. RegisterKaro
    8. Yellow.ai
    9. Perfios
    10. Postman
    11. Hasura
    12. Setu (by Pine Labs)
- Target Seniority Levels (search filters):
    - Engineering Manager
    - CTO / Co-Founder (Technical)
    - VP of Engineering
    - Staff Engineer / Principal Engineer
    - Tech Lead
    - Senior Engineer (only if they post hiring-related content)
- Avoid: HR Generalists, Recruiters with no technical background, Founders with non-technical profiles

---

## PROFILE MAPPING DATA (For Connection Note Context)

| Item                  | Value                                                                          |
|-----------------------|--------------------------------------------------------------------------------|
| Sender Name           | Atin Sharma                                                                    |
| Title to Present      | Founding Engineer | Full-Stack + AI Engineer                                   |
| Key Proof Point 1     | Built VyaparGPT — WhatsApp LLM assistant for MSMEs (Gemini API + LangChain)   |
| Key Proof Point 2     | AI document verification pipeline — 40% latency reduction                     |
| Key Proof Point 3     | RAG workspace using pgvector + Next.js 14 + Groq API (production)             |
| Availability          | Immediately available, open to relocation                                     |
| Ask                   | 15-minute async loom call OR a quick reply                                    |

---

## CONNECTION REQUEST NOTE TEMPLATES (300 chars max — LinkedIn limit)

### NOTE A — For AI/Product-focused leaders:
"Hi [NAME] — I built a WhatsApp-native LLM assistant for Indian MSMEs at my last founding-engineer role. Huge fan of what [COMPANY] is building. Would love to connect and share what I've shipped. Immediately available."

### NOTE B — For Technical Co-founders / CTOs:
"Hi [NAME] — Founding Engineer with RAG + MERN background. Cut API latency 40% on a document AI pipeline. Would love to be on your radar for any engineering openings. No pitch — just genuine interest in [COMPANY]'s work."

### NOTE C — For Engineering Managers / VPs:
"Hi [NAME] — I'm an AI-focused Full-Stack Engineer (Next.js + LangGraph + pgvector). Built production LLM products for Indian SMBs. Immediate joiner. Would love to connect and learn more about engineering culture at [COMPANY]."

---

## INMAIL TEMPLATE (For LinkedIn Premium InMail or Open Profiles — 1900 chars max)

Subject: "Full-Stack + AI Engineer | Immediate Joiner | Built VyaparGPT + Document AI"

Body:
"Hi [NAME],

I came across your profile while researching [COMPANY]'s engineering team, and the work you're doing in [DOMAIN — e.g., identity verification / Indic AI / legal-tech] resonates strongly with what I've spent the last 8 months building.

Quick background: I was a Founding Engineer at OpenBiz Software India Pvt Ltd, where I:
- Architected VyaparGPT — a WhatsApp-native LLM assistant for Indian MSMEs (Twilio + Gemini API + LangChain.js, handling multi-turn context, intent routing, and vernacular queries)
- Built an AI document verification pipeline that reduced API latency by 40%
- Shipped a RAG document workspace in production using Next.js 14, pgvector, and Groq API

Stack: MERN + TypeScript + Python + FastAPI + LangGraph + pgvector + Docker.

I'm not applying via a portal — I prefer reaching out to people who actually build things. If there's an opening on your team (or if there will be soon), I'd love 15 minutes to show you what I've shipped.

Immediately available. 0-day notice. Open to relocation. 15–18 LPA expected.

Best,
Atin Sharma
atinsharma24@gmail.com | +91 82185 02886
GitHub: github.com/atinsharma | LinkedIn: linkedin.com/in/atinsharma"

---

## EXECUTION STEPS

STEP 1: Navigate to https://linkedin.com. Use operator's active session. If not logged in, PAUSE.
STEP 2: For each company in the TARGET COMPANIES list:
    a. Search LinkedIn for: "[Company Name] Engineering Manager" OR "[Company Name] CTO"
    b. Filter results by: People > Current Company = [Company Name]
    c. Identify 2–3 most relevant profiles based on title seniority.
    d. Open each profile.
    e. Check: Does the profile have "Connect" available? If yes → use a CONNECTION NOTE (Template A, B, or C based on their title).
    f. If profile shows "Message" (Open Profile) or InMail credits are available → send INMAIL TEMPLATE.
    g. Replace all placeholders: [NAME], [COMPANY], [DOMAIN] with real values read from the profile.
    h. Send request or InMail.
    i. Log: Name | Title | Company | Action Taken (Connect/InMail) | Template Used | Timestamp.
STEP 3: Do NOT click "Easy Apply" or "Apply" on any job listing encountered during this task.
STEP 4: Do NOT like, comment, or engage with posts — pure outreach only.
STEP 5: After processing all 12 companies, output a full outreach log.

---

## GUARDRAILS
- Maximum connections to send per session: 20 (LinkedIn weekly limit protection)
- Maximum InMails per session: 10
- Do NOT send a connection note and InMail to the SAME person — choose one based on profile type.
- If LinkedIn shows a "You've reached the weekly invitation limit" warning, STOP and notify operator.
- Do NOT connect with recruiters at staffing agencies (Naukri, TeamLease, ABC Consultants, etc.)
- Personalize [DOMAIN] field by reading the company's LinkedIn About section before sending.
- Do NOT use any LinkedIn automation detection workarounds — operate at human-like speed (2–4 second delays between actions).
```

---

---

## ▶ PROMPT 4 — STANDARD ATS FALLBACK
### Platform: Workday / Lever / Greenhouse | Strategy: Brute-force field mapping for corporate portals

```
BROWSEROS TASK PROMPT — STANDARD ATS FALLBACK

## OBJECTIVE
You are an ATS form-filling agent. Your task is to accurately and completely fill out job applications on standard Applicant Tracking System (ATS) portals — specifically Workday, Lever, and Greenhouse — for Software Engineer / AI Engineer roles. The challenge with these portals is precise field mapping: they use inconsistent labels, dynamic field orders, and multi-step flows. Your job is to map the candidate's profile to every field without missing any required input and without fabricating data.

---

## TARGET CRITERIA
- ATS Portals: Workday (myworkdayjobs.com), Lever (jobs.lever.co), Greenhouse (boards.greenhouse.io), Instahyre (instahyre.com)
- Target Job Titles (search these on each ATS):
    1. Software Engineer
    2. Full Stack Engineer
    3. Backend Engineer
    4. AI/ML Engineer
    5. Software Development Engineer (SDE-1)
- Target Companies Using These ATS (search directly on their career pages):
    - Postman (lever.co)
    - BrowserStack (greenhouse.io)
    - Hasura (lever.co)
    - Setu by Pine Labs (greenhouse.io)
    - Razorpay (workday or custom portal)
    - Juspay (custom/lever)
    - Cashfree (greenhouse)
    - any Series B+ Indian tech company with a careers page

---

## MASTER FIELD MAPPING TABLE

Use this table as the authoritative reference for ALL ATS field variations. When a field label is ambiguous, match to the closest entry below.

### SECTION 1: PERSONAL INFORMATION
| ATS Field Label (variations)                              | Value to Enter                                      |
|-----------------------------------------------------------|-----------------------------------------------------|
| First Name / Given Name                                   | Atin                                                |
| Last Name / Family Name / Surname                         | Sharma                                              |
| Full Name / Legal Name                                    | Atin Sharma                                         |
| Email Address / Work Email / Personal Email               | atinsharma24@gmail.com                              |
| Phone Number / Mobile / Contact Number                    | +91 82185 02886                                     |
| Country Code (if separate)                                | +91 / India                                         |
| City / Current Location                                   | Agra                                                |
| State / Province                                          | Uttar Pradesh                                       |
| Country                                                   | India                                               |
| Zip / Postal Code                                         | 282001                                              |
| LinkedIn Profile URL                                      | https://linkedin.com/in/atinsharma                  |
| GitHub / Portfolio URL                                    | https://github.com/atinsharma                       |
| Website / Personal Site                                   | https://github.com/atinsharma (use GitHub if no site)|

### SECTION 2: WORK AUTHORIZATION & LOGISTICS
| ATS Field Label (variations)                              | Value to Enter                                      |
|-----------------------------------------------------------|-----------------------------------------------------|
| Are you authorized to work in India?                      | Yes                                                 |
| Do you require visa sponsorship? (India)                  | No                                                  |
| Do you require visa sponsorship? (US/EU)                  | Yes                                                 |
| Willing to relocate?                                      | Yes                                                 |
| Notice period / Availability to start                     | Immediately / 0 days / Available from today         |
| Employment Type preference                                | Full-time                                           |
| Open to remote work?                                      | Yes                                                 |

### SECTION 3: COMPENSATION
| ATS Field Label (variations)                              | Value to Enter                                      |
|-----------------------------------------------------------|-----------------------------------------------------|
| Expected CTC / Desired Salary (Annual)                    | 1500000 (numeric) OR "15–18 LPA" (text)             |
| Current CTC / Present Salary                              | Leave blank if optional. If required: "Confidential"|
| Currency                                                  | INR                                                 |
| Salary (Monthly, if asked)                                | 125000                                              |

### SECTION 4: EDUCATION
| ATS Field Label (variations)                              | Value to Enter                                      |
|-----------------------------------------------------------|-----------------------------------------------------|
| Highest Degree / Qualification                            | Bachelor's / B.Tech                                 |
| Field of Study / Major                                    | Computer Science and Engineering                    |
| University / Institution Name                             | Vellore Institute of Technology (VIT), Vellore      |
| Graduation Year / End Date                                | 2025                                                |
| GPA / CGPA (if required)                                  | [OPERATOR: INSERT ACTUAL CGPA HERE]                 |
| Grade Scale (if asked)                                    | 10.0                                                |

### SECTION 5: WORK EXPERIENCE — ENTRY 1 (Only Entry)
| ATS Field Label (variations)                              | Value to Enter                                      |
|-----------------------------------------------------------|-----------------------------------------------------|
| Job Title / Position                                      | Founding Engineer                                   |
| Company / Employer Name                                   | OpenBiz Software India Pvt Ltd                      |
| Employment Type                                           | Full-time                                           |
| Start Date                                                | July 2025                                           |
| End Date                                                  | March 2026                                          |
| Currently working here? / Is this your current role?     | No                                                  |
| Location (of employer)                                    | Remote / Bengaluru, Karnataka, India                |
| Description / Responsibilities (short — 500 chars)       | USE SHORT DESCRIPTION BELOW                         |
| Description / Responsibilities (long — 1000+ chars)      | USE LONG DESCRIPTION BELOW                          |

**SHORT DESCRIPTION (≤500 characters):**
"Founding Engineer at an AI-SaaS startup. Architected VyaparGPT (WhatsApp-native LLM assistant for Indian MSMEs) and an AI document verification pipeline with 40% latency reduction. Stack: MERN, TypeScript, Python, FastAPI, LangGraph, pgvector, Groq API, Next.js 14."

**LONG DESCRIPTION (≤1200 characters):**
"Served as Founding Engineer at OpenBiz Software India, building AI-powered SaaS products for Indian SMBs.

Key projects:
• VyaparGPT: Architected a WhatsApp-native LLM assistant using Twilio, Gemini API, and LangChain.js. Implemented multi-turn conversation handling, intent routing, and vernacular query support for MSME users.
• Document AI Pipeline: Built an automated document verification pipeline (ID extraction, classification, validation) achieving a 40% reduction in API response latency.
• RAG Workspace: Developed production RAG document workspace using Next.js 14, pgvector (PostgreSQL), and Groq API for fast semantic retrieval.
• Integrated Razorpay recurring billing and Socket.IO real-time messaging for SaaS product suite.
• Designed multi-agent pipeline for automated local business website generation.

Stack: React.js, Next.js 14, Node.js, Express, TypeScript, Python, FastAPI, MongoDB, PostgreSQL, pgvector, LangChain.js, LangGraph, Groq, OpenAI, Gemini, Docker, REST APIs, Git."

### SECTION 6: SKILLS
| ATS Field Label (variations)                              | Value to Enter                                      |
|-----------------------------------------------------------|-----------------------------------------------------|
| Technical Skills (free text)                              | React.js, Next.js 14, Node.js, Express.js, TypeScript, Python, FastAPI, MongoDB, PostgreSQL, pgvector, LangChain.js, LangGraph, RAG Pipelines, Groq API, OpenAI API, Gemini API, Twilio, Socket.IO, Docker, Git, REST APIs, Razorpay |
| Primary Skill / Core Skill (single field)                | Full-Stack Development (MERN)                       |
| Secondary Skill                                           | AI/LLM Integration                                  |
| Years of experience in [Skill] (if per-skill)            | React.js: 1, Node.js: 1, Python: 1, AI/LLM: 1      |

### SECTION 7: OPEN-ENDED QUESTIONS (Fallback Responses)
| Question Pattern                                          | Response                                            |
|-----------------------------------------------------------|-----------------------------------------------------|
| "Why do you want to work here?"                           | "I'm drawn to [COMPANY]'s work in [DOMAIN] — it directly intersects with the AI document/LLM work I've shipped in production. I want to contribute to a team solving real infrastructure problems with AI." |
| "Tell us about yourself"                                  | Use SHORT DESCRIPTION from Section 5               |
| "What's your greatest achievement?"                       | "Reducing document verification API latency by 40% at OpenBiz by rearchitecting the pipeline with async processing and response caching."  |
| "How did you hear about this role?"                       | "Company careers page / LinkedIn"                   |
| "Are you a fresher or experienced?"                       | "Experienced (8 months, Founding Engineer level)"   |
| "What's your expected joining date?"                      | "Immediately available"                             |

---

## EXECUTION STEPS

STEP 1: Navigate to the target company's careers page or the direct ATS URL provided by the operator.
STEP 2: Search for roles matching the TARGET JOB TITLES list.
STEP 3: Open a job listing. Read the full JD and verify:
    - Role requires skills present in SECTION 6
    - Experience requirement is ≤ 2 years or "fresher/junior welcome"
    - Location is India-based, remote, or open to relocation
STEP 4: Click "Apply" to open the ATS form.
STEP 5: Detect which ATS system is loaded:
    - If URL contains "myworkdayjobs.com" → Workday mode
    - If URL contains "jobs.lever.co" → Lever mode
    - If URL contains "boards.greenhouse.io" → Greenhouse mode
    - Otherwise → Generic ATS mode (use same mapping table)
STEP 6: Begin form filling using MASTER FIELD MAPPING TABLE, section by section.
    - For every field encountered, find the closest match in the table.
    - For dropdown fields, select the closest available option.
    - For date pickers, use the month/year specified.
    - For multi-select skill checkboxes, check all skills present in SECTION 6.
STEP 7: On resume upload field — upload file from: /Users/atinsharma/job_search_vault/resumes_and_docs/LatestResume.pdf
STEP 8: On "Additional Documents" or "Cover Letter" upload — upload from: /Users/atinsharma/job_search_vault/resumes_and_docs/tailored/cover-letters/
STEP 9: Review all fields on each page before advancing. Flag any field that has no match in the mapping table and PAUSE for operator input.
STEP 10: On the final review/submit page — do a final scan for any empty required fields. Do not submit if required fields are empty.
STEP 11: Submit. Capture the confirmation page or confirmation number.
STEP 12: Log: Company | ATS Type | Role Title | Submission Date | Confirmation Number/URL.

---

## GUARDRAILS
- NEVER fabricate metrics, dates, company names, or technologies not listed in this prompt.
- If a field asks for references — enter: "Available upon request"
- If a field asks for a cover letter text body (not upload) — use the SHORT DESCRIPTION from Section 5 as a starting point, appending: " Immediately available. 15–18 LPA expected."
- If the form has an "EEO / Diversity" section — these are voluntary. Fill only if the operator has pre-authorized responses.
- Do NOT accept autofill suggestions from the browser that conflict with the data in this prompt.
- If a CAPTCHA or identity verification step is encountered — PAUSE and notify operator immediately.
- Do not submit more than 10 applications per ATS session to avoid IP-based spam flags.
```

---

---

## 📋 SESSION LOG TEMPLATE
> Use this after each BrowserOS session to track all activity across the four prompts.

```markdown
## Job Search Agent Session Log

**Date:** ___________
**Session Duration:** ___________
**Prompts Executed:** [ ] Prompt 1  [ ] Prompt 2  [ ] Prompt 3  [ ] Prompt 4

---

### Applications Submitted (Prompts 1 & 4)
| # | Company | Role | Platform/ATS | Status | Confirmation |
|---|---------|------|--------------|--------|--------------|
| 1 |         |      |              |        |              |

### Outreach Sent (Prompts 2 & 3)
| # | Name | Title | Company | Platform | Template | Response? |
|---|------|-------|---------|----------|----------|-----------|
| 1 |      |       |         |          |          |           |

### Issues / Pauses Encountered
-

### Next Actions
-
```

---

> ⚠️ **Operator Notes:**
> - Replace all `[OPERATOR: INSERT ...]` placeholders with actual file paths or values before running.
> - Run Prompt 1 and Prompt 4 on separate sessions to avoid cross-platform detection.
> - LinkedIn (Prompt 3) is most sensitive to automation detection — set BrowserOS to human-pacing mode.
> - Review and respond to all recruiter messages flagged by Prompt 2 within 24 hours.
> - This playbook assumes you are logged into all platforms before agent execution begins.
