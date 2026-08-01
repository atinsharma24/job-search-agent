#!/usr/bin/env python3

import json
import os
import sys
from pathlib import Path

# Try importing standard Gemini or Google GenAI
try:
    from google import genai
    from google.genai import types
except ImportError:
    try:
        import google.generativeai as genai
    except ImportError:
        print("Please install google-genai or google-generativeai to use this script.", file=sys.stderr)
        sys.exit(1)

VAULT_ROOT = Path(__file__).resolve().parents[2]
FACT_SHEET_PATH = VAULT_ROOT / "core_vault" / "JobApplyFiles" / "01_atomic_fact_sheet.json"
LOGISTICS_PATH = VAULT_ROOT / "core_vault" / "JobApplyFiles" / "06_logistics_mapping.json"
TECH_DEEP_DIVE = VAULT_ROOT / "core_vault" / "JobApplyFiles" / "03_technical_deep_dive.md"

def load_file(path: Path) -> str:
    if not path.exists():
        return ""
    with open(path, "r") as f:
        return f.read()

def get_answer_from_llm(question_label: str) -> str:
    fact_sheet = load_file(FACT_SHEET_PATH)
    logistics = load_file(LOGISTICS_PATH)
    tech_deep_dive = load_file(TECH_DEEP_DIVE)
        
    prompt = f"""
    You are an automated job application assistant filling out a form on behalf of a candidate.
    You have access to the candidate's core facts and pre-written answers.
    
    Candidate Facts & Logistics:
    {fact_sheet}
    {logistics}
    
    Candidate Technical Details:
    {tech_deep_dive}
    
    The form requires an answer to the following field/question: "{question_label}"
    
    Provide ONLY the direct, concise text that should be typed into this field. Do not include any conversational filler, explanations, or quotes. If it's a Yes/No question, answer Yes or No.
    """
    
    env_path = VAULT_ROOT / "dev.env"
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    if '=' in line:
                        k, v = line.strip().split('=', 1)
                        os.environ[k.strip()] = v.strip().strip('"\'')

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        return ""
        
    try:
        if 'google.genai' in sys.modules:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.0)
            )
            return response.text.strip()
        else:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt, generation_config={"temperature": 0.0})
            return response.text.strip()
            
    except Exception as e:
        print(f"LLM Error: {e}", file=sys.stderr)
        return ""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ats_fallback_agent.py <question_label>")
        sys.exit(1)
    
    answer = get_answer_from_llm(sys.argv[1])
    print(answer)
