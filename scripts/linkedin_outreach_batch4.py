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
PROGRESS_FILE = VAULT_ROOT / "active_application_context" / "linkedin_outreach_progress_batch4.json"
TRACKER_FILE = VAULT_ROOT / "active_application_context" / "job_applications_tracker.md"

PROFILES = [
    {
        "index": 1,
        "name": "Girish Mathrubootham",
        "company": "Freshworks",
        "url": "https://www.linkedin.com/in/girishmathrubootham",
        "note": "Hey Girish, I am a Full Stack and AI engineer. Shipped MERN TypeScript systems and LangGraph agents at OpenBiz (founding engineer). Exploring roles at Freshworks. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 2,
        "name": "Sridhar Vembu",
        "company": "Zoho",
        "url": "https://www.linkedin.com/in/sridharvembu",
        "note": "Hey Sridhar, I am a Full Stack and AI engineer. Built Nimbus RAG (sub 800ms), VyaparGPT (WhatsApp AI, 40 SMBs), and LangGraph agents at OpenBiz. Exploring roles at Zoho. Would you refer me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 3,
        "name": "Raju Vegesna",
        "company": "Zoho",
        "url": "https://www.linkedin.com/in/rajuvegesna",
        "note": "Hey Raju, I am a Full Stack and AI engineer (MERN, Python, LangGraph, pgvector RAG). Exploring engineering roles at Zoho. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
    },
    {
        "index": 4,
        "name": "Ragy Thomas",
        "company": "Sprinklr",
        "url": "https://www.linkedin.com/in/ragythomas",
        "note": "Hey Ragy, I am a Full Stack and AI engineer. Built LangGraph stateful agents and VyaparGPT (WhatsApp AI, 40 SMBs) at OpenBiz. Exploring AI engineering roles at Sprinklr. Would you refer me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 5,
        "name": "Rohit Chennamaneni",
        "company": "Darwinbox",
        "url": "https://www.linkedin.com/in/rohitchennamaneni",
        "note": "Hey Rohit, I am a Full Stack and AI engineer (MERN, TypeScript, Python, LangGraph). Exploring engineering roles at Darwinbox. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
    },
    {
        "index": 6,
        "name": "Chaitanya Peddi",
        "company": "Darwinbox",
        "url": "https://www.linkedin.com/in/chaitanyapeddi",
        "note": "Hey Chaitanya, I am a Full Stack and AI engineer. Shipped LangGraph agents and MERN TypeScript systems at OpenBiz. Exploring roles at Darwinbox. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 7,
        "name": "Jayant Paleti",
        "company": "Darwinbox",
        "url": "https://www.linkedin.com/in/jayantpaleti",
        "note": "Hey Jayant, I am a Full Stack and AI engineer (LangGraph, pgvector RAG, MERN TypeScript). Exploring engineering roles at Darwinbox. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
    },
    {
        "index": 8,
        "name": "Vibhor Jain",
        "company": "Darwinbox",
        "url": "https://www.linkedin.com/in/vibhorjain",
        "note": "Hey Vibhor, I am a Full Stack and AI engineer. Shipped LangGraph agents and MERN TypeScript systems at OpenBiz. Exploring AI engineering roles at Darwinbox. Would you refer me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 9,
        "name": "Sameer Nigam",
        "company": "PhonePe",
        "url": "https://www.linkedin.com/in/sameernigam",
        "note": "Hey Sameer, I am a Full Stack engineer. Shipped idempotent payment webhook billing with 100% consistency and cut API latency 40% at OpenBiz. Exploring roles at PhonePe. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 10,
        "name": "Rahul Chari",
        "company": "PhonePe",
        "url": "https://www.linkedin.com/in/rahulchari",
        "note": "Hey Rahul, I am a Full Stack engineer. Built idempotent payment webhook billing (100% consistency) and resolved N plus 1 patterns cutting API latency 40% at OpenBiz. Exploring engineering roles at PhonePe. Would you refer me if there are openings? Happy to share my resume."
    },
    {
        "index": 11,
        "name": "Deepak Abbot",
        "company": "PhonePe",
        "url": "https://www.linkedin.com/in/deepakabbot",
        "note": "Hey Deepak, I am a Full Stack engineer. Shipped idempotent payment webhook billing and cut API latency 40% at OpenBiz. Exploring engineering roles at PhonePe. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 12,
        "name": "Kunal Shah",
        "company": "CRED",
        "url": "https://www.linkedin.com/in/kunalb11",
        "note": "Hey Kunal, I am a Full Stack and AI engineer. Built LangGraph agents, pgvector RAG, and idempotent payment webhook systems at OpenBiz. Exploring engineering roles at CRED. Would you refer me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 13,
        "name": "Lalit Keshre",
        "company": "Groww",
        "url": "https://www.linkedin.com/in/lalitkeshre",
        "note": "Hey Lalit, I am a Full Stack and AI engineer (MERN, TypeScript, LangGraph). Exploring engineering roles at Groww in fintech. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
    },
    {
        "index": 14,
        "name": "Vidit Aatrey",
        "company": "Meesho",
        "url": "https://www.linkedin.com/in/viditaatrey",
        "note": "Hey Vidit, I am a Full Stack and AI engineer. Built LangGraph agents and a pgvector RAG pipeline at OpenBiz. Exploring AI engineering roles at Meesho. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 15,
        "name": "Sanjeev Barnwal",
        "company": "Meesho",
        "url": "https://www.linkedin.com/in/sanjeevbarnwal",
        "note": "Hey Sanjeev, I am a Full Stack and AI engineer (MERN, TypeScript, LangGraph, pgvector RAG). Exploring engineering roles at Meesho. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
    },
    {
        "index": 16,
        "name": "Aadit Palicha",
        "company": "Zepto",
        "url": "https://www.linkedin.com/in/aaditpalicha",
        "note": "Hey Aadit, I am a Full Stack and AI engineer. Built LangGraph agents and MERN TypeScript systems at OpenBiz. Exploring engineering roles at Zepto. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 17,
        "name": "Kaivalya Vohra",
        "company": "Zepto",
        "url": "https://www.linkedin.com/in/kaivalyavohra",
        "note": "Hey Kaivalya, I am a Full Stack and AI engineer (MERN, Python, TypeScript, LangGraph). Exploring engineering roles at Zepto. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
    },
    {
        "index": 18,
        "name": "Raviteja Dodda",
        "company": "MoEngage",
        "url": "https://www.linkedin.com/in/ravitejadodda",
        "note": "Hey Raviteja, I am a Full Stack and AI engineer. Shipped LangGraph agents and a pgvector RAG pipeline at OpenBiz. Exploring roles at MoEngage. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 19,
        "name": "Avlesh Singh",
        "company": "WebEngage",
        "url": "https://www.linkedin.com/in/avleshsingh",
        "note": "Hey Avlesh, I am a Full Stack and AI engineer. Built LangGraph agents and a provider agnostic LLM layer at OpenBiz. Exploring AI engineering roles at WebEngage. Would you refer me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 20,
        "name": "Srikanth Velamakanni",
        "company": "Fractal",
        "url": "https://www.linkedin.com/in/srikanthvelamakanni",
        "note": "Hey Srikanth, I am a Full Stack and AI engineer. Shipped LangGraph agents, pgvector RAG (sub 800ms), and Gemini Vision doc extraction at OpenBiz. Exploring AI roles at Fractal. Would love to be considered for relevant openings. Happy to share my resume."
    },
    {
        "index": 21,
        "name": "Pranay Agrawal",
        "company": "Fractal",
        "url": "https://www.linkedin.com/in/pranayagrawal",
        "note": "Hey Pranay, I am a Full Stack and AI engineer (LangGraph, pgvector RAG, MERN TypeScript). Exploring AI engineering roles at Fractal. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
    },
    {
        "index": 22,
        "name": "Prashant Warier",
        "company": "Qure.ai",
        "url": "https://www.linkedin.com/in/prashantwarier",
        "note": "Hey Prashant, I am a Full Stack and AI engineer. Built Gemini Vision document extraction pipelines and LangGraph agents at OpenBiz. Exploring applied AI roles at Qure.ai. Would love to be considered for relevant openings. Happy to share my resume."
    },
    {
        "index": 23,
        "name": "Shivakumar",
        "company": "Exotel",
        "url": "https://www.linkedin.com/in/shivku",
        "note": "Hey Shivakumar, I am a Full Stack and AI engineer. Shipped LangGraph agents and VyaparGPT (WhatsApp AI, 40 SMBs) at OpenBiz. Exploring roles at Exotel. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 24,
        "name": "Baskar Subramanian",
        "company": "Amagi",
        "url": "https://www.linkedin.com/in/baskarsubramanian",
        "note": "Hey Baskar, I am a Full Stack and AI engineer (LangGraph, pgvector RAG, MERN TypeScript). Exploring engineering roles at Amagi. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
    },
    {
        "index": 25,
        "name": "Abhiraj Bahl",
        "company": "UrbanCompany",
        "url": "https://www.linkedin.com/in/abhirajbahl",
        "note": "Hey Abhiraj, I am a Full Stack and AI engineer. Built LangGraph agents and MERN TypeScript systems at OpenBiz. Exploring AI engineering roles at UrbanCompany. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 26,
        "name": "Varun Khaitan",
        "company": "UrbanCompany",
        "url": "https://www.linkedin.com/in/varunkhaitan",
        "note": "Hey Varun, I am a Full Stack and AI engineer (MERN, TypeScript, Python, LangGraph). Exploring engineering roles at UrbanCompany. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
    },
    {
        "index": 27,
        "name": "Aravind Sanka",
        "company": "Rapido",
        "url": "https://www.linkedin.com/in/aravindsanka",
        "note": "Hey Aravind, I am a Full Stack and AI engineer (LangGraph, pgvector RAG, MERN TypeScript). Exploring engineering roles at Rapido. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
    },
    {
        "index": 28,
        "name": "Bhavin Turakhia",
        "company": "Zeta",
        "url": "https://www.linkedin.com/in/bhavinturakhia",
        "note": "Hey Bhavin, I am a Full Stack engineer. Shipped idempotent payment webhook billing (100% consistency) and LangGraph agents at OpenBiz. Exploring fintech engineering roles at Zeta. Would you refer me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 29,
        "name": "Ramki Gaddipati",
        "company": "Zeta",
        "url": "https://www.linkedin.com/in/ramkigaddipati",
        "note": "Hey Ramki, I am a Full Stack engineer. Built idempotent payment webhook systems and LangGraph agents at OpenBiz. Exploring fintech engineering roles at Zeta. Would you be open to referring me if there are openings? Happy to share my resume."
    },
    {
        "index": 30,
        "name": "Jitendra Gupta",
        "company": "Jupiter",
        "url": "https://www.linkedin.com/in/jitgupta",
        "note": "Hey Jitendra, I am a Full Stack engineer. Shipped idempotent payment webhook billing and LangGraph agents at OpenBiz. Exploring fintech engineering roles at Jupiter. Would you be open to referring me if there are openings? Happy to share my resume."
    },
    {
        "index": 31,
        "name": "Rajan Bajaj",
        "company": "Slice",
        "url": "https://www.linkedin.com/in/rajanbajaj",
        "note": "Hey Rajan, I am a Full Stack and AI engineer. Shipped idempotent payment webhook systems and LangGraph agents at OpenBiz. Exploring engineering roles at Slice. Would you be open to referring me if there are openings? Happy to share my resume."
    },
    {
        "index": 32,
        "name": "Sujith Narayanan",
        "company": "Fi.Money",
        "url": "https://www.linkedin.com/in/sujithnarayanan",
        "note": "Hey Sujith, I am a Full Stack and AI engineer (MERN, TypeScript, Python, LangGraph). Exploring fintech engineering roles at Fi.Money. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
    },
    {
        "index": 33,
        "name": "Sumit Gwalani",
        "company": "Fi.Money",
        "url": "https://www.linkedin.com/in/sumitgwalani",
        "note": "Hey Sumit, I am a Full Stack and AI engineer. Built payment webhook systems and LangGraph AI agents at OpenBiz. Exploring fintech engineering roles at Fi.Money. Would you be open to referring me if there are openings? Happy to share my resume."
    },
    {
        "index": 34,
        "name": "Soumyadeb",
        "company": "RudderStack",
        "url": "https://www.linkedin.com/in/soumyadeb",
        "note": "Hey Soumyadeb, I am a Full Stack and AI engineer. Shipped MERN TypeScript systems and pgvector RAG pipelines at OpenBiz. Exploring data engineering roles at RudderStack. Would you refer me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 35,
        "name": "Ankit Nayan",
        "company": "SigNoz",
        "url": "https://www.linkedin.com/in/ankitnayan",
        "note": "Hey Ankit, I am a Full Stack and AI engineer (MERN, TypeScript, Python). Built developer tooling and LangGraph agents at OpenBiz. Exploring engineering roles at SigNoz. Would you be open to referring me if there are openings? Happy to share my resume."
    },
    {
        "index": 36,
        "name": "Pranay Shah",
        "company": "SigNoz",
        "url": "https://www.linkedin.com/in/pranayshah",
        "note": "Hey Pranay, I am a Full Stack and AI engineer (MERN, TypeScript, Python). Built developer tooling and autonomous web agents at OpenBiz. Exploring engineering roles at SigNoz. Would you be open to referring me if there are openings? Happy to share my resume."
    },
    {
        "index": 37,
        "name": "Gaurav Munjal",
        "company": "Unacademy",
        "url": "https://www.linkedin.com/in/gauravmunjal",
        "note": "Hey Gaurav, I am a Full Stack and AI engineer. Shipped LangGraph agents and MERN TypeScript systems at OpenBiz. Exploring engineering roles at Unacademy. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 38,
        "name": "Hemesh Singh",
        "company": "Unacademy",
        "url": "https://www.linkedin.com/in/hemeshsingh",
        "note": "Hey Hemesh, I am a Full Stack and AI engineer (MERN, TypeScript, Python, LangGraph). Exploring engineering roles at Unacademy. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
    },
    {
        "index": 39,
        "name": "Roman Saini",
        "company": "Unacademy",
        "url": "https://www.linkedin.com/in/romansaini",
        "note": "Hey Roman, I am a Full Stack and AI engineer (MERN, TypeScript, Python, LangGraph). Exploring engineering roles at Unacademy. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
    },
    {
        "index": 40,
        "name": "Vamsi Krishna",
        "company": "Vedantu",
        "url": "https://www.linkedin.com/in/vamsikrishna",
        "note": "Hey Vamsi, I am a Full Stack and AI engineer. Built LangGraph agents and MERN TypeScript systems at OpenBiz. Exploring engineering roles at Vedantu. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 41,
        "name": "Niraj Ranjan Rout",
        "company": "Hiver",
        "url": "https://www.linkedin.com/in/nirajranjanrout",
        "note": "Hey Niraj, I am a Full Stack and AI engineer (MERN, TypeScript, Python, LangGraph). Exploring engineering roles at Hiver. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
    },
    {
        "index": 42,
        "name": "Anand Jain",
        "company": "CleverTap",
        "url": "https://www.linkedin.com/in/anandjain1",
        "note": "Hey Anand, I am a Full Stack and AI engineer. Shipped LangGraph agents and a pgvector RAG pipeline at OpenBiz. Exploring AI engineering roles at CleverTap. Would you be open to referring me if there are openings? Happy to share my resume."
    },
    {
        "index": 43,
        "name": "Suresh Vasudevan",
        "company": "CleverTap",
        "url": "https://www.linkedin.com/in/sureshvasudevan",
        "note": "Hey Suresh, I am a Full Stack and AI engineer. Shipped LangGraph agents and a pgvector RAG pipeline at OpenBiz. Exploring AI engineering roles at CleverTap. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 44,
        "name": "Rajesh Jain",
        "company": "Netcore Cloud",
        "url": "https://www.linkedin.com/in/rajeshjainnm",
        "note": "Hey Rajesh, I am a Full Stack and AI engineer. Built LangGraph agents and a provider agnostic LLM layer at OpenBiz. Exploring AI engineering roles at Netcore Cloud. Would you refer me if there are openings? Happy to share my resume."
    },
    {
        "index": 45,
        "name": "Kalpit Jain",
        "company": "Netcore",
        "url": "https://www.linkedin.com/in/kalpitjain",
        "note": "Hey Kalpit, I am a Full Stack and AI engineer. Built LangGraph agents and a provider agnostic LLM layer at OpenBiz. Exploring AI engineering roles at Netcore. Would you be open to referring me if there are openings? Happy to share my resume."
    },
    {
        "index": 46,
        "name": "Manav Garg",
        "company": "Eka",
        "url": "https://www.linkedin.com/in/manavgarg",
        "note": "Hey Manav, I am a Full Stack and AI engineer. Shipped LangGraph agents and pgvector RAG pipelines at OpenBiz. Exploring AI engineering roles at Eka. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 47,
        "name": "Mukul Rustagi",
        "company": "Classplus",
        "url": "https://www.linkedin.com/in/mukulrustagi",
        "note": "Hey Mukul, I am a Full Stack and AI engineer (MERN, TypeScript, Python, LangGraph). Exploring engineering roles at Classplus. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
    },
    {
        "index": 48,
        "name": "Pawan Gupta",
        "company": "Classplus",
        "url": "https://www.linkedin.com/in/pawangupta",
        "note": "Hey Pawan, I am a Full Stack and AI engineer. Built LangGraph agents and MERN TypeScript systems at OpenBiz. Exploring engineering roles at Classplus. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 49,
        "name": "Adit Jain",
        "company": "Leena AI",
        "url": "https://www.linkedin.com/in/aditjain",
        "note": "Hey Adit, I am a Full Stack and AI engineer. Shipped LangGraph agents and VyaparGPT (WhatsApp AI, 40 SMBs) at OpenBiz. Exploring roles at Leena AI. Would you refer me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 50,
        "name": "Shridhar Marri",
        "company": "Kaleyra",
        "url": "https://www.linkedin.com/in/shridharmarri",
        "note": "Hey Shridhar, I am a Full Stack and AI engineer. Shipped VyaparGPT (WhatsApp AI, LangGraph, 40 SMBs) and conversational AI pipelines at OpenBiz. Exploring roles at Kaleyra. Would you refer me if there are openings? Happy to share my resume."
    }
]

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
    # Also remove any mention of salary/CTC/LPA
    note = re.sub(r'\b(salary|ctc|lpa|15\s*l|15\s*lpa|15\s*lakhs?)\b', '', note, flags=re.IGNORECASE)
    # Remove double spaces
    note = re.sub(r'\s+', ' ', note).strip()
    return note

def get_first_name(full_name: str) -> str:
    return full_name.split()[0]

def format_note_for_vit(name: str, standard_note: str) -> str:
    # Rule 1: Replace "Hey [Name]" with "Hey [Name], fellow VIT alum here."
    first_name = get_first_name(name)
    greeting_pattern = re.compile(rf"^Hey\s+{re.escape(first_name)}(,\s*|\s+)", re.IGNORECASE)
    
    if greeting_pattern.match(standard_note):
        new_greeting = f"Hey {first_name}, fellow VIT alum here. "
        rest = greeting_pattern.sub("", standard_note)
        note = new_greeting + rest
    else:
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
    body_text = page.locator("body").inner_text().lower()
    # Rule 6: CAPTCHA / Security halt
    if "captcha" in body_text or "security verification" in body_text or "suspicious activity" in body_text:
        print("HALTED_CAPTCHA: CAPTCHA / Security Verification detected.")
        sys.exit(EXIT_CAPTCHA)
        
    if "checkpoint" in page.url or "challenge" in page.url:
        print("HALTED_CAPTCHA: Security challenge page detected.")
        sys.exit(EXIT_CAPTCHA)
        
    if "sign in" in body_text and "linkedin" in body_text and page.locator("input[type='password']").count() > 0:
        print("STOPPING: LinkedIn logged out or sign-in required.")
        sys.exit(EXIT_LOGIN_REQUIRED)

def send_invitation(page, slug: str, note: str) -> str:
    # Rule 5: Use preload URL
    direct_url = f"https://www.linkedin.com/preload/custom-invite/?vanityName={slug}"
    print(f"Opening direct customize invite URL: {direct_url}")
    page.goto(direct_url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3000)
    
    check_security_challenges(page)
    
    dialog = page.locator('.artdeco-modal').first
    # Rule 4: SKIPPED_NO_CONNECT if modal is absent
    if dialog.count() == 0 or not dialog.is_visible():
        print(f"Invite modal didn't open for slug: {slug}. Connection options might be absent.")
        return "SKIPPED_NO_CONNECT"
        
    dialog_text = dialog.inner_text().lower()
    
    limit_keywords = [
        "weekly invitation limit", 
        "reached the limit", 
        "try again tomorrow", 
        "maximum number of invitations", 
        "out of invitations",
        "weekly limit"
    ]
    for kw in limit_keywords:
        if kw in dialog_text or kw in page.locator("body").inner_text().lower():
            print(f"STOPPING: Reached LinkedIn invitation limit. Found '{kw}'")
            sys.exit(EXIT_LIMIT_REACHED)
            
    add_note_btn = dialog.locator('button:has-text("Add a note")')
    if add_note_btn.count() > 0 and add_note_btn.is_visible():
        print("Clicking 'Add a note'...")
        add_note_btn.click()
        page.wait_for_timeout(1000)
        
    textarea = dialog.locator('textarea')
    if textarea.count() == 0:
        print("Textarea not found in the custom invite dialog.")
        return "SKIPPED_NO_CONNECT"
        
    textarea.wait_for(timeout=5000)
    print(f"Typing note ({len(note)} chars): {note}")
    textarea.fill(note)
    page.wait_for_timeout(1000)
    
    send_btn = dialog.locator('button:has-text("Send"), button:has-text("Send invitation")')
    if send_btn.count() == 0:
        print("Send button not found in the custom invite dialog.")
        return "SKIPPED_NO_CONNECT"
        
    print("Clicking 'Send'...")
    send_btn.click()
    page.wait_for_timeout(3000)
    
    body_text_after = page.locator("body").inner_text().lower()
    for kw in limit_keywords:
        if kw in body_text_after:
            print(f"STOPPING: Reached LinkedIn invitation limit after click. Found '{kw}'")
            sys.exit(EXIT_LIMIT_REACHED)
            
    return "SENT"

def run_outreach():
    progress = load_progress()
    print(f"Loaded progress: {len(progress)}/{len(PROFILES)} profiles processed.")
    
    try:
        with sync_playwright() as p:
            print("Connecting to Chrome on port 9222...")
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            page = browser.contexts[0].pages[0]
            
            for profile in PROFILES:
                idx = profile["index"]
                name = profile["name"]
                company = profile["company"]
                url = profile["url"]
                std_note = profile["note"]
                
                slug = url.rstrip("/").split("/")[-1]
                
                if str(idx) in progress:
                    saved = progress[str(idx)]
                    # Only skip if it's already completely processed or skipped
                    if saved["status"] not in ["FAILED", "Unknown"]:
                        continue
                
                print(f"\n[{idx}/50] Processing {name} ({company}) - {url}")
                
                # Navigate to profile first to check connection & education
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(3000)
                
                check_security_challenges(page)
                
                # Rule 4 & Rule 8 check on profile page
                conn_status = check_connection_status(page)
                print(f"Connection Status check: {conn_status}")
                
                if conn_status in ["SKIPPED_404", "SKIPPED_ALREADY_CONNECTED"]:
                    progress[str(idx)] = {
                        "name": name,
                        "company": company,
                        "url": url,
                        "status": conn_status,
                        "note": "None",
                        "timestamp": datetime.now().isoformat()
                    }
                    save_progress(progress)
                    continue
                    
                # Rule 1: VIT Alumni Check
                is_vit = check_vit_education(page)
                print(f"Is VIT Alum: {is_vit}")
                
                # Format Note
                if is_vit:
                    note = format_note_for_vit(name, std_note)
                else:
                    note = std_note
                    
                # Rule 2: Clean note of dashes / salary terms
                note = clean_note_text(note)
                
                # Rule 3: Character Limit check (strict skip, no truncation)
                if len(note) > 300:
                    print(f"SKIPPED_OVERLIMIT: Note has {len(note)} chars (max 300).")
                    progress[str(idx)] = {
                        "name": name,
                        "company": company,
                        "url": url,
                        "status": "SKIPPED_OVERLIMIT",
                        "note": note,
                        "timestamp": datetime.now().isoformat()
                    }
                    save_progress(progress)
                    continue
                
                # Send invitation
                status_result = send_invitation(page, slug, note)
                
                progress[str(idx)] = {
                    "name": name,
                    "company": company,
                    "url": url,
                    "status": status_result,
                    "note": note if status_result == "SENT" else "None",
                    "timestamp": datetime.now().isoformat()
                }
                save_progress(progress)
                
                if status_result == "SENT":
                    log_to_tracker(company, name, "Invite Sent", f"SENT (Outreach Batch 4)")
                    
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
        # Catch sys.exit for limit or captcha
        if e.code == EXIT_CAPTCHA:
            # Update currently active profile as HALTED_CAPTCHA
            pass
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
