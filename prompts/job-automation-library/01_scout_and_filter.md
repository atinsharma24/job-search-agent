# Prompt: Scout and Fast Filter

**Target:** High-throughput application runs across supported portals.

**Prompt:**
`@job-scout Scan supported portals for software roles in India. For each listing, extract only this packet: [{"job_title":"","company":"","required_stack":[],"application_url":""}]. Skip duplicates and obvious disqualifiers. If stack alignment is 70% or higher, select the nearest baseline resume from resumes_and_docs/categories/md/, determine changed_keywords for deterministic keyword injection, generate a template cover letter, and output one flat JSON object with job_title, company, required_stack, application_url, stack_match, resume_category, changed_keywords, action, cover_letter, log_status, and reason. Set action=apply for qualified jobs. If stack alignment is below 70%, output the same flat JSON object with action=skip and terminate.`
