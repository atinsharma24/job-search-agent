"""
send_connections.py

Reads queue/approved.json and sends LinkedIn connection requests
using the persistent playwright session (either CDP or local profile).

Advanced Anti-Detection Features integrated:
- Webdriver masking startup script
- Human-like variable keystroke typing simulation
- Casual profile reading scroll simulation
- Unpredictable human delay pauses (micro-jitter ranges)
- Behavioral break feed visits every 4-6 successful sends
- Halts immediately on security verifications/CAPTCHAs
"""

import json
import time
import random
import sys
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

ROOT = Path(__file__).parent.parent
APPROVED_JSON = ROOT / "queue" / "approved.json"
SENT_JSON = ROOT / "queue" / "sent.json"
OUTREACH_LOG = ROOT / "logs" / "outreach.log"
ERRORS_LOG = ROOT / "logs" / "errors.log"
SESSION_DIR = Path("/Users/atinsharma/job_search_vault/active_application_context/playwright/linkedin-profile")

DAILY_CAP = int(os.environ.get("DAILY_CAP", 15))
DELAY_MIN = int(os.environ.get("DELAY_MIN", 45))
DELAY_MAX = int(os.environ.get("DELAY_MAX", 90))


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def log_outreach(line: str):
    with open(OUTREACH_LOG, "a") as f:
        f.write(f"[{now_iso()}] {line}\n")
    print(line)


def log_error(line: str):
    with open(ERRORS_LOG, "a") as f:
        f.write(f"[{now_iso()}] {line}\n")
    print(f"[ERROR] {line}", file=sys.stderr)


def load_json(path: Path):
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def save_json(path: Path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def check_security_challenge(page) -> bool:
    url = page.url.lower()
    page_title = page.title().lower()
    
    try:
        body_text = page.locator("body").inner_text().lower()
    except Exception:
        body_text = ""

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

    return is_challenge


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


def human_delay(min_sec=15.0, max_sec=45.0):
    """Delay execution by a random floating point number of seconds to avoid rhythm detection."""
    delay = random.uniform(min_sec, max_sec)
    print(f"  Stealth delay: pausing for {delay:.2f}s...")
    time.sleep(delay)


def type_like_human(element_locator, text):
    """Simulate keypress events with random delays to look like actual typing."""
    element_locator.focus()
    for char in text:
        element_locator.press(char)
        # Random typing delay per character
        time.sleep(random.uniform(0.04, 0.18))


def check_vit_education(page) -> bool:
    """Scroll naturally through the profile to read experiences (simulating reading) and check for VIT education."""
    print("Simulating organic profile reading scroll and checking education...")
    scrolls = random.randint(3, 5)
    vit_found = False
    
    vit_keywords = [
        "vellore institute of technology", 
        "vit university", 
        "vit vellore", 
        "vit, vellore"
    ]
    
    for _ in range(scrolls):
        scroll_amount = random.randint(350, 750)
        page.mouse.wheel(0, scroll_amount)
        # Random sleep mimicking reading experience blocks
        time.sleep(random.uniform(1.5, 3.5))
        
        # Check text on the fly
        try:
            page_text = page.locator("body").inner_text().lower()
            if any(kw in page_text for kw in vit_keywords):
                vit_found = True
        except Exception:
            pass
            
    try:
        edu_section = page.locator("section:has(#education), #education").first
        if edu_section.count() > 0:
            edu_text = edu_section.inner_text().lower()
            if re.search(r"\bvit\b", edu_text):
                print("Matched '\\bvit\\b' in education section.")
                vit_found = True
    except Exception:
        pass
            
    return vit_found


def visit_home_feed(page):
    """Break sequential profile loops by visiting and scrolling the home feed casually."""
    print("\n[Stealth Break] Simulating casual LinkedIn home feed visit...")
    try:
        page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(random.uniform(2.0, 4.0))
        # Scroll the feed a few times
        scrolls = random.randint(2, 4)
        for _ in range(scrolls):
            scroll_amount = random.randint(300, 700)
            page.mouse.wheel(0, scroll_amount)
            time.sleep(random.uniform(2.0, 5.0))
        print("[Stealth Break] Home feed visit complete. Returning to queue.\n")
    except Exception as e:
        print(f"[Warning] Failed feed visit break: {e}")


def check_connection_status(page) -> str:
    page.evaluate("""() => {
        const overlay = document.querySelector('.msg-overlay-container');
        if (overlay) overlay.style.display = 'none';
    }""")
    
    page_text = page.locator("body").inner_text()
    
    if "this page doesn’t exist" in page_text.lower() or "page not found" in page_text.lower() or "page not exist" in page_text.lower():
        return "SKIPPED_404"
        
    top_card = page.locator("main > section, .pv-top-card").first
    top_card_text = top_card.inner_text() if top_card.count() > 0 else page_text
    
    if "• 1st" in top_card_text or "1st degree" in top_card_text:
        return "SKIPPED_ALREADY_CONNECTED"
        
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


def click_profile_connect_button(page) -> bool:
    # 1. Try to find Connect button directly on the page
    connect_btn = page.locator("main button:has-text('Connect'), main a:has-text('Connect')").first
    if connect_btn.count() > 0 and connect_btn.is_visible():
        print("Found 'Connect' button directly on top card. Clicking...")
        connect_btn.click()
        time.sleep(random.uniform(1.5, 3.0))
        return True
        
    # 2. Try to find in 'More' dropdown
    more_btn = page.locator("main button:has-text('More'), main button[aria-label*='More actions']").first
    if more_btn.count() > 0 and more_btn.is_visible():
        print("Clicking 'More' actions button...")
        more_btn.click()
        time.sleep(random.uniform(1.0, 2.0))
        
        dropdown_connect = page.locator("div[role='aria-dropdown'] button:has-text('Connect'), div[role='dropdown'] button:has-text('Connect'), button[role='menuitem']:has-text('Connect'), .artdeco-dropdown__content button:has-text('Connect')").first
        if dropdown_connect.count() > 0 and dropdown_connect.is_visible():
            print("Found 'Connect' in the 'More' dropdown. Clicking...")
            dropdown_connect.click()
            time.sleep(random.uniform(1.5, 3.0))
            return True
            
    return False


def send_connection(page, entry: dict, dry_run: bool) -> bool:
    """Navigate to profile and send connection request with note. Returns True on success."""
    url = entry["url"]
    name = entry["name"]
    standard_message = entry["message"]

    slug = url.rstrip("/").split("/")[-1]
    preload_url = f"https://www.linkedin.com/preload/custom-invite/?vanityName={slug}"

    print(f"\n{'='*60}")
    print(f"Target  : {name} @ {entry['company']}")
    print(f"URL     : {url}")
    print(f"Preload : {preload_url}")
    print(f"{'='*60}")

    auto_confirm = os.environ.get("AUTO_CONFIRM") == "1"
    if auto_confirm:
        print("AUTO_CONFIRM: Automatically confirming connection request.")
        confirm = "y"
    else:
        confirm = input(f"Process connection request for {name}? [Y/n]: ").strip().lower()

    if confirm not in ("y", ""):
        log_outreach(f"SKIPPED | {name} | {entry['company']} | user skipped")
        entry["status"] = "skipped"
        return False

    try:
        # Step A: Try preload URL
        print(f"Step A: Opening preload URL: {preload_url}")
        page.goto(preload_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(random.uniform(3.0, 5.0))

        if check_security_challenge(page):
            log_error(f"HUMAN_INTERVENTION_REQUIRED | security challenge on preload")
            print("\n[HALT] LinkedIn security challenge detected. Stopping. Please resolve manually.")
            sys.exit(1)

        dialog = page.locator('.artdeco-modal').first
        modal_opened = dialog.count() > 0 and dialog.is_visible()

        is_vit = False
        if modal_opened:
            print("Preload invite modal opened successfully!")
            # Check weekly limit in the dialog
            dialog_text = dialog.inner_text().lower()
            limit_keywords = ["weekly invitation limit", "reached the limit", "try again tomorrow", "maximum number of invitations", "weekly limit"]
            for kw in limit_keywords:
                if kw in dialog_text or kw in page.locator("body").inner_text().lower():
                    print(f"STOPPING: Reached LinkedIn invitation limit. Found '{kw}'")
                    sys.exit(1)
            
            # Check VIT education (organic scrolling check background)
            is_vit = check_vit_education(page)
            print(f"Is VIT Alum: {is_vit}")

        else:
            print("Step A: Preload modal did not open. Trying Step B (direct profile navigation)...")
            # Step B: Direct profile navigation
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            time.sleep(random.uniform(3.0, 5.0))

            if check_security_challenge(page):
                log_error(f"HUMAN_INTERVENTION_REQUIRED | security challenge on {url}")
                print("\n[HALT] LinkedIn security challenge detected. Stopping. Please resolve manually.")
                sys.exit(1)

            # Check connection status
            conn_status = check_connection_status(page)
            print(f"Direct connection check: {conn_status}")
            if conn_status in ["SKIPPED_404", "SKIPPED_ALREADY_CONNECTED"]:
                log_outreach(f"{conn_status} | {name} | {entry['company']} | {url}")
                entry["status"] = "skipped"
                entry["error"] = conn_status
                return False

            is_vit = check_vit_education(page)
            print(f"Is VIT Alum: {is_vit}")

            # Click Connect button
            connect_clicked = click_profile_connect_button(page)
            if not connect_clicked:
                log_error(f"BUTTON_NOT_FOUND | {name} | {url} | no Connect button found.")
                entry["status"] = "failed"
                entry["error"] = "Connect button not found"
                return False

            # Wait for modal dialog
            dialog = page.locator('.artdeco-modal').first
            if dialog.count() == 0 or not dialog.is_visible():
                log_error(f"MODAL_NOT_FOUND | {name} | Invite modal did not appear after clicking Connect.")
                entry["status"] = "failed"
                entry["error"] = "Invite modal not found"
                return False

        # Format and clean message
        if is_vit:
            message = format_note_for_vit(name, standard_message)
        else:
            message = standard_message

        message = clean_note_text(message)
        print(f"\nFinal Note ({len(message)} chars):")
        print(f"  {message}\n")

        if len(message) > 300:
            log_error(f"CONNECTION_EXCEEDS_LIMIT | {name} | {url} | note has {len(message)} chars (max 300).")
            entry["status"] = "failed"
            entry["error"] = "Message too long"
            return False

        # Click Add a note if needed
        add_note_btn = dialog.locator('button:has-text("Add a note")').first
        if add_note_btn.count() > 0 and add_note_btn.is_visible():
            print("Clicking 'Add a note'...")
            add_note_btn.click()
            time.sleep(random.uniform(1.0, 2.0))

        # Type the message
        textarea = dialog.locator('textarea').first
        if textarea.count() == 0:
            # Fallback for standard textarea selectors
            textarea = page.locator("textarea#custom-message").first
            if not textarea.is_visible(timeout=2000):
                textarea = page.locator("textarea[name='message']").first

        if textarea.count() == 0 or not textarea.is_visible(timeout=3000):
            log_error(f"TEXTAREA_NOT_FOUND | {name}")
            entry["status"] = "failed"
            entry["error"] = "Message textarea not found"
            return False

        # Human-like typing simulation
        type_like_human(textarea, message)
        time.sleep(random.uniform(1.0, 2.0))

        # Find Send button
        send_btn = dialog.locator('button:has-text("Send"), button:has-text("Send invitation")').first
        if send_btn.count() == 0:
            send_btn = page.locator("button:has-text('Send')").first

        if send_btn.count() == 0 or not send_btn.is_visible(timeout=5000):
            log_error(f"SEND_BUTTON_NOT_FOUND | {name}")
            entry["status"] = "failed"
            entry["error"] = "Send button not found"
            return False

        if not send_btn.is_enabled():
            log_error(f"SEND_BUTTON_DISABLED | {name} | Send button is disabled (email verification required?)")
            entry["status"] = "failed"
            entry["error"] = "Send button disabled"
            return False

        # Take a screenshot to verify pasting
        page.screenshot(path="/tmp/connection_note_pasted.png")
        print("Saved screenshot to /tmp/connection_note_pasted.png")

        if dry_run:
            print("DRY_RUN: Skipping click on Send button.")
            time.sleep(random.uniform(1.5, 3.0))
            entry["status"] = "approved"  # keep as approved
            return True

        print("Clicking 'Send'...")
        send_btn.click()
        time.sleep(random.uniform(3.0, 5.0))

        entry["status"] = "sent"
        entry["sent_at"] = now_iso()
        log_outreach(f"SENT | {name} | {entry['company']} | {url}")
        print(f"  ✓ Sent to {name}")
        return True

    except Exception as e:
        log_error(f"SEND_ERROR | {name} | {entry['company']} | {e}")
        entry["status"] = "failed"
        entry["error"] = str(e)
        return False


def load_already_sent_targets():
    sent_slugs = set()
    sent_names = set()

    def get_slug(url: str) -> str:
        if not url:
            return ''
        url = url.split('?')[0].rstrip('/')
        return url.split('/')[-1].lower()

    # 1. Parse tracker markdown
    tracker_file = Path("/Users/atinsharma/job_search_vault/active_application_context/job_applications_tracker.md")
    if tracker_file.exists():
        try:
            content = tracker_file.read_text(encoding='utf-8')
            for line in content.splitlines():
                if 'Referral Outreach' in line or 'Invite Sent' in line:
                    match = re.search(r'Referral Outreach \(([^)]+)\)', line)
                    if match:
                        sent_names.add(match.group(1).strip().lower())
                    urls = re.findall(r'https?://[^\s|]+', line)
                    for u in urls:
                        slug = get_slug(u)
                        if slug:
                            sent_slugs.add(slug)
        except Exception as e:
            log_error(f"Error reading tracker file: {e}")

    # 2. Parse progress files
    context_dir = Path("/Users/atinsharma/job_search_vault/active_application_context")
    if context_dir.exists():
        for p in context_dir.glob('linkedin_*progress*.json'):
            try:
                data = json.loads(p.read_text(encoding='utf-8'))
                entries = data.values() if isinstance(data, dict) else data
                for entry in entries:
                    status = entry.get('status', '').upper()
                    if status in ['SENT', 'SENT_INVITE', 'INVITE SENT', 'DRY_RUN_SUCCESS']:
                        name = entry.get('name')
                        url = entry.get('url')
                        if name:
                            sent_names.add(name.strip().lower())
                        if url:
                            slug = get_slug(url)
                            if slug:
                                sent_slugs.add(slug)
            except Exception as e:
                pass

    # 3. Parse sent.json
    sent_json_path = ROOT / "queue" / "sent.json"
    if sent_json_path.exists():
        try:
            sent_data = json.loads(sent_json_path.read_text(encoding='utf-8'))
            for entry in sent_data:
                name = entry.get('name')
                url = entry.get('url')
                if name:
                    sent_names.add(name.strip().lower())
                if url:
                    slug = get_slug(url)
                    if slug:
                        sent_slugs.add(slug)
        except Exception as e:
            pass

    return sent_names, sent_slugs


def main():
    approved = load_json(APPROVED_JSON)
    
    # Run de-duplication check against already sent targets
    sent_names, sent_slugs = load_already_sent_targets()
    
    def get_slug(url: str) -> str:
        if not url:
            return ''
        url = url.split('?')[0].rstrip('/')
        return url.split('/')[-1].lower()

    modified = False
    for entry in approved:
        if entry.get("status") == "approved":
            name_clean = entry.get("name", "").strip().lower()
            url_clean = entry.get("url", "")
            slug_clean = get_slug(url_clean)

            if (name_clean in sent_names) or (slug_clean in sent_slugs):
                print(f"Skipping already-sent contact: {entry.get('name')} ({entry.get('company')})")
                entry["status"] = "skipped"
                entry["error"] = "Already sent (dedup filter)"
                modified = True

    if modified:
        save_json(APPROVED_JSON, approved)

    pending_send = [e for e in approved if e.get("status") == "approved"]

    if not pending_send:
        print("No approved entries to send. Run prepare + approve first.")
        sys.exit(0)

    dry_run = "--dry-run" in sys.argv
    print(f"\nLinkedIn Connection Sender")
    if dry_run:
        print("  *** RUNNING IN DRY RUN MODE ***")
    print(f"  Approved queue : {len(pending_send)}")
    print(f"  Daily cap      : {DAILY_CAP}")
    print(f"  Delay          : {DELAY_MIN}–{DELAY_MAX}s between sends")
    use_cdp = os.environ.get("PLAYWRIGHT_USE_CDP") == "1"
    cdp_url = os.environ.get("PLAYWRIGHT_CDP_URL", "http://localhost:9222")

    if not use_cdp and not SESSION_DIR.exists():
        print(f"\n[ERROR] LinkedIn session not found at {SESSION_DIR}")
        print("Run: python3 scripts/playwright_login_setup.py to create it.")
        sys.exit(1)

    sent = load_json(SENT_JSON)
    sent_count = 0
    sends_since_break = 0

    with sync_playwright() as p:
        if use_cdp:
            print(f"Connecting to Chrome over CDP at {cdp_url}...")
            browser = p.chromium.connect_over_cdp(cdp_url)
            context = browser.contexts[0]
            # Webdriver stealth masking
            context.add_init_script("delete Object.getPrototypeOf(navigator).webdriver")
            page = context.new_page()
        else:
            print(f"Launching persistent browser context from {SESSION_DIR}...")
            browser = p.chromium.launch_persistent_context(
                str(SESSION_DIR),
                headless=False,
                args=["--no-sandbox"],
            )
            # Webdriver stealth masking
            browser.add_init_script("delete Object.getPrototypeOf(navigator).webdriver")
            page = browser.new_page()
            
            # Verify we're logged in
            page.goto("https://www.linkedin.com/feed/", timeout=30000, wait_until="domcontentloaded")
            time.sleep(3)

            if "login" in page.url or "authwall" in page.url:
                print("\n[ERROR] LinkedIn session expired. Please log in manually first.")
                print(f"Run: python3 scripts/playwright_login_setup.py")
                browser.close()
                sys.exit(1)

        print(f"\n  Logged in. Starting sends...\n")

        for entry in pending_send:
            if sent_count >= DAILY_CAP:
                print(f"\n[HALT] Daily cap of {DAILY_CAP} reached. Re-run tomorrow.")
                log_outreach(f"DAILY_CAP_REACHED | {sent_count} sent this session")
                break

            success = send_connection(page, entry, dry_run)

            if entry["status"] == "sent":
                sent.append(entry)
                sent_count += 1
                sends_since_break += 1
            elif entry["status"] == "failed":
                pass  # stays in approved.json for retry

            # Persist state after every send attempt
            save_json(SENT_JSON, sent)
            save_json(APPROVED_JSON, approved)

            if success and not dry_run and sent_count < DAILY_CAP and pending_send.index(entry) < len(pending_send) - 1:
                # Trigger casual home feed break every 4 to 6 sends
                if sends_since_break >= random.randint(4, 6):
                    visit_home_feed(page)
                    sends_since_break = 0
                
                # Unpredictable human-delay paused micro-jitter range
                human_delay(DELAY_MIN, DELAY_MAX)
            elif success and dry_run:
                # Minimal delay in dry-run mode
                time.sleep(random.uniform(2.0, 4.0))

        browser.close()

    if dry_run:
        print(f"\nDone. Dry run complete. Simulating {sent_count} sends.")
    else:
        print(f"\nDone. Sent {sent_count} connection requests this session.")
        log_outreach(f"SESSION_END | {sent_count} sent")


if __name__ == "__main__":
    main()
