#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright is not installed. Please install it to use this script.", file=sys.stderr)
    sys.exit(1)

VAULT_ROOT = Path(__file__).resolve().parents[2]
TRACKER_PATH = VAULT_ROOT / "active_application_context" / "job_applications_tracker.md"
FALLBACK_AGENT = Path(__file__).parent / "ats_fallback_agent.py"

# Add scripts dir to sys.path to import helpers
sys.path.append(str(VAULT_ROOT / "scripts"))
from playwright_form_helpers import build_base_answer_bank, map_answer

FACT_SHEET_PATH = VAULT_ROOT / "core_vault" / "JobApplyFiles" / "01_atomic_fact_sheet.json"
LOGISTICS_PATH = VAULT_ROOT / "core_vault" / "JobApplyFiles" / "06_logistics_mapping.json"

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
    ((r"\bexperience\b", r"\byears of\b"), "years_experience"),
    ((r"\bexpected salary\b", r"\bexpected ctc\b", r"\bdesired salary\b", r"\bcompensation\b"), "expected_ctc_min"),
    ((r"\bcurrent salary\b", r"\bcurrent ctc\b"), "current_ctc"),
    ((r"\bwork authorization\b", r"\blegally authorized\b"), "work_authorized"),
    ((r"\bsponsorship\b", r"\bvisa\b"), "requires_sponsorship"),
    ((r"\brelocat",), "open_to_relocate"),
    ((r"\bdegree\b",), "degree"),
    ((r"\buniversity\b", r"\binstitution\b", r"\bcollege\b"), "university"),
    ((r"\bpassword\b", r"\bcreate password\b", r"\bconfirm password\b"), "password"),
]

def answer_mapper(answer_bank: dict, label_text: str):
    val = map_answer(label_text, answer_bank, LINKEDIN_MAPPING)
    if val is not None:
        return val

    label_lower = label_text.casefold()
    
    # Don't treat "why", "how", "what", "describe", "explain" as yes/no even if they have question marks
    if any(open_word in label_lower for open_word in ["why", "how", "what", "describe", "explain", "details"]):
        return None
        
    is_yes_no = (
        any(label_lower.startswith(prefix) for prefix in ["do you", "have you", "are you", "will you", "would you", "is ", "can "])
        or "?" in label_lower
        or "experience" in label_lower
        or "worked on" in label_lower
        or "willing to" in label_lower
        or "authorized" in label_lower
    )

    if is_yes_no:
        if any(kw in label_lower for kw in ["sponsorship", "visa", "clearance", "convicted", "felony", "drug", "crime"]):
            return "No"
        return "Yes"

    return None

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simplify Jobs integration orchestrator using Playwright CDP.")
    parser.add_argument("--application-url", required=True, help="The ATS job URL to apply to.")
    parser.add_argument("--dry-run", action="store_true", help="Do not actually click submit.")
    return parser.parse_args()

def log_application(url: str, status: str, notes: str):
    TRACKER_PATH.parent.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"\n| {date_str} | [Simplify-Integration] {url} | {status} | {notes} |"
    
    with open(TRACKER_PATH, "a") as f:
        f.write(log_entry)
    print(f"Logged application status: {status}")

def get_llm_answer(label: str) -> str:
    print(f"Asking LLM for: {label}")
    try:
        result = subprocess.run(
            [sys.executable, str(FALLBACK_AGENT), label],
            capture_output=True,
            text=True,
            check=True
        )
        if result.stderr.strip():
            print(f"Fallback Agent Log: {result.stderr.strip()}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error querying LLM: {e.stderr}", file=sys.stderr)
        return ""

def apply_to_page(page, url: str, dry_run: bool = False):
    try:
        # Load answer bank locally so we don't have to keep reloading it
        answer_bank = build_base_answer_bank(FACT_SHEET_PATH, LOGISTICS_PATH)
        
        # Inject specific credentials
        answer_bank["email"] = "atinsharma24@gmail.com"
        answer_bank["password"] = "Avengers@123"

        for step in range(10): # Pagination loop
            print(f"--- Application Step {step + 1} ---")
            # Wait for Simplify extension to autofill
            print("Waiting 6 seconds for Simplify extension to populate fields...")
            time.sleep(6)
            
            # Fallback logic: Find all unfilled input/textarea elements
            unfilled_selectors = [
                "input[type='text']:visible",
                "input[type='email']:visible",
                "input[type='password']:visible",
                "textarea:visible"
            ]
            
            for selector in unfilled_selectors:
                elements = page.locator(selector).all()
                for el in elements:
                    current_val = el.input_value()
                    if current_val and current_val.strip() != "":
                        continue
                        
                    id_attr = el.get_attribute("id")
                    label_text = ""
                    if id_attr:
                        label_el = page.locator(f"label[for='{id_attr}']")
                        if label_el.count() > 0:
                            label_text = label_el.first.inner_text().strip()
                    
                    if not label_text:
                        parent_label = el.locator("xpath=ancestor::label")
                        if parent_label.count() > 0:
                            label_text = parent_label.first.inner_text().strip()
                    
                    if label_text:
                        # First try hardcoded dictionary mapped answer
                        answer = answer_mapper(answer_bank, label_text)
                        if answer:
                            print(f"Filling mapping answer for '{label_text}': {'***' if answer == 'Avengers@123' else answer[:50]}...")
                            el.fill(answer)
                            continue
                            
                        # Fallback to LLM
                        answer = get_llm_answer(label_text)
                        if answer:
                            print(f"Filling LLM answer for '{label_text}': {answer[:50]}...")
                            el.fill(answer)
                        else:
                            print(f"Could not get an answer for '{label_text}'")

            # Blindly check any mandatory/unchecked checkboxes (consent forms, TOS)
            checkboxes = page.locator("input[type='checkbox']:visible").all()
            for cb in checkboxes:
                try:
                    if not cb.is_checked():
                        cb.check(force=True)
                except Exception:
                    pass

            # Comprehensive Submit button selector
            submit_texts = ['Submit Application', 'Submit']
            sub_selectors = []
            for t in submit_texts:
                sub_selectors.append(f"button:has-text('{t}')")
                sub_selectors.append(f"a:has-text('{t}')")
                sub_selectors.append(f"div[role='button']:has-text('{t}')")
                sub_selectors.append(f"input[type='button'][value='{t}']")
                sub_selectors.append(f"input[type='submit'][value='{t}']")
            
            submit_button = page.locator(", ".join(sub_selectors)).first
            if submit_button.count() > 0 and submit_button.is_visible():
                if dry_run:
                    print("Dry run enabled. Not submitting.")
                    log_application(url, "Dry-Run Complete", "Reached submit, dry-run triggered")
                    return 0
                submit_button.click(force=True)
                print("Clicked submit (forced)!")
                time.sleep(3) # wait for submission to register
                log_application(url, "Submitted", "Successfully applied via Simplify-Integration")
                return 0
                
            # Comprehensive Progression button selector
            prog_texts = ['Next', 'Save and Continue', 'Create Account', 'Sign In', 'Apply', 'Apply Now', 'Continue', 'Accept', 'I Agree']
            prog_selectors = []
            for t in prog_texts:
                prog_selectors.append(f"button:has-text('{t}')")
                prog_selectors.append(f"a:has-text('{t}')")
                prog_selectors.append(f"div[role='button']:has-text('{t}')")
                prog_selectors.append(f"span[role='button']:has-text('{t}')")
                prog_selectors.append(f"input[type='button'][value='{t}']")
                prog_selectors.append(f"input[type='submit'][value='{t}']")
                
            progress_btn = page.locator(", ".join(prog_selectors)).first
            if progress_btn.count() > 0 and progress_btn.is_visible():
                print(f"Found progression button. Clicking (forced)...")
                progress_btn.click(force=True)
                time.sleep(5) # wait for next page
            else:
                if dry_run:
                    print("Dry run enabled. Form filled.")
                    log_application(url, "Dry-Run Complete", "Form filled, no buttons found")
                    return 0
                print("Submit or progression button not found!")
                log_application(url, "Failed", "Could not find progression or submit button")
                return 1
                
        print("Reached max pagination steps.")
        log_application(url, "Failed", "Max pagination steps reached")
        return 1
            
    except Exception as e:
        print(f"An error occurred during application: {e}", file=sys.stderr)
        log_application(url, "Error", str(e)[:100])
        return 1

def main():
    args = parse_args()
    
    cdp_url = os.environ.get("PLAYWRIGHT_CDP_URL", "http://localhost:9222")
    
    with sync_playwright() as p:
        try:
            print(f"Connecting to Chrome over CDP at {cdp_url}...")
            browser = p.chromium.connect_over_cdp(cdp_url)
            context = browser.contexts[0]
            
            page = context.pages[0] if context.pages else context.new_page()
            
            print(f"Navigating to {args.application_url}")
            page.goto(args.application_url, wait_until="domcontentloaded")
            
            return apply_to_page(page, args.application_url, args.dry_run)
            
        except Exception as e:
            print(f"An error occurred: {e}", file=sys.stderr)
            return 1
        finally:
            print("Done.")

if __name__ == "__main__":
    sys.exit(main())
