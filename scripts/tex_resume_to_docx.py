#!/usr/bin/env python3
"""
Build .docx resumes from the LaTeX sources so Word output never drifts from the PDFs.

The category .tex files use the Jake's Resume macro set (\\resumeSubheading,
\\resumeItem, ...). Pandoc cannot expand those, so this script lowers the macros to
Markdown first, then shells out to pandoc for the .docx.

Usage:
    python3 scripts/tex_resume_to_docx.py                 # all four categories
    python3 scripts/tex_resume_to_docx.py GenAI_Prompt_Engineer [...]

Source of truth: resumes_and_docs/categories/tex/<name>.tex
Output:          resumes_and_docs/categories/docx/<name>.docx
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEX_DIR = ROOT / "resumes_and_docs" / "categories" / "tex"
DOCX_DIR = ROOT / "resumes_and_docs" / "categories" / "docx"
DEFAULT = ["AI_Integrated_FullStack", "Backend_AI_Specialist",
           "Cloud_Native_FullStack", "GenAI_Prompt_Engineer"]

# Literal LaTeX -> plain text. Applied after macro lowering.
LITERALS = [
    (r"$\rightarrow$", "→"), (r"$\leftarrow$", "←"), (r"$|$", "|"),
    (r"$< 0.4$", "< 0.4"), (r"\&", "&"), (r"\%", "%"), (r"\$", "$"),
    (r"\#", "#"), (r"\_", "_"), ("---", "—"), ("--", "–"),
    ("``", '"'), ("''", '"'), (r"\ldots", "…"),
]


def strip_braces(s):
    """Drop one balanced outer {...} pair if it wraps the whole string."""
    s = s.strip()
    if s.startswith("{") and s.endswith("}"):
        depth = 0
        for i, c in enumerate(s):
            depth += (c == "{") - (c == "}")
            if depth == 0 and i < len(s) - 1:
                return s
        return s[1:-1].strip()
    return s


def split_args(s, n):
    """Read n consecutive brace groups off the front of s. Returns (args, rest)."""
    args, i = [], 0
    for _ in range(n):
        while i < len(s) and s[i] != "{":
            i += 1
        if i >= len(s):
            args.append("")
            continue
        depth, start = 0, i
        while i < len(s):
            depth += (s[i] == "{") - (s[i] == "}")
            i += 1
            if depth == 0:
                break
        args.append(s[start + 1:i - 1])
    return args, s[i:]


def inline(s):
    """Lower inline LaTeX markup to Markdown."""
    s = re.sub(r"\\href\{([^}]*)\}\{(.*?)\}", r"[\2](\1)", s)
    for cmd, wrap in (("textbf", "**"), ("textit", "*"), ("emph", "*"), ("texttt", "`")):
        # innermost-first so nested calls resolve
        while True:
            s2 = re.sub(r"\\%s\{([^{}]*)\}" % cmd, wrap + r"\1" + wrap, s)
            if s2 == s:
                break
            s = s2
    s = re.sub(r"\\(vspace|hspace)\{[^}]*\}", "", s)
    s = re.sub(r"\\(small|large|Huge|scshape|raggedright|bfseries|item)\b", "", s)
    s = s.replace("\\\\", " ").replace("\\,", " ")
    for a, b in LITERALS:
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip(" {}").strip()


def convert(tex):
    body = tex.split(r"\begin{document}", 1)[1].split(r"\end{document}", 1)[0]
    body = re.sub(r"(?m)^\s*%.*$", "", body)          # comment lines
    out, i = [], 0
    while i < len(body):
        m = re.compile(
            r"\\(section|resumeSubheading|resumeProjectHeading|resumeItem)\b"
        ).search(body, i)
        if not m:
            break
        cmd, rest = m.group(1), body[m.end():]
        if cmd == "section":
            (a,), rest2 = split_args(rest, 1)
            out.append(f"\n## {inline(a).upper()}\n")
        elif cmd == "resumeSubheading":
            (a, b, c, d), rest2 = split_args(rest, 4)
            out.append(f"\n**{inline(a)}** — {inline(b)}  \n*{inline(c)}* — *{inline(d)}*\n")
        elif cmd == "resumeProjectHeading":
            (a, b), rest2 = split_args(rest, 2)
            head, tail = inline(a), inline(b)
            out.append(f"\n**{head}**" + (f" — {tail}" if tail else "") + "\n")
        else:  # resumeItem
            (a,), rest2 = split_args(rest, 1)
            txt = inline(a)
            if txt:
                out.append(f"- {txt}")
        i = len(body) - len(rest2)

    # Header: name + the two contact lines from the \begin{center} block.
    md = ["# ATIN SHARMA", ""]
    cen = re.search(r"\\begin\{center\}(.*?)\\end\{center\}", body, re.S)
    if cen:
        for line in cen.group(1).split(r"\\"):
            t = inline(line)
            if t and "ATIN SHARMA" not in t.upper():
                md.append(t + "  ")
    # Profile paragraph sits between \section{Profile} and the next \section.
    prof = re.search(r"\\section\{Profile\}(.*?)(?=\\section)", body, re.S)
    if prof:
        p = re.sub(r"\\vspace\{[^}]*\}", "", prof.group(1))
        p = re.sub(r"\\small\s*\{(.*)\}", r"\1", p.strip(), flags=re.S)
        md += ["", "## PROFILE", "", inline(p)]
    md += [l for l in out if not l.startswith("\n## PROFILE")]
    return "\n".join(md) + "\n"


def main():
    names = sys.argv[1:] or DEFAULT
    DOCX_DIR.mkdir(parents=True, exist_ok=True)
    rc = 0
    for name in names:
        src = TEX_DIR / f"{name}.tex"
        if not src.exists():
            print(f"!! missing {src}")
            rc = 1
            continue
        md = convert(src.read_text(encoding="utf-8"))
        dst = DOCX_DIR / f"{name}.docx"
        r = subprocess.run(["pandoc", "-f", "markdown", "-t", "docx", "-o", str(dst)],
                           input=md, text=True, capture_output=True)
        if r.returncode:
            print(f"!! pandoc failed for {name}: {r.stderr.strip()}")
            rc = 1
        else:
            print(f"built {dst.relative_to(ROOT)}  ({len(md)} chars of markdown)")
    return rc


if __name__ == "__main__":
    sys.exit(main())
