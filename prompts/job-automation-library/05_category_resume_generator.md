# Prompt: Generate and Maintain Baseline Category Resumes

**Objective:** Preserve a small set of reusable baseline resumes for fast-path applications.

**Prompt:**
`@job-scout Read resumes_and_docs/categories/md/. Maintain each file as a reusable baseline. When a target job is supplied, choose the closest baseline and replace only target keywords in summary, skills, and key highlights. Do not regenerate the full resume. Do not reorder sections. Compile or export only if the requested baseline output is missing. Output flat JSON with resume_category, target_keywords, output_path, and status.`
