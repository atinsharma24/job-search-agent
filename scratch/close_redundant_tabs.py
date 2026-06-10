import sys
from playwright.sync_api import sync_playwright

def main():
    try:
        with sync_playwright() as p:
            print("Connecting to Chrome over CDP...")
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            pages = context.pages
            print(f"Total tabs open: {len(pages)}")
            closed_count = 0
            # Iterate backwards so index doesn't shift when closing
            for i in range(len(pages) - 1, -1, -1):
                page = pages[i]
                try:
                    url = page.url
                    title = page.title()
                    # Close redundant search result tabs, profile tabs, job view tabs, and preload invite tabs
                    if "linkedin.com/search" in url or "linkedin.com/in/" in url or "linkedin.com/jobs/view" in url or "linkedin.com/preload/" in url:
                        print(f"Closing redundant tab [{i}]: {title} ({url})")
                        page.close()
                        closed_count += 1
                except Exception as e:
                    print(f"Error checking tab [{i}]: {e}")
            print(f"Cleaned up {closed_count} tabs successfully.")
    except Exception as e:
        print(f"Error connecting over CDP: {e}")

if __name__ == "__main__":
    main()
