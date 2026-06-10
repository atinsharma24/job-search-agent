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
    ((r"\bcurrent salary\b", r"\bcurrent ctc\b"), "current_ctc"),
    ((r"\bwork authorization\b", r"\blegally authorized\b"), "work_authorized"),
    ((r"\bsponsorship\b", r"\bvisa\b"), "requires_sponsorship"),
    ((r"\brelocat",), "open_to_relocate"),
    ((r"\bdegree\b",), "degree"),
    ((r"\buniversity\b", r"\binstitution\b", r"\bcollege\b"), "university"),
    ((r"\btell us about yourself\b", r"\babout yourself\b", r"\bintroduce yourself\b", r"\bbackground\b"), "qa_about_me"),
    ((r"\btechnical challenge\b", r"\bcomplex bug\b", r"\bperformance issue\b", r"\bdifficult problem\b"), "qa_tech_challenge"),
    ((r"\bproduct you built\b", r"\bside project\b", r"\bmost proud\b", r"\bbuild from scratch\b"), "qa_innovation"),
    ((r"\bconflict\b", r"\binitiative\b", r"\bteam problem\b", r"\bleadership\b", r"\btook ownership\b"), "qa_leadership"),
    ((r"\bproduct impact\b", r"\bend users\b", r"\bhow.*helped\b", r"\buser value\b"), "qa_product_impact"),
    ((r"\bwhy.*role\b", r"\bwhy.*position\b", r"\bwhy.*company\b", r"\bwhy.*interest\b", r"\bmotivation\b"), "qa_why_role"),
    ((r"\bcover letter\b", r"\bcover note\b", r"\badditional information\b", r"\banything else\b"), "qa_about_me"),
]

def answer_mapper(answer_bank: dict, label_text: str) -> str:
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
        resume_path = Path("/Users/atinsharma/job_search_vault/active_application_context/staged_application_resume.pdf")
        
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            new_page = context.new_page()
            url = "https://in.linkedin.com/jobs/view/fullstack-software-engineer-ai-focused-at-improva-4405961612"
            new_page.goto(url, wait_until="domcontentloaded", timeout=60000)
            new_page.wait_for_timeout(5000)
            
            print(f"URL: {new_page.url}")
            print(f"Title: {new_page.title()}")
            sys.stdout.flush()
            
            easy_apply = new_page.locator("a, button, [role='button']").filter(has_text=re.compile(r"Easy Apply", re.I))
            print(f"Easy Apply elements found: {easy_apply.count()}")
            sys.stdout.flush()
            
            if easy_apply.count() > 0:
                print(f"Clicking first Easy Apply element (Tag={easy_apply.first.evaluate('el => el.tagName')})...")
                sys.stdout.flush()
                easy_apply.first.click()
                new_page.wait_for_timeout(5000)
                
                dialog = new_page.locator('[role="dialog"]').last
                print(f"Dialog elements found: {dialog.count()}")
                sys.stdout.flush()
                
                if dialog.count() == 0:
                    new_page.screenshot(path="/tmp/dialog_not_opened.png")
                    print("Error: Dialog not opened after click. Saved screenshot to /tmp/dialog_not_opened.png")
                    sys.stdout.flush()
                    return
            else:
                new_page.screenshot(path="/tmp/no_easy_apply_found.png")
                print("Error: No Easy Apply element found. Saved screenshot to /tmp/no_easy_apply_found.png")
                sys.stdout.flush()
                return

            print("=== Walking through the Easy Apply Steps ===")
            sys.stdout.flush()
            for step in range(12):
                print(f"\n--- STEP {step} ---")
                screenshot_path = f"/tmp/easy_apply_step_{step}.png"
                dialog.screenshot(path=screenshot_path)
                print(f"Saved screenshot: {screenshot_path}")
                sys.stdout.flush()
                
                # Report all inputs present
                inputs = dialog.locator("input, select, textarea")
                print(f"Number of inputs: {inputs.count()}")
                sys.stdout.flush()
                for i in range(inputs.count()):
                    inp = inputs.nth(i)
                    tag = inp.evaluate("el => el.tagName")
                    placeholder = inp.evaluate("el => el.getAttribute('placeholder')") or ""
                    val = inp.evaluate("el => el.value") or ""
                    name = inp.evaluate("el => el.getAttribute('name')") or ""
                    type_attr = inp.evaluate("el => el.getAttribute('type')") or ""
                    label_text = ""
                    id_attr = inp.evaluate("el => el.id")
                    if id_attr:
                        label = dialog.locator(f"label[for='{id_attr}']")
                        if label.count() > 0:
                            label_text = label.first.inner_text().strip()
                    if not label_text:
                        label_text = inp.evaluate("el => el.closest('div').innerText")
                    label_text = clean_label(label_text)
                    print(f"  Input {i}: Tag={tag}, Name='{name}', Type='{type_attr}', Placeholder='{placeholder}', Label='{label_text[:60]}', Value='{val[:30]}'")
                    sys.stdout.flush()
                
                # Fill elements on this page
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
                
                # Verify if any validation errors are visible
                errors = dialog.locator(".artdeco-inline-feedback--error, [class*='error']")
                if errors.count() > 0:
                    print(f"Warning: {errors.count()} error feedback elements found:")
                    sys.stdout.flush()
                    for j in range(errors.count()):
                        err_text = errors.nth(j).inner_text().strip()
                        if err_text:
                            print(f"  Error {j}: '{err_text}'")
                            sys.stdout.flush()

                # Action buttons
                submit_button = find_action_button(dialog, ["Submit application"])
                if submit_button is not None:
                    print("Found Submit button! Stopping here for dry run.")
                    sys.stdout.flush()
                    dialog.screenshot(path="/tmp/easy_apply_submit_page.png")
                    break
                
                review_button = find_action_button(dialog, ["Review your application"])
                if review_button is not None:
                    print("Clicking Review button...")
                    sys.stdout.flush()
                    review_button.click()
                    new_page.wait_for_timeout(2000)
                    continue
                    
                next_button = find_action_button(dialog, ["Continue to next step", "Next"])
                if next_button is not None:
                    print("Clicking Next button...")
                    sys.stdout.flush()
                    next_button.click()
                    new_page.wait_for_timeout(2000)
                    continue
                    
                print("No action button (Next, Review, Submit) found! Stuck on this step.")
                sys.stdout.flush()
                break
                
            new_page.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
