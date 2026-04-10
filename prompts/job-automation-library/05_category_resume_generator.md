# Prompt: Generate Category-Specific Resumes (MD to PDF)

**Objective:** Convert markdown-based resume categories into production-ready LaTeX files and compile them to PDF.

**Prompt:**
"@job-scout Analyze the markdown files in `resumes_and_docs/categories/md/`. 
For each file:
1. Load the LaTeX template `resumes_and_docs/templates/master_resume_alt.tex`.
2. **Remove** the `\input{glyphtounicode}` and `\pdfgentounicode=1` lines (incompatible with Tectonic/XeLaTeX).
3. **Inject** the `Profile` and `Key Experience Highlights` from the MD file into the corresponding LaTeX sections.
4. Update the `Skills` section if the MD file has a specific `Tech Focus`.
5. Save the resulting LaTeX to `resumes_and_docs/categories/tex/[CATEGORY_NAME].tex`.
6. Run `tectonic resumes_and_docs/categories/tex/[CATEGORY_NAME].tex -o resumes_and_docs/categories/pdf/`.
7. Ensure each resume remains strictly **ONE PAGE**."
