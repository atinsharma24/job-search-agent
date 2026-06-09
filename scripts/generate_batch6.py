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
    "persona_1_founders": "Building compliance or conversational AI at [Company]? I shipped a WhatsApp native LLM assistant and RAG pipeline at a fintech startup. LangGraph, pgvector, MERN. Would value connecting.",
    "persona_2_vp_eng": "Shipping LLM features into MERN backends without accumulating debt is a specific skill. I have done it, LangGraph orchestration, pgvector RAG, Docker. Building at [Company] looks like the right next problem.",
    "persona_3_eng_managers": "Managing a team shipping AI adjacent backend features? I own the full loop, MERN, LangGraph, Docker, RAG pipelines. Founding engineer background means I do not wait for specs. Would like to connect.",
    "persona_4_senior_engineers": "Fellow engineer building LLM integrated backends. Curious how [Company] handles context window management at scale, LangGraph or something custom? Would value a quick exchange.",
    "persona_5_recruiters": "Full stack and AI engineer, open to roles at [Company]. Stack: MERN, LangGraph, RAG/pgvector, Docker, TypeScript. Targeting backend or AI engineering. Would like to connect."
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

# 1. Load processed urls
processed_usernames = set()
for pf in progress_files:
    path = os.path.join(workspace, pf)
    if os.path.exists(path):
        with open(path, 'r') as f:
            try:
                data = json.load(f)
                items = data.values() if isinstance(data, dict) else data
                for item in items:
                    if isinstance(item, dict) and 'url' in item:
                        u = clean_url(item['url'])
                        if u:
                            processed_usernames.add(u)
            except Exception as e:
                print(f"Error loading {pf}: {e}")

# 2. Load candidates from JSON queue
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
                    if not username or username in processed_usernames:
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

# 3. Load candidates from CSV files
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
            if not username or username in processed_usernames:
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

# 4. Filter and score priority
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

# 5. Clean / generate messages
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
    if cand['message']:
        cleaned = clean_message(cand['message'])
        if cleaned:
            return cleaned
            
    p = cand['persona'].lower()
    company = cand['company']
    
    tpl = templates["persona_1_founders"]
    if "persona_2_vp_eng" in p or "vp" in p or "executive" in p:
        tpl = templates["persona_2_vp_eng"]
    elif "persona_3_eng_managers" in p or "manager" in p:
        tpl = templates["persona_3_eng_managers"]
    elif "persona_4_senior_engineers" in p or "engineer" in p:
        tpl = templates["persona_4_senior_engineers"]
    elif "persona_5_recruiters" in p or "recruiter" in p:
        tpl = templates["persona_5_recruiters"]
        
    msg = tpl.replace("[Company]", company)
    return clean_message(msg)

for cand in filtered_candidates:
    cand['final_message'] = get_message_for_candidate(cand)

# 6. Sort and select top 100
filtered_candidates.sort(key=lambda x: (x['priority'], x['name']))

# Slice top 100
selected_candidates = filtered_candidates[:100]

# 7. Write JSON
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

# 8. Write TXT
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

print(f"SUCCESS: Generated 100 profiles. Saved to {json_path} and {txt_path}")
