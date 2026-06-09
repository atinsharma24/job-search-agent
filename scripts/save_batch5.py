import json
from pathlib import Path

def main():
    profiles = [
        {
            "index": 1,
            "name": "Deepinder Goyal",
            "company": "Zomato",
            "url": "https://www.linkedin.com/in/deepindergoyal",
            "note": "Hey Deepinder, I am a Full Stack and AI engineer. Shipped MERN TypeScript systems and LangGraph agents at OpenBiz. Exploring AI engineering roles at Zomato. Would you be open to referring me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 2,
            "name": "Sriharsha Majety",
            "company": "Swiggy",
            "url": "https://www.linkedin.com/in/sriharsha",
            "note": "Hey Sriharsha, I am a Full Stack and AI engineer. Built LangGraph agents and MERN TypeScript systems at OpenBiz. Exploring AI engineering roles at Swiggy. Would you be open to referring me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 3,
            "name": "Nandan Reddy",
            "company": "Swiggy",
            "url": "https://www.linkedin.com/in/nandanreddy",
            "note": "Hey Nandan, I am a Full Stack and AI engineer (MERN, TypeScript, Python, LangGraph). Exploring engineering roles at Swiggy. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
        },
        {
            "index": 4,
            "name": "Sahil Barua",
            "company": "Delhivery",
            "url": "https://www.linkedin.com/in/sahilbarua",
            "note": "Hey Sahil, I am a Full Stack and AI engineer. Shipped LangGraph agents and MERN TypeScript systems at OpenBiz. Exploring engineering roles at Delhivery. Would you be open to referring me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 5,
            "name": "Suraj Saharan",
            "company": "Delhivery",
            "url": "https://www.linkedin.com/in/surajsaharan",
            "note": "Hey Suraj, I am a Full Stack and AI engineer (MERN, TypeScript, Python, LangGraph). Exploring engineering roles at Delhivery. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
        },
        {
            "index": 6,
            "name": "Reeju Datta",
            "company": "Cashfree Payments",
            "url": "https://www.linkedin.com/in/reejudatta",
            "note": "Hey Reeju, I am a Full Stack engineer. Shipped idempotent payment webhook billing (100% consistency) and cut API latency 40% at OpenBiz. Exploring engineering roles at Cashfree. Would you refer me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 7,
            "name": "Akash Sinha",
            "company": "Cashfree Payments",
            "url": "https://www.linkedin.com/in/akashsinha",
            "note": "Hey Akash, I am a Full Stack engineer. Built idempotent payment webhook billing and LangGraph agents at OpenBiz. Exploring fintech engineering roles at Cashfree. Would you be open to referring me if there are openings? Happy to share my resume."
        },
        {
            "index": 8,
            "name": "Anish Achuthan",
            "company": "Open Financial",
            "url": "https://www.linkedin.com/in/anishachuthan",
            "note": "Hey Anish, I am a Full Stack engineer. Shipped idempotent payment webhook billing and LangGraph AI agents at OpenBiz. Exploring fintech engineering roles at Open. Would you be open to referring me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 9,
            "name": "Mabel Chacko",
            "company": "Open Financial",
            "url": "https://www.linkedin.com/in/mabelchacko",
            "note": "Hey Mabel, I am a Full Stack and AI engineer (MERN, TypeScript, Python, LangGraph). Exploring fintech engineering roles at Open Financial. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
        },
        {
            "index": 10,
            "name": "Sachin Bansal",
            "company": "Navi Technologies",
            "url": "https://www.linkedin.com/in/sachinbansal",
            "note": "Hey Sachin, I am a Full Stack engineer. Built idempotent payment webhook systems and LangGraph agents at OpenBiz. Exploring fintech engineering roles at Navi. Would you be open to referring me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 11,
            "name": "Nithin Kamath",
            "company": "Zerodha",
            "url": "https://www.linkedin.com/in/nithinkamath",
            "note": "Hey Nithin, I am a Full Stack and AI engineer. Shipped MERN TypeScript systems and LangGraph agents at OpenBiz. Exploring engineering roles at Zerodha. Would you be open to referring me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 12,
            "name": "Krish Subramanian",
            "company": "Chargebee",
            "url": "https://www.linkedin.com/in/krishsubramanian",
            "note": "Hey Krish, I am a Full Stack engineer. Shipped idempotent payment webhook billing (100% consistency) and LangGraph agents at OpenBiz. Exploring engineering roles at Chargebee. Would you refer me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 13,
            "name": "Rajaraman Santhanam",
            "company": "Chargebee",
            "url": "https://www.linkedin.com/in/rajaramansanthanam",
            "note": "Hey Rajaraman, I am a Full Stack engineer. Built idempotent payment webhook billing and LangGraph AI agents at OpenBiz. Exploring engineering roles at Chargebee. Would you be open to referring me if there are openings? Happy to share my resume."
        },
        {
            "index": 14,
            "name": "Nilesh Patel",
            "company": "LeadSquared",
            "url": "https://www.linkedin.com/in/nileshpatel",
            "note": "Hey Nilesh, I am a Full Stack and AI engineer. Built LangGraph agents and MERN TypeScript systems at OpenBiz. Exploring engineering roles at LeadSquared. Would you be open to referring me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 15,
            "name": "Aneesh Reddy",
            "company": "Capillary Technologies",
            "url": "https://www.linkedin.com/in/aneeshreddy",
            "note": "Hey Aneesh, I am a Full Stack and AI engineer. Shipped LangGraph agents and a pgvector RAG pipeline at OpenBiz. Exploring AI engineering roles at Capillary. Would you refer me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 16,
            "name": "Naveen Tewari",
            "company": "InMobi",
            "url": "https://www.linkedin.com/in/naveentewari",
            "note": "Hey Naveen, I am a Full Stack and AI engineer. Built LangGraph agents and a provider agnostic LLM layer at OpenBiz. Exploring AI engineering roles at InMobi. Would you be open to referring me if there are openings? Happy to share my resume."
        },
        {
            "index": 17,
            "name": "Ankush Sachdeva",
            "company": "ShareChat",
            "url": "https://www.linkedin.com/in/ankushsachdeva",
            "note": "Hey Ankush, I am a Full Stack and AI engineer. Shipped LangGraph agents and MERN TypeScript systems at OpenBiz. Exploring AI engineering roles at ShareChat. Would you be open to referring me if there are openings? Happy to share my resume."
        },
        {
            "index": 18,
            "name": "Farid Ahsan",
            "company": "ShareChat",
            "url": "https://www.linkedin.com/in/faridahsan",
            "note": "Hey Farid, I am a Full Stack and AI engineer (MERN, TypeScript, Python, LangGraph). Exploring AI engineering roles at ShareChat. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
        },
        {
            "index": 19,
            "name": "Vijay Shekar Sharma",
            "company": "Paytm",
            "url": "https://www.linkedin.com/in/vijayshekarsharma",
            "note": "Hey Vijay, I am a Full Stack and AI engineer. Shipped LangGraph agents and idempotent payment webhook billing at OpenBiz. Exploring engineering roles at Paytm. Would you be open to referring me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 20,
            "name": "Mayank Kumar",
            "company": "UpGrad",
            "url": "https://www.linkedin.com/in/mayankumar",
            "note": "Hey Mayank, I am a Full Stack and AI engineer. Built LangGraph agents and MERN TypeScript systems at OpenBiz. Exploring engineering roles at UpGrad. Would you be open to referring me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 21,
            "name": "Abhimanyu Saxena",
            "company": "Scaler Academy",
            "url": "https://www.linkedin.com/in/abhimanyusaxena",
            "note": "Hey Abhimanyu, I am a Full Stack and AI engineer. Shipped MERN TypeScript systems and LangGraph agents at OpenBiz. Exploring engineering roles at Scaler Academy. Would you refer me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 22,
            "name": "Anshuman Singh",
            "company": "Scaler Academy",
            "url": "https://www.linkedin.com/in/anshumansingh",
            "note": "Hey Anshuman, I am a Full Stack and AI engineer (MERN, TypeScript, Python, LangGraph). Exploring engineering roles at Scaler Academy. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
        },
        {
            "index": 23,
            "name": "Alakh Pandey",
            "company": "PhysicsWallah",
            "url": "https://www.linkedin.com/in/alakhpandey",
            "note": "Hey Alakh, I am a Full Stack and AI engineer. Built LangGraph agents and MERN TypeScript systems at OpenBiz. Exploring engineering roles at PhysicsWallah. Would you be open to referring me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 24,
            "name": "Mihir Gupta",
            "company": "Teachmint",
            "url": "https://www.linkedin.com/in/mihirgupta",
            "note": "Hey Mihir, I am a Full Stack and AI engineer. Shipped LangGraph agents and MERN TypeScript systems at OpenBiz. Exploring engineering roles at Teachmint. Would you be open to referring me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 25,
            "name": "Payoj Jain",
            "company": "Teachmint",
            "url": "https://www.linkedin.com/in/payojjain",
            "note": "Hey Payoj, I am a Full Stack and AI engineer (MERN, TypeScript, Python, LangGraph). Exploring engineering roles at Teachmint. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
        },
        {
            "index": 26,
            "name": "Aloke Bajpai",
            "company": "Ixigo",
            "url": "https://www.linkedin.com/in/alokebajpai",
            "note": "Hey Aloke, I am a Full Stack and AI engineer. Built LangGraph agents and MERN TypeScript systems at OpenBiz. Exploring engineering roles at Ixigo. Would you be open to referring me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 27,
            "name": "Ravish Naresh",
            "company": "Khatabook",
            "url": "https://www.linkedin.com/in/ravishn",
            "note": "Hey Ravish, I am a Full Stack and AI engineer. Built VyaparGPT (WhatsApp AI, LangGraph, 40 SMBs) at OpenBiz for Indian SMBs. Exploring engineering roles at Khatabook. Would you be open to referring me if there are openings? Happy to share my resume."
        },
        {
            "index": 28,
            "name": "Kalyan Krishnamurthy",
            "company": "Flipkart",
            "url": "https://www.linkedin.com/in/kalyankrishnamurthy",
            "note": "Hey Kalyan, I am a Full Stack and AI engineer. Built LangGraph agents and a pgvector RAG pipeline at OpenBiz. Exploring AI engineering roles at Flipkart. Would you be open to referring me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 29,
            "name": "Nandita Sinha",
            "company": "Myntra",
            "url": "https://www.linkedin.com/in/nanditasinha",
            "note": "Hey Nandita, I am a Full Stack and AI engineer. Shipped LangGraph agents and MERN TypeScript systems at OpenBiz. Exploring AI engineering roles at Myntra. Would you be open to referring me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 30,
            "name": "Abhinav Shashank",
            "company": "Innovaccer",
            "url": "https://www.linkedin.com/in/abhinavshashank",
            "note": "Hey Abhinav, I am a Full Stack and AI engineer. Shipped LangGraph agents, pgvector RAG (sub 800ms), and Gemini Vision doc extraction at OpenBiz. Exploring AI roles at Innovaccer. Would you refer me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 31,
            "name": "Kanav Hasija",
            "company": "Innovaccer",
            "url": "https://www.linkedin.com/in/kanavhasija",
            "note": "Hey Kanav, I am a Full Stack and AI engineer (MERN, TypeScript, Python, LangGraph). Exploring AI engineering roles at Innovaccer. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
        },
        {
            "index": 32,
            "name": "Rajesh Yabaji",
            "company": "BlackBuck",
            "url": "https://www.linkedin.com/in/rajeshyabaji",
            "note": "Hey Rajesh, I am a Full Stack and AI engineer. Shipped LangGraph agents and MERN TypeScript systems at OpenBiz. Exploring engineering roles at BlackBuck. Would you be open to referring me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 33,
            "name": "Tarun Dua",
            "company": "E2E Networks",
            "url": "https://www.linkedin.com/in/tarundua",
            "note": "Hey Tarun, I am a Full Stack and AI engineer. Shipped LangGraph agents, pgvector RAG, and MERN TypeScript systems at OpenBiz. Exploring engineering roles at E2E Networks. Would you be open to referring me if there are openings? Happy to share my resume."
        },
        {
            "index": 34,
            "name": "Sumit Agarwal",
            "company": "Vyapar",
            "url": "https://www.linkedin.com/in/sumitagarwal",
            "note": "Hey Sumit, I am a Full Stack and AI engineer. Built VyaparGPT (WhatsApp AI, LangGraph, 40 SMBs) at OpenBiz as a conversational AI layer for businesses. Exploring roles at Vyapar. Would you refer me if there are openings? Happy to share my resume."
        },
        {
            "index": 35,
            "name": "Bharat Goenka",
            "company": "Tally Solutions",
            "url": "https://www.linkedin.com/in/bharatgoenka",
            "note": "Hey Bharat, I am a Full Stack and AI engineer. Shipped VyaparGPT (WhatsApp AI, 40 SMBs) and LangGraph agents at OpenBiz. Exploring AI engineering roles at Tally. Would you refer me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 36,
            "name": "Vikas Malpani",
            "company": "Porter",
            "url": "https://www.linkedin.com/in/vikasmalpani",
            "note": "Hey Vikas, I am a Full Stack and AI engineer. Shipped LangGraph agents and MERN TypeScript systems at OpenBiz. Exploring engineering roles at Porter. Would you be open to referring me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 37,
            "name": "Vimal Kumar",
            "company": "Juspay",
            "url": "https://www.linkedin.com/in/vimalkumar",
            "note": "Hey Vimal, I am a Full Stack engineer. Shipped idempotent payment webhook billing (100% consistency) and LangGraph agents at OpenBiz. Exploring engineering roles at Juspay. Would you be open to referring me if there are openings? Happy to share my resume."
        },
        {
            "index": 38,
            "name": "Ramakant Sharma",
            "company": "Livspace",
            "url": "https://www.linkedin.com/in/ramakantsharma",
            "note": "Hey Ramakant, I am a Full Stack and AI engineer. Built LangGraph agents and MERN TypeScript systems at OpenBiz. Exploring engineering roles at Livspace. Would you be open to referring me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 39,
            "name": "Anuj Srivastava",
            "company": "Livspace",
            "url": "https://www.linkedin.com/in/anujsrivastava",
            "note": "Hey Anuj, I am a Full Stack and AI engineer (MERN, TypeScript, Python, LangGraph). Exploring engineering roles at Livspace. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
        },
        {
            "index": 40,
            "name": "Saahil Goel",
            "company": "Shiprocket",
            "url": "https://www.linkedin.com/in/saahilgoel",
            "note": "Hey Saahil, I am a Full Stack and AI engineer. Shipped LangGraph agents and MERN TypeScript systems at OpenBiz. Exploring engineering roles at Shiprocket. Would you be open to referring me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 41,
            "name": "Vishesh Khurana",
            "company": "Shiprocket",
            "url": "https://www.linkedin.com/in/visheshkhurana",
            "note": "Hey Vishesh, I am a Full Stack and AI engineer (MERN, TypeScript, Python, LangGraph). Exploring engineering roles at Shiprocket. Would you be open to referring me if there are relevant openings? Happy to share my resume. Thank you."
        },
        {
            "index": 42,
            "name": "Rohit Taneja",
            "company": "Decentro",
            "url": "https://www.linkedin.com/in/rohittaneja",
            "note": "Hey Rohit, I am a Full Stack and AI engineer. Built LangGraph agents and idempotent payment webhook systems at OpenBiz. Exploring fintech API roles at Decentro. Would you be open to referring me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 43,
            "name": "Pratik Gadekar",
            "company": "Decentro",
            "url": "https://www.linkedin.com/in/pratikgadekar",
            "note": "Hey Pratik, I am a Full Stack and AI engineer. Shipped idempotent payment webhook billing and LangGraph agents at OpenBiz. Exploring fintech engineering roles at Decentro. Would you be open to referring me if there openings? Happy to share my resume."
        },
        {
            "index": 44,
            "name": "Arpit Dave",
            "company": "Recko",
            "url": "https://www.linkedin.com/in/arpitdave",
            "note": "Hey Arpit, I am a Full Stack engineer. Shipped idempotent payment webhook billing (100% consistency) and LangGraph agents at OpenBiz. Exploring fintech engineering roles at Recko. Would you refer me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 45,
            "name": "Sujay Nair",
            "company": "Recko",
            "url": "https://www.linkedin.com/in/sujaynair",
            "note": "Hey Sujay, I am a Full Stack engineer. Built idempotent payment webhook billing and LangGraph AI agents at OpenBiz. Exploring fintech engineering roles at Recko. Would you be open to referring me if there openings? Happy to share my resume."
        },
        {
            "index": 46,
            "name": "Naman Sarawagi",
            "company": "RudderStack",
            "url": "https://www.linkedin.com/in/namansarawagi",
            "note": "Hey Naman, I am a Full Stack and AI engineer. Shipped MERN TypeScript systems and pgvector RAG pipelines at OpenBiz. Exploring engineering roles at RudderStack. Would you be open to referring me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 47,
            "name": "Mrinal Sinha",
            "company": "Instabase",
            "url": "https://www.linkedin.com/in/mrinalsinha",
            "note": "Hey Mrinal, I am a Full Stack and AI engineer. Built Gemini Vision document extraction pipelines and LangGraph agents at OpenBiz. Exploring AI engineering roles at Instabase. Would you be open to referring me if there openings? Happy to share my resume."
        },
        {
            "index": 48,
            "name": "Prasad Varma",
            "company": "Keka HR",
            "url": "https://www.linkedin.com/in/prasadvarma",
            "note": "Hey Prasad, I am a Full Stack and AI engineer. Shipped LangGraph agents and MERN TypeScript systems at OpenBiz. Exploring engineering roles at Keka HR. Would you be open to referring me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 49,
            "name": "Saurabh Kumar Tiwari",
            "company": "PhonePe",
            "url": "https://www.linkedin.com/in/saurabhkumartiwari",
            "note": "Hey Saurabh, I am a Full Stack engineer. Shipped idempotent payment webhook billing and cut API latency 40% at OpenBiz. Exploring engineering roles at PhonePe. Would you be open to referring me if there are relevant openings? Happy to share my resume."
        },
        {
            "index": 50,
            "name": "Harish Kumar",
            "company": "Cashfree Payments",
            "url": "https://www.linkedin.com/in/harishkumar",
            "note": "Hey Harish, I am a Full Stack engineer. Built idempotent payment webhook billing (100% consistency) and LangGraph agents at OpenBiz. Exploring engineering roles at Cashfree. Would you be open to referring me if there openings? Happy to share my resume."
        }
    ]

    vault_root = Path("/Users/atinsharma/job_search_vault")
    active_dir = vault_root / "active_application_context"
    
    # Write proposed_batch5.json
    json_path = active_dir / "proposed_batch5.json"
    json_path.write_text(json.dumps(profiles, indent=2), encoding="utf-8")
    print(f"Saved {len(profiles)} profiles to {json_path}")
    
    # Write proposed_batch5.txt in text preview format
    txt_path = active_dir / "proposed_batch5.txt"
    txt_content = ""
    for p in profiles:
        txt_content += f"[{p['index']}] {p['name']} · CEO/Exec/Eng @ {p['company']}\n"
        txt_content += f"PROFILE: {p['url']}\n"
        txt_content += f"NOTE: {p['note']}\n\n"
    txt_path.write_text(txt_content.strip(), encoding="utf-8")
    print(f"Saved text preview to {txt_path}")

if __name__ == "__main__":
    main()
