#!/usr/bin/env python3
"""
Resume selection and upload safety.

Two defects this exists to make impossible:

  1. An image-only PDF was uploaded 424 times. `NewResDocPdf.pdf` has ZERO
     extractable characters — invisible to any ATS that parses text. Nothing
     checked, so nothing complained.

  2. The tracker recorded a resume that was never uploaded. Per-job dicts carry a
     "resume" key that was logged but ignored, while a hardcoded RESUME_PATH went
     out on every application.

validate_resume() is called from *inside* safe_upload(), so there is no code path
that uploads without validating first.

    from vault_resume import resume_for_job, safe_upload
    pdf = resume_for_job(jd_text, title, explicit=job.get("resume"))
    safe_upload(page, pdf)
"""

from __future__ import annotations

import re
import subprocess
from functools import lru_cache
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = VAULT_ROOT / "resumes_and_docs" / "categories" / "pdf"

DEFAULT_CATEGORY = "AI_Integrated_FullStack"

# Bad files measure 0 chars; good ones 4,346-4,645. 800 is far from both edges.
MIN_TEXT_CHARS = 800
# Catches "extracts something, but it's garbage".
REQUIRED_MARKERS = ("Atin", "@")

# Mirrors the "Resume Selection Logic" table in CLAUDE.md. Order is precedence:
# on a tie, the earlier entry wins.
ROUTING: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("GenAI_Prompt_Engineer", (
        "llm", "rag", "conversational", "chatbot", "vector", "embedding", "groq",
        "pgvector", "langchain", "langgraph", "prompt engineer", "genai", "gen ai",
        "generative ai", "agentic", "fine-tun",
    )),
    ("Backend_AI_Specialist", (
        "compliance", "kyc", "legal", "identity", "aml", "document verification",
        "regtech", "onboarding verification", "fraud",
    )),
    ("Cloud_Native_FullStack", (
        "cloud", "devops", "docker", "kubernetes", "aws", "infra", "terraform",
        "sre", "platform engineer", "ci/cd",
    )),
    ("AI_Integrated_FullStack", (
        "full-stack", "full stack", "fullstack", "mern", "react", "next.js",
        "product engineer", "founding", "payments", "payout", "wallet", "banking",
        "fintech", "razorpay", "billing",
    )),
)


class ResumeUnusable(RuntimeError):
    """The PDF would be invisible or garbled to an ATS. Never upload it."""


@lru_cache(maxsize=32)
def _extract(path_str: str, mtime: float, size: int) -> str:
    """Cached on (path, mtime, size) so repeated validation is ~free."""
    path = Path(path_str)
    try:
        from pypdf import PdfReader

        return "".join((p.extract_text() or "") for p in PdfReader(str(path)).pages)
    except Exception:
        pass
    try:
        out = subprocess.run(
            ["pdftotext", str(path), "-"], capture_output=True, text=True, timeout=30
        )
        return out.stdout if out.returncode == 0 else ""
    except Exception:
        return ""


def extractable_text(pdf: Path) -> str:
    st = pdf.stat()
    return _extract(str(pdf), st.st_mtime, st.st_size)


def validate_resume(pdf: Path, *, min_chars: int = MIN_TEXT_CHARS) -> Path:
    """Return `pdf` if an ATS could read it; otherwise raise ResumeUnusable."""
    pdf = Path(pdf)
    if not pdf.exists():
        raise ResumeUnusable(f"missing: {pdf}")
    text = extractable_text(pdf)
    stripped = re.sub(r"\s+", "", text)
    if len(stripped) < min_chars:
        raise ResumeUnusable(
            f"{pdf.name}: only {len(stripped)} extractable chars (need >= {min_chars}). "
            "This is an image-only PDF and is invisible to ATS parsers."
        )
    # Case-insensitive: the LaTeX template sets the name in small-caps, which
    # extracts as "ATIN SHARMA".
    lowered = text.casefold()
    missing = [m for m in REQUIRED_MARKERS if m.casefold() not in lowered]
    if missing:
        raise ResumeUnusable(
            f"{pdf.name}: extracted text is missing {missing} — likely corrupt encoding"
        )
    return pdf


def category_path(category: str) -> Path:
    return PDF_DIR / f"{category}.pdf"


def select_category(jd_text: str, title: str = "", explicit: str | None = None) -> str:
    """Pick a resume category. Explicit wins; else keyword-score; else default."""
    if explicit and category_path(explicit).exists():
        return explicit
    # Title is weighted 3x: portal JD scraping is unreliable, titles rarely are.
    haystack = ((title + " ") * 3 + " " + (jd_text or "")).casefold()
    best, best_score = DEFAULT_CATEGORY, 0
    for category, keywords in ROUTING:
        score = sum(1 for k in keywords if k in haystack)
        if score > best_score:  # strict > preserves ROUTING order on ties
            best, best_score = category, score
    return best


def resume_for_job(jd_text: str, title: str = "", explicit: str | None = None) -> Path:
    """Validated resume PDF for this job. Falls back only to a *valid* file."""
    chosen = category_path(select_category(jd_text, title, explicit))
    try:
        return validate_resume(chosen)
    except ResumeUnusable:
        fallback = category_path(DEFAULT_CATEGORY)
        if fallback != chosen:
            return validate_resume(fallback)
        raise


def safe_upload(root, pdf: Path, selector: str = 'input[type="file"]') -> bool:
    """Upload only after validation. The single chokepoint for every upload."""
    from playwright_form_helpers import maybe_upload_file

    return maybe_upload_file(root, validate_resume(pdf), selector)


def audit() -> list[str]:
    """Check every resume in PDF_DIR. Returns problems (empty == OK)."""
    problems: list[str] = []
    for category, _ in ROUTING:
        path = category_path(category)
        try:
            validate_resume(path)
        except ResumeUnusable as exc:
            problems.append(str(exc))
    return problems


if __name__ == "__main__":
    import sys

    print(f"resume dir: {PDF_DIR}\n")
    for pdf in sorted(PDF_DIR.glob("*.pdf")):
        try:
            validate_resume(pdf)
            n = len(re.sub(r"\s+", "", extractable_text(pdf)))
            print(f"  ✓ {pdf.name:<38} {n:>5} chars")
        except ResumeUnusable as exc:
            print(f"  ✗ {pdf.name:<38} {exc}")
    print("\nrouting:")
    for jd, title in [
        ("Build RAG pipelines with pgvector and Groq", "GenAI Engineer"),
        ("KYC and AML document verification platform", "Backend Engineer"),
        ("Kubernetes, Terraform, AWS infrastructure", "DevOps Engineer"),
        ("React and Node.js product work, Razorpay billing", "Full Stack Engineer"),
        ("", "Software Engineer"),
    ]:
        print(f"  {title:<22} -> {select_category(jd, title)}")
    sys.exit(1 if audit() else 0)
