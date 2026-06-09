#!/usr/bin/env python3
import sys
import os
import json
import re
import time
import random
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

# Constants
EXIT_SUCCESS = 0
EXIT_CAPTCHA = 10
EXIT_LIMIT_REACHED = 11
EXIT_LOGIN_REQUIRED = 12

VAULT_ROOT = Path(__file__).resolve().parents[1]
PROFILES_JSON = VAULT_ROOT / "active_application_context" / "proposed_batch6.json"
PROGRESS_FILE = VAULT_ROOT / "active_application_context" / "linkedin_outreach_progress_batch6.json"
TRACKER_FILE = VAULT_ROOT / "active_application_context" / "job_applications_tracker.md"

def load_profiles() -> list:
    if not PROFILES_JSON.exists():
        print(f"Error: Profiles list not found at {PROFILES_JSON}")
        sys.exit(1)
    return json.loads(PROFILES_JSON.read_text(encoding="utf-8"))

def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Error reading progress file: {e}. Starting fresh.")
    return {}

def save_progress(progress: dict):
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_FILE.write_text(json.dumps(progress, indent=2), encoding="utf-8")

def log_to_tracker(company: str, person: str, status: str, note_type: str):
    date_str = datetime.today().strftime("%Y-%m-%d")
    log_line = f"- [{date_str}] **Company:** {company} | **Role:** Referral Outreach ({person}) | **Status:** {status} | **Note:** {note_type}\n"
    
    try:
        TRACKER_FILE.parent.mkdir(parents=True, exist_ok=True)
        if TRACKER_FILE.exists():
            content = TRACKER_FILE.read_text(encoding="utf-8")
            if not content.endswith("\n"):
                content += "\n"
            TRACKER_FILE.write_text(content + log_line, encoding="utf-8")
        print(f"Logged to tracker: {person} ({company})")
    except Exception as e:
        print(f"Warning: Could not log to tracker file: {e}")

def clean_note_text(note: str) -> str:
    # Rule 2: Remove all hyphens/dashes, replace with space
    note = note.replace("-", " ").replace("—", " ").replace("--", " ")
    # Also remove any mention of salary/CTC/LPA/negotiable
    note = re.sub(r'\b(salary|ctc|lpa|15\s*l|15\s*lpa|15\s*lakhs?|negotiable)\b', '', note, flags=re.IGNORECASE)
    # Clean up residual "+ ()." or "+ ()" or empty parens
    note = note.replace("+ ().", "").replace("+ ()", "").replace("().", "").replace("()", "")
    # Remove double spaces
    note = re.sub(r'\s+', ' ', note).strip()
    return note

def get_first_name(full_name: str) -> str:
    return full_name.split()[0]

def format_note_for_vit(name: str, standard_note: str) -> str:
    # Rule 1: Replace "Hey [Name]" or "Hi [Name]" with "Hey [Name], fellow VIT alum here." or "Hi [Name], fellow VIT alum here."
    first_name = get_first_name(name)
    
    hey_pattern = re.compile(rf"^Hey\s+{re.escape(first_name)}(,\s*|\s+)", re.IGNORECASE)
    hi_pattern = re.compile(rf"^Hi\s+{re.escape(first_name)}(,\s*|\s+)", re.IGNORECASE)
    
    if hey_pattern.match(standard_note):
        new_greeting = f"Hey {first_name}, fellow VIT alum here. "
        rest = hey_pattern.sub("", standard_note)
        note = new_greeting + rest
    elif hi_pattern.match(standard_note):
        new_greeting = f"Hi {first_name}, fellow VIT alum here. "
        rest = hi_pattern.sub("", standard_note)
        note = new_greeting + rest
    else:
        # Default fallback
        note = f"Hey {first_name}, fellow VIT alum here. " + standard_note
        
    return note

def check_connection_status(page) -> str:
    page.evaluate("""() => {
        const overlay = document.querySelector('.msg-overlay-container');
        if (overlay) overlay.style.display = 'none';
    }""")
    
    page_text = page.locator("body").inner_text()
    
    # Rule 8: 404 check
    if "this page doesn’t exist" in page_text.lower() or "page not found" in page_text.lower() or "page not exist" in page_text.lower():
        return "SKIPPED_404"
        
    top_card = page.locator("main > section, .pv-top-card").first
    top_card_text = top_card.inner_text() if top_card.count() > 0 else page_text
    
    # Check if 1st degree
    if "• 1st" in top_card_text or "1st degree" in top_card_text:
        return "SKIPPED_ALREADY_CONNECTED"
        
    # Check if pending
    buttons_text = []
    buttons = page.locator("button").all()
    for btn in buttons:
        try:
            if btn.is_visible():
                t = btn.inner_text().strip().lower()
                if t:
                    buttons_text.append(t)
        except:
            pass
            
    for t in buttons_text:
        if t in ["pending", "withdraw request", "invited", "sent"]:
            return "SKIPPED_ALREADY_CONNECTED"
            
    if "pending" in top_card_text.lower() or "withdraw request" in top_card_text.lower():
        return "SKIPPED_ALREADY_CONNECTED"
        
    return "Not Connected"

def check_vit_education(page) -> bool:
    print("Scrolling to Education section...")
    for _ in range(5):
        page.mouse.wheel(0, 900)
        page.wait_for_timeout(1000)
        
    page_text = page.locator("body").inner_text().lower()
    
    vit_keywords = [
        "vellore institute of technology", 
        "vit university", 
        "vit vellore", 
        "vit, vellore"
    ]
    for kw in vit_keywords:
        if kw in page_text:
            print(f"Matched VIT keyword on page: {kw}")
            return True
            
    edu_section = page.locator("section:has(#education), #education").first
    if edu_section.count() > 0:
        edu_text = edu_section.inner_text().lower()
        if re.search(r"\bvit\b", edu_text):
            print("Matched '\\bvit\\b' in education section.")
            return True
            
    return False

def check_security_challenges(page):
    url = page.url.lower()
    page_title = page.title().lower()
    body_text = page.locator("body").inner_text().lower()
    
    is_challenge = False
    if "checkpoint" in url or "challenge" in url:
        is_challenge = True
    elif "security check" in page_title or "security verification" in page_title:
        is_challenge = True
    elif "quick security check" in body_text or "verify you're a human" in body_text:
        is_challenge = True
    elif "security verification" in body_text or "suspicious activity" in body_text:
        is_challenge = True
    elif "captcha" in body_text and not ("/in/" in url):
        is_challenge = True
        
    if is_challenge:
        print(f"HALTED_CAPTCHA: CAPTCHA / Security Verification detected. URL: {page.url}, Title: {page.title()}")
        sys.exit(EXIT_CAPTCHA)
        
    if "sign in" in body_text and "linkedin" in body_text and page.locator("input[type='password']").count() > 0:
        if not ("/in/" in url) or page.locator("main").count() == 0:
            print("STOPPING: LinkedIn logged out or sign-in required.")
            sys.exit(EXIT_LOGIN_REQUIRED)

def click_profile_connect_button(page) -> bool:
    # 1. Try to find Connect button directly on the page
    connect_btn = page.locator("main button:has-text('Connect'), main a:has-text('Connect')").first
    if connect_btn.count() > 0 and connect_btn.is_visible():
        print("Found 'Connect' button directly on top card. Clicking...")
        connect_btn.click()
        page.wait_for_timeout(2000)
        return True
        
    # 2. Try to find in 'More' dropdown
    more_btn = page.locator("main button:has-text('More'), main button[aria-label*='More actions']").first
    if more_btn.count() > 0 and more_btn.is_visible():
        print("Clicking 'More' actions button...")
        more_btn.click()
        page.wait_for_timeout(1000)
        
        dropdown_connect = page.locator("div[role='aria-dropdown'] button:has-text('Connect'), div[role='dropdown'] button:has-text('Connect'), button[role='menuitem']:has-text('Connect'), .artdeco-dropdown__content button:has-text('Connect')").first
        if dropdown_connect.count() > 0 and dropdown_connect.is_visible():
            print("Found 'Connect' in the 'More' dropdown. Clicking...")
            dropdown_connect.click()
            page.wait_for_timeout(2000)
            return True
            
    return False

def process_profile(page, profile, dry_run: bool) -> str:
    name = profile["name"]
    company = profile["company"]
    url = profile["url"]
    std_note = profile["note"]
    
    slug = url.rstrip("/").split("/")[-1]
    
    # STEP A: Try preload URL
    preload_url = f"https://www.linkedin.com/preload/custom-invite/?vanityName={slug}"
    print(f"Step A: Opening preload URL: {preload_url}")
    page.goto(preload_url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3000)
    
    check_security_challenges(page)
    
    dialog = page.locator('.artdeco-modal').first
    modal_opened = dialog.count() > 0 and dialog.is_visible()
    
    if modal_opened:
        print("Preload invite modal opened successfully!")
        
        # Check weekly limit
        dialog_text = dialog.inner_text().lower()
        limit_keywords = ["weekly invitation limit", "reached the limit", "try again tomorrow", "maximum number of invitations", "weekly limit"]
        for kw in limit_keywords:
            if kw in dialog_text or kw in page.locator("body").inner_text().lower():
                print(f"STOPPING: Reached LinkedIn invitation limit. Found '{kw}'")
                sys.exit(EXIT_LIMIT_REACHED)
                
        # Scroll background to check VIT education
        is_vit = check_vit_education(page)
        print(f"Is VIT Alum: {is_vit}")
        
        # Format and clean note
        if is_vit:
            note = format_note_for_vit(name, std_note)
        else:
            note = std_note
        note = clean_note_text(note)
        
        # Check limit
        if len(note) > 300:
            print(f"SKIPPED_OVERLIMIT: Note has {len(note)} chars (max 300).")
            return "SKIPPED_OVERLIMIT"
            
        # Click Add a note
        add_note_btn = dialog.locator('button:has-text("Add a note")')
        if add_note_btn.count() > 0 and add_note_btn.is_visible():
            print("Clicking 'Add a note'...")
            add_note_btn.click()
            page.wait_for_timeout(1000)
            
        textarea = dialog.locator('textarea')
        if textarea.count() == 0:
            print("Textarea not found in custom invite dialog.")
            return "SKIPPED_NO_CONNECT"
            
        textarea.wait_for(timeout=5000)
        print(f"Typing note ({len(note)} chars): {note}")
        textarea.focus()
        textarea.fill(note)
        textarea.evaluate("el => el.dispatchEvent(new Event('input', { bubbles: true }))")
        textarea.press("Space")
        textarea.press("Backspace")
        page.wait_for_timeout(1000)
        
        # Find Send button
        send_btn = dialog.locator('button:has-text("Send"), button:has-text("Send invitation")').first
        if send_btn.count() == 0:
            print("Send button not found.")
            return "SKIPPED_NO_CONNECT"
            
        if not send_btn.is_enabled():
            print("Send button is disabled (possibly requires email verification). Skipping.")
            return "SKIPPED_NO_CONNECT"
            
        if dry_run:
            print(f"[DRY RUN] Would have clicked send for {name}.")
            return "DRY_RUN_SUCCESS"
            
        print("Clicking 'Send'...")
        send_btn.click()
        page.wait_for_timeout(3000)
        return "SENT"
        
    else:
        print("Step A: Preload modal did not open. Trying Step B (direct profile navigation)...")
        # STEP B: Navigate to direct profile URL
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)
        
        check_security_challenges(page)
        
        # Connection status & 404 check
        conn_status = check_connection_status(page)
        print(f"Direct connection check: {conn_status}")
        
        if conn_status in ["SKIPPED_404", "SKIPPED_ALREADY_CONNECTED"]:
            return conn_status
            
        # Scroll to Education to check VIT
        is_vit = check_vit_education(page)
        print(f"Is VIT Alum: {is_vit}")
        
        # Format and clean note
        if is_vit:
            note = format_note_for_vit(name, std_note)
        else:
            note = std_note
        note = clean_note_text(note)
        
        # Check limit
        if len(note) > 300:
            print(f"SKIPPED_OVERLIMIT: Note has {len(note)} chars (max 300).")
            return "SKIPPED_OVERLIMIT"
            
        # Click connect button
        connect_clicked = click_profile_connect_button(page)
        if not connect_clicked:
            print("Connect button not found or could not be clicked.")
            return "SKIPPED_NO_CONNECT"
            
        # Wait for modal dialog
        dialog = page.locator('.artdeco-modal').first
        if dialog.count() == 0 or not dialog.is_visible():
            print("Invite modal did not appear after clicking Connect.")
            return "SKIPPED_NO_CONNECT"
            
        # Click Add a note
        add_note_btn = dialog.locator('button:has-text("Add a note")')
        if add_note_btn.count() > 0 and add_note_btn.is_visible():
            print("Clicking 'Add a note'...")
            add_note_btn.click()
            page.wait_for_timeout(1000)
            
        textarea = dialog.locator('textarea')
        if textarea.count() == 0:
            print("Textarea not found in custom invite dialog.")
            return "SKIPPED_NO_CONNECT"
            
        textarea.wait_for(timeout=5000)
        print(f"Typing note ({len(note)} chars): {note}")
        textarea.focus()
        textarea.fill(note)
        textarea.evaluate("el => el.dispatchEvent(new Event('input', { bubbles: true }))")
        textarea.press("Space")
        textarea.press("Backspace")
        page.wait_for_timeout(1000)
        
        # Find Send button
        send_btn = dialog.locator('button:has-text("Send"), button:has-text("Send invitation")').first
        if send_btn.count() == 0:
            print("Send button not found.")
            return "SKIPPED_NO_CONNECT"
            
        if not send_btn.is_enabled():
            print("Send button is disabled (possibly requires email verification). Skipping.")
            return "SKIPPED_NO_CONNECT"
            
        if dry_run:
            print(f"[DRY RUN] Would have clicked send for {name}.")
            return "DRY_RUN_SUCCESS"
            
        print("Clicking 'Send'...")
        send_btn.click()
        page.wait_for_timeout(3000)
        return "SENT"

def run_outreach():
    dry_run = "--dry-run" in sys.argv
    profiles = load_profiles()
    progress = load_progress()
    print(f"Loaded profiles: {len(profiles)}")
    print(f"Loaded progress: {len(progress)}/{len(profiles)} processed.")
    
    try:
        with sync_playwright() as p:
            print("Connecting to Chrome on port 9222...")
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            page = browser.contexts[0].pages[0]
            
            for i, profile in enumerate(profiles):
                idx = i + 1
                name = profile["name"]
                company = profile["company"]
                url = profile["url"]
                
                if str(idx) in progress:
                    saved = progress[str(idx)]
                    if saved["status"] not in ["FAILED", "Unknown"]:
                        continue
                
                print(f"\n[{idx}/50] Processing {name} ({company}) - {url}")
                
                status_result = process_profile(page, profile, dry_run)
                
                progress[str(idx)] = {
                    "name": name,
                    "company": company,
                    "url": url,
                    "status": status_result,
                    "note": profile["note"] if status_result == "SENT" else "None",
                    "timestamp": datetime.now().isoformat()
                }
                save_progress(progress)
                
                if status_result == "SENT":
                    log_to_tracker(company, name, "Invite Sent", f"SENT (Outreach Batch 6)")
                    
                    # Rule 7: Wait 40 to 70 seconds between each successful send
                    delay = random.randint(40, 70)
                    print(f"Waiting {delay} seconds (Rule 7 delay)...")
                    time.sleep(delay)
                else:
                    print(f"Result for {name}: {status_result}")
                    time.sleep(5)
            
            browser.close()
            print("\n=== LinkedIn Outreach complete! ===")
            
    except SystemExit as e:
        raise
    except Exception as e:
        print(f"Script error: {e}")
        import traceback
        traceback.print_exc()

def print_summary():
    progress = load_progress()
    
    if not progress:
        print("No progress data found to summarize.")
        return
        
    print("\n\n## FINAL OUTPUT")
    print("| # | Name | Company | Status | Note |")
    print("|---|------|---------|--------|------|")
    
    for idx in sorted([int(k) for k in progress.keys()]):
        entry = progress[str(idx)]
        status = entry.get("status", "Unknown")
        note = entry.get("note", "None")
        print(f"| {idx} | {entry['name']} | {entry['company']} | {status} | {note} |")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--summary":
        print_summary()
    else:
        run_outreach()
        print_summary()
