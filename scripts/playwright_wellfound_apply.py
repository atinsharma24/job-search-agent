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
    build_field_key,
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
WELLFOUND_DOMAINS = ("wellfound.com", "angel.co")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministic Wellfound application executor."
    )
    parser.add_argument("--application-url", required=True)
    parser.add_argument("--resume-path", required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def build_answer_bank() -> dict:
    answer_bank = build_base_answer_bank(FACT_SHEET_PATH, LOGISTICS_PATH)

    pitch = (
        "Founding engineer with hands-on experience building production AI and full-stack "
        "systems at OpenBiz. Shipped WhatsApp-native LLM workflows, RAG pipelines, and "
        "TypeScript backend systems with measurable latency improvements. Immediate joiner."
    )

    answer_bank["pitch"] = pitch
    answer_bank["location"] = (
        f"{answer_bank['city']}, {answer_bank['state']}, {answer_bank['country']}"
    )
    return answer_bank


def detect_status_from_text(text: str) -> Optional[int]:
    lowered = text.casefold()
    if "captcha" in lowered or "security check" in lowered or "verify you are human" in lowered:
        return EXIT_CAPTCHA
    if "sign in" in lowered or "log in" in lowered:
        if "wellfound" in lowered or "angel" in lowered:
            return EXIT_LOGIN_REQUIRED
    return None


def save_artifact(page, name: str) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(ARTIFACT_DIR / name), full_page=False)


def save_dry_run_state(page, name: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(LOG_DIR / name), full_page=False)


WELLFOUND_MAPPING = [
    ((r"\bfirst name\b",), "first_name"),
    ((r"\blast name\b",), "last_name"),
    ((r"\bfull name\b", r"\bname\b"), "full_name"),
    ((r"\be-?mail\b",), "email"),
    ((r"\bphone\b", r"\bmobile\b"), "phone"),
    ((r"\bcity\b", r"\blocation\b"), "city"),
    ((r"\bcountry\b",), "country"),
    ((r"\bgithub\b", r"\bportfolio\b", r"\bwebsite\b"), "github"),
    ((r"\blinkedin\b",), "linkedin_profile"),
    ((r"\bpitch\b", r"\bwhy .*interested\b", r"\bwhy .*join\b", r"\babout yourself\b", r"\bsummary\b"), "qa_about_me"),
    ((r"\bavailability\b", r"\bstart date\b", r"\bnotice\b", r"\bjoin\b"), "availability"),
    ((r"\bexperience\b", r"\byears of\b"), "years_experience"),
    ((r"\bsalary\b", r"\bcompensation\b", r"\bctc\b"), "expected_salary_min"),
    ((r"\bwork authorization\b", r"\blegally authorized\b"), "work_authorized"),
    ((r"\bsponsorship\b", r"\bvisa\b"), "requires_sponsorship"),
    ((r"\brelocat",), "open_to_relocate"),
    ((r"\bdegree\b",), "degree"),
    ((r"\buniversity\b", r"\binstitution\b", r"\bcollege\b"), "university"),
    # Open-ended text / textarea questions — answered from qa_bank
    ((r"\btechnical challenge\b", r"\bcomplex bug\b", r"\bperformance issue\b", r"\bdifficult problem\b"), "qa_tech_challenge"),
    ((r"\bproduct you built\b", r"\bside project\b", r"\bmost proud\b", r"\bbuild from scratch\b"), "qa_innovation"),
    ((r"\bconflict\b", r"\binitiative\b", r"\bteam problem\b", r"\bleadership\b", r"\btook ownership\b"), "qa_leadership"),
    ((r"\bproduct impact\b", r"\bend users\b", r"\bhow.*helped\b", r"\buser value\b"), "qa_product_impact"),
    ((r"\bwhy.*role\b", r"\bwhy.*position\b", r"\bwhy.*company\b", r"\bmotivation\b"), "qa_why_role"),
    ((r"\bcover letter\b", r"\bcover note\b", r"\badditional information\b", r"\banything else\b"), "qa_about_me"),
]


def answer_mapper(answer_bank: dict, label_text: str) -> Optional[str]:
    return map_answer(label_text, answer_bank, WELLFOUND_MAPPING)


def fill_ranges(root, answer_bank: dict) -> None:
    sliders = root.locator('input[type="range"]')
    for index in range(sliders.count()):
        locator = sliders.nth(index)
        if not locator.is_visible() or locator.is_disabled():
            continue
        label = build_field_key(locator).casefold()
        if "experience" in label:
            target = answer_bank["years_experience"]
        elif "notice" in label or "availability" in label:
            target = answer_bank["notice_period_days"]
        else:
            continue
        locator.evaluate(
            """(element, value) => {
                element.value = value;
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
            }""",
            target,
        )


def detect_external_redirect(page) -> bool:
    url = page.url.casefold()
    return not any(domain in url for domain in WELLFOUND_DOMAINS)


def find_action_button(root, names: list[str]):
    for name in names:
        button = root.get_by_role("button", name=re.compile(re.escape(name), re.I))
        if button.count() > 0 and button.first.is_visible():
            return button.first
    return None


def find_apply_root(page):
    dialog = page.locator('[role="dialog"]')
    if dialog.count() > 0 and dialog.last.is_visible():
        return dialog.last
    return page.locator("body")


def click_entry_apply(page) -> None:
    body = page.locator("body")
    candidates = [
        "Apply now",
        "Apply",
        "Easy Apply",
    ]
    for name in candidates:
        button = page.get_by_role("button", name=re.compile(re.escape(name), re.I))
        if button.count() > 0 and button.first.is_visible():
            button.first.click()
            page.wait_for_timeout(1500)
            return
    if body.locator("text=/Apply now/i").count() > 0:
        body.locator("text=/Apply now/i").first.click()
        page.wait_for_timeout(1500)


def execute_apply(page, resume_path: Path, answer_bank: dict, dry_run: bool) -> int:
    status = detect_status_from_text(page.locator("body").inner_text())
    if status is not None:
        return status

    click_entry_apply(page)

    for step in range(10):
        body_text = page.locator("body").inner_text()
        status = detect_status_from_text(body_text)
        if status is not None:
            save_artifact(page, f"wellfound_status_{step}.png")
            return status

        if detect_external_redirect(page):
            save_artifact(page, f"wellfound_redirect_{step}.png")
            return EXIT_EXTERNAL_REDIRECT

        if "company website" in body_text.casefold() or "external application" in body_text.casefold():
            save_artifact(page, f"wellfound_external_{step}.png")
            return EXIT_EXTERNAL_REDIRECT

        root = find_apply_root(page)
        maybe_upload_file(root, resume_path)
        fill_text_inputs(
            root,
            lambda label: answer_mapper(answer_bank, label),
            wrapper_selector="[data-testid], .application-form, form, fieldset",
            selector='input:not([type="hidden"]):not([type="file"]):not([type="radio"]):not([type="checkbox"]):not([type="range"])',
        )
        fill_textareas(
            root,
            lambda label: answer_mapper(answer_bank, label),
            wrapper_selector="[data-testid], .application-form, form, fieldset",
        )
        fill_selects(
            root,
            lambda label: answer_mapper(answer_bank, label),
            wrapper_selector="[data-testid], .application-form, form, fieldset",
        )
        fill_radio_groups(
            root,
            lambda label: answer_mapper(answer_bank, label),
            container_selector="fieldset, [role='radiogroup']",
            option_selector="label, button, [role='radio']",
        )
        fill_ranges(root, answer_bank)

        submit_button = find_action_button(
            root,
            ["Submit application", "Submit", "Send application", "Apply now"],
        )
        if submit_button is not None:
            if dry_run:
                save_dry_run_state(page, "wellfound_dry_run_state.png")
                return EXIT_SUCCESS
            submit_button.click()
            page.wait_for_timeout(2500)
            success_text = page.locator("body").inner_text().casefold()
            if "application sent" in success_text or "application submitted" in success_text or "you applied" in success_text:
                save_artifact(page, "wellfound_submitted.png")
                return EXIT_SUCCESS
            save_artifact(page, "wellfound_submit_postcheck.png")
            return EXIT_GENERIC_FAILURE

        next_button = find_action_button(root, ["Continue", "Next", "Review"])
        if next_button is not None:
            next_button.click()
            page.wait_for_timeout(1200)
            continue

        if step == 0 and root.locator("input, textarea, select").count() > 0:
            continue

        save_artifact(page, f"wellfound_unknown_step_{step}.png")
        return EXIT_GENERIC_FAILURE

    save_artifact(page, "wellfound_step_limit.png")
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

    headless = os.environ.get("WELLFOUND_PLAYWRIGHT_HEADLESS", "").lower() in {"1", "true", "yes"}
    profile_dir = Path(
        os.environ.get(
            "WELLFOUND_PLAYWRIGHT_PROFILE_DIR",
            str(VAULT_ROOT / "active_application_context" / "playwright" / "wellfound-profile"),
        )
    ).expanduser()
    profile_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=headless,
            channel=os.environ.get("WELLFOUND_PLAYWRIGHT_CHANNEL") or None,
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
