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
    lowered = text.casefold()
    if "captcha" in lowered or "security verification" in lowered or "suspicious activity" in lowered:
        return EXIT_CAPTCHA
    if "sign in" in lowered and "linkedin" in lowered:
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
    ((r"\bnotice\b", r"\bjoin\b", r"\bstart date\b", r"\bavailability\b"), "availability"),
    ((r"\bexperience\b", r"\byears of\b"), "years_experience"),
    ((r"\bexpected salary\b", r"\bexpected ctc\b", r"\bdesired salary\b", r"\bcompensation\b"), "expected_ctc_min"),
    ((r"\bcurrent salary\b", r"\bcurrent ctc\b"), "current_ctc"),
    ((r"\bwork authorization\b", r"\blegally authorized\b"), "work_authorized"),
    ((r"\bsponsorship\b", r"\bvisa\b"), "requires_sponsorship"),
    ((r"\brelocat",), "open_to_relocate"),
    ((r"\bdegree\b",), "degree"),
    ((r"\buniversity\b", r"\binstitution\b", r"\bcollege\b"), "university"),
    # Open-ended text / textarea questions — answered from qa_bank
    ((r"\btell us about yourself\b", r"\babout yourself\b", r"\bintroduce yourself\b", r"\bbackground\b"), "qa_about_me"),
    ((r"\btechnical challenge\b", r"\bcomplex bug\b", r"\bperformance issue\b", r"\bdifficult problem\b"), "qa_tech_challenge"),
    ((r"\bproduct you built\b", r"\bside project\b", r"\bmost proud\b", r"\bbuild from scratch\b"), "qa_innovation"),
    ((r"\bconflict\b", r"\binitiative\b", r"\bteam problem\b", r"\bleadership\b", r"\btook ownership\b"), "qa_leadership"),
    ((r"\bproduct impact\b", r"\bend users\b", r"\bhow.*helped\b", r"\buser value\b"), "qa_product_impact"),
    ((r"\bwhy.*role\b", r"\bwhy.*position\b", r"\bwhy.*company\b", r"\bwhy.*interest\b", r"\bmotivation\b"), "qa_why_role"),
    ((r"\bcover letter\b", r"\bcover note\b", r"\badditional information\b", r"\banything else\b"), "qa_about_me"),
]


def answer_mapper(answer_bank: dict, label_text: str) -> Optional[str]:
    return map_answer(label_text, answer_bank, LINKEDIN_MAPPING)


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
    for name in names:
        button = dialog.get_by_role("button", name=re.compile(rf"^{re.escape(name)}$", re.I))
        if button.count() > 0 and button.first.is_visible():
            return button.first
    return None


def save_artifact(page, name: str) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(ARTIFACT_DIR / name), full_page=False)


def save_dry_run_state(page, name: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(LOG_DIR / name), full_page=False)


def execute_easy_apply(page, resume_path: Path, answer_bank: dict, dry_run: bool) -> int:
    text_status = detect_status_from_text(page.locator("body").inner_text())
    if text_status is not None:
        return text_status

    if detect_external_redirect(page):
        return EXIT_EXTERNAL_REDIRECT

    easy_apply = page.get_by_role("button", name=re.compile(r"Easy Apply", re.I))
    if easy_apply.count() == 0:
        save_artifact(page, "linkedin_easy_apply_missing_button.png")
        return EXIT_GENERIC_FAILURE
    easy_apply.first.click()

    dialog = page.locator('[role="dialog"]').last
    dialog.wait_for(timeout=15000)

    for step in range(12):
        body_text = page.locator("body").inner_text()
        text_status = detect_status_from_text(body_text)
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
            page.wait_for_timeout(1500)
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

    headless = os.environ.get("LINKEDIN_PLAYWRIGHT_HEADLESS", "").lower() in {"1", "true", "yes"}
    profile_dir = Path(
        os.environ.get(
            "LINKEDIN_PLAYWRIGHT_PROFILE_DIR",
            str(VAULT_ROOT / "active_application_context" / "playwright" / "linkedin-profile"),
        )
    ).expanduser()
    profile_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=headless,
            channel=os.environ.get("LINKEDIN_PLAYWRIGHT_CHANNEL") or None,
            viewport={"width": 1440, "height": 1200},
        )
        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(args.application_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2500)
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
            context.close()


if __name__ == "__main__":
    raise SystemExit(main())
