import sys
import re
from urllib.parse import quote
from playwright.sync_api import sync_playwright

def search_company(page, company_name):
    print(f"\n==================================================")
    print(f"SEARCHING FOR {company_name} VIT ALUMNI...")
    print(f"==================================================")
    keywords = f'"Vellore Institute of Technology" AND "{company_name}" AND "Software Engineer"'
    url = f"https://www.linkedin.com/search/results/people/?keywords={quote(keywords)}"
    print(f"Navigating to: {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(5000)
    
    # Check for redirection to login/auth wall
    if "login" in page.url or "authwall" in page.url:
        print("Warning: Redirected to login/auth wall!")
        return []

    # JS-based parser to extract profiles
    extracted = page.evaluate(f"""() => {{
        const results = [];
        const links = Array.from(document.querySelectorAll("a[href*='/in/']"));
        const seenUrls = new Set();
        
        links.forEach((link, idx) => {{
            const url = link.href.split('?')[0];
            if (seenUrls.has(url)) return;
            if (url.includes('/in/ACoA') || url.includes('/search/')) return;
            
            const nameText = (link.innerText || '').trim().split('\\n')[0].trim();
            if (!nameText || nameText.length < 2 || nameText.includes('photo') || nameText.includes('View') || nameText.includes('profile')) return;
            
            // Find smallest ancestor containing a button or link with action text
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
            
            // Extract title from card text
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
                    if (title.toLowerCase() === 'connect' || title.toLowerCase() === 'message' || title.toLowerCase().includes('followers')) {{
                        title = '';
                    }}
                }}
            }}
            
            if (!title) {{
                const textNodes = Array.from(card.querySelectorAll('div, span, p')).map(el => el.innerText.trim()).filter(t => t.length > 20);
                const potentialHeadline = textNodes.find(t => {{
                    const tl = t.toLowerCase();
                    return !tl.includes(nameText.toLowerCase()) && 
                           !tl.includes('connect') && 
                           !tl.includes('message') && 
                           !tl.includes('followers') && 
                           !tl.includes('mutual connections');
                }});
                if (potentialHeadline) title = potentialHeadline;
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
    
    print(f"Extracted {len(extracted)} profiles:")
    for j, person in enumerate(extracted):
        print(f"  [{j+1}] Name: {person['name']}")
        print(f"      URL: {person['url']}")
        print(f"      Title: {person.get('title', '')}")
    return extracted

def main():
    try:
        with sync_playwright() as p:
            print("Connecting to Chrome over CDP...")
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = context.new_page()
            
            all_prospects = []
            
            for company in ["BrowserStack", "Juspay", "LambdaTest"]:
                prospects = search_company(page, company)
                all_prospects.extend(prospects)
                page.wait_for_timeout(3000)
                
            print(f"\n==================================================")
            print(f"TOTAL EXTRACTED: {len(all_prospects)}")
            print(f"==================================================")
            
            page.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
