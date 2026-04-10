# 🛠️ Setup Guide

Follow these steps to set up your environment for autonomous job searching.

## 1. Install Dependencies
You need a way to compile LaTeX locally. **Tectonic** is the recommended engine because it is fast, self-contained, and works directly from the command line.

**macOS (Homebrew):**
```bash
brew install tectonic
```

**Ubuntu/Linux:**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://drop-sh.fullyjustified.net | sh
```

## 2. Browser Authentication
The AI agent uses your **active browser session**. 
- Open your browser (Chrome/Edge/etc.).
- Log into **LinkedIn**, **Cutshort**, and **Arc**.
- Make sure "Remember Me" is checked.
- Keep the browser window open in the background.

## 3. Configure the Agent (First Run)
Open your Gemini CLI (or any agent) and paste the **Master Bootloader Prompt**:
`system_handover_config/MASTER_BOOTLOADER_PROMPT.md`

This will:
1. Load the vault architecture.
2. Adopt the **@job-scout** persona.
3. Verify your `tectonic` installation.

## 4. Test the PDF Generation
Run a test compilation to ensure the resume pipeline is ready:
```bash
python3 scripts/generate_category_resumes.py
```
Check `resumes_and_docs/categories/pdf/` to see the results.


