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
PROFILES_JSON = VAULT_ROOT / "active_application_context" / "proposed_connected_outreach.json"
PROGRESS_FILE = VAULT_ROOT / "active_application_context" / "linkedin_connected_outreach_progress.json"
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

def check_connection_status(page) -> str:
    page.evaluate("""() => {
        const overlay = document.querySelector('.msg-overlay-container');
        if (overlay) overlay.style.display = 'none';
    }""")
    
    page_text = page.locator("body").inner_text()
    
    # 404 check
    if "this page doesn’t exist" in page_text.lower() or "page not found" in page_text.lower() or "page not exist" in page_text.lower():
        return "SKIPPED_404"
        
    top_card = page.locator("main > section, .pv-top-card").first
    top_card_text = top_card.inner_text() if top_card.count() > 0 else page_text
    
    # Check if 1st degree
    if "• 1st" in top_card_text or "1st degree" in top_card_text:
        return "CONNECTED"
        
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
            return "SKIPPED_PENDING"
            
    if "pending" in top_card_text.lower() or "withdraw request" in top_card_text.lower():
        return "SKIPPED_PENDING"
        
    # Check if Message button is present and visible
    msg_btn = page.locator("main a:has-text('Message'), main button:has-text('Message')").first
    if msg_btn.count() > 0 and msg_btn.is_visible():
        return "CONNECTED"
        
    return "SKIPPED_NOT_CONNECTED"

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

def generate_referral_message(name: str, company: str, is_vit: bool) -> str:
    first_name = name.split()[0]
    
    if is_vit:
        greeting = f"Hey {first_name}, fellow VIT alum here."
    else:
        greeting = f"Hey {first_name},"
        
    message = (
        f"{greeting} hope you are doing well. "
        f"I am a Full Stack and AI Engineer and served as a Founding Engineer at OpenBiz. "
        f"I recently shipped VyaparGPT, a WhatsApp native AI assistant for 40 SMBs, and Nimbus RAG, a pgvector pipeline with sub 800ms retrieval. "
        f"I am exploring engineering roles at {company} and noticed we are connected. "
        f"Would you be open to referring me for relevant technical openings? Happy to share my resume. "
        f"Thank you!"
    )
    return message

def send_referral_message(page, name: str, message: str, dry_run: bool) -> str:
    # 1. Click the Message button
    message_btn = page.locator("main a:has-text('Message'), main button:has-text('Message')").first
    if message_btn.count() == 0:
        message_btn = page.locator("a:has-text('Message'), button:has-text('Message')").first
        
    if message_btn.count() == 0 or not message_btn.is_visible():
        print("Message button is not visible or could not be found.")
        return "FAILED_MESSAGE_BUTTON_NOT_FOUND"
        
    print("Clicking 'Message' button...")
    message_btn.click()
    page.wait_for_timeout(3000)
    
    # 2. Find the chat textbox
    textbox = page.locator("div.msg-form__contenteditable, div[role='textbox']").first
    if textbox.count() == 0 or not textbox.is_visible():
        print("Chat textbox is not visible or could not be found.")
        return "FAILED_TEXTBOX_NOT_FOUND"
        
    print(f"Typing referral message ({len(message)} chars)...")
    textbox.focus()
    textbox.fill(message)
    page.wait_for_timeout(1000)
    
    # 3. Verify the Send button is enabled
    send_btn = page.locator("button.msg-form__send-button").first
    if send_btn.count() == 0:
        print("Send button not found inside chat box.")
        return "FAILED_SEND_BUTTON_NOT_FOUND"
        
    if not send_btn.is_enabled():
        print("Send button is disabled. Attempting to trigger events...")
        textbox.evaluate("el => el.dispatchEvent(new Event('input', { bubbles: true }))")
        textbox.press("Space")
        textbox.press("Backspace")
        page.wait_for_timeout(1000)
        
    if not send_btn.is_enabled():
        print("Send button remains disabled. Cannot send message.")
        return "FAILED_SEND_BUTTON_DISABLED"
        
    # 4. Handle Send or Dry Run
    if dry_run:
        print(f"[DRY RUN] Message would have been sent to {name}.")
        # Capture screenshot for review
        screenshot_dir = VAULT_ROOT / "active_application_context" / "playwright"
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = screenshot_dir / f"dry_run_{name.replace(' ', '_')}.png"
        page.screenshot(path=str(screenshot_path))
        print(f"[DRY RUN] Screenshot saved to {screenshot_path}")
        
        # Close the chat box
        close_btn = page.locator("button:has-text('Close your conversation with'), button[aria-label*='Close your conversation']").first
        if close_btn.count() > 0 and close_btn.is_visible():
            close_btn.click()
            page.wait_for_timeout(1000)
        return "DRY_RUN_SUCCESS"
    else:
        print(f"Sending message to {name}...")
        send_btn.click()
        page.wait_for_timeout(2000)
        
        # Close the chat box to keep workspace clean
        close_btn = page.locator("button:has-text('Close your conversation with'), button[aria-label*='Close your conversation']").first
        if close_btn.count() > 0 and close_btn.is_visible():
            close_btn.click()
            page.wait_for_timeout(1000)
        return "SENT"

def run_outreach():
    dry_run = "--dry-run" in sys.argv
    limit = None
    for arg in sys.argv:
        if arg.startswith("--limit="):
            try:
                limit = int(arg.split("=")[1])
            except:
                pass
                
    profiles = load_profiles()
    progress = load_progress()
    
    print(f"Loaded {len(profiles)} profiles of connected connections.")
    print(f"Loaded progress: {len(progress)}/{len(profiles)} processed.")
    if dry_run:
        print("=== RUNNING IN DRY-RUN MODE (will type messages and screenshot, but not send) ===")
        
    processed_count = 0
    
    try:
        with sync_playwright() as p:
            print("Connecting to Chrome on port 9222...")
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            page = browser.contexts[0].pages[0]
            
            for i, profile in enumerate(profiles):
                idx = profile["index"]
                name = profile["name"]
                company = profile["company"]
                url = profile["url"]
                
                # Check if already processed
                if str(idx) in progress:
                    saved = progress[str(idx)]
                    if saved["status"] in ["SENT", "SKIPPED_PENDING", "SKIPPED_NOT_CONNECTED", "SKIPPED_404"] and not dry_run:
                        continue
                        
                if limit is not None and processed_count >= limit:
                    print(f"Reached processing limit of {limit}. Stopping.")
                    break
                    
                print(f"\n[{idx}/{len(profiles)}] Processing {name} ({company}) - {url}")
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(3000)
                
                check_security_challenges(page)
                
                # Verify they are actually connected (1st degree)
                conn_status = check_connection_status(page)
                print(f"Connection Status check: {conn_status}")
                
                if conn_status != "CONNECTED":
                    progress[str(idx)] = {
                        "name": name,
                        "company": company,
                        "url": url,
                        "status": conn_status,
                        "message": "None",
                        "timestamp": datetime.now().isoformat()
                    }
                    save_progress(progress)
                    continue
                    
                # Check if VIT Alum
                is_vit = check_vit_education(page)
                print(f"Is VIT Alum: {is_vit}")
                
                # Generate and clean message
                message = generate_referral_message(name, company, is_vit)
                message = clean_note_text(message)
                
                # Send the message
                status_result = send_referral_message(page, name, message, dry_run)
                
                progress[str(idx)] = {
                    "name": name,
                    "company": company,
                    "url": url,
                    "status": status_result,
                    "message": message if "SUCCESS" in status_result or status_result == "SENT" else "None",
                    "timestamp": datetime.now().isoformat()
                }
                save_progress(progress)
                
                if status_result == "SENT":
                    log_to_tracker(company, name, "Referral Msg Sent", "SENT (Connected Referral Outreach)")
                    
                    # Delay 40-70 seconds (Rule 7 delay)
                    delay = random.randint(40, 70)
                    print(f"Waiting {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"Result for {name}: {status_result}")
                    time.sleep(5)
                    
                processed_count += 1
                
            browser.close()
            print("\n=== Connected Outreach Complete! ===")
            
    except SystemExit as e:
        raise
    except Exception as e:
        print(f"Script error: {e}")
        import traceback
        traceback.print_exc()

def print_summary():
    progress = load_progress()
    if not progress:
        print("No progress data found.")
        return
        
    print("\n\n## OUTREACH SUMMARY REPORT")
    print("| # | Name | Company | Status | Message |")
    print("|---|------|---------|--------|---------|")
    
    for idx in sorted([int(k) for k in progress.keys()]):
        entry = progress[str(idx)]
        status = entry.get("status", "Unknown")
        msg = entry.get("message", "None")
        print(f"| {idx} | {entry['name']} | {entry['company']} | {status} | {msg} |")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--summary":
        print_summary()
    else:
        run_outreach()
        print_summary()
