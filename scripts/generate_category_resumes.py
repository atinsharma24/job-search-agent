import os
import re
import subprocess

TEMPLATE_PATH = "resumes_and_docs/templates/master_resume_alt.tex"
MD_DIR = "resumes_and_docs/categories/md/"
TEX_DIR = "resumes_and_docs/categories/tex/"
PDF_DIR = "resumes_and_docs/categories/pdf/"

os.makedirs(TEX_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

with open(TEMPLATE_PATH, 'r') as f:
    template_content = f.read()

# Clean template for Tectonic
template_content = template_content.replace("\\input{glyphtounicode}", "")
template_content = template_content.replace("\\pdfgentounicode=1", "")

def latex_escape(text):
    text = text.replace('&', r'\&')
    text = text.replace('%', r'\%')
    return text

def extract_section(md_content, section_name):
    pattern = rf"\*\*{section_name}:\*\*\n(.*?)(?=\n\*\*|\Z)"
    match = re.search(pattern, md_content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def md_bullets_to_latex(bullets_text):
    # Convert "- Item" to "\resumeItem{Item}"
    lines = bullets_text.split('\n')
    latex_items = []
    for line in lines:
        line = line.strip()
        if line.startswith('- '):
            item = line[2:]
            item = latex_escape(item)
            latex_items.append("    \\resumeItem{" + item + "}")
    return "\n".join(latex_items)

for md_file in os.listdir(MD_DIR):
    if not md_file.endswith('.md'):
        continue
    
    with open(os.path.join(MD_DIR, md_file), 'r') as f:
        md_content = f.read()
    
    profile = extract_section(md_content, "Profile")
    highlights = extract_section(md_content, "Key Experience Highlights")
    tech_focus = extract_section(md_content, "Tech Focus")
    
    category_name = md_file.replace('.md', '')
    
    # 1. Update Profile Section
    p_text = latex_escape(profile)
    profile_latex = "\\section{Profile}\n\\vspace{2pt}\n\\small{" + p_text + "}\n\\vspace{-4pt}\n\\resumeItemListStart\n" + md_bullets_to_latex(highlights) + "\n\\resumeItemListEnd"
    
    # Simple split and join to avoid re.sub replacement issues
    parts = re.split(r"\\section\{Profile\}.*?(?=\\section\{Professional Experience\})", template_content, flags=re.DOTALL)
    new_tex = profile_latex.join(parts)
    
    # 2. Update Skills if tech_focus exists
    if tech_focus:
        tf_text = latex_escape(tech_focus)
        new_tex = new_tex.replace("\\textbf{Languages:}", "\\textbf{Focus Stack:}{ " + tf_text + " } \\\\ \n     \\textbf{Languages:}", 1)

    tex_file_path = os.path.join(TEX_DIR, category_name + ".tex")
    with open(tex_file_path, 'w') as f:
        f.write(new_tex)
    
    print("Compiling " + category_name + "...")
    subprocess.run(["tectonic", tex_file_path, "-o", PDF_DIR])

print("Finished generating all category resumes.")
