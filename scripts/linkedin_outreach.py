#!/usr/bin/env python3
import sys
import os
import json
import re
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

# Constants
EXIT_SUCCESS = 0
EXIT_CAPTCHA = 10
EXIT_LIMIT_REACHED = 11
EXIT_LOGIN_REQUIRED = 12

VAULT_ROOT = Path(__file__).resolve().parents[1]
PROGRESS_FILE = VAULT_ROOT / "active_application_context" / "linkedin_outreach_progress.json"
TRACKER_FILE = VAULT_ROOT / "active_application_context" / "job_applications_tracker.md"

PROFILES = [
    {
        "index": 1,
        "name": "Bhavish Aggarwal",
        "company": "Krutrim",
        "url": "https://www.linkedin.com/in/bhavishaggarwal",
        "note": "Hey Bhavish, I am a Full Stack and AI engineer who built dual model LLM fallback (OpenAI to Gemini) and Nimbus RAG (sub 800ms) at OpenBiz. Genuinely excited about Krutrim's foundation model work. Would love to be considered for any relevant engineering roles. Happy to share my resume."
    },
    {
        "index": 2,
        "name": "Prasad Kavuri",
        "company": "Krutrim",
        "url": "https://www.linkedin.com/in/prasadkavuri",
        "note": "Hey Prasad, I am a Full Stack and AI engineer (LangGraph, pgvector RAG, MERN). Shipped dual model LLM fallback and Nimbus RAG at OpenBiz. Exploring engineering roles at Krutrim. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 3,
        "name": "Vivek Raghavan",
        "company": "Sarvam AI",
        "url": "https://www.linkedin.com/in/vivekraghavan",
        "note": "Hey Vivek, I am a Full Stack and AI engineer. Shipped dual model LLM fallback (OpenAI to Gemini on 5xx) and a provider agnostic layer at OpenBiz. Exploring roles at Sarvam AI. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 4,
        "name": "Pratyush Kumar",
        "company": "Sarvam AI",
        "url": "https://www.linkedin.com/in/pratyush-kumar-9b1b1b",
        "note": "Hey Pratyush, I am a Full Stack and AI engineer. Built Nimbus RAG (sub 800ms pgvector) and a provider agnostic LLM layer at OpenBiz. Exploring roles at Sarvam AI. Would you refer me if there are relevant openings? Happy to share my resume. Thank you."
    },
    {
        "index": 5,
        "name": "Madhav Chinta",
        "company": "Yellow.ai",
        "url": "https://www.linkedin.com/in/madhavchinta",
        "note": "Hey Madhav, I am a Full Stack and AI engineer. Built VyaparGPT (WhatsApp native LLM, LangGraph, 40 SMBs) and a pgvector RAG pipeline at OpenBiz. Exploring roles at Yellow.ai. Would you be open to referring me if there are openings? Happy to share my resume."
    },
    {
        "index": 6,
        "name": "Jithendra Vepa",
        "company": "Observe.AI",
        "url": "https://www.linkedin.com/in/jithendravepa",
        "note": "Hey Jithendra, I am a Full Stack and AI engineer. Shipped LangGraph stateful agents and a real time WhatsApp LLM for 40 SMBs at OpenBiz. Exploring roles at Observe.AI in contact center AI. Would you refer me if there are openings? Happy to share my resume."
    },
    {
        "index": 7,
        "name": "Ayush Kumar",
        "company": "Observe.AI",
        "url": "https://www.linkedin.com/in/ayush-kumar-iitp",
        "note": "Hey Ayush, I am a Full Stack and AI engineer. Built LangGraph agents and a real time WhatsApp LLM for 40 SMBs at OpenBiz. Exploring engineering roles at Observe.AI. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 8,
        "name": "Muzammil Badbade",
        "company": "Observe.AI",
        "url": "https://www.linkedin.com/in/muzammilbadbade",
        "note": "Hey Muzammil, I am a Full Stack and AI engineer. Shipped LangGraph agents and a WhatsApp native LLM for 40 SMBs at OpenBiz. Exploring roles at Observe.AI. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 9,
        "name": "Anup Pattnaik",
        "company": "Observe.AI",
        "url": "https://www.linkedin.com/in/anup-pattnaik",
        "note": "Hey Anup, I am a Full Stack and AI engineer. Shipped LangGraph stateful agents and a real time WhatsApp LLM for 40 SMBs at OpenBiz. Exploring engineering roles at Observe.AI. Would you refer me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 10,
        "name": "Navtej Reddy",
        "company": "Observe.AI",
        "url": "https://www.linkedin.com/in/navtej-reddy",
        "note": "Hey Navtej, I am a Full Stack and AI engineer. Built LangGraph agents and a WhatsApp native LLM for 40 SMBs in prod at OpenBiz. Exploring roles at Observe.AI. Would you be open to referring me if there are openings? Happy to share my resume."
    },
    {
        "index": 11,
        "name": "Ravi Mayuram",
        "company": "Uniphore",
        "url": "https://www.linkedin.com/in/ravimayuram",
        "note": "Hey Ravi, I am a Full Stack and AI engineer. Built VyaparGPT (WhatsApp native LLM, LangGraph, 40 SMBs) and conversational AI pipelines at OpenBiz. Exploring roles at Uniphore. Would you refer me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 12,
        "name": "Ashwini Asokan",
        "company": "Mad Street Den",
        "url": "https://www.linkedin.com/in/ashwiniasokan",
        "note": "Hey Ashwini, I am a Full Stack and AI engineer (LangGraph, pgvector RAG, Gemini Vision doc extraction) from OpenBiz. Really excited about Mad Street Den's applied AI work. Would love to be considered for any relevant engineering roles. Happy to share my resume."
    },
    {
        "index": 13,
        "name": "Anand Chandrasekaran",
        "company": "Mad Street Den",
        "url": "https://www.linkedin.com/in/anand-chandrasekaran-7b1b1b",
        "note": "Hey Anand, I am a Full Stack and AI engineer. Shipped Gemini Vision document extraction and LangGraph AI agents at OpenBiz. Exploring roles at Mad Street Den in applied AI. Would you refer me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 14,
        "name": "Muddu Sudhakar",
        "company": "Aisera",
        "url": "https://www.linkedin.com/in/muddusudhakar",
        "note": "Hey Muddu, I am a Full Stack and AI engineer (LangGraph agents, pgvector RAG, MERN). Built production AI systems for 40 SMBs at OpenBiz. Exploring roles at Aisera in enterprise AI. Would love to be considered for relevant openings. Happy to share my resume."
    },
    {
        "index": 15,
        "name": "Chinna Polinati",
        "company": "Aisera",
        "url": "https://www.linkedin.com/in/chinna-polinati-aisera",
        "note": "Hey Chinna, I am a Full Stack and AI engineer. Shipped LangGraph agents and VyaparGPT (WhatsApp LLM, 40 SMBs) at OpenBiz. Exploring engineering roles at Aisera. Would you be open to referring me if there are openings? Happy to share my resume."
    },
    {
        "index": 16,
        "name": "Shubham Mishra",
        "company": "Pixis",
        "url": "https://www.linkedin.com/in/shubham-mishra-pixis",
        "note": "Hey Shubham, I am a Full Stack and AI engineer. Built LangGraph agents and a provider agnostic LLM layer at OpenBiz. Exploring AI engineering roles at Pixis. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 17,
        "name": "Vrushali Prasade",
        "company": "Pixis",
        "url": "https://www.linkedin.com/in/vrushali-prasade",
        "note": "Hey Vrushali, I am a Full Stack and AI engineer. Shipped LangGraph agents and a pgvector RAG pipeline at OpenBiz. Exploring AI roles at Pixis. Would you be willing to refer me if there are relevant openings? Happy to share my resume. Thank you."
    },
    {
        "index": 18,
        "name": "Vikas Mishra",
        "company": "Pixis",
        "url": "https://www.linkedin.com/in/vikas-mishra-pixis",
        "note": "Hey Vikas, I am a Full Stack and AI engineer (LangGraph, pgvector RAG, MERN TypeScript). Exploring AI engineering roles at Pixis. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
    },
    {
        "index": 19,
        "name": "Ajey Hare Prasath",
        "company": "Pixis",
        "url": "https://www.linkedin.com/in/ajeyhareprasath",
        "note": "Hey Ajey, I am a Full Stack and AI engineer (LangGraph, pgvector RAG, MERN TypeScript). Exploring AI engineering roles at Pixis. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
    },
    {
        "index": 20,
        "name": "Ayushree Chatterjee",
        "company": "Pixis",
        "url": "https://www.linkedin.com/in/ayushree-chatterjee",
        "note": "Hey Ayushree, I am a Full Stack and AI engineer. Shipped LangGraph agents and provider agnostic LLM systems at OpenBiz. Exploring AI roles at Pixis. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 21,
        "name": "Ananth Nagaraj",
        "company": "Gnani.ai",
        "url": "https://www.linkedin.com/in/ananth-nagaraj-gnani",
        "note": "Hey Ananth, I am a Full Stack and AI engineer. Built VyaparGPT (WhatsApp LLM, LangGraph, 40 SMBs) and a pgvector RAG pipeline at OpenBiz. Exploring roles at Gnani.ai. Would you refer me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 22,
        "name": "Abhijeet Pustake",
        "company": "Haptik",
        "url": "https://www.linkedin.com/in/abhijeetpustake",
        "note": "Hey Abhijeet, I am a Full Stack and AI engineer. Built VyaparGPT (WhatsApp native LLM, LangGraph, 40 SMBs) and pgvector RAG at OpenBiz. Exploring roles at Haptik. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 23,
        "name": "Beerud Sheth",
        "company": "Gupshup",
        "url": "https://www.linkedin.com/in/beerud",
        "note": "Hey Beerud, I am a Full Stack and AI engineer. Built a WhatsApp native LLM for 40 SMBs (LangGraph, provider fallback, webhook lifecycle) at OpenBiz. Exploring roles at Gupshup. Would you refer me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 24,
        "name": "Vivek Agarwal",
        "company": "Razorpay",
        "url": "https://www.linkedin.com/in/vivekagarwal",
        "note": "Hey Vivek, I am a Full Stack engineer. Shipped idempotent Razorpay webhook billing with 100% payment consistency and cut API latency 40% at OpenBiz. Exploring roles at Razorpay. Would you be open to referring me if there are openings? Happy to share my resume."
    },
    {
        "index": 25,
        "name": "Prathamesh Joshi",
        "company": "Razorpay",
        "url": "https://www.linkedin.com/in/prathameshjoshi",
        "note": "Hey Prathamesh, I am a Full Stack and AI engineer. Built idempotent Razorpay webhook billing (100% payment consistency) and LangGraph agents at OpenBiz. Exploring roles at Razorpay. Could you refer me if there are openings? Happy to share my resume."
    },
    {
        "index": 26,
        "name": "Chirag Dagha",
        "company": "BrowserStack",
        "url": "https://www.linkedin.com/in/chiragdagha",
        "note": "Hey Chirag, I am a Full Stack and AI engineer. Shipped a Claude plus MCP autonomous web agent for DOM level browser automation at OpenBiz. Exploring roles at BrowserStack. Would you be open to referring me if there are openings? Happy to share my resume."
    },
    {
        "index": 27,
        "name": "Sagar Nautiyal",
        "company": "BrowserStack",
        "url": "https://www.linkedin.com/in/sagarnautiyal",
        "note": "Hey Sagar, I am a Full Stack and AI engineer (MERN, Python, TypeScript). Built a Claude plus MCP autonomous web agent at OpenBiz. Exploring engineering roles at BrowserStack. Would you refer me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 28,
        "name": "Ankit Sobti",
        "company": "Postman",
        "url": "https://www.linkedin.com/in/ankitsobti",
        "note": "Hey Ankit, I am a Full Stack engineer with a Claude plus MCP autonomous web agent and MERN TypeScript experience at OpenBiz. Exploring roles at Postman. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thanks."
    },
    {
        "index": 29,
        "name": "Charu Natarajan",
        "company": "Postman",
        "url": "https://www.linkedin.com/in/charunatarajan",
        "note": "Hey Charu, I am a Full Stack and AI engineer (MERN, Python, LangGraph, RAG). Built a Claude plus MCP autonomous web agent at OpenBiz. Exploring engineering roles at Postman. Could you refer me if there are openings? Happy to share my resume."
    },
    {
        "index": 30,
        "name": "Navitha Pereira",
        "company": "Postman",
        "url": "https://www.linkedin.com/in/navithapereira",
        "note": "Hey Navitha, I am a Full Stack and AI engineer actively exploring roles at Postman. Built VyaparGPT (WhatsApp AI, 40 SMBs) and a Claude plus MCP agent at OpenBiz. Would you be open to referring me? Happy to share my resume. Thank you."
    },
    {
        "index": 31,
        "name": "Manushi Khanna",
        "company": "Hasura",
        "url": "https://www.linkedin.com/in/manushikhanna",
        "note": "Hey Manushi, I am a Full Stack engineer. Resolved deep N plus 1 query chains (40% latency drop) and built a pgvector RAG pipeline at OpenBiz. Exploring roles at Hasura. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 32,
        "name": "Brandon Martin",
        "company": "Hasura",
        "url": "https://www.linkedin.com/in/brandonmartin",
        "note": "Hey Brandon, I am a Full Stack and AI engineer. Built a pgvector RAG pipeline with sub 800ms retrieval and resolved N plus 1 patterns cutting latency 40% at OpenBiz. Exploring roles at Hasura. Would you be open to referring me? Happy to share my resume."
    },
    {
        "index": 33,
        "name": "Jay Singh",
        "company": "LambdaTest",
        "url": "https://www.linkedin.com/in/jaysingh",
        "note": "Hey Jay, I am a Full Stack and AI engineer. Built a Claude plus MCP autonomous web agent handling DOM navigation and WAF detection at OpenBiz. Exploring engineering roles at LambdaTest. Would you be open to referring me? Happy to share my resume."
    },
    {
        "index": 34,
        "name": "Asad Khan",
        "company": "LambdaTest",
        "url": "https://www.linkedin.com/in/asadkhan",
        "note": "Hey Asad, I am a Full Stack and AI engineer. Shipped a Claude plus MCP autonomous agent for DOM level browser automation at OpenBiz. Exploring roles at LambdaTest. Would you be open to referring me if there are openings? Happy to share my resume."
    },
    {
        "index": 35,
        "name": "Japneet Singh Chawla",
        "company": "LambdaTest",
        "url": "https://www.linkedin.com/in/japneetsinghchawla",
        "note": "Hey Japneet, I am a Full Stack and AI engineer (MERN, Python, TypeScript). Built a Claude plus MCP autonomous web agent at OpenBiz. Exploring engineering roles at LambdaTest. Would you refer me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 36,
        "name": "Prince Verma",
        "company": "LambdaTest",
        "url": "https://www.linkedin.com/in/princeverma",
        "note": "Hey Prince, I am a Full Stack and AI engineer. Shipped a Claude plus MCP autonomous web agent and test automation systems at OpenBiz. Exploring roles at LambdaTest. Would you be open to referring me if there are openings? Happy to share my resume."
    },
    {
        "index": 37,
        "name": "Rishabh Arya",
        "company": "LambdaTest",
        "url": "https://www.linkedin.com/in/rishabharya",
        "note": "Hey Rishabh, I am a Full Stack and AI engineer. Built a Claude plus MCP autonomous web agent for browser automation at OpenBiz. Exploring engineering roles at LambdaTest. Would you refer me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 38,
        "name": "Abhishek Nayak",
        "company": "Appsmith",
        "url": "https://www.linkedin.com/in/abhisheknayak",
        "note": "Hey Abhishek, I am a Full Stack and AI engineer (MERN, TypeScript, Python, LangGraph). Built developer tooling and autonomous web agents at OpenBiz. Exploring roles at Appsmith. Would you be open to referring me if there are openings? Happy to share my resume."
    },
    {
        "index": 39,
        "name": "Arpit Mohan",
        "company": "Appsmith",
        "url": "https://www.linkedin.com/in/arpitmohan",
        "note": "Hey Arpit, I am a Full Stack engineer. Shipped MERN TypeScript systems and a Claude plus MCP autonomous web agent at OpenBiz. Exploring engineering roles at Appsmith. Would you refer me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 40,
        "name": "Rahul Barwal",
        "company": "Appsmith",
        "url": "https://www.linkedin.com/in/rahulbarwal",
        "note": "Hey Rahul, I am a Full Stack and AI engineer (MERN, TypeScript, Python, LangGraph). Built developer tooling at OpenBiz. Exploring roles at Appsmith. Would you be open to referring me if there are openings? Happy to share my resume. Thank you."
    },
    {
        "index": 41,
        "name": "Pranav Kanade",
        "company": "Appsmith",
        "url": "https://www.linkedin.com/in/pranavkanade",
        "note": "Hey Pranav, I am a Full Stack engineer with MERN, TypeScript, and Python experience. Built developer tooling and autonomous web agents at OpenBiz. Exploring roles at Appsmith. Would you be open to referring me if there are openings? Happy to share my resume."
    },
    {
        "index": 42,
        "name": "Abhishek Agarwala",
        "company": "Tekion",
        "url": "https://www.linkedin.com/in/abhishekagarwala",
        "note": "Hey Abhishek, I am a Full Stack and AI engineer (LangGraph, pgvector RAG, MERN TypeScript). Exploring engineering roles at Tekion. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
    },
    {
        "index": 43,
        "name": "Sudheer Thunga",
        "company": "Tekion",
        "url": "https://www.linkedin.com/in/sudheerthunga",
        "note": "Hey Sudheer, I am a Full Stack engineer (MERN, TypeScript, Python). Built LangGraph stateful agents and a pgvector RAG pipeline at OpenBiz. Exploring roles at Tekion. Would you be open to referring me if there are openings? Happy to share my resume."
    },
    {
        "index": 44,
        "name": "Mudit Singhal",
        "company": "Tekion",
        "url": "https://www.linkedin.com/in/muditsinghal",
        "note": "Hey Mudit, I am a Full Stack and AI engineer. Shipped LangGraph agents and a pgvector RAG pipeline with sub 800ms retrieval at OpenBiz. Exploring engineering roles at Tekion. Would you be open to referring me? Happy to share my resume. Thank you."
    },
    {
        "index": 45,
        "name": "Shobhan C",
        "company": "Tekion",
        "url": "https://www.linkedin.com/in/shobhanc",
        "note": "Hey Shobhan, I am a Full Stack and AI engineer (LangGraph, pgvector RAG, MERN, TypeScript). Built production AI systems at OpenBiz. Exploring roles at Tekion. Would you be open to referring me if there are relevant openings? Happy to share my resume."
    },
    {
        "index": 46,
        "name": "Paul Davies C",
        "company": "Locus",
        "url": "https://www.linkedin.com/in/pauldaviesc",
        "note": "Hey Paul, I am a Full Stack and AI engineer (LangGraph agents, webhook pipelines, MERN TypeScript). Exploring engineering roles at Locus in dispatch or AI optimization. Would you be open to referring me if there are openings? Happy to share my resume."
    },
    {
        "index": 47,
        "name": "Susan Leonard",
        "company": "Kissflow",
        "url": "https://www.linkedin.com/in/susanleonard",
        "note": "Hey Susan, I am a Full Stack and AI engineer. Shipped LangGraph workflow agents and a Claude plus MCP web agent at OpenBiz. Exploring roles at Kissflow. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
    },
    {
        "index": 48,
        "name": "Geetha Manjunath",
        "company": "Niramai",
        "url": "https://www.linkedin.com/in/geethamanjunath",
        "note": "Hey Geetha, I am a Full Stack and AI engineer. Built Gemini Vision document extraction pipelines and LangGraph AI agents at OpenBiz. Would love to explore roles at Niramai in applied AI. Would you be open to referring me? Happy to share my resume. Thank you."
    },
    {
        "index": 49,
        "name": "Shubham Mishra",
        "company": "Pixis",
        "url": "https://www.linkedin.com/in/shubhammishra",
        "note": "Hey Shubham, I am a Full Stack and AI engineer with LangGraph agents and pgvector RAG in prod. Exploring AI engineering roles at Pixis. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
    },
    {
        "index": 50,
        "name": "Vrushali Prasade",
        "company": "Pixis",
        "url": "https://www.linkedin.com/in/vrushaliprasade",
        "note": "Hey Vrushali, I am a Full Stack and AI engineer. Shipped LangGraph agents and provider fallback LLM systems at OpenBiz. Exploring AI roles at Pixis. Would you be willing to refer me if there are openings? Happy to share my resume. Thanks."
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
        else:
            TRACKER_FILE.write_text("# Job Application Tracker\n\n" + log_line, encoding="utf-8")
        print(f"Logged to tracker: {person} ({company})")
    except Exception as e:
        print(f"Warning: Could not log to tracker file: {e}")

def get_first_name(full_name: str) -> str:
    return full_name.split()[0]

def format_note_for_vit(name: str, standard_note: str) -> str:
    first_name = get_first_name(name)
    greeting_pattern = re.compile(rf"^Hey\s+{re.escape(first_name)}(,\s*|\s+)", re.IGNORECASE)
    
    if greeting_pattern.match(standard_note):
        new_greeting = f"Hey {first_name}, fellow VIT alum here. "
        rest = greeting_pattern.sub("", standard_note)
        note = new_greeting + rest
    else:
        note = f"Hey {first_name}, fellow VIT alum here. " + standard_note
        
    if len(note) <= 300:
        return note
        
    sentences = re.split(r'(?<=[.!?])\s+', note)
    if len(sentences) >= 3:
        greeting_sent = sentences[0]
        if len(sentences) >= 4 and len(sentences[-2]) + len(sentences[-1]) < 120:
            ask_sent = sentences[-2] + " " + sentences[-1]
            middle_sentences = sentences[1:-2]
        else:
            ask_sent = sentences[-1]
            middle_sentences = sentences[1:-1]
            
        middle_text = " ".join(middle_sentences)
        allowed_middle_len = 300 - len(greeting_sent) - len(ask_sent) - 2
        
        if allowed_middle_len > 10:
            truncated_middle = middle_text[:allowed_middle_len - 3] + "..."
            note = f"{greeting_sent} {truncated_middle} {ask_sent}"
        else:
            note = f"{greeting_sent} {ask_sent}"
            
    if len(note) > 300:
        note = note[:297] + "..."
        
    return note

def clean_note_text(note: str) -> str:
    # Remove all hyphens or dashes and replace with space
    note = note.replace("-", " ").replace("—", " ").replace("--", " ")
    # Remove any salary/CTC/LPA mentions
    note = re.sub(r'\b(salary|ctc|lpa|15\s*l|15\s*lpa|15\s*lakhs?)\b', '', note, flags=re.IGNORECASE)
    # Remove double spaces
    note = re.sub(r'\s+', ' ', note).strip()
    return note

def check_connection_status(page) -> str:
    page.evaluate("""() => {
        const overlay = document.querySelector('.msg-overlay-container');
        if (overlay) overlay.style.display = 'none';
    }""")
    
    page_text = page.locator("body").inner_text()
    
    if "this page doesn’t exist" in page_text.lower() or "page not found" in page_text.lower() or "page not exist" in page_text.lower():
        return "404"
        
    top_card = page.locator("main > section, .pv-top-card").first
    top_card_text = top_card.inner_text() if top_card.count() > 0 else page_text
    
    if "• 1st" in top_card_text or "1st degree" in top_card_text:
        return "1st"
        
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
            return "Pending"
            
    if "pending" in top_card_text.lower() or "withdraw request" in top_card_text.lower():
        return "Pending"
        
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
    if "captcha" in body_text or "security verification" in body_text or "suspicious activity" in body_text:
        print("STOPPING: CAPTCHA / Security Verification detected.")
        sys.exit(EXIT_CAPTCHA)
        
    if "checkpoint" in page.url or "challenge" in page.url:
        print("STOPPING: Security challenge page detected.")
        sys.exit(EXIT_CAPTCHA)
        
    if "sign in" in body_text and "linkedin" in body_text and page.locator("input[type='password']").count() > 0:
        print("STOPPING: LinkedIn logged out or sign-in required.")
        sys.exit(EXIT_LOGIN_REQUIRED)

def send_invitation(page, slug: str, note: str) -> bool:
    direct_url = f"https://www.linkedin.com/preload/custom-invite/?vanityName={slug}"
    print(f"Opening direct customize invite URL: {direct_url}")
    page.goto(direct_url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3000)
    
    check_security_challenges(page)
    
    dialog = page.locator('.artdeco-modal').first
    if dialog.count() == 0 or not dialog.is_visible():
        print(f"Invite modal didn't open for slug: {slug}")
        return False
        
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
        return False
        
    textarea.wait_for(timeout=5000)
    print(f"Typing note ({len(note)} chars): {note}")
    textarea.fill(note)
    page.wait_for_timeout(1000)
    
    send_btn = dialog.locator('button:has-text("Send"), button:has-text("Send invitation")')
    if send_btn.count() == 0:
        print("Send button not found in the custom invite dialog.")
        return False
        
    print("Clicking 'Send'...")
    send_btn.click()
    page.wait_for_timeout(3000)
    
    body_text_after = page.locator("body").inner_text().lower()
    for kw in limit_keywords:
        if kw in body_text_after:
            print(f"STOPPING: Reached LinkedIn invitation limit after click. Found '{kw}'")
            sys.exit(EXIT_LIMIT_REACHED)
            
    return True

def run_outreach():
    progress = load_progress()
    print(f"Loaded progress: {len(progress)}/{len(PROFILES)} profiles processed.")
    
    try:
        with sync_playwright() as p:
            print("Connecting to Chrome on port 9222...")
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            page = browser.contexts[0].pages[0]
            
            sends_in_session = 0
            
            for profile in PROFILES:
                idx = profile["index"]
                name = profile["name"]
                company = profile["company"]
                url = profile["url"]
                std_note = profile["note"]
                
                slug = url.rstrip("/").split("/")[-1]
                
                if str(idx) in progress:
                    saved = progress[str(idx)]
                    if saved["status"] in ["SENT", "SKIPPED"]:
                        continue
                
                print(f"\n[{idx}/50] Processing {name} ({company}) - {url}")
                
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(3000)
                
                check_security_challenges(page)
                
                conn_status = check_connection_status(page)
                print(f"Connection Status: {conn_status}")
                
                if conn_status == "404":
                    print("Profile not found (404). Skipping.")
                    progress[str(idx)] = {
                        "name": name,
                        "company": company,
                        "url": url,
                        "status": "SKIPPED",
                        "reason": "Profile not found (404)",
                        "vit_alumni": "Unknown",
                        "note_type": "None",
                        "timestamp": datetime.now().isoformat()
                    }
                    save_progress(progress)
                    continue
                    
                if conn_status in ["1st", "Pending"]:
                    print(f"Already connected or request pending ({conn_status}). Skipping.")
                    progress[str(idx)] = {
                        "name": name,
                        "company": company,
                        "url": url,
                        "status": "SKIPPED",
                        "reason": f"Connection is {conn_status}",
                        "vit_alumni": "Unknown",
                        "note_type": "None",
                        "timestamp": datetime.now().isoformat()
                    }
                    save_progress(progress)
                    continue
                    
                is_vit = check_vit_education(page)
                print(f"Is VIT Alum: {is_vit}")
                
                if is_vit:
                    note = format_note_for_vit(name, std_note)
                    note_type = "VIT alumni note"
                else:
                    note = std_note
                    note_type = "standard note"
                
                # Apply the clean function to ensure no hyphens or salary mentions exist
                note = clean_note_text(note)
                success = send_invitation(page, slug, note)
                
                if success:
                    print(f"Successfully sent invitation to {name}!")
                    progress[str(idx)] = {
                        "name": name,
                        "company": company,
                        "url": url,
                        "status": "SENT",
                        "vit_alumni": "Yes" if is_vit else "No",
                        "note_type": note_type,
                        "timestamp": datetime.now().isoformat()
                    }
                    save_progress(progress)
                    
                    log_to_tracker(company, name, "Invite Sent", f"SENT ({note_type})")
                    
                    sends_in_session += 1
                    
                    if sends_in_session % 10 == 0:
                        print("Waiting 90 seconds (rate limiting pause after 10 sends)...")
                        time.sleep(90)
                    else:
                        print("Waiting 10 seconds before next profile...")
                        time.sleep(10)
                else:
                    print(f"Failed to send invite to {name}.")
                    progress[str(idx)] = {
                        "name": name,
                        "company": company,
                        "url": url,
                        "status": "FAILED",
                        "reason": "Could not open or submit customize invite modal",
                        "vit_alumni": "Yes" if is_vit else "No",
                        "note_type": note_type,
                        "timestamp": datetime.now().isoformat()
                    }
                    save_progress(progress)
                    time.sleep(5)
            
            browser.close()
            print("\n=== LinkedIn Outreach complete! ===")
            
    except Exception as e:
        print(f"Script error: {e}")
        import traceback
        traceback.print_exc()

def print_summary():
    progress = load_progress()
    
    if not progress:
        print("No progress data found to summarize.")
        return
        
    print("\n\n## SUMMARY REPORT")
    print("| # | Name | Company | VIT Alumni | Status | Note Type |")
    print("|---|------|---------|------------|--------|-----------|")
    
    vit_count = 0
    sent_count = 0
    skipped_count = 0
    failed_count = 0
    
    for idx in sorted([int(k) for k in progress.keys()]):
        entry = progress[str(idx)]
        vit = entry.get("vit_alumni", "Unknown")
        status = entry.get("status", "Unknown")
        note_type = entry.get("note_type", "None")
        
        if status == "SENT":
            note_label = "VIT version" if "vit" in note_type.lower() else "Standard"
        else:
            note_label = "None"
            
        print(f"| {idx} | {entry['name']} | {entry['company']} | {vit} | {status} | {note_label} |")
        
        if vit == "Yes":
            vit_count += 1
        if status == "SENT":
            sent_count += 1
        elif status == "SKIPPED":
            skipped_count += 1
        elif status == "FAILED":
            failed_count += 1
            
    print(f"\n**Totals:** Sent: {sent_count} | Skipped: {skipped_count} | Failed: {failed_count} | VIT Alumni Detected: {vit_count}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--summary":
        print_summary()
    else:
        run_outreach()
        print_summary()
