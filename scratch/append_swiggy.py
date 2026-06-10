import json
import re
import csv
from urllib.parse import quote
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path("/Users/atinsharma/job_search_vault")
OUTPUT_CSV = ROOT / "linkedin_outreach" / "contacts" / "batch6_referral.csv"

# Load existing csv names
with open(OUTPUT_CSV, "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
existing_slugs = set()
for r in rows:
    u = r["url"].split("?")[0].rstrip("/")
    existing_slugs.add(u.split("/")[-1].lower())

def clean_note_text(note: str) -> str:
    note = note.replace("-", " ").replace("—", " ").replace("--", " ")
    note = re.sub(r"\b(salary|ctc|lpa|15\s*l|15\s*lpa|15\s*lakhs?|negotiable)\b", "", note, flags=re.IGNORECASE)
    note = note.replace("+ ().", "").replace("+ ()", "").replace("().", "").replace("()", "")
    note = re.sub(r"\s+", " ", note).strip()
    return note

def get_first_name(full_name: str) -> str:
    return full_name.split()[0]

def get_notes(name: str, company: str) -> tuple[str, str]:
    first_name = get_first_name(name)
    conn = f"Hey {first_name}, fellow VIT alum here. Shipped idempotent payments webhooks (100% consistency) and cut API latency 40% via N+1 resolution at OpenBiz. Would value connecting to learn about engineering roles at Swiggy."
    dm = f"Hey {first_name}, fellow VIT alum here. I'm Atin, a Full Stack and AI engineer. Shipped idempotent payment webhook billing (100% consistency) and cut API latency 40% via N+1 fixes at OpenBiz. Would value connecting to learn about engineering roles at Swiggy."
    return clean_note_text(conn), clean_note_text(dm)

with sync_playwright() as p:
    print("Connecting to Chrome over CDP on port 9222...")
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    page = browser.contexts[0].new_page()
    keywords = '"Vellore Institute of Technology" AND "Swiggy" AND "Software Engineer"'
    url = f"https://www.linkedin.com/search/results/people/?keywords={quote(keywords)}"
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)
    
    extracted = page.evaluate("""() => {
        const results = [];
        const links = Array.from(document.querySelectorAll("a[href*='/in/']"));
        const seenUrls = new Set();
        links.forEach((link) => {
            const url = link.href.split('?')[0];
            if (seenUrls.has(url)) return;
            if (url.includes('/in/ACoA') || url.includes('/search/')) return;
            const nameText = (link.innerText || '').trim().split('\\n')[0].trim();
            if (!nameText || nameText.length < 2 || nameText.includes('photo') || nameText.includes('View') || nameText.includes('profile')) return;
            seenUrls.add(url);
            results.push({ name: nameText, url: url });
        });
        return results;
    }""")
    
    appended = 0
    for p_item in extracted:
        if len(rows) >= 50:
            break
        slug = p_item["url"].split("?")[0].rstrip("/").split("/")[-1].lower()
        if slug in existing_slugs or "alumni" in p_item["name"].lower() or "association" in p_item["name"].lower():
            continue
        
        conn, dm = get_notes(p_item["name"], "Swiggy")
        rows.append({
            "name": p_item["name"],
            "url": p_item["url"],
            "company": "Swiggy",
            "role": "Software Engineer",
            "connection_note": conn,
            "dm_note": dm
        })
        existing_slugs.add(slug)
        appended += 1
        print(f"Appended Swiggy prospect: {p_item['name']}")
        
    page.close()

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "url", "company", "role", "connection_note", "dm_note"])
    writer.writeheader()
    writer.writerows(rows)
    
print(f"Final list has {len(rows)} rows.")
