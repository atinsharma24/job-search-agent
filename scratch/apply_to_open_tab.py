import sys
import re
from pathlib import Path

# Add scripts folder to sys.path
sys.path.append(str(Path("/Users/atinsharma/job_search_vault/scripts")))

from playwright.sync_api import sync_playwright
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

VAULT_ROOT = Path("/Users/atinsharma/job_search_vault")
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
    ((r"\bnotice\b", r"\bjoin\b", r"\bstart date\b", r"\bavailability\b"), "availability"),
    ((r"\bexperience\b", r"\byears of\b"), "years_experience"),
    ((r"\bexpected salary\b", r"\bexpected ctc\b", r"\bdesired salary\b", r"\bcompensation\b"), "expected_ctc_min"),
    ((r"\bcurrent salary\b", r"\bcurrent ctc\b"), "current_salary_val"),
    ((r"\bwork authorization\b", r"\blegally authorized\b"), "work_authorized"),
    ((r"\bsponsorship\b", r"\bvisa\b"), "requires_sponsorship"),
    ((r"\brelocat",), "open_to_relocate"),
    ((r"\bdegree\b",), "degree"),
    ((r"\buniversity\b", r"\binstitution\b", r"\bcollege\b"), "university"),
    ((r"\brate yourself out of 10 in fullstack\b", r"\brating\b"), "coding_rating"),
    ((r"\btell us about yourself\b", r"\babout yourself\b", r"\bintroduce yourself\b", r"\bbackground\b"), "qa_about_me"),
    ((r"\btechnical challenge\b", r"\bcomplex bug\b", r"\bperformance issue\b", r"\bdifficult problem\b"), "qa_tech_challenge"),
    ((r"\bproduct you built\b", r"\bside project\b", r"\bmost proud\b", r"\bbuild from scratch\b"), "qa_innovation"),
    ((r"\bconflict\b", r"\binitiative\b", r"\bteam problem\b", r"\bleadership\b", r"\btook ownership\b"), "qa_leadership"),
    ((r"\bproduct impact\b", r"\bend users\b", r"\bhow.*helped\b", r"\buser value\b"), "qa_product_impact"),
    ((r"\bwhy.*role\b", r"\bwhy.*position\b", r"\bwhy.*company\b", r"\bwhy.*interest\b", r"\bmotivation\b"), "qa_why_role"),
    ((r"\bcover letter\b", r"\bcover note\b", r"\badditional information\b", r"\banything else\b"), "qa_about_me"),
]

def answer_mapper(answer_bank: dict, label_text: str) -> str:
    # Handle the specific case for current salary if 0 is blocked
    lbl = clean_label(label_text).casefold()
    if "current salary" in lbl or "current ctc" in lbl:
        return "1.0" # Use 1.0 since 0.0 is blocked by decimal validation > 0
    return map_answer(label_text, answer_bank, LINKEDIN_MAPPING)

def find_action_button(dialog, names: list[str]):
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
        button = dialog.get_by_role("button", name=re.compile(re.escape(name), re.I))
        if button.count() > 0 and button.first.is_visible():
            return button.first
        button_text = dialog.locator("button, [role='button']").filter(has_text=re.compile(re.escape(name), re.I))
        if button_text.count() > 0 and button_text.first.is_visible():
            return button_text.first
    return None

def main():
    try:
        answer_bank = build_base_answer_bank(FACT_SHEET_PATH, LOGISTICS_PATH)
        # Custom additions
        answer_bank["coding_rating"] = "9"
        answer_bank["current_salary_val"] = "1.0"
        
        resume_path = Path("/Users/atinsharma/job_search_vault/active_application_context/staged_application_resume.pdf")
        
        print("Connecting to Chrome on port 9222...")
        sys.stdout.flush()
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            
            target_page = None
            for page in context.pages:
                if "4405961612" in page.url or "improva" in page.url.lower():
                    target_page = page
                    break
            
            if target_page is None:
                print("Error: Could not find an open tab at the requested URL on your Chrome browser.")
                sys.stdout.flush()
                return
            
            print(f"Found active tab: '{target_page.title()}' at URL: {target_page.url}")
            sys.stdout.flush()
            
            # Check if dialog is already open
            dialog = target_page.locator('[role="dialog"]').last
            if dialog.count() == 0 or not dialog.first.is_visible():
                print("Dialog not open. Clicking 'Easy Apply'...")
                sys.stdout.flush()
                easy_apply = target_page.locator("a, button, [role='button']").filter(has_text=re.compile(r"Easy Apply", re.I))
                if easy_apply.count() > 0:
                    easy_apply.first.click()
                    target_page.wait_for_timeout(3000)
                    dialog = target_page.locator('[role="dialog"]').last
                else:
                    print("Error: 'Easy Apply' element not found on page.")
                    sys.stdout.flush()
                    return
            
            if dialog.count() == 0:
                print("Error: Failed to open dialog.")
                sys.stdout.flush()
                return

            print("=== Filling Form Fields ===")
            sys.stdout.flush()
            
            last_inputs_state = ""
            stuck_count = 0
            
            for step in range(12):
                print(f"\n--- Step {step} ---")
                sys.stdout.flush()
                
                # Check for inputs and fill
                inputs = dialog.locator("input, select, textarea")
                current_state_str = ""
                for i in range(inputs.count()):
                    inp = inputs.nth(i)
                    current_state_str += f"{inp.evaluate('el => el.id')}:{inp.evaluate('el => el.value')};"
                
                if current_state_str == last_inputs_state and current_state_str != "":
                    stuck_count += 1
                    if stuck_count >= 2:
                        print("Stuck on the same step twice. Stopping to prevent loop.")
                        sys.stdout.flush()
                        break
                else:
                    stuck_count = 0
                last_inputs_state = current_state_str
                
                # Print questions on the page
                for i in range(inputs.count()):
                    inp = inputs.nth(i)
                    tag = inp.evaluate("el => el.tagName")
                    id_attr = inp.evaluate("el => el.id")
                    label_text = ""
                    if id_attr:
                        label = dialog.locator(f"label[for='{id_attr}']")
                        if label.count() > 0:
                            label_text = label.first.inner_text().strip()
                    if not label_text:
                        label_text = inp.evaluate("el => el.closest('div').innerText")
                    label_text = clean_label(label_text)
                    print(f"  Field {i}: Label='{label_text[:70]}' -> Value='{inp.evaluate('el => el.value')}'")
                    sys.stdout.flush()
                
                # Fill elements
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
                
                # Try to advance
                submit_button = find_action_button(dialog, ["Submit application"])
                if submit_button is not None:
                    print("Submit button is now visible! Form has been fully filled.")
                    print("Stopping here so you can review and click Submit yourself in Chrome.")
                    sys.stdout.flush()
                    break
                
                review_button = find_action_button(dialog, ["Review your application"])
                if review_button is not None:
                    print("Clicking 'Review' button...")
                    sys.stdout.flush()
                    review_button.click()
                    target_page.wait_for_timeout(2000)
                    continue
                    
                next_button = find_action_button(dialog, ["Continue to next step", "Next"])
                if next_button is not None:
                    print("Clicking 'Next' button...")
                    sys.stdout.flush()
                    next_button.click()
                    target_page.wait_for_timeout(2000)
                    continue
                
                print("No navigation button found. Stopping.")
                sys.stdout.flush()
                break
                
            print("Execution completed.")
            sys.stdout.flush()
    except Exception as e:
        print(f"Error: {e}")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
