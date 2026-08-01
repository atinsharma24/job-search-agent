#!/usr/bin/env python3

import argparse
import os
import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright is not installed. Please install it to use this script.", file=sys.stderr)
    sys.exit(1)

# Import the orchestrator logic
from simplify_orchestrator import apply_to_page

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simplify Jobs Dashboard Crawler")
    parser.add_argument("--dry-run", action="store_true", help="Do not actually click submit.")
    parser.add_argument("--max-apps", type=int, default=10, help="Maximum number of applications to process.")
    return parser.parse_args()

def main():
    args = parse_args()
    cdp_url = os.environ.get("PLAYWRIGHT_CDP_URL", "http://localhost:9222")
    
    with sync_playwright() as p:
        try:
            print(f"Connecting to Chrome over CDP at {cdp_url}...")
            browser = p.chromium.connect_over_cdp(cdp_url)
            context = browser.contexts[0]
            
            # Use the first available page
            dashboard_page = context.pages[0] if context.pages else context.new_page()
            
            dashboard_url = "https://simplify.jobs/matches"
            print(f"Navigating to dashboard: {dashboard_url}")
            # domcontentloaded is safer for SPAs
            dashboard_page.goto(dashboard_url, wait_until="domcontentloaded")
            
            print("Waiting for jobs to load...")
            time.sleep(8)
            
            # Find all Apply buttons
            apply_btns = dashboard_page.locator("button:has-text('Apply')").all()
            print(f"Found {len(apply_btns)} 'Apply' buttons on the dashboard.")
            
            if not apply_btns:
                print("No jobs found. Exiting.")
                return 0
                
            applied_count = 0
            
            for i in range(len(apply_btns)):
                # Re-query to avoid stale elements
                btns = dashboard_page.locator("button:has-text('Apply')").all()
                if i >= len(btns):
                    break
                    
                btn = btns[i]
                
                if applied_count >= args.max_apps:
                    print(f"Reached max limit of {args.max_apps} applications.")
                    break
                    
                print(f"\\n--- Processing Job {applied_count + 1} ---")
                
                try:
                    # Click might open a new tab or a modal
                    with context.expect_page(timeout=5000) as new_page_info:
                        btn.click()
                    
                    ats_page = new_page_info.value
                    ats_page.wait_for_load_state("domcontentloaded")
                    print(f"Redirected to ATS tab: {ats_page.url}")
                    
                    # Run orchestrator
                    apply_to_page(ats_page, ats_page.url, dry_run=args.dry_run)
                    
                    print("Closing job tab.")
                    ats_page.close()
                    applied_count += 1
                    
                except Exception:
                    # Timeout waiting for new page means it didn't open a new tab
                    print("No new tab opened. It might be an internal Simplify application modal or a redirect.")
                    # If it's a modal, we can try running apply_to_page on the dashboard_page
                    time.sleep(3)
                    if dashboard_page.url != dashboard_url:
                        print(f"Redirected in same tab to: {dashboard_page.url}")
                        
                        # If it's a Simplify job page, click Apply to reach the ATS
                        if "simplify.jobs/p/" in dashboard_page.url or "simplify.jobs/jobs/" in dashboard_page.url:
                            inner_apply = dashboard_page.locator("a:has-text('Apply'), button:has-text('Apply')")
                            if inner_apply.count() > 0:
                                print("Clicking 'Apply' on inner job page...")
                                try:
                                    with context.expect_page(timeout=5000) as inner_page_info:
                                        inner_apply.first.click()
                                    ats_page = inner_page_info.value
                                    ats_page.wait_for_load_state("domcontentloaded")
                                    print(f"Redirected to ATS tab: {ats_page.url}")
                                    apply_to_page(ats_page, ats_page.url, dry_run=args.dry_run)
                                    ats_page.close()
                                except Exception:
                                    print("No new tab from inner apply. Trying orchestrator on current page...")
                                    apply_to_page(dashboard_page, dashboard_page.url, dry_run=args.dry_run)
                            else:
                                apply_to_page(dashboard_page, dashboard_page.url, dry_run=args.dry_run)
                        else:
                            apply_to_page(dashboard_page, dashboard_page.url, dry_run=args.dry_run)
                            
                        print("Going back to dashboard...")
                        dashboard_page.goto(dashboard_url, wait_until="domcontentloaded")
                        time.sleep(5)
                        applied_count += 1
                        applied_count += 1
                    else:
                        print("Assuming it's a modal or internal Simplify app.")
                        apply_to_page(dashboard_page, dashboard_page.url, dry_run=args.dry_run)
                        # We might need to close the modal or hit escape
                        dashboard_page.keyboard.press("Escape")
                        time.sleep(2)
                        applied_count += 1
                
                time.sleep(2) # brief pause between jobs
                
        except Exception as e:
            print(f"Fatal error in scraper: {e}", file=sys.stderr)
            return 1
            
    print("Crawler finished successfully.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
