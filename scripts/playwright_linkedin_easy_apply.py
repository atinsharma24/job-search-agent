#!/usr/bin/env python3

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

from playwright_form_helpers import (
    build_base_answer_bank,
    clean_label,
    fill_radio_groups,
    fill_selects,
    fill_text_inputs,
    fill_textareas,
    map_answer,
    maybe_upload_file,
)


EXIT_SUCCESS = 0
EXIT_GENERIC_FAILURE = 1
EXIT_CAPTCHA = 10
EXIT_EXTERNAL_REDIRECT = 11
EXIT_LOGIN_REQUIRED = 12
EXIT_UNANSWERABLE = 14   # required question outside answering policy

VAULT_ROOT = Path(__file__).resolve().parents[1]
FACT_SHEET_PATH = VAULT_ROOT / "core_vault" / "JobApplyFiles" / "01_atomic_fact_sheet.json"
LOGISTICS_PATH = VAULT_ROOT / "core_vault" / "JobApplyFiles" / "06_logistics_mapping.json"
ARTIFACT_DIR = VAULT_ROOT / "output" / "playwright"
LOG_DIR = VAULT_ROOT / "logs"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministic LinkedIn Easy Apply executor."
    )
    parser.add_argument("--application-url", required=True)
    parser.add_argument("--resume-path", required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def build_answer_bank() -> dict:
    return build_base_answer_bank(FACT_SHEET_PATH, LOGISTICS_PATH)


def detect_status_from_text(text: str) -> Optional[int]:
    """Text-only fallback. Deliberately conservative.

    The previous version returned EXIT_LOGIN_REQUIRED whenever the page contained
    both "sign in" and "linkedin" — which is true of essentially every LinkedIn
    page, logged in or not, because those words appear in footers and modals.
    That produced spurious error:12 aborts on healthy sessions. Prefer
    detect_status_from_page(), which checks the URL and a password field.
    """
    lowered = text.casefold()
    if "captcha" in lowered or "security verification" in lowered or "suspicious activity" in lowered:
        return EXIT_CAPTCHA
    # Only unambiguous session-expiry phrasing; never bare "sign in".
    for phrase in ("session expired", "you have been signed out", "you've been signed out",
                   "please log in again", "sign in to continue"):
        if phrase in lowered:
            return EXIT_LOGIN_REQUIRED
    return None


def detect_status_from_page(page) -> Optional[int]:
    """Structural check — URL and password field — rather than page prose."""
    try:
        import vault_browser as vb
        kind = vb.detect_security_challenge(page)
    except Exception:
        return None
    if kind in ("captcha", "waf"):
        return EXIT_CAPTCHA
    if kind == "login":
        return EXIT_LOGIN_REQUIRED
    return None


LINKEDIN_MAPPING = [
    ((r"\bfirst name\b",), "first_name"),
    ((r"\blast name\b",), "last_name"),
    ((r"\bfull name\b", r"\bname\b"), "full_name"),
    ((r"\be-?mail\b",), "email"),
    ((r"\bphone\b", r"\bmobile\b"), "phone"),
    ((r"\bcity\b", r"\bcurrent city\b", r"\blocation\b"), "city"),
    ((r"\bstate\b",), "state"),
    ((r"\bcountry\b",), "country"),
    ((r"\bpin\b", r"\bpostal\b", r"\bzip\b"), "pincode"),
    ((r"\bgithub\b", r"\bportfolio\b", r"\bwebsite\b"), "github"),
    ((r"\blinkedin\b",), "linkedin_profile"),
    ((r"\bnotice period\b", r"\bnotice\b"), "notice_period_days"),
    ((r"\bjoin\b", r"\bstart date\b", r"\bavailability\b"), "availability"),
    ((r"\bexpected salary\b", r"\bexpected ctc\b", r"\bdesired salary\b", r"\bcompensation\b"), "expected_ctc_min"),
    ((r"\bcurrent salary\b", r"\bcurrent ctc\b"), "current_ctc"),
    ((r"\bwork authorization\b", r"\blegally authorized\b"), "work_authorized"),
    ((r"\bsponsorship\b", r"\bvisa\b"), "requires_sponsorship"),
    ((r"\brelocat",), "open_to_relocate"),
    ((r"\bdegree\b",), "degree"),
    ((r"\buniversity\b", r"\binstitution\b", r"\bcollege\b"), "university"),
    # NOTE: the qa_bank entries that used to live here have been removed.
    # They matched on bare topic words — `\bleadership\b` answered
    # "Rate your leadership 1-10" with a 500-word essay — and duplicated
    # vault_answers, which now handles open-ended questions first and refuses
    # rating-style prompts outright. This table is identity fields only.
]


_WIDGET_LABEL = re.compile(
    r"\.pdf\b.*\.pdf\b|\.docx?\b.*\.docx?\b|"          # a list of stored files
    r"\b(upload|choose|select)\s+(a\s+)?(new\s+)?(resume|cv|file)|"
    r"\bbe sure to include an updated resume\b|"
    r"\bdrag and drop\b|\bsupported formats\b",
    re.I,
)


def _is_widget_not_question(label: str) -> bool:
    """True for file pickers and similar chrome that only look like fields."""
    return bool(_WIDGET_LABEL.search(label or ""))


# Labels this run declined to answer. A required one blocks the form, so the step
# loop would otherwise spin to its limit re-reading the same dead page.
UNANSWERED: list[str] = []


def answer_mapper(answer_bank: dict, label_text: str) -> Optional[str]:
    """Resolve a form field label to an answer.

    Order matters. This function previously did the opposite of what it should:
    LINKEDIN_MAPPING ran first (its blanket `\\bexperience\\b` rule answered
    "how many years with PowerShell?" with the candidate's TOTAL experience), and
    anything left over fell into

        is_yes_no = (... or "?" in label_lower or ...)
        if is_yes_no: return "Yes"

    — a blanket Yes for essentially every question on the form, which is how
    sponsorship, bond and inflated-experience questions all got affirmed.

    Now the question-aware policy in vault_answers decides first, and a field it
    will not answer is left BLANK rather than guessed. A blank required field
    fails the step visibly; a wrong answer does not.
    """
    label = clean_label(label_text)
    if not label:
        return None

    try:
        import vault_answers as va
        ans = va.answer_for_question(label, bank=answer_bank)
        if ans.decision is va.Decision.VALUE and ans.value:
            return ans.value
        if ans.decision is va.Decision.YES:
            return "Yes"
        if ans.decision is va.Decision.NO:
            return "No"
    except Exception as exc:  # never let policy failure fall through to a guess
        print(f"  [answer_mapper] policy error on {label[:60]!r}: {exc}", flush=True)
        return None

    # Identity fields only — unambiguous, no judgement involved.
    val = map_answer(label, answer_bank, LINKEDIN_MAPPING)
    if val is not None:
        return val

    # LinkedIn's resume picker is a radio list of previously uploaded files, not a
    # question. We upload a fresh file separately, so it must not be counted as an
    # unanswerable field — doing so blocked otherwise-valid applications.
    if _is_widget_not_question(label):
        return None

    print(f"  \u26a0 No answer for field: {label[:110]!r} — leaving blank", flush=True)
    UNANSWERED.append(label)
    return None


def clear_follow_company(dialog) -> None:
    labels = dialog.locator("label")
    for index in range(labels.count()):
        label = labels.nth(index)
        text = clean_label(label.inner_text()).casefold()
        if "follow company" in text:
            checkbox = label.locator('input[type="checkbox"]')
            if checkbox.count() > 0 and checkbox.first.is_checked():
                label.click()


def detect_external_redirect(page) -> bool:
    return "linkedin.com" not in page.url.casefold()


def find_action_button(dialog, names: list[str]):
    # Check for direct data attributes and common button text first
    if "Submit application" in names:
        btn = dialog.locator("button[data-easy-apply-submit-button], button:has-text('Submit')")
        if btn.count() > 0 and btn.first.is_visible():
            return btn.first
    if "Review your application" in names:
        btn = dialog.locator("button:has-text('Review')")
        if btn.count() > 0 and btn.first.is_visible():
            return btn.first
    if "Next" in names or "Continue to next step" in names:
        btn = dialog.locator("button[data-easy-apply-next-button], button:has-text('Next'), button:has-text('Continue')")
        if btn.count() > 0 and btn.first.is_visible():
            return btn.first

    for name in names:
        # Fallback to accessible name and text matches
        button = dialog.get_by_role("button", name=re.compile(re.escape(name), re.I))
        if button.count() > 0 and button.first.is_visible():
            return button.first
        button_text = dialog.locator("button, [role='button']").filter(has_text=re.compile(re.escape(name), re.I))
        if button_text.count() > 0 and button_text.first.is_visible():
            return button_text.first
    return None


def save_artifact(page, name: str) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(ARTIFACT_DIR / name), full_page=False)


def step_signature(dialog) -> str:
    """Cheap fingerprint of the current dialog, to detect a form that is stuck."""
    try:
        return dialog.inner_text()[:400]
    except Exception:
        return ""


def save_dry_run_state(page, name: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(LOG_DIR / name), full_page=False)


def execute_easy_apply(page, resume_path: Path, answer_bank: dict, dry_run: bool) -> int:
    text_status = detect_status_from_page(page) or detect_status_from_text(page.locator("body").inner_text())
    if text_status is not None:
        return text_status

    if detect_external_redirect(page):
        return EXIT_EXTERNAL_REDIRECT

    details_pane = page.locator("main, div.jobs-search__job-details--wrapper, div.jobs-details").first
    easy_apply = None
    if details_pane.count() > 0:
        easy_apply_locator = details_pane.locator("a, button, [role='button']").filter(has_text=re.compile(r"Easy Apply", re.I))
        if easy_apply_locator.count() > 0:
            easy_apply = easy_apply_locator.first
        else:
            easy_apply_locator = details_pane.locator("text=/Easy Apply/i")
            if easy_apply_locator.count() > 0:
                easy_apply = easy_apply_locator.first
                
    if easy_apply is None:
        easy_apply_locator = page.locator("a, button, [role='button']").filter(has_text=re.compile(r"Easy Apply", re.I))
        if easy_apply_locator.count() > 0:
            easy_apply = easy_apply_locator.first
        else:
            easy_apply_locator = page.locator("text=/Easy Apply/i")
            if easy_apply_locator.count() > 0:
                easy_apply = easy_apply_locator.first

    if easy_apply is None:
        save_artifact(page, "linkedin_easy_apply_missing_button.png")
        return EXIT_GENERIC_FAILURE
    try:
        easy_apply.scroll_into_view_if_needed(timeout=3000)
    except Exception:
        pass
    try:
        easy_apply.click(timeout=8000)
    except Exception:
        try:
            easy_apply.click(force=True, timeout=5000)
        except Exception:
            easy_apply.evaluate("el => el.click()")
    page.wait_for_timeout(6000)

    dialog = None
    try:
        candidates = page.locator('dialog, .artdeco-modal, [role="dialog"]')
        count = candidates.count()
        for idx in reversed(range(count)):
            candidate = candidates.nth(idx)
            is_msg = candidate.evaluate(
                "el => el.closest('#msg-overlay, .msg-overlay-container, .msg-overlay-bubble-header') !== null"
            )
            if not is_msg:
                dialog = candidate
                break
        
        if dialog is not None:
            dialog.wait_for(timeout=5000)
            print("Using matched non-message dialog container.")
            # Wait for dialog contents/inputs to load (spinner to disappear)
            try:
                # Wait for any loaders to be hidden
                dialog.locator('.artdeco-loader, .artdeco-loader__spinner, [aria-busy="true"]').first.wait_for(state="hidden", timeout=10000)
                # Wait for form buttons to be visible
                dialog.locator('button:has-text("Next"), button:has-text("Review"), button:has-text("Submit"), button:has-text("Continue")').first.wait_for(state="visible", timeout=10000)
            except Exception:
                pass
        else:
            raise Exception("No non-message dialog found")
    except Exception:
        # Fallback to main page if we navigated to a full-page apply form
        if "/apply/" in page.url:
            dialog = page
            print("Using main page as dialog container.")
        else:
            save_artifact(page, "linkedin_easy_apply_dialog_missing.png")
            return EXIT_GENERIC_FAILURE


    UNANSWERED.clear()
    stalled_signature = None
    stalled_count = 0

    for step in range(12):
        body_text = page.locator("body").inner_text()

        # Bail out when the same dialog reappears with fields we refuse to answer.
        # A required question outside our policy cannot be completed, so spinning
        # to the step limit just re-reads a dead page 12 times.
        if UNANSWERED:
            signature = (step_signature(dialog), tuple(sorted(set(UNANSWERED))))
            if signature == stalled_signature:
                stalled_count += 1
                if stalled_count >= 2:
                    save_artifact(page, f"linkedin_unanswerable_{step}.png")
                    print(f"  \U0001f6d1 Cannot complete: {len(set(UNANSWERED))} unanswerable "
                          f"required field(s) — {sorted(set(UNANSWERED))[:2]}", flush=True)
                    return EXIT_UNANSWERABLE
            else:
                stalled_signature, stalled_count = signature, 0
        text_status = detect_status_from_page(page) or detect_status_from_text(body_text)
        if text_status is not None:
            save_artifact(page, f"linkedin_easy_apply_status_{step}.png")
            return text_status

        if detect_external_redirect(page):
            save_artifact(page, f"linkedin_easy_apply_redirect_{step}.png")
            return EXIT_EXTERNAL_REDIRECT

        if dialog.locator("text=/Continue to application/i").count() > 0:
            save_artifact(page, f"linkedin_easy_apply_external_cta_{step}.png")
            return EXIT_EXTERNAL_REDIRECT

        maybe_upload_file(dialog, resume_path)
        fill_text_inputs(dialog, lambda label: answer_mapper(answer_bank, label))
        fill_textareas(dialog, lambda label: answer_mapper(answer_bank, label))
        fill_selects(dialog, lambda label: answer_mapper(answer_bank, label))
        fill_radio_groups(
            dialog,
            lambda label: answer_mapper(answer_bank, label),
            container_selector="fieldset",
            option_selector="label, span[data-test-text-selectable-option__label], div.fb-text-selectable__option",
        )
        clear_follow_company(dialog)

        # Dismiss any open typeahead/autocomplete dropdown before clicking buttons.
        # LinkedIn's suggestion overlay intercepts pointer events on the Next button.
        try:
            if page.locator("[data-test-single-typeahead-entity-form-search-result]").count() > 0:
                page.keyboard.press("Escape")
                page.wait_for_timeout(400)
        except Exception:
            pass

        submit_button = find_action_button(dialog, ["Submit application"])
        if submit_button is not None:
            if dry_run:
                save_dry_run_state(page, "linkedin_dry_run_state.png")
                return EXIT_SUCCESS
            submit_button.click()
            page.wait_for_timeout(3000)
            success_text = page.locator("body").inner_text().casefold()
            if "application submitted" in success_text or "your application was sent" in success_text:
                save_artifact(page, "linkedin_easy_apply_submitted.png")
                return EXIT_SUCCESS
            save_artifact(page, "linkedin_easy_apply_submit_postcheck.png")
            return EXIT_GENERIC_FAILURE

        review_button = find_action_button(dialog, ["Review your application"])
        if review_button is not None:
            review_button.click()
            page.wait_for_timeout(1500)
            continue

        next_button = find_action_button(dialog, ["Continue to next step", "Next"])
        if next_button is not None:
            next_button.click()
            page.wait_for_timeout(1800)
            continue

        save_artifact(page, f"linkedin_easy_apply_unknown_step_{step}.png")
        return EXIT_GENERIC_FAILURE

    save_artifact(page, "linkedin_easy_apply_step_limit.png")
    return EXIT_GENERIC_FAILURE


def main() -> int:
    args = parse_args()
    resume_path = Path(args.resume_path).expanduser().resolve()
    if not resume_path.exists():
        print(json.dumps({"status": "error", "reason": "resume file not found"}), file=sys.stderr)
        return EXIT_GENERIC_FAILURE

    answer_bank = build_answer_bank()

    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        print(json.dumps({"status": "error", "reason": f"playwright import failed: {exc}"}), file=sys.stderr)
        return EXIT_GENERIC_FAILURE

    profile_dir = Path(
        os.environ.get(
            "LINKEDIN_PLAYWRIGHT_PROFILE_DIR",
            str(VAULT_ROOT / "active_application_context" / "playwright" / "linkedin-profile"),
        )
    ).expanduser()
    headless = os.environ.get("LINKEDIN_PLAYWRIGHT_HEADLESS", "1").lower() not in {"0", "false", "no"}

    use_cdp = os.environ.get("PLAYWRIGHT_USE_CDP", "").lower() in {"1", "true", "yes"}
    cdp_url = os.environ.get("PLAYWRIGHT_CDP_URL", "http://localhost:9222")

    with sync_playwright() as playwright:
        if use_cdp:
            browser = playwright.chromium.connect_over_cdp(cdp_url, no_defaults=True)
            context = browser.contexts[0]
            page = context.new_page()
        else:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                headless=headless,
                channel=os.environ.get("LINKEDIN_PLAYWRIGHT_CHANNEL") or None,
                viewport={"width": 1440, "height": 1200},
            )
            page = context.pages[0] if context.pages else context.new_page()

        try:
            page.goto(args.application_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)
            exit_code = execute_easy_apply(page, resume_path, answer_bank, args.dry_run)
            result = {
                "status": "ok" if exit_code == EXIT_SUCCESS else "error",
                "exit_code": exit_code,
                "application_url": args.application_url,
                "dry_run": args.dry_run,
            }
            stream = sys.stdout if exit_code == EXIT_SUCCESS else sys.stderr
            print(json.dumps(result), file=stream)
            return exit_code
        finally:
            if use_cdp:
                page.close()
            else:
                context.close()


if __name__ == "__main__":
    raise SystemExit(main())
