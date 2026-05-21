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

VAULT_ROOT = Path(__file__).resolve().parents[1]
FACT_SHEET_PATH = VAULT_ROOT / "core_vault" / "JobApplyFiles" / "01_atomic_fact_sheet.json"
LOGISTICS_PATH = VAULT_ROOT / "core_vault" / "JobApplyFiles" / "06_logistics_mapping.json"
ARTIFACT_DIR = VAULT_ROOT / "output" / "playwright"
LOG_DIR = VAULT_ROOT / "logs"

NAUKRI_DOMAINS = ("naukri.com", "naukri.com")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministic Naukri application executor."
    )
    parser.add_argument("--application-url", required=True)
    parser.add_argument("--resume-path", required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def build_answer_bank() -> dict:
    answer_bank = build_base_answer_bank(FACT_SHEET_PATH, LOGISTICS_PATH)
    # Naukri CTC fields are in LPA as plain numbers
    answer_bank["naukri_current_ctc"] = "0"
    answer_bank["naukri_expected_ctc"] = str(
        answer_bank.get("expected_ctc_min", "15")
    )
    answer_bank["naukri_notice_period"] = "0"  # 0 weeks / immediately
    return answer_bank


def detect_status_from_text(text: str) -> Optional[int]:
    lowered = text.casefold()
    if "captcha" in lowered or "verify you are human" in lowered or "robot" in lowered:
        return EXIT_CAPTCHA
    if (
        "login" in lowered or "sign in" in lowered or "nlogin" in lowered
    ) and "naukri" in lowered:
        return EXIT_LOGIN_REQUIRED
    return None


def save_artifact(page, name: str) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(ARTIFACT_DIR / name), full_page=False)


def save_dry_run_state(page, name: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(LOG_DIR / name), full_page=False)


NAUKRI_MAPPING = [
    ((r"\bfirst name\b",), "first_name"),
    ((r"\blast name\b",), "last_name"),
    ((r"\bfull name\b", r"\bname\b"), "full_name"),
    ((r"\be-?mail\b",), "email"),
    ((r"\bphone\b", r"\bmobile\b"), "phone"),
    ((r"\bcity\b", r"\blocation\b", r"\bcurrent location\b"), "city"),
    ((r"\bstate\b",), "state"),
    ((r"\bcountry\b",), "country"),
    ((r"\bgithub\b", r"\bportfolio\b", r"\bwebsite\b"), "github"),
    ((r"\blinkedin\b",), "linkedin_profile"),
    ((r"\bcurrent ctc\b", r"\bcurrent salary\b", r"\bpresent ctc\b"), "naukri_current_ctc"),
    ((r"\bexpected ctc\b", r"\bexpected salary\b", r"\bdesired ctc\b"), "naukri_expected_ctc"),
    ((r"\bnotice period\b", r"\bnotice\b", r"\bjoining time\b"), "naukri_notice_period"),
    ((r"\bcover\b", r"\bwhy.*interest\b", r"\bmessage\b", r"\bnote\b"), "qa_about_me"),
    ((r"\bavailability\b", r"\bstart date\b", r"\bjoin\b"), "availability"),
    ((r"\bexperience\b", r"\byears of\b"), "years_experience"),
    ((r"\bwork authorization\b", r"\blegally authorized\b"), "work_authorized"),
    ((r"\bsponsorship\b", r"\bvisa\b"), "requires_sponsorship"),
    ((r"\brelocat",), "open_to_relocate"),
    ((r"\bdegree\b",), "degree"),
    ((r"\buniversity\b", r"\binstitution\b", r"\bcollege\b"), "university"),
]


def answer_mapper(answer_bank: dict, label_text: str) -> Optional[str]:
    return map_answer(label_text, answer_bank, NAUKRI_MAPPING)


def detect_external_redirect(page) -> bool:
    url = page.url.casefold()
    return "naukri.com" not in url


def find_apply_button(page):
    """Find the primary Apply button on the Naukri job detail page."""
    candidates = [
        page.get_by_role("button", name=re.compile(r"apply now", re.I)),
        page.get_by_role("button", name=re.compile(r"^apply$", re.I)),
        page.locator("a.apply-button"),
        page.locator("[class*='applyButton']"),
        page.locator("[class*='apply-button']"),
        page.locator("[id*='apply-button']"),
        page.locator("button[class*='apply']"),
    ]
    for locator in candidates:
        try:
            if locator.count() > 0 and locator.first.is_visible():
                return locator.first
        except Exception:
            continue
    return None


def find_apply_modal(page):
    """Find the apply modal / drawer after clicking Apply."""
    candidates = [
        page.locator("[class*='applyModal']"),
        page.locator("[class*='apply-modal']"),
        page.locator("[class*='DrawerContainer']"),
        page.locator("[class*='chatbot']"),
        page.locator("[role='dialog']"),
    ]
    for locator in candidates:
        try:
            if locator.count() > 0 and locator.first.is_visible():
                return locator.first
        except Exception:
            continue
    return None


def fill_naukri_ctc(root, answer_bank: dict) -> None:
    """Fill Naukri's dedicated CTC input fields by placeholder/label patterns."""
    for selector, key in [
        ("input[placeholder*='Current']", "naukri_current_ctc"),
        ("input[placeholder*='current']", "naukri_current_ctc"),
        ("input[id*='current'][id*='sal']", "naukri_current_ctc"),
        ("input[id*='currentSalary']", "naukri_current_ctc"),
        ("input[placeholder*='Expected']", "naukri_expected_ctc"),
        ("input[placeholder*='expected']", "naukri_expected_ctc"),
        ("input[id*='expected'][id*='sal']", "naukri_expected_ctc"),
        ("input[id*='expectedSalary']", "naukri_expected_ctc"),
    ]:
        try:
            el = root.locator(selector)
            if el.count() > 0 and el.first.is_visible() and not el.first.is_disabled():
                if not el.first.input_value().strip():
                    el.first.fill(answer_bank[key])
        except Exception:
            continue


def fill_naukri_notice(root, answer_bank: dict) -> None:
    """Fill Naukri notice period dropdown — select the shortest option."""
    selectors = [
        "select[name*='notice']",
        "select[id*='notice']",
        "select[placeholder*='notice']",
        "[class*='notice'] select",
    ]
    for selector in selectors:
        try:
            el = root.locator(selector)
            if el.count() == 0 or not el.first.is_visible():
                continue
            # Try selecting "Immediately" or "0" or the first option
            options = el.first.locator("option")
            for i in range(options.count()):
                opt_text = clean_label(options.nth(i).inner_text()).casefold()
                if any(k in opt_text for k in ("immediate", "0 day", "less than 15", "15 day", "1 week")):
                    el.first.select_option(index=i)
                    return
            # Fallback: select option index 1 (skip empty placeholder)
            if options.count() > 1:
                el.first.select_option(index=1)
        except Exception:
            continue


def find_action_button(root, names: list[str]):
    for name in names:
        button = root.get_by_role("button", name=re.compile(re.escape(name), re.I))
        if button.count() > 0 and button.first.is_visible():
            return button.first
    return None


def execute_apply(page, resume_path: Path, answer_bank: dict, dry_run: bool) -> int:
    status = detect_status_from_text(page.locator("body").inner_text())
    if status is not None:
        return status

    if detect_external_redirect(page):
        return EXIT_EXTERNAL_REDIRECT

    # Click the Apply button on the job detail page
    apply_btn = find_apply_button(page)
    if apply_btn is None:
        save_artifact(page, "naukri_apply_button_missing.png")
        return EXIT_GENERIC_FAILURE

    apply_btn.click()
    page.wait_for_timeout(2500)

    status = detect_status_from_text(page.locator("body").inner_text())
    if status is not None:
        save_artifact(page, "naukri_post_click_status.png")
        return status

    if detect_external_redirect(page):
        save_artifact(page, "naukri_external_redirect.png")
        return EXIT_EXTERNAL_REDIRECT

    # Check for "Apply on company website" pattern (Naukri redirects to ATS)
    body_text = page.locator("body").inner_text().casefold()
    if "apply on company website" in body_text or "external application" in body_text:
        save_artifact(page, "naukri_external_ats.png")
        return EXIT_EXTERNAL_REDIRECT

    # Try to find the modal/drawer
    modal = find_apply_modal(page)
    root = modal if modal is not None else page.locator("body")

    for step in range(10):
        body_text = page.locator("body").inner_text()
        status = detect_status_from_text(body_text)
        if status is not None:
            save_artifact(page, f"naukri_status_{step}.png")
            return status

        if detect_external_redirect(page):
            save_artifact(page, f"naukri_redirect_{step}.png")
            return EXIT_EXTERNAL_REDIRECT

        # Upload resume if file input present
        maybe_upload_file(root, resume_path)

        # Fill Naukri-specific CTC and notice fields first
        fill_naukri_ctc(root, answer_bank)
        fill_naukri_notice(root, answer_bank)

        # Fill generic text fields
        fill_text_inputs(root, lambda label: answer_mapper(answer_bank, label))
        fill_textareas(root, lambda label: answer_mapper(answer_bank, label))
        fill_selects(root, lambda label: answer_mapper(answer_bank, label))
        fill_radio_groups(
            root,
            lambda label: answer_mapper(answer_bank, label),
            container_selector="fieldset, [role='radiogroup'], [class*='radio-group']",
            option_selector="label, [role='radio'], button",
        )

        # Check for submit / apply button inside modal
        submit_btn = find_action_button(
            root, ["Apply", "Apply Now", "Submit", "Send Application"]
        )
        if submit_btn is not None:
            if dry_run:
                save_dry_run_state(page, "naukri_dry_run_state.png")
                return EXIT_SUCCESS
            submit_btn.click()
            page.wait_for_timeout(2500)
            success_text = page.locator("body").inner_text().casefold()
            if any(
                phrase in success_text
                for phrase in (
                    "application sent",
                    "application submitted",
                    "applied successfully",
                    "thank you for applying",
                    "your application",
                )
            ):
                save_artifact(page, "naukri_submitted.png")
                return EXIT_SUCCESS
            save_artifact(page, "naukri_submit_postcheck.png")
            return EXIT_GENERIC_FAILURE

        # Next / Continue button
        next_btn = find_action_button(root, ["Next", "Continue", "Proceed"])
        if next_btn is not None:
            next_btn.click()
            page.wait_for_timeout(1500)
            # Refresh modal reference after navigation
            modal = find_apply_modal(page)
            root = modal if modal is not None else page.locator("body")
            continue

        # If first step has inputs, keep iterating
        if step == 0 and root.locator("input, textarea, select").count() > 0:
            continue

        save_artifact(page, f"naukri_unknown_step_{step}.png")
        return EXIT_GENERIC_FAILURE

    save_artifact(page, "naukri_step_limit.png")
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

    headless = os.environ.get("NAUKRI_PLAYWRIGHT_HEADLESS", "").lower() in {"1", "true", "yes"}
    profile_dir = Path(
        os.environ.get(
            "NAUKRI_PLAYWRIGHT_PROFILE_DIR",
            str(VAULT_ROOT / "active_application_context" / "playwright" / "naukri-profile"),
        )
    ).expanduser()
    profile_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=headless,
            channel=os.environ.get("NAUKRI_PLAYWRIGHT_CHANNEL") or None,
            viewport={"width": 1440, "height": 1200},
        )
        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(args.application_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2500)
            exit_code = execute_apply(page, resume_path, answer_bank, args.dry_run)
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
            context.close()


if __name__ == "__main__":
    raise SystemExit(main())
