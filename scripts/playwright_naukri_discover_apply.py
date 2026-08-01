#!/usr/bin/env python3
"""
Naukri Discover + Apply — via CDP (Chrome on port 9222)

1. Closes stale/redundant Chrome tabs
2. Searches Naukri for fresh relevant jobs (AI/Full-Stack/GenAI, 0-3 yrs, India)
3. Applies queued jobs from naukri_queue.md
4. Selects a category resume per JD (vault_resume), validated for extractable text
5. Logs every result to job_applications_tracker.md

Usage:
  python3 scripts/playwright_naukri_discover_apply.py [--dry-run] [--max-apply 20]

CTC and notice period are read from core_vault/JobApplyFiles/ via vault_config.
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent))
import vault_config as vc
import vault_answers as va
from vault_resume import resume_for_job, validate_resume
import vault_state as vs
import vault_browser as vb

VAULT_ROOT = Path(__file__).resolve().parents[1]
FACT_SHEET_PATH  = VAULT_ROOT / "core_vault" / "JobApplyFiles" / "01_atomic_fact_sheet.json"
LOGISTICS_PATH   = VAULT_ROOT / "core_vault" / "JobApplyFiles" / "06_logistics_mapping.json"
TRACKER_PATH     = VAULT_ROOT / "active_application_context" / "job_applications_tracker.md"
STATE_PATH       = VAULT_ROOT / "active_application_context" / "background_agent_state.json"
# NOTE: last-resort fallback only. Per-job selection now goes through
# vault_resume.resume_for_job(), which validates extractable text before upload.
RESUME_PATH      = VAULT_ROOT / "resumes_and_docs" / "categories" / "pdf" / "Atin_Sharma_Resume_2026.pdf"
ARTIFACT_DIR     = VAULT_ROOT / "output" / "playwright"
CDP_URL          = "http://localhost:9222"

CURRENT_CTC  = vc.current_ctc_lpa()       # canonical: 01_atomic_fact_sheet.json
EXPECTED_CTC = vc.expected_ctc_numeric()  # stated floor; never the private floor

# ---------------------------------------------------------------------------
# Naukri search URLs (Slugified and filtered with experience=0 and jobAge=15)
# ---------------------------------------------------------------------------
def get_search_urls():
    keywords = [
        "typescript node engineer",
        "nextjs react developer",
        "full stack engineer ai node react",
        "founding engineer ai startup",
        "ai engineer llm rag",
        "genai engineer python",
        "langchain langgraph python engineer",
        "full stack engineer",
        "node js developer",
        "react developer",
        "python developer",
        "llm engineer",
        "ai engineer",
        "prompt engineer",
        "react node developer"
    ]
    urls = [
        "https://www.naukri.com/recommendedjobs",
        "https://www.naukri.com/mnj/recommendedjobs"
    ]
    for kw in keywords:
        slug = re.sub(r'[^a-zA-Z0-9]+', '-', kw.strip().lower()).strip('-')
        # Generate URLs for experience range 0 to 3
        # using jobAge=15 to focus on fresh postings
        for exp in [0, 1, 2, 3]:
            urls.append(f"https://www.naukri.com/{slug}-jobs-in-india?experience={exp}&jobAge=15")
    return urls

SEARCH_URLS = get_search_urls()

# Pre-queued jobs from naukri_queue.md
QUEUED_JOBS = [
    {
        "id": "naukri_qure_llm",
        "company": "Qure.ai",
        "role": "LLM Engineer",
        "search_query": "LLM Engineer Qure.ai",
        "url": None,  # Will be discovered via search
        "note": "Qure.ai's mission to deploy AI in real-world clinical workflows resonates with my experience shipping production LLM applications. I built VyaparGPT — a WhatsApp AI for SMBs serving 40+ pilots — using RAG pipelines with pgvector, LangChain.js, and OpenAI APIs on a FastAPI + Node.js stack. At OpenBiz I owned end-to-end AI architecture including stateful multi-agent systems with LangGraph. I can join within 15 days, eager to bring that production LLM depth to Qure's diagnostics AI.",
    },
    {
        "id": "naukri_babblebots_genai",
        "company": "Babblebots AI",
        "role": "GenAI Engineer",
        "search_query": "GenAI Engineer Babblebots",
        "url": None,
        "note": "My work building VyaparGPT — a WhatsApp-native conversational AI for small businesses — used the same tech stack Babblebots AI is hiring for: LangChain.js orchestration, RAG with pgvector, OpenAI function calling, and production Node.js APIs. I built multi-turn stateful agents using LangGraph deployed to 40+ live pilots. As founding engineer at OpenBiz I owned the full stack. Can join within 15 days.",
    },
    {
        "id": "naukri_techblocks_agentic",
        "company": "TechBlocks",
        "role": "Agentic Engineer",
        "search_query": "Agentic Engineer TechBlocks",
        "url": None,
        "note": "Agentic AI is the core of my recent work — I designed a stateful multi-agent CRM system using LangGraph with agents for lead qualification, follow-up scheduling, and data enrichment. VyaparGPT further demonstrates my ability to build LangChain-orchestrated products serving real production users. Available to join within 15 days.",
    },
    {
        "id": "naukri_protectt_ai_red",
        "company": "PROTECTT.AI Labs",
        "role": "AI Red Teaming Engineer",
        "search_query": "AI Red Teaming Engineer PROTECTT",
        "url": None,
        "note": "Building production LLM applications has given me deep intuition for where AI systems break — prompt injection in RAG pipelines, adversarial inputs in multi-agent flows. At OpenBiz we designed input sanitization and output validation layers for our WhatsApp AI. PROTECTT.AI Labs' red teaming focus is a compelling application of that production knowledge. Available within 15 days.",
    },
    {
        "id": "naukri_aiotor_ai",
        "company": "Aiotor Labs",
        "role": "AI Engineer",
        "search_query": None,
        "url": "https://www.naukri.com/job-listings-ai-engineer-aiotor-labs-private-limited-pune-1-to-4-years-120526502847",
        "note": "Aiotor Labs' focus on scalable AI solutions maps onto my end-to-end AI engineering experience. My primary strength is LLM application engineering (RAG, LangChain, agentic systems) backed by solid Python/ML fundamentals. Pune is a preferred city and I'm on a 15-day notice period.",
    },
    {
        "id": "naukri_aventior_genai",
        "company": "Aventior Digital",
        "role": "GenAI Engineer",
        "search_query": "GenAI Engineer Aventior Digital",
        "url": None,
        "note": "My GenAI product experience — VyaparGPT for SMB automation, AI CRM with LangGraph agents — maps well onto Aventior Digital's digital transformation practice. I bring production OpenAI/RAG architecture and full-stack TypeScript/Node.js skills. Available within 15 days for Hyderabad or remote.",
    },
]

# Score keywords (prioritized core stack)
CORE_POSITIVE = [
    "llm", "rag", "langchain", "langgraph", "openai", "gemini", "groq",
    "ai engineer", "genai", "gen ai", "agentic", "agent", "vector", "pgvector",
    "node.js", "nodejs", "react", "typescript",
    "full stack", "fullstack", "founding", "startup", "product engineer",
    "embedding", "prompt", "chatbot", "conversational", "nlp",
]
SECONDARY_POSITIVE = [
    "python", "fastapi", "django", "flask"
]
NEGATIVE = [
    "java ", " scala", ".net developer", "c# developer", "c++ engineer",
    "ruby on rails", "golang engineer", "senior manager", "vp of",
    "10+ years", "15+ years", "12+ years", "ios developer", "android developer",
    "game developer", "unity developer", "mechanical", "hardware",
    "principal", "staff", "director", "head", "vp", "intern", "internship", "trainee"
]
SCORE_THRESHOLD = 0.25


# ---------------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--max-apply", type=int, default=20)
    p.add_argument("--cdp-url", default=CDP_URL)
    return p.parse_args()


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def _legacy_load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {"seen_job_ids": [], "applied_job_ids": [], "blocked_jobs": []}


def save_state(state: dict):
    STATE_PATH.write_text(json.dumps(state, indent=2))


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "").casefold()).strip("-")


def make_job_id(company: str, role: str) -> str:
    return f"{slugify(company)}:{slugify(role)}"


def score_job(title: str, desc: str, company: str = "") -> float:
    title_lower = title.casefold()
    company_lower = (company or "").casefold()
    
    # Check if FAANG-level company
    faang_keywords = ["google", "apple", "meta", "amazon", "microsoft", "netflix", "alphabet", "facebook"]
    is_faang = any(f in company_lower for f in faang_keywords)
    
    # Absolute strict exclusions for internship or trainee roles, unless FAANG
    if not is_faang:
        for word in ["intern", "internship", "trainee", "apprentice"]:
            if word in title_lower:
                return 0.0

    text = (title + " " + desc).casefold()
    score = 0.0
    
    def get_pattern(kw: str) -> str:
        # Prepend \b only if first char is alphanumeric, append \b only if last is alphanumeric
        start = r'\b' if kw[0].isalnum() or kw[0] == '_' else ''
        end = r'\b' if kw[-1].isalnum() or kw[-1] == '_' else ''
        return start + re.escape(kw) + end

    for kw in CORE_POSITIVE:
        pattern = get_pattern(kw)
        if re.search(pattern, title_lower):
            score += 0.20
        elif re.search(pattern, text):
            score += 0.08
            
    for kw in SECONDARY_POSITIVE:
        pattern = get_pattern(kw)
        if re.search(pattern, title_lower):
            score += 0.08
        elif re.search(pattern, text):
            score += 0.03
            
    # If Python-based but has NO Node/TS/React/Express/NestJS/MERN, penalize heavily
    has_core = any(re.search(get_pattern(k), text) for k in ["node", "typescript", "react", "express", "nestjs", "mern", "javascript"])
    has_python = any(re.search(get_pattern(k), text) for k in SECONDARY_POSITIVE)
    if has_python and not has_core:
        score -= 0.25
            
    for kw in NEGATIVE:
        clean_kw = kw.strip()
        if not clean_kw:
            continue
        pattern = get_pattern(clean_kw)
        if re.search(pattern, text):
            score -= 0.30
            
    return min(max(score, 0.0), 1.0)


def is_experience_suitable(exp_str: str) -> bool:
    if not exp_str:
        return True
    match = re.search(r'\b(\d+)\b', exp_str)
    if match:
        min_exp = int(match.group(1))
        # Candidate has 1 YOE (Founding Engineer), so min_exp must be <= 3 YOE
        return min_exp <= 3
    return True


def is_location_suitable(loc_str: str) -> bool:
    if not loc_str:
        return True
    l = loc_str.casefold()
    allowed = [
        "remote", "bangalore", "bengaluru", "hyderabad", "pune",
        "delhi", "noida", "gurgaon", "gurugram", "ncr", "mumbai", "agra"
    ]
    return any(city in l for city in allowed)


def is_salary_suitable(sal_str: str) -> bool:
    # User requested to apply to all jobs under 2 yoe irrespective of CTC shown in JD
    return True


def append_tracker(company: str, role: str, url: str, status: str, note: str = ""):
    today = datetime.now().strftime("%Y-%m-%d")
    line = (
        f"\n- [{today}] **Company:** {company} | **Role:** {role} | "
        f"**Status:** {status} | **URL:** {url} | "
        f"**CTC:** Current {CURRENT_CTC}L / Expected {EXPECTED_CTC}L | **Note:** {note}"
    )
    with open(TRACKER_PATH, "a", encoding="utf-8") as f:
        f.write(line)
    log(f"  → Tracker: {status}")


def close_redundant_tabs(context, keep_domains=("naukri.com",)):
    """Close all page tabs that are not Naukri or new-tab."""
    closed = 0
    for page in list(context.pages):
        url = page.url.casefold()
        is_new_tab = url in ("chrome://newtab/", "about:blank", "")
        is_naukri  = any(d in url for d in keep_domains)
        if not is_new_tab and not is_naukri:
            try:
                page.close()
                closed += 1
            except Exception:
                pass
    if closed:
        log(f"  🗑  Closed {closed} redundant tab(s)")


def build_answer_bank() -> dict:
    """Canonical answers, plus Naukri-specific aliases.

    `naukri_notice_period` was hardcoded to "0" here, contradicting the canonical
    15-day notice on every Naukri application.
    """
    bank = vc.build_answer_bank()
    bank["naukri_current_ctc"]   = bank["current_ctc"]
    bank["naukri_expected_ctc"]  = bank["expected_ctc_min"]
    bank["naukri_notice_period"] = str(vc.notice_period_days())
    return bank


# ---------------------------------------------------------------------------
# Naukri Apply Core
# ---------------------------------------------------------------------------
def clean_label(v):
    return re.sub(r"\s+", " ", v or "").strip()


def find_apply_button(page):
    """Find the primary Apply Now button on the Naukri job detail page (not the search bar)."""
    for sel in [
        ".styles_apply-button__uJI3A",
        "[class*='jhc__apply']",
        "button[class*='applyButton']",
        "a[class*='applyButton']",
        "[id*='apply-button']",
    ]:
        el = page.locator(sel)
        if el.count() > 0:
            for i in range(el.count()):
                btn = el.nth(i)
                try:
                    if btn.is_visible():
                        txt = btn.inner_text().strip().casefold()
                        if "apply" in txt or "easy" in txt:
                            return btn
                except Exception:
                    pass
    for text in ["Apply", "Apply Now", "Easy Apply"]:
        btn = page.get_by_role("button", name=re.compile(text, re.I))
        if btn.count() > 0 and btn.first.is_visible():
            return btn.first
    return None


def find_modal(page):
    for sel in [
        "[class*='applyModal']", "[class*='apply-modal']",
        "[class*='DrawerContainer']", "[class*='chatbot']",
        "[class*='modal'][class*='open']", "[role='dialog']",
    ]:
        el = page.locator(sel)
        if el.count() > 0 and el.first.is_visible():
            return el.first
    return None


def find_action_btn(root, names: list[str]):
    for name in names:
        btn = root.get_by_role("button", name=re.compile(re.escape(name), re.I))
        if btn.count() > 0 and btn.first.is_visible():
            return btn.first
        btn2 = root.locator("button, [role='button']").filter(
            has_text=re.compile(re.escape(name), re.I)
        )
        if btn2.count() > 0 and btn2.first.is_visible():
            return btn2.first
    return None


def fill_ctc_fields(root):
    for sel, val in [
        ("input[placeholder*='Current' i]", str(CURRENT_CTC)),
        ("input[id*='currentSalary' i]",    str(CURRENT_CTC)),
        ("input[id*='current'][id*='sal' i]", str(CURRENT_CTC)),
        ("input[placeholder*='Expected' i]", str(EXPECTED_CTC)),
        ("input[id*='expectedSalary' i]",   str(EXPECTED_CTC)),
        ("input[id*='expected'][id*='sal' i]", str(EXPECTED_CTC)),
    ]:
        try:
            el = root.locator(sel)
            if el.count() > 0 and el.first.is_visible() and not el.first.is_disabled():
                if not el.first.input_value().strip():
                    el.first.fill(val)
        except Exception:
            pass


def fill_notice_period(root):
    for sel in ["select[name*='notice' i]", "select[id*='notice' i]", "[class*='notice'] select"]:
        try:
            el = root.locator(sel)
            if el.count() == 0 or not el.first.is_visible():
                continue
            opts = el.first.locator("option")
            for i in range(opts.count()):
                t = clean_label(opts.nth(i).inner_text()).casefold()
                if any(k in t for k in ("immediate", "0 day", "15 day", "1 week", "less than")):
                    el.first.select_option(index=i)
                    return
            if opts.count() > 1:
                el.first.select_option(index=1)
        except Exception:
            pass


def upload_resume(root, resume_path: Path) -> bool:
    # Validate first: an image-only PDF is invisible to ATS parsers, and one was
    # uploaded 424 times before this check existed.
    resume_path = validate_resume(resume_path)
    for sel in ['input[type="file"]', 'input[accept*="pdf"]', 'input[accept*=".pdf"]']:
        try:
            el = root.locator(sel)
            if el.count() > 0:
                el.first.set_input_files(str(resume_path))
                log("  ✓ Resume uploaded")
                return True
        except Exception:
            pass
    return False


def already_applied(page) -> bool:
    """Check if Naukri shows this job as already applied."""
    # Naukri shows a div with class containing 'applied' and text 'Applied'
    try:
        applied_els = page.locator("[class*='applied'], [class*='Applied']")
        for i in range(applied_els.count()):
            el = applied_els.nth(i)
            try:
                if el.is_visible() and "applied" in el.inner_text().casefold():
                    return True
            except Exception:
                pass
    except Exception:
        pass
    body = page.locator("body").inner_text().casefold()
    return any(p in body[:3000] for p in [
        "already applied", "application submitted", "you have applied",
    ])


def execute_naukri_apply(page, resume_path: Path, answer_bank: dict, dry_run: bool, note: str = "") -> str:
    """Full apply flow. Returns: 'submitted' | 'dry_run' | 'already_applied' | 'external' | 'error:<reason>'"""
    try:
        clicked_texts = []
        notified_form_urls = set()
        last_clicked_question = ""
        last_clicked_answer = ""
        # Questions we refused to guess at. A non-empty list means the job needs a
        # human, and is reported as 'blocked:unanswerable' rather than submitted.
        unanswered_questions: list[str] = []
        # Already applied?
        if already_applied(page):
            return "already_applied"

        body = page.locator("body").inner_text().casefold()
        # Login check
        if "login" in body[:300] and "naukri" in page.url.casefold() and "/job" not in page.url.casefold():
            return "error:login_required"

        # Find Apply button
        apply_btn = find_apply_button(page)
        if apply_btn is None:
            ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(ARTIFACT_DIR / "naukri_no_apply_btn.png"))
            return "error:no_apply_button"

        log(f"  Clicking apply: {apply_btn.inner_text().strip()[:30]}")
        # Scroll + JS click
        try:
            apply_btn.scroll_into_view_if_needed(timeout=4000)
            page.wait_for_timeout(400)
        except Exception:
            pass
        try:
            apply_btn.click(timeout=8000)
        except Exception:
            apply_btn.evaluate("el => el.click()")
        page.wait_for_timeout(4000)

        # Re-check if already applied now (some pages redirect)
        if already_applied(page):
            return "already_applied"

        # Check for external redirect
        body2 = page.locator("body").inner_text().casefold()
        if "apply on company website" in body2 or "external application" in body2:
            ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(ARTIFACT_DIR / "naukri_external_ats.png"))
            return "external:company_website"

        # Wait for chatbot/modal to appear
        modal = None
        try:
            page.wait_for_selector(
                "[class*='chatbot'], [class*='DrawerContainer'], [class*='applyModal'], [role='dialog'], [class*='bot-container']",
                timeout=8000, state="visible"
            )
            modal = find_modal(page)
        except Exception:
            modal = find_modal(page)

        root = modal if modal else page.locator("body")
        resume_uploaded = False

        # Extra wait for Naukri chatbot input to render if it's a chatbot flow
        try:
            page.wait_for_selector(
                'div[contenteditable][placeholder*="message" i], div[contenteditable][placeholder*="type" i], div.textArea[contenteditable]',
                timeout=5000, state="visible"
            )
        except Exception:
            pass  # Not a chatbot flow — regular modal, continue normally

        for step in range(35):
            page.wait_for_timeout(1500)

            # Scan text for external form links
            try:
                bubbles = page.locator("[class*='message'], [class*='bubble'], [class*='chat'], [class*='bot'], div[class*='text'] p, div[class*='text'], a")
                for idx in range(bubbles.count()):
                    b = bubbles.nth(idx)
                    try:
                        if b.is_visible(timeout=500):
                            href = b.get_attribute("href")
                            text = b.inner_text().strip()
                            urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)
                            if href:
                                urls.append(href)
                            for url in urls:
                                url_clean = url.rstrip(",.()\"'")
                                if url_clean not in notified_form_urls:
                                    if any(domain in url_clean.casefold() for domain in ("form", "tally.so", "typeform.com", "gle/")):
                                        if any(k in url_clean.casefold() for k in ("naukri.com", "naukrirecruiter")):
                                            continue
                                        notified_form_urls.add(url_clean)
                                        log(f"⚠️ FOUND EXTERNAL FORM LINK: {url_clean}")
                                        print(f"\n========================================================")
                                        print(f"⚠️ ACTION REQUIRED: Job application requires external form!")
                                        print(f"URL: {url_clean}")
                                        print(f"Please copy and fill it.")
                                        print(f"========================================================\n", flush=True)
                    except Exception:
                        pass
            except Exception:
                pass

            # Re-check already applied
            if already_applied(page):
                return "already_applied"

            # Success detection
            body_text = page.locator("body").inner_text().casefold()
            if any(p in body_text for p in [
                "application sent", "application submitted", "applied successfully",
                "thank you for applying", "your application has been", "successfully applied",
                "applied to",
            ]):
                ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(ARTIFACT_DIR / "naukri_submitted.png"))
                return "submitted"

            # Extract the current chatbot question
            question = ""
            try:
                bubbles = page.locator("[class*='message'], [class*='bubble'], [class*='chat'], [class*='bot'], div[class*='text'] p, div[class*='text']")
                for q in range(bubbles.count()):
                    el = bubbles.nth(q)
                    try:
                        if el.is_visible():
                            t = el.inner_text(timeout=1000).strip()
                            if t and len(t) > 5 and "type message" not in t.casefold() and "search" not in t.casefold():
                                question = t.casefold()
                    except Exception:
                        pass
            except Exception:
                pass

            # Refresh modal ref
            modal = find_modal(page)
            root = modal if modal else page.locator("body")

            # Upload resume (only if explicitly asked or required by the chatbot prompt)
            if not resume_uploaded:
                try:
                    modal_text = root.inner_text().casefold()
                    if any(k in modal_text for k in ("upload resume", "upload cv", "attach resume", "attach cv", "latest resume", "select resume")):
                        if upload_resume(root, resume_path):
                            resume_uploaded = True
                except Exception:
                    pass

            # Fill CTC + notice
            fill_ctc_fields(root)
            fill_notice_period(root)

            # Fill cover note if textarea present and empty
            tas = root.locator("textarea")
            for ti in range(tas.count()):
                ta = tas.nth(ti)
                if ta.is_visible():
                    try:
                        if not ta.input_value().strip() and note:
                            ta.fill(note[:500])
                    except Exception:
                        pass
            
            # Naukri chatbot input is a contenteditable DIV (not input/textarea)
            bot_inputs_all = page.locator('div[contenteditable][placeholder*="message" i], div[contenteditable][placeholder*="type" i], div.textArea[contenteditable]')
            visible_bot_inputs = []
            for bi in range(bot_inputs_all.count()):
                try:
                    el = bot_inputs_all.nth(bi)
                    if el.is_visible(timeout=500):
                        visible_bot_inputs.append(el)
                except Exception:
                    pass
            bot_typed = False
            if visible_bot_inputs:
                log(f"  Found {len(visible_bot_inputs)} visible chatbot input(s)")
            for inp in visible_bot_inputs:
                try:
                    log(f"  Detected chatbot input. Last question: '{question[:80]}'")

                    # Answers come from vault_answers, which reads the question.
                    #
                    # This block previously hardcoded a lookup table whose worst
                    # entries were `"10 LPA"` for any salary question — below the
                    # current CTC and 8 LPA under the stated floor — and a catch-all
                    # `else` that typed a skills list into ANY unrecognised question.
                    # It also answered "Immediate" for notice and named a former
                    # employer as current.
                    if "skill" in question or "tech" in question or "stack" in question \
                            or "programming" in question or "primary" in question:
                        val = ", ".join(sorted(vc.load_facts()["tech_stack"]["languages"]
                                               + vc.load_facts()["tech_stack"]["frontend"][:3]))
                    elif "secondary" in question:
                        val = ", ".join(vc.load_facts()["tech_stack"]["devops_cloud"])
                    else:
                        ans = va.answer_for_question(question, bank=answer_bank)
                        if ans.decision is va.Decision.VALUE and ans.value:
                            val = ans.value
                        elif ans.decision in (va.Decision.YES, va.Decision.NO):
                            val = ans.value
                        else:
                            # Abstain rather than guess. The job is surfaced for
                            # human review instead of receiving a wrong answer.
                            log(f"  ⚠ Unanswerable question, abstaining: '{question[:100]}'")
                            unanswered_questions.append(question)
                            break

                    log(f"  Typing answer: '{val}'")
                    inp.click()
                    page.wait_for_timeout(300)
                    inp.evaluate(f"el => {{ el.innerText = {repr(val)}; el.dispatchEvent(new Event('input', {{bubbles: true}})); }}")
                    page.wait_for_timeout(500)
                    inp.press("Enter")
                    page.wait_for_timeout(2000)
                    last_clicked_question = question
                    last_clicked_answer = val.casefold()
                    bot_typed = True
                    break
                except Exception as e:
                    log(f"  Chatbot input error: {e}")

            if bot_typed:
                continue

            # Fill text inputs generically
            inputs = root.locator('input:not([type="hidden"]):not([type="file"]):not([type="radio"]):not([type="checkbox"]):not([placeholder*="keyword" i]):not([placeholder*="location" i])')
            for ii in range(inputs.count()):
                inp = inputs.nth(ii)
                try:
                    if not inp.is_visible() or inp.is_disabled():
                        continue
                    if inp.input_value().strip():
                        continue
                    label = inp.evaluate("""el => {
                        if (el.labels && el.labels.length) return el.labels[0].textContent;
                        return el.getAttribute('placeholder') || el.getAttribute('aria-label') || '';
                    }""").casefold()
                    val = None
                    if "name" in label and "company" not in label:
                        val = answer_bank.get("full_name")
                    elif "email" in label or "mail" in label:
                        val = answer_bank.get("email")
                    elif "phone" in label or "mobile" in label:
                        val = answer_bank.get("phone")
                    elif "current ctc" in label or "current salary" in label:
                        val = str(CURRENT_CTC)
                    elif "expected ctc" in label or "expected salary" in label:
                        val = str(EXPECTED_CTC)
                    elif "notice" in label:
                        val = "0"
                    elif "city" in label or "location" in label:
                        val = answer_bank.get("city")
                    elif "experience" in label or "years" in label:
                        val = answer_bank.get("years_experience")
                    if val:
                        inp.fill(str(val))
                except Exception:
                    pass

            # Click chatbot option buttons if any match our answer bank / preferences
            clicked_option = False
            for opt_sel in ["button", "[role='button']", "div[class*='option']", "div[class*='chip']", "label", "[class*='radio']", "[class*='label']"]:
                els = root.locator(opt_sel)
                try:
                    for i in reversed(range(els.count())):
                        el = els.nth(i)
                        if not el.is_visible() or el.is_disabled():
                            continue
                        txt = clean_label(el.inner_text()).strip()
                        if not txt:
                            continue
                        txt_lower = txt.casefold()
                        
                        # Loop prevention: check if we clicked this exact answer for this exact question
                        is_duplicate_click = (last_clicked_question == question and last_clicked_answer == txt_lower)
                        if is_duplicate_click and question != "":
                            continue
                        
                        # Fallback loop prevention: don't click the exact same option text more than 6 times total
                        if clicked_texts.count(txt_lower) >= 6:
                            continue
                        
                        # Avoid clicking submit/navigation buttons here
                        if txt_lower in ("apply", "apply now", "submit", "send application", 
                                         "save and apply", "save & apply", "save",
                                         "next", "continue", "proceed", "ok", "okay"):
                            continue
                            
                        # City preferences
                        cities = ["agra", "remote", "bangalore", "bengaluru", "hyderabad", "pune", "delhi", "noida", "gurgaon", "mumbai"]
                        if any(city in txt_lower for city in cities):
                            log(f"  Clicking city/location option: {txt}")
                            el.click()
                            clicked_texts.append(txt_lower)
                            last_clicked_question = question
                            last_clicked_answer = txt_lower
                            clicked_option = True
                            page.wait_for_timeout(1000)
                            break
                            
                        # Yes/No — gated on the QUESTION, not just the option text.
                        #
                        # This branch used to click any option reading "yes"/"agree"
                        # without ever inspecting `question`, so "Do you require visa
                        # sponsorship?", "Will you sign a 2-year bond?" and "Do you
                        # have 5+ years experience?" all got an unconditional Yes.
                        if txt_lower in va.YES_TOKENS or txt_lower in va.NO_TOKENS:
                            ans = va.answer_for_question(question, bank=answer_bank)
                            want_yes = txt_lower in va.YES_TOKENS
                            allowed = (
                                (want_yes and ans.decision is va.Decision.YES)
                                or (not want_yes and ans.decision is va.Decision.NO)
                            )
                            if not allowed:
                                # Never affirm something we have not reasoned about.
                                if ans.decision is va.Decision.ABSTAIN:
                                    log(f"  ⚠ Won't answer '{txt}' — unrecognised question: "
                                        f"'{question[:90]}'")
                                    if question and question not in unanswered_questions:
                                        unanswered_questions.append(question)
                                continue
                            log(f"  Clicking '{txt}' via rule [{ans.rule}] for: '{question[:70]}'")
                            el.click()
                            clicked_texts.append(txt_lower)
                            last_clicked_question = question
                            last_clicked_answer = txt_lower
                            clicked_option = True
                            page.wait_for_timeout(1000)
                            break

                        # Skip / Optional question validation
                        if "skip" in txt_lower:
                            log(f"  Clicking skip/optional option: {txt}")
                            el.click()
                            clicked_texts.append(txt_lower)
                            last_clicked_question = question
                            last_clicked_answer = txt_lower
                            clicked_option = True
                            page.wait_for_timeout(1000)
                            break
                    if clicked_option:
                        break
                except Exception:
                    pass
            if clicked_option:
                continue

            # Refuse to submit a form containing a question we would only be
            # guessing at. Abstaining costs one application; a wrong answer to
            # "do you have 5+ years" or a bond clause costs credibility.
            if unanswered_questions:
                ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(ARTIFACT_DIR / f"naukri_unanswerable_step{step}.png"))
                log(f"  🛑 Not submitting — {len(unanswered_questions)} unanswered question(s)")
                for q in unanswered_questions[:3]:
                    log(f"     · {q[:110]}")
                return "blocked:unanswerable_question"

            if dry_run:
                ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(ARTIFACT_DIR / f"naukri_dry_run_step{step}.png"))
                return "dry_run"

            # Submit — 'Save' is also a submit button in Naukri chatbot
            submit = find_action_btn(root, ["Apply", "Apply Now", "Submit", "Send Application", "Save and Apply", "Save & Apply", "Save"])
            if submit:
                try:
                    submit.scroll_into_view_if_needed(timeout=3000)
                    page.wait_for_timeout(300)
                except Exception:
                    pass
                try:
                    submit.click(timeout=8000)
                except Exception:
                    submit.evaluate("el => el.click()")
                page.wait_for_timeout(2000)
                continue

            # Next / Continue / Skip in chatbot
            nxt = find_action_btn(root, ["Next", "Continue", "Proceed", "OK", "Okay", "Skip this question", "Skip"])
            if nxt:
                try:
                    nxt.scroll_into_view_if_needed(timeout=3000)
                except Exception:
                    pass
                try:
                    nxt.click(timeout=6000)
                except Exception:
                    nxt.evaluate("el => el.click()")
                page.wait_for_timeout(1500)
                modal = find_modal(page)
                root = modal if modal else page.locator("body")
                continue

            # No actionable button — take screenshot and break
            ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(ARTIFACT_DIR / f"naukri_stuck_step{step}.png"))
            log(f"  ⚠ No action button at step {step}")
            break

        return "error:step_limit"

    except vb.SecurityChallenge:
        raise  # must reach __main__ and abort the run, never be swallowed
    except Exception as exc:
        return f"error:{exc}"


# ---------------------------------------------------------------------------
# Discovery helpers
# ---------------------------------------------------------------------------
def discover_jobs_on_search_page(page) -> list[dict]:
    """Parse Naukri search result cards and return list of {title, company, url, location, experience, salary, description}."""
    jobs = []
    seen_urls: set = set()
    cards = page.locator("article.jobTuple, .srp-jobtuple-wrapper, [class*='jobTuple'], .cust-job-tuple")
    for i in range(min(cards.count(), 40)):
        card = cards.nth(i)
        try:
            title, company, url = "", "", ""
            # Title: h2 > a.title
            for t_sel in ["h2 a.title", "a.title", "h2 a", ".title a"]:
                el = card.locator(t_sel)
                if el.count() > 0:
                    title = clean_label(el.first.inner_text())
                    url = el.first.get_attribute("href") or ""
                    break
            # Company: a.comp-name
            for c_sel in ["a.comp-name", ".comp-name", ".comp-dtls-wrap a", ".subTitle a"]:
                el = card.locator(c_sel)
                if el.count() > 0:
                    company = clean_label(el.first.inner_text())
                    break
            if not url or not title:
                continue
            if url and not url.startswith("http"):
                url = "https://www.naukri.com" + url
            # Deduplicate by URL
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            # Parse Location
            location = ""
            for l_sel in [".loc-wrap", "span.locWdth", ".loc", "[class*='location']"]:
                el = card.locator(l_sel)
                if el.count() > 0:
                    location = clean_label(el.first.inner_text())
                    break
            
            # Parse Experience
            experience = ""
            for e_sel in [".exp-wrap", "span.expwdth", ".exp", "[class*='experience']"]:
                el = card.locator(e_sel)
                if el.count() > 0:
                    experience = clean_label(el.first.inner_text())
                    break

            # Parse Salary
            salary = ""
            for s_sel in [".sal-wrap", "span.salWdth", ".sal", "[class*='salary']"]:
                el = card.locator(s_sel)
                if el.count() > 0:
                    salary = clean_label(el.first.inner_text())
                    break

            # Parse Description snippet
            desc = ""
            for d_sel in [".job-desc", "[class*='description']", ".desc"]:
                el = card.locator(d_sel)
                if el.count() > 0:
                    desc = clean_label(el.first.inner_text())
                    break

            # Parse Tags (Skills)
            tags = []
            tag_els = card.locator(".tag-li, [class*='tag-li']")
            for ti in range(tag_els.count()):
                t_txt = clean_label(tag_els.nth(ti).inner_text())
                if t_txt:
                    tags.append(t_txt)
            skills_str = ", ".join(tags)
            
            combined_desc = desc
            if skills_str:
                combined_desc += " " + skills_str

            jobs.append({
                "title": title,
                "company": company,
                "url": url,
                "location": location,
                "experience": experience,
                "salary": salary,
                "description": combined_desc
            })
        except Exception:
            continue
    return jobs


def search_and_apply_queued(page, apply_page, context, state: dict, answer_bank: dict,
                             applied_count: list, max_apply: int, dry_run: bool):
    """For queued jobs, find the job URL on Naukri and apply."""
    for job in QUEUED_JOBS:
        if applied_count[0] >= max_apply:
            break
        job_id = job["id"]
        skip, why = state.should_skip(job_id)
        if skip:
            log(f"  ⏭  SKIP ({why}): {job['company']} — {job['role']}")
            continue

        # If direct URL, use it; else search
        if job.get("url"):
            target_url = job["url"]
        elif job.get("search_query"):
            log(f"  🔍 Searching Naukri for: {job['search_query']}")
            search_url = f"https://www.naukri.com/jobs-in-india?k={job['search_query'].replace(' ', '+')}"
            page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            discovered = discover_jobs_on_search_page(page)
            # Find EXACT company match first, then fuzzy
            target_url = None
            company_lower = job["company"].casefold()
            # Exact company match
            for d in discovered:
                if company_lower in d["company"].casefold():
                    target_url = d["url"]
                    log(f"    Found exact match: {d['company']} — {d['title']}")
                    break
            # Fuzzy: company name in title/URL
            if not target_url:
                for d in discovered:
                    if company_lower in d["url"].casefold() or company_lower in d["title"].casefold():
                        target_url = d["url"]
                        log(f"    Found URL match: {d['title']}")
                        break
            if not target_url:
                log(f"  ❌ Could not find URL for: {job['company']} — {job['role']}")
                append_tracker(job["company"], job["role"], "", "FAILED (no URL found)", "Job not listed or search mismatch")
                # Previously recorded nothing here, so this path re-ran on every
                # search URL and every future run — 89 duplicate tracker rows.
                vs.record_outcome(job_id, vs.Outcome.BLOCKED_PERMANENT, reason="no_url_found")
                state.record(job_id, vs.Outcome.BLOCKED_PERMANENT, reason="no_url_found")
                continue
        else:
            log(f"  ⏭  SKIP (no URL or search): {job['company']}")
            continue

        log(f"\n▶ QUEUED JOB: {job['company']} — {job['role']}")
        log(f"  URL: {target_url}")

        try:
            vb.guarded_goto(apply_page, target_url, timeout=30000,
                            label=f"{job['company']} {job['role']}")
            apply_page.wait_for_timeout(3000)
            queued_resume = resume_for_job(job.get("note", ""), job.get("role", ""), explicit=job.get("resume"))
            status = execute_naukri_apply(apply_page, queued_resume, answer_bank, dry_run, job.get("note", ""))
            log(f"  STATUS: {status}")

            outcome = vs.classify(status)
            if outcome in (vs.Outcome.APPLIED, vs.Outcome.APPLIED_UNCONFIRMED):
                append_tracker(job["company"], job["role"], target_url, "APPLIED ✅", f"{queued_resume.name} | queued job")
                applied_count[0] += 1
            elif outcome is vs.Outcome.DRY_RUN:
                append_tracker(job["company"], job["role"], target_url, "DRY_RUN", "")
                applied_count[0] += 1
            elif outcome is vs.Outcome.ALREADY_APPLIED:
                append_tracker(job["company"], job["role"], target_url, "ALREADY_APPLIED ⏭️", "")
            elif outcome is vs.Outcome.BLOCKED_PERMANENT:
                append_tracker(job["company"], job["role"], target_url, f"BLOCKED ⚠️ ({status})", "Needs manual review")
            else:
                append_tracker(job["company"], job["role"], target_url, f"FAILED ({status})", "")
            # This branch chain used to write the tracker but never touch state on
            # failure, so failures were retried forever (one URL logged 54 times).
            vs.record_outcome(job_id, outcome, reason=status, url=target_url)
            state.record(job_id, outcome, reason=status, url=target_url)
        finally:
            time.sleep(2)


def discover_and_apply_search(page, apply_page, context, search_url: str, state: dict,
                               answer_bank: dict, applied_count: list,
                               max_apply: int, dry_run: bool):
    """Search Naukri, score, and apply to fresh matching jobs."""
    try:
        log(f"  Searching: {search_url[:90]}...")
        page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)

        jobs = discover_jobs_on_search_page(page)
        log(f"  Found {len(jobs)} job listings")

        for job in jobs:
            if applied_count[0] >= max_apply:
                return
            title   = job["title"]
            company = job["company"]
            url     = job["url"]
            location = job.get("location", "")
            experience = job.get("experience", "")
            salary = job.get("salary", "")
            combined_desc = job.get("description", "")
            job_id  = make_job_id(company, title)

            skip, why = state.should_skip(job_id)
            if skip:
                log(f"  ⏭  SKIP ({why}): {company} — {title}")
                continue

            # Python-side filtering for relevancy
            if not is_experience_suitable(experience):
                log(f"  ⏭  SKIP (experience filter: {experience}): {company} — {title}")
                vs.record_outcome(job_id, vs.Outcome.SKIPPED_FILTER, reason="experience", url=url)
                state.record(job_id, vs.Outcome.SKIPPED_FILTER)
                continue

            if not is_location_suitable(location):
                log(f"  ⏭  SKIP (location filter: {location}): {company} — {title}")
                vs.record_outcome(job_id, vs.Outcome.SKIPPED_FILTER, reason="location", url=url)
                state.record(job_id, vs.Outcome.SKIPPED_FILTER)
                continue

            if not is_salary_suitable(salary):
                log(f"  ⏭  SKIP (salary filter: {salary}): {company} — {title}")
                vs.record_outcome(job_id, vs.Outcome.SKIPPED_FILTER, reason="salary", url=url)
                state.record(job_id, vs.Outcome.SKIPPED_FILTER)
                continue

            score = score_job(title, combined_desc, company)

            if score < SCORE_THRESHOLD:
                log(f"  ⏭  SKIP (score {score:.2f}): {company} — {title}")
                vs.record_outcome(job_id, vs.Outcome.SKIPPED_FILTER,
                                  reason=f"score {score:.2f}", url=url)
                state.record(job_id, vs.Outcome.SKIPPED_FILTER)
                continue

            log(f"\n  ▶ APPLYING [{score:.2f}]: {company} — {title}")
            try:
                vb.guarded_goto(apply_page, url, timeout=30000, label=f"{company} {title}")
                apply_page.wait_for_timeout(3000)
                chosen_resume = resume_for_job(combined_desc if "combined_desc" in dir() else title, title)
                status = execute_naukri_apply(apply_page, chosen_resume, answer_bank, dry_run)
                log(f"  STATUS: {status}")

                note_str = f"Score {score:.2f}. {chosen_resume.name}."
                outcome = vs.classify(status)
                if outcome in (vs.Outcome.APPLIED, vs.Outcome.APPLIED_UNCONFIRMED):
                    append_tracker(company, title, url, "APPLIED ✅", note_str)
                    applied_count[0] += 1
                elif outcome is vs.Outcome.DRY_RUN:
                    append_tracker(company, title, url, "DRY_RUN", note_str)
                    applied_count[0] += 1
                elif outcome is vs.Outcome.ALREADY_APPLIED:
                    append_tracker(company, title, url, "ALREADY_APPLIED ⏭️", "")
                elif outcome is vs.Outcome.BLOCKED_PERMANENT:
                    append_tracker(company, title, url, f"BLOCKED ⚠️ ({status})", note_str)
                else:
                    append_tracker(company, title, url, f"FAILED ({status})", note_str)
                vs.record_outcome(job_id, outcome, reason=status, url=url)
                state.record(job_id, outcome, reason=status, url=url)
            finally:
                time.sleep(2)

    except vb.SecurityChallenge:
        raise
    except Exception as exc:
        log(f"  Search error: {exc}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    args = parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: playwright not installed.", file=sys.stderr)
        sys.exit(1)

    if not RESUME_PATH.exists():
        print(f"ERROR: Resume not found: {RESUME_PATH}", file=sys.stderr)
        sys.exit(1)

    log("=" * 65)
    log(f"NAUKRI DISCOVER + APPLY — {'DRY RUN' if args.dry_run else 'LIVE'}")
    log(f"Current CTC: {CURRENT_CTC} LPA  |  Expected CTC: {EXPECTED_CTC} LPA")
    log(f"Resume: {RESUME_PATH.name}")
    log(f"Queued jobs: {len(QUEUED_JOBS)}  |  Max new: {args.max_apply}")
    log("=" * 65)

    state  = vs.load_state()
    answer_bank = build_answer_bank()
    applied_count = [0]

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(args.cdp_url, no_defaults=True)
        context = browser.contexts[0] if browser.contexts else browser.new_context()

        # ── Step 0: Close redundant tabs ──────────────────────────────────
        log("\n── Step 0: Closing redundant tabs ──")
        close_redundant_tabs(context, keep_domains=("naukri.com",))

        # ── Step 1: Queued jobs (from naukri_queue.md) ────────────────────
        log("\n── Step 1: Applying queued jobs ──")
        search_page = context.pages[0] if context.pages else context.new_page()
        apply_page = context.pages[1] if len(context.pages) > 1 else context.new_page()
        try:
            search_and_apply_queued(search_page, apply_page, context, state, answer_bank,
                                    applied_count, args.max_apply, args.dry_run)
        finally:
            pass  # keep pages open for Step 2

        # ── Step 2: Discover fresh jobs from search ───────────────────────
        log("\n── Step 2: Discovering fresh Naukri jobs ──")
        for search_url in SEARCH_URLS:
            if applied_count[0] >= args.max_apply:
                break
            discover_and_apply_search(search_page, apply_page, context, search_url, state,
                                      answer_bank, applied_count, args.max_apply,
                                      args.dry_run)
            # Close extra tabs after each search batch (keeping search and apply tabs)
            close_redundant_tabs(context, keep_domains=("naukri.com",))
            time.sleep(2)

        # Final cleanup
        close_redundant_tabs(context, keep_domains=())

    log("\n" + "=" * 65)
    log(f"NAUKRI PIPELINE COMPLETE")
    log(f"Applications submitted: {applied_count[0]}")
    log(f"Tracker: {TRACKER_PATH.name}")
    log("=" * 65)


if __name__ == "__main__":
    # A security challenge must abort the run with exit 10 (or 12 for a login
    # wall) so run_apply_all.sh stops the whole pipeline. Continuing after a
    # challenge deepens the flag on this IP/profile.
    try:
        main()
    except vb.SecurityChallenge as _exc:
        print(f"🛑 SECURITY CHALLENGE ({_exc.kind}): {_exc}", flush=True)
        raise SystemExit(_exc.exit_code)
