# 📄 Resume Workflow

This vault uses a **LaTeX-first** resume workflow to ensure professional-grade formatting that is also 100% machine-readable (ATS-friendly).

## 1. Templates
- **`master_resume.tex`**: Standard professional template.
- **`master_resume_alt.tex`** (`res2.tex`): Your preferred modern formatting (Jake's Resume). This is the default used by the **@job-scout**.

## 2. Automated Tailoring Logic
The **@job-scout** follows these steps when tailoring:
1.  **JD Analysis:** Identify the 3 most important keywords from the job posting.
2.  **Profile Swap:** Replace the generic `Profile` in the `.tex` file with one that emphasizes these keywords.
3.  **Bullet Swapping:** If you have more relevant projects in your `01_atomic_fact_sheet.json`, the agent will swap one of your current resume bullet points with a more relevant project experience.
4.  **One-Page Constraint:** The agent will prune words or bullet points to ensure the final PDF remains a **SINGLE PAGE**.

## 3. Compilation with Tectonic
The agent uses the following command to compile:
```bash
tectonic tailored_resume.tex -o resumes_and_docs/tailored/resumes/
```
**Important:** If the agent encounters compilation errors (e.g., related to `glyphtounicode`), it is trained to automatically remove these lines, as they are often incompatible with XeLaTeX (used by Tectonic).

## 4. Safety First
- **`LatestResume.pdf`** is your master copy. It will **never** be modified by the agent.
- All tailored resumes are saved to `resumes_and_docs/tailored/resumes/` with the filename format: `[COMPANY]_[ROLE].pdf`.
