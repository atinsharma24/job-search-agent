import os
import json
import csv
import glob
import urllib.parse
import re

workspace = "/Users/atinsharma/job_search_vault"

# Progress files
progress_files = [
    "active_application_context/linkedin_outreach_progress.json",
    "active_application_context/linkedin_outreach_progress_batch4.json",
    "active_application_context/linkedin_outreach_progress_batch5.json",
    "active_application_context/linkedin_connected_outreach_progress.json"
]

# Large companies to skip celebrity CEOs/founders
skip_companies = ["zomato", "swiggy", "paytm", "delhivery", "flipkart", "myntra"]

# Connection templates
templates = {
    "persona_1_founders": "Building compliance/conversational AI at [Company]? I shipped a WhatsApp native LLM and pgvector RAG at a fintech. Stack: MERN, LangGraph, Docker. Open to technical roles. Would you be open to a referral? Happy to share my resume. Thanks!",
    "persona_2_vp_eng": "Shipping LLM features into MERN backends without debt is a specific skill. I have done it (LangGraph, pgvector RAG, Docker). Building at [Company] looks like a great next problem. Open to backend/AI roles. Would you be open to a referral? Happy to share my resume. Thanks!",
    "persona_3_eng_managers": "Managing a team shipping AI adjacent backend features? I own the full loop: MERN, LangGraph, Docker, pgvector RAG pipelines. Founding engineer background. Open to backend/AI roles. Would you be open to a referral? Happy to share my resume. Thanks!",
    "persona_4_senior_engineers": "Fellow engineer building LLM integrated backends. Curious how [Company] handles context management at scale, LangGraph or something custom? Open to technical roles and would value connecting or a referral. Happy to share my resume. Thanks!",
    "persona_5_recruiters": "Full stack + AI engineer, open to roles at [Company]. Stack: MERN, LangGraph, pgvector RAG, Docker, TypeScript. Targeting backend or AI roles. Would you be open to referring me? Happy to share my resume. Thanks!"
}

def clean_url(url):
    if not url or not isinstance(url, str):
        return ""
    url = url.strip().lower()
    parsed = urllib.parse.urlparse(url)
    path = parsed.path
    if path.endswith('/'):
        path = path[:-1]
    if '/in/' in path:
        username = path.split('/in/')[-1]
        return username
    return path

def normalize_name(name):
    return re.sub(r'[^a-z0-9]', '', name.lower())

def normalize_company(company):
    return re.sub(r'[^a-z0-9]', '', company.lower())

# Collect already processed candidates
processed_urls = set()
processed_names = set() # Set of (normalized_name, normalized_company)

# 1. Load from progress files
for pf in progress_files:
    path = os.path.join(workspace, pf)
    if os.path.exists(path):
        with open(path, 'r') as f:
            try:
                data = json.load(f)
                items = data.values() if isinstance(data, dict) else data
                for item in items:
                    if isinstance(item, dict):
                        u = clean_url(item.get('url', ''))
                        if u:
                            processed_urls.add(u)
                        name = item.get('name')
                        company = item.get('company')
                        if name and company:
                            processed_names.add((normalize_name(name), normalize_company(company)))
            except Exception as e:
                print(f"Error loading {pf}: {e}")

# 2. Load from outreach.log
log_path = os.path.join(workspace, "linkedin_outreach/logs/outreach.log")
if os.path.exists(log_path):
    with open(log_path, 'r') as f:
        for line in f:
            match = re.search(r'https://www.linkedin.com/in/[^\s\|/]+/?', line)
            if match:
                u = clean_url(match.group(0))
                if u:
                    processed_urls.add(u)
            parts = line.strip().split(' | ')
            if len(parts) >= 3:
                name = parts[1]
                company = parts[2]
                processed_names.add((normalize_name(name), normalize_company(company)))

# 3. Load from job_applications_tracker.md
tracker_path = os.path.join(workspace, "active_application_context/job_applications_tracker.md")
if os.path.exists(tracker_path):
    with open(tracker_path, 'r') as f:
        for line in f:
            comp_match = re.search(r'\*\*Company:\*\*\s*(.*?)\s*\|', line)
            role_match = re.search(r'\*\*Role:\*\*\s*(.*?)\s*\|', line)
            if comp_match and role_match:
                company = comp_match.group(1).strip()
                role = role_match.group(1).strip()
                if 'Referral Outreach' in role:
                    name_match = re.search(r'\((.*?)\)', role)
                    if name_match:
                        name = name_match.group(1).strip()
                        processed_names.add((normalize_name(name), normalize_company(company)))

print(f"Loaded {len(processed_urls)} processed URLs and {len(processed_names)} processed names.")

# Load candidates from JSON queue
all_candidates = {}

queue_files = [
    "linkedin_outreach/queue/pending.json",
    "linkedin_outreach/queue/approved.json"
]
for qf in queue_files:
    path = os.path.join(workspace, qf)
    if os.path.exists(path):
        with open(path, 'r') as f:
            try:
                data = json.load(f)
                for item in data:
                    name = item.get('name', '').strip()
                    url = item.get('url', '').strip()
                    company = item.get('company', '').strip()
                    persona = item.get('persona', '').strip()
                    message = item.get('message', '').strip()
                    notes = item.get('notes', '').strip()
                    
                    if not name or not url:
                        continue
                    
                    username = clean_url(url)
                    if not username:
                        continue
                        
                    # Skip if already processed
                    norm_name = normalize_name(name)
                    norm_company = normalize_company(company)
                    if username in processed_urls or (norm_name, norm_company) in processed_names:
                        continue
                    
                    if username not in all_candidates:
                        all_candidates[username] = {
                            'name': name, 'url': url, 'company': company,
                            'persona': persona, 'message': message, 'notes': notes
                        }
                    else:
                        cand = all_candidates[username]
                        if message and not cand['message']:
                            cand['message'] = message
                        if notes and not cand['notes']:
                            cand['notes'] = notes
                        if persona and not cand['persona']:
                            cand['persona'] = persona
            except Exception as e:
                print(f"Error loading queue {qf}: {e}")

# Load candidates from CSV files
csv_files = glob.glob(os.path.join(workspace, "linkedin_outreach/contacts/*.csv"))
for cf in csv_files:
    with open(cf, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cleaned_row = {k.strip().lower().replace('"', ''): v for k, v in row.items() if k is not None}
            name = cleaned_row.get('name', '').strip()
            url = cleaned_row.get('url', '').strip()
            company = cleaned_row.get('company', '').strip()
            persona = cleaned_row.get('persona', '').strip()
            message = cleaned_row.get('message', '').strip()
            notes = cleaned_row.get('notes', '').strip()
            
            if not name or not url:
                continue
                
            username = clean_url(url)
            if not username:
                continue
                
            # Skip if already processed
            norm_name = normalize_name(name)
            norm_company = normalize_company(company)
            if username in processed_urls or (norm_name, norm_company) in processed_names:
                continue
                
            if username not in all_candidates:
                all_candidates[username] = {
                    'name': name, 'url': url, 'company': company,
                    'persona': persona, 'message': message, 'notes': notes
                }
            else:
                cand = all_candidates[username]
                if message and not cand['message']:
                    cand['message'] = message
                if notes and not cand['notes']:
                    cand['notes'] = notes
                if persona and not cand['persona']:
                    cand['persona'] = persona

# Inject newly sourced high-quality profiles
newly_sourced = [
    {
        "name": "Pradeep Kumar Thummala",
        "company": "Qure.ai",
        "url": "https://www.linkedin.com/in/pradeep-kumar-thummala-51515320/",
        "persona": "persona_2_vp_eng",
        "message": "",
        "notes": "CTO @ Qure.ai"
    },
    {
        "name": "Vijay Senapathi",
        "company": "Qure.ai",
        "url": "https://www.linkedin.com/in/vijaysenapathi/",
        "persona": "persona_2_vp_eng",
        "message": "",
        "notes": "SVP of Engineering @ Qure.ai"
    },
    {
        "name": "Roli Gupta",
        "company": "Babblebots AI",
        "url": "https://www.linkedin.com/in/rolig/",
        "persona": "persona_1_founders",
        "message": "",
        "notes": "Founder & CEO @ Babblebots.ai"
    },
    {
        "name": "Nikhil Goel",
        "company": "Salarybox",
        "url": "https://www.linkedin.com/in/nikhil-goel-1a613636/",
        "persona": "persona_1_founders",
        "message": "",
        "notes": "Founder & CEO @ Salarybox"
    }
]

for ns in newly_sourced:
    username = clean_url(ns['url'])
    norm_name = normalize_name(ns['name'])
    norm_company = normalize_company(ns['company'])
    if username not in processed_urls and (norm_name, norm_company) not in processed_names:
        if username not in all_candidates:
            all_candidates[username] = ns

# Filter and score priority
filtered_candidates = []

def is_founder_ceo(persona_str, notes_str):
    p = persona_str.lower()
    n = notes_str.lower()
    founder_keywords = ['founder', 'ceo', 'co-founder', 'cofounder', 'chief executive officer', 'c-suite', 'persona_1_founders']
    for kw in founder_keywords:
        if kw in p or kw in n:
            return True
    return False

def is_engineering_leader(persona_str, notes_str):
    p = persona_str.lower()
    n = notes_str.lower()
    eng_keywords = ['cto', 'vp', 'vice president', 'director of engineering', 'engineering manager', 'em', 'tech lead', 'technical lead', 'engineering lead', 'persona_2_vp_eng', 'persona_3_eng_managers']
    for kw in eng_keywords:
        if kw in p or kw in n:
            return True
    return False

for username, cand in all_candidates.items():
    company_lower = cand['company'].lower()
    persona = cand['persona']
    notes = cand['notes']
    
    is_very_large = any(sc in company_lower for sc in skip_companies)
    is_founder = is_founder_ceo(persona, notes)
    is_eng_leader = is_engineering_leader(persona, notes)
    
    # Skip celebrity CEOs/founders of very large companies
    if is_very_large and is_founder:
        continue
        
    # Priority 1: engineering leaders or founders/CEOs of early/mid stage startups
    if is_eng_leader or (is_founder and not is_very_large):
        priority = 1
    else:
        priority = 2
        
    cand['priority'] = priority
    cand['is_eng_leader'] = is_eng_leader
    cand['is_founder'] = is_founder
    filtered_candidates.append(cand)

# Clean / generate messages
def clean_message(msg):
    if not msg:
        return ""
    # Replace common hyphenated words
    msg = re.sub(r'\b([fF])ull-([sS])tack\b', r'\1ull \2tack', msg)
    msg = re.sub(r'\b([wW])hats([aA])pp-([nN])ative\b', r'\1hats\2pp \3ative', msg)
    msg = re.sub(r'\b([cC])o-([fF])ounder\b', r'\1o \2ounder', msg)
    msg = re.sub(r'\b([sS])ub-800ms\b', r'\1ub 800ms', msg)
    msg = re.sub(r'\b([dD])ay-([oO])ne\b', r'\1ay \2ne', msg)
    
    # Remove/replace all hyphens and dashes
    msg = msg.replace("--", " ")
    msg = msg.replace(" — ", ", ")
    msg = msg.replace(" – ", ", ")
    msg = msg.replace("—", ", ")
    msg = msg.replace("–", ", ")
    msg = msg.replace("-", " ")
    
    # Remove salary/CTC/LPA mentions
    msg = re.sub(r'\b\d+\s*[lL]\s*\+?\s*\(?negotiable\)?', '', msg)
    msg = re.sub(r'\b\d+\s*[lL]\s*\+?', '', msg)
    msg = re.sub(r'\b\d+\s*[lL][pP][aA]\s*\+?', '', msg)
    msg = re.sub(r'\b\d+\s*lakhs?\s*\+?', '', msg, flags=re.IGNORECASE)
    msg = re.sub(r'\bexpected\s+ctc\b', '', msg, flags=re.IGNORECASE)
    msg = re.sub(r'\bctc\b', '', msg, flags=re.IGNORECASE)
    msg = re.sub(r'\blpa\b', '', msg, flags=re.IGNORECASE)
    msg = re.sub(r'\bsalary\b', '', msg, flags=re.IGNORECASE)
    
    msg = re.sub(r'\s+', ' ', msg)
    msg = msg.replace(" .", ".").replace(" ,", ",")
    
    if len(msg) > 300:
        msg = msg[:300].strip()
        last_space = msg.rfind(' ')
        if last_space > 280:
            msg = msg[:last_space].strip()
        if not msg.endswith(('.', '!', '?')):
            msg += '.'
        msg = msg[:300].strip()
    return msg

def get_message_for_candidate(cand):
    msg = ""
    if cand.get('message'):
        msg = clean_message(cand['message'])
        
    if not msg:
        p = cand['persona'].lower()
        company = cand['company']
        
        tpl = templates["persona_1_founders"]
        if "persona_2_vp_eng" in p or "vp" in p or "executive" in p or "cto" in p:
            tpl = templates["persona_2_vp_eng"]
        elif "persona_3_eng_managers" in p or "manager" in p:
            tpl = templates["persona_3_eng_managers"]
        elif "persona_4_senior_engineers" in p or "engineer" in p:
            tpl = templates["persona_4_senior_engineers"]
        elif "persona_5_recruiters" in p or "recruiter" in p:
            tpl = templates["persona_5_recruiters"]
            
        msg = tpl.replace("[Company]", company)
        msg = clean_message(msg)
        
    # Append referral ask if "refer" is not in the message
    if "refer" not in msg.lower():
        if "recruiter" in cand['persona'].lower() or "persona_5_recruiters" in cand['persona'].lower():
            append_str = " Would you be open to referring me or sharing details on open tech roles? Happy to share resume. Thanks!"
        else:
            append_str = " Open to technical roles. Would you be open to a referral if there is an opening? Happy to share resume. Thanks!"
            
        if len(msg) + len(append_str) > 300:
            allowed_len = 300 - len(append_str)
            msg = msg[:allowed_len].strip()
            last_period = msg.rfind('.')
            if last_period > allowed_len - 30:
                msg = msg[:last_period + 1]
            else:
                last_space = msg.rfind(' ')
                if last_space > allowed_len - 15:
                    msg = msg[:last_space]
                # Strip trailing conjunctions and prepositions
                msg = re.sub(r'\s+(and|or|but|with|at|in|on|for|to)\s*$', '', msg, flags=re.IGNORECASE).strip()
                if not msg.endswith(('.', '!', '?')):
                    msg += '.'
        msg = msg + append_str
        msg = clean_message(msg)
        
    return msg

for cand in filtered_candidates:
    cand['final_message'] = get_message_for_candidate(cand)

# Sort and select top 100
filtered_candidates.sort(key=lambda x: (x['priority'], x['name']))

# Slice top 100
selected_candidates = filtered_candidates[:100]

# Write JSON
json_output = []
for idx, cand in enumerate(selected_candidates, 1):
    json_output.append({
        "index": idx,
        "name": cand['name'],
        "company": cand['company'],
        "url": cand['url'],
        "note": cand['final_message']
    })

json_path = os.path.join(workspace, "active_application_context/proposed_batch6.json")
with open(json_path, 'w') as f:
    json.dump(json_output, f, indent=2)

# Write TXT
txt_path = os.path.join(workspace, "active_application_context/proposed_batch6.txt")
with open(txt_path, 'w') as f:
    for idx, cand in enumerate(selected_candidates, 1):
        label = "CEO/Exec/Eng"
        if cand['is_eng_leader']:
            label = "Eng Leader"
        elif cand['is_founder']:
            label = "Founder/CEO"
        elif "recruiter" in cand['persona'].lower() or "persona_5_recruiters" in cand['persona'].lower():
            label = "Recruiter"
        elif "engineer" in cand['persona'].lower() or "persona_4_senior_engineers" in cand['persona'].lower():
            label = "Senior Engineer"
            
        f.write(f"[{idx}] {cand['name']} · {label} @ {cand['company']}\n")
        f.write(f"PROFILE: {cand['url']}\n")
        f.write(f"NOTE: {cand['final_message']}\n\n")

print(f"SUCCESS: Generated {len(json_output)} profiles. Saved to {json_path} and {txt_path}")
