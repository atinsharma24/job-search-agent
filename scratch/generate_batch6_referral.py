import json
import re
import csv
import sys
from urllib.parse import quote
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path("/Users/atinsharma/job_search_vault")
TRACKER_FILE = ROOT / "active_application_context" / "job_applications_tracker.md"
APPROVED_JSON = ROOT / "linkedin_outreach" / "queue" / "approved.json"
SENT_JSON = ROOT / "linkedin_outreach" / "queue" / "sent.json"
OUTPUT_CSV = ROOT / "linkedin_outreach" / "contacts" / "batch6_referral.csv"

def get_slug(url: str) -> str:
    if not url:
        return ''
    url = url.split('?')[0].rstrip('/')
    return url.split('/')[-1].lower()

def load_already_sent_targets():
    sent_slugs = set()
    sent_names = set()

    # 1. Parse tracker markdown
    if TRACKER_FILE.exists():
        try:
            content = TRACKER_FILE.read_text(encoding='utf-8')
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
            print(f"Error reading tracker file: {e}")

    # 2. Parse progress files
    context_dir = ROOT / "active_application_context"
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
    if SENT_JSON.exists():
        try:
            sent_data = json.loads(SENT_JSON.read_text(encoding='utf-8'))
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

def get_notes(name: str, company: str) -> tuple[str, str]:
    first_name = get_first_name(name)
    co = company.lower()
    
    if "juspay" in co:
        conn = f"Hey {first_name}, fellow VIT alum here. Shipped idempotent payments webhooks with 100% payment consistency and cut API latency 40% via N+1 resolution. No ramp on payments engineering stack. Looking to connect."
        dm = f"Hey {first_name}, fellow VIT alum here. I'm Atin, a Full Stack and AI engineer. At OpenBiz I shipped idempotent payment webhooks (100% consistency), cut API latency 40% via N+1 fixes, and built LangGraph agents. I'm exploring roles at Juspay and would love to connect."
    elif "browserstack" in co:
        conn = f"Hey {first_name}, fellow VIT alum here. Shipped an autonomous web agent (Claude + MCP) and MERN platform serving 1000+ users. No ramp on BrowserStack's test automation backend. Would like to connect."
        dm = f"Hey {first_name}, fellow VIT alum here. I'm Atin, a Full Stack and AI engineer. Shipped an autonomous web agent using Claude + MCP for DOM interactions and MERN platform serving 1000+ users. No ramp on BrowserStack's test automation backend. Would value connecting."
    elif "lambdatest" in co:
        conn = f"Hey {first_name}, fellow VIT alum here. Shipped an autonomous web agent (Claude + MCP) handling DOM interactions and CAPTCHA detection. No ramp on LambdaTest's test automation backend. Would like to connect."
        dm = f"Hey {first_name}, fellow VIT alum here. I'm Atin, a Full Stack and AI engineer. Shipped an autonomous web agent (Claude + MCP) handling DOM interactions and CAPTCHA detection. Looking at engineering roles at LambdaTest and would love to connect."
    elif "swiggy" in co:
        conn = f"Hey {first_name}, fellow VIT alum here. Shipped idempotent payments webhooks (100% consistency) and cut API latency 40% via N+1 resolution at OpenBiz. Would value connecting to learn about engineering roles at Swiggy."
        dm = f"Hey {first_name}, fellow VIT alum here. I'm Atin, a Full Stack and AI engineer. Shipped idempotent payment webhook billing (100% consistency) and cut API latency 40% via N+1 fixes at OpenBiz. Would value connecting to learn about engineering roles at Swiggy."
    elif "decentro" in co:
        conn = f"Hey {first_name}, fellow VIT alum here. Shipped idempotent payment webhook billing (100% consistency) and pgvector RAG at OpenBiz. Exploring fintech engineering roles at Decentro. Would value connecting."
        dm = f"Hey {first_name}, fellow VIT alum here. I'm Atin, a Full Stack and AI engineer. Shipped idempotent payment webhook billing (100% consistency) and pgvector RAG at OpenBiz. Exploring fintech engineering roles at Decentro. Would value connecting."
    elif "signzy" in co:
        conn = f"Hey {first_name}, fellow VIT alum here. Shipped Gemini Vision doc extraction (GST, invoices, Aadhaar) and N+1 fix (40% latency drop) at OpenBiz. Ready to contribute to Signzy's KYC engineering stack from day one."
        dm = f"Hey {first_name}, fellow VIT alum here. I'm Atin, a Full Stack and AI engineer. Shipped Gemini Vision doc extraction (GST, invoices, Aadhaar) and N+1 fix (40% latency drop) at OpenBiz. Ready to contribute to Signzy's KYC engineering stack from day one."
    elif "yellow.ai" in co:
        conn = f"Hey {first_name}, fellow VIT alum here. Shipped VyaparGPT (WhatsApp native LLM, LangGraph, 40 SMBs) and pgvector RAG. Yellow.ai's conversational AI backend is the right next problem. Would value connecting."
        dm = f"Hey {first_name}, fellow VIT alum here. I'm Atin, a Full Stack and AI engineer. Shipped VyaparGPT (WhatsApp native LLM, LangGraph, 40 SMBs) and pgvector RAG at OpenBiz. Yellow.ai's conversational AI backend is a great fit. Would value connecting."
    elif "sarvam" in co:
        conn = f"Hey {first_name}, fellow VIT alum here. Shipped Nimbus RAG (sub-800ms pgvector) and dual-model fallback at OpenBiz. Sarvam AI's LLM infrastructure is where this experience maps. Would like to connect."
        dm = f"Hey {first_name}, fellow VIT alum here. I'm Atin, a Full Stack and AI engineer. Shipped Nimbus RAG (sub-800ms pgvector) and dual-model fallback at OpenBiz. Sarvam AI's LLM infrastructure is where this experience maps. Would like to connect."
    elif "qure" in co:
        conn = f"Hey {first_name}, fellow VIT alum here. Shipped LangGraph stateful agents, pgvector RAG, and MERN TypeScript backend at OpenBiz. Exploring engineering roles at Qure.ai. Would value connecting."
        dm = f"Hey {first_name}, fellow VIT alum here. I'm Atin, a Full Stack and AI engineer. Shipped LangGraph stateful agents, pgvector RAG, and MERN TypeScript backend at OpenBiz. Exploring engineering roles at Qure.ai. Would value connecting."
    elif "babblebots" in co:
        conn = f"Hey {first_name}, fellow VIT alum here. Shipped VyaparGPT (WhatsApp native LLM, LangGraph, 40 SMBs) and pgvector RAG. Exploring conversational AI engineer roles at Babblebots.ai. Would value connecting."
        dm = f"Hey {first_name}, fellow VIT alum here. I'm Atin, a Full Stack and AI engineer. Shipped VyaparGPT (WhatsApp native LLM, LangGraph, 40 SMBs) and pgvector RAG at OpenBiz. Exploring conversational AI engineering roles at Babblebots.ai. Would value connecting."
    else:
        conn = f"Hey {first_name}, fellow VIT alum here. Shipped LangGraph stateful agents, pgvector RAG, and MERN TypeScript backend at OpenBiz. Exploring engineering roles at {company}. Would value connecting."
        dm = f"Hey {first_name}, fellow VIT alum here. I'm Atin, a Full Stack and AI engineer. Shipped LangGraph stateful agents, pgvector RAG, and MERN TypeScript backend at OpenBiz. Exploring engineering roles at {company}. Would value connecting."
        
    return clean_note_text(conn), clean_note_text(dm)

def search_company(page, company_name, sent_names, sent_slugs):
    print(f"\nSearching for {company_name} VIT Alumni...")
    prospects_company = []
    seen_urls_session = set()
    
    page_num = 1
    max_pages = 5  # Scan up to 5 pages of search results per company
    
    while page_num <= max_pages:
        print(f"  Scanning page {page_num}...")
        keywords = f'\"Vellore Institute of Technology\" AND \"{company_name}\" AND \"Software Engineer\"'
        url = f"https://www.linkedin.com/search/results/people/?keywords={quote(keywords)}&page={page_num}"
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(4000)
        
        if check_security_challenge(page):
            print("\n[HALT] LinkedIn security challenge / CAPTCHA detected. Stopping.")
            sys.exit(1)
            
        if "login" in page.url or "authwall" in page.url:
            print("    [Warning] Redirected to login/auth wall!")
            break

        extracted = page.evaluate(f"""() => {{
            const results = [];
            const links = Array.from(document.querySelectorAll("a[href*='/in/']"));
            const seenUrls = new Set();
            
            links.forEach((link) => {{
                const url = link.href.split('?')[0];
                if (seenUrls.has(url)) return;
                if (url.includes('/in/ACoA') || url.includes('/search/')) return;
                
                const nameText = (link.innerText || '').trim().split('\\n')[0].trim();
                if (!nameText || nameText.length < 2 || nameText.includes('photo') || nameText.includes('View') || nameText.includes('profile')) return;
                
                let card = null;
                let p = link.parentElement;
                for (let depth = 0; depth < 10; depth++) {{
                    if (!p) break;
                    const text = (p.innerText || '').toLowerCase();
                    if (text.includes('connect') || text.includes('message') || text.includes('pending') || text.includes('follow')) {{
                        card = p;
                        break;
                    }}
                    p = p.parentElement;
                }}
                
                if (!card) return;
                seenUrls.add(url);
                
                const cardText = card.innerText || '';
                const lines = cardText.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                
                let title = '';
                const nameIdx = lines.findIndex(l => l.includes(nameText));
                if (nameIdx !== -1) {{
                    let titleIdx = nameIdx + 1;
                    if (titleIdx < lines.length && (lines[titleIdx].includes('•') || lines[titleIdx].match(/^\\d(st|nd|rd|th)/))) {{
                        titleIdx++;
                    }}
                    if (titleIdx < lines.length) {{
                        title = lines[titleIdx];
                    }}
                }}
                results.push({{
                    name: nameText,
                    url: url,
                    title: title.split('\\n')[0].trim(),
                    company: "{company_name}"
                }});
            }});
            return results;
        }}""")
        
        if not extracted:
            print("    No profiles found on this page. Moving to next company.")
            break
            
        new_on_page = 0
        for p in extracted:
            name = p["name"]
            url = p["url"]
            slug = get_slug(url)
            name_clean = name.strip().lower()
            
            # Precise organization filter
            org_terms = ['alumni', 'association', 'university', 'institute', 'placement cell']
            is_org = any(term in name_clean for term in org_terms) or name_clean == 'vit'
            
            if is_org:
                continue
            if slug in seen_urls_session:
                continue
            if name_clean in sent_names or slug in sent_slugs:
                continue
                
            seen_urls_session.add(slug)
            conn_note, dm_note = get_notes(name, company_name)
            
            prospects_company.append({
                "name": name,
                "url": url,
                "company": company_name,
                "role": p.get("title") or "Software Engineer",
                "connection_note": conn_note,
                "dm_note": dm_note
            })
            new_on_page += 1
            
        print(f"    Page {page_num} added {new_on_page} new prospects.")
        if new_on_page == 0:
            print("    No new prospects found on this page. Moving to next company.")
            break
            
        page_num += 1
        page.wait_for_timeout(2000)
        
    print(f"  Found {len(prospects_company)} total unique prospects at {company_name}.")
    return prospects_company

def main():
    print("Loading already contacted lists...")
    sent_names, sent_slugs = load_already_sent_targets()
    print(f"Already contacted: {len(sent_names)} names, {len(sent_slugs)} slugs")

    # Expand to all 10 fresher-friendly target companies
    target_companies = [
        "Juspay", "BrowserStack", "LambdaTest", "Swiggy", 
        "Decentro", "Signzy", "Yellow.ai", "Sarvam AI", 
        "Qure.ai", "Babblebots AI"
    ]
    prospects_collected = []
    
    try:
        with sync_playwright() as p:
            print("Connecting to Chrome over CDP on port 9222...")
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = context.new_page()
            
            for company in target_companies:
                prospects = search_company(page, company, sent_names, sent_slugs)
                prospects_collected.extend(prospects)
                page.wait_for_timeout(3000)
                
            page.close()
            
    except Exception as e:
        print(f"Scraper error: {e}")

    print(f"\n==================================================")
    print(f"TOTAL PROSPECTS GATHERED: {len(prospects_collected)}")
    print(f"==================================================")

    # Write to CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "url", "company", "role", "connection_note", "dm_note"])
        writer.writeheader()
        writer.writerows(prospects_collected)
        
    print(f"Saved {len(prospects_collected)} prospects to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
