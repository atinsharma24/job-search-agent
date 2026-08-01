#!/usr/bin/env python3
"""
Question-aware screening answers.

Replaces two blind-affirmation defects:

  playwright_naukri_discover_apply.py:719   clicked any option reading "yes"/"agree"
                                            without ever inspecting the question
  playwright_linkedin_easy_apply.py:110     returned "Yes" for any yes/no field

Consequence: "Do you have 5+ years of experience?", "Are you willing to sign a
2-year bond?", "Do you require visa sponsorship?" all received an unconditional Yes.

The governing principle here is that **abstaining is always safe and answering
wrongly never is.** An unrecognised question returns ABSTAIN, which surfaces the
job for human review rather than guessing. That is the correctness-first trade:
fewer submissions, none of them wrong.

Policy lives in this file rather than in the canonical JSONs because it is
behaviour, not candidate data — one file to review, one file to diff.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

import vault_config as vc


class Decision(str, Enum):
    YES = "yes"
    NO = "no"
    VALUE = "value"
    SKIP = "skip"
    ABSTAIN = "abstain"


@dataclass(frozen=True)
class Answer:
    decision: Decision
    value: str = ""
    rule: str = ""  # which rule fired — logged so decisions stay auditable


YES_TOKENS = frozenset({"yes", "y", "i agree", "agree", "confirm", "accept", "ok", "sure"})
NO_TOKENS = frozenset({"no", "n", "decline", "disagree", "not applicable", "na"})

# Anything matching these must be answered NO. Getting one wrong is expensive:
# a bond commits you legally, a sponsorship "yes" is a lie, an inflated years
# figure is caught at interview.
_HARD_NO = (
    ("sponsorship", r"\bsponsor|sponsorship|require.*visa|visa.*require"),
    ("work_permit", r"\bwork permit\b|\bh-?1b\b|\bgreen card\b"),
    ("criminal", r"convicted|felony|criminal record|background.*conviction"),
    ("drug_test", r"drug (test|screen)"),
    ("bond", r"\bbond\b|service agreement|minimum.*commitment.*year"),
    ("pay_to_apply", r"pay.*(fee|deposit|registration charge)|franchise|investment required"),
    ("long_notice", r"notice period.*(30|45|60|90)\s*day|(30|45|60|90)\s*day.*notice"),
    ("relocate_abroad", r"relocat.*(abroad|overseas|outside india|us\b|uk\b)"),
)

_HARD_YES = (
    ("authorized_india", r"legally (authoriz|entitled)|eligible to work in india|indian citizen"),
    ("relocate_india", r"willing to relocate|open to relocat|comfortable relocat"),
    ("work_mode", r"comfortable.*(remote|wfo|work(ing)? from (the )?\w*\s*office|hybrid|onsite|in[- ]person|from office)|willing to work from"),
    ("terms", r"agree.*(terms|conditions|privacy|policy)|read and understood"),
    ("notice_ok", r"can you join|able to join|available to join"),
    # --- objectively verifiable facts about the candidate ---
    ("has_laptop", r"(own|personal).*(laptop|computer|system)|have.*laptop"),
    ("has_internet", r"stable.*(internet|broadband|connection)|reliable internet"),
    ("wfh_setup", r"work from home setup|home office setup|dedicated workspace"),
    ("graduate", r"\b(are you|do you have).*(graduat\w*|bachelor|b\.?tech|degree)\b"),
    ("full_time_avail", r"available (for|to work) full[- ]time|full[- ]time (role|position|basis)"),
    ("english", r"(fluent|proficient|comfortable).*(english|communication)"),
    ("own_transport", r"own (vehicle|transport|conveyance)"),
    ("background_check", r"(willing|consent).*(background (check|verification)|bgv)"),
    ("start_immediately_15", r"join within (15|fifteen|30|thirty) days|join in (a|1) month"),
    # Current engagement is full-time Remote at AGI Ready — all verifiable.
    ("currently_remote", r"currently working (in a )?remote|working remotely (now|currently)|"
                         r"is your current (role|job) remote"),
    ("currently_employed", r"are you (currently )?(employed|working)\b(?!.*remote)|"
                           r"do you have a (current )?job"),
    ("ok_with_startup", r"comfortable (working )?(in|at|with) (a )?(startup|early[- ]stage|fast[- ]paced)"),
    ("ok_with_contract", r"open to (a )?(contract|contractual|c2h|freelance) (role|position|engagement)"),
)

# Objectively verifiable NO. Distinct from _HARD_NO (which is about consequence) —
# these are simple facts that happen to be false.
_FACT_NO = (
    ("no_gap", r"(career|employment) (gap|break)"),
    ("not_fresher", r"\bare you a fresher\b"),
    ("no_pending_offer", r"any (other )?(pending|active) offer"),
    ("not_currently_unemployed", r"currently (unemployed|not working|without a job)"),
    ("no_notice_buyout_needed", r"require.*notice.*buy[- ]?out"),
    # Canonical notice is 15 days, so "immediate" is factually No. The vault used
    # to claim Immediate Joiner; that was corrected, and this answer follows it.
    ("not_immediate_joiner", r"\bimmediate joiner\b|(join|start)(ing)? immediately|"
                             r"can you (join|start) (immediately|right away|at once)|"
                             r"zero notice|available immediately"),
)

# question-pattern -> answer-bank key
_VALUE_RULES = (
    ("current_ctc", r"current.*(ctc|salary|compensation|package)|present.*(ctc|salary)", "current_ctc"),
    ("expected_ctc", r"expect.*(ctc|salary|compensation|package)|salary expect|desired salary", "expected_ctc_min"),
    ("notice", r"notice period|joining time|how soon|availability to join|when can you join", "notice_period_days"),
    ("current_employer", r"current (company|employer|organi)|present (company|employer)", "current_employer"),
    ("location", r"current location|where are you (based|located)|your city|present location", "city"),
    ("preferred_location", r"preferred location|preferred work location|location preference", "preferred_location"),
    ("email", r"\be-?mail\b", "email"),
    ("phone", r"\b(phone|mobile|contact number)\b", "phone"),
    ("linkedin", r"linkedin", "linkedin_profile"),
    ("github", r"\bgithub\b|portfolio", "github"),
    ("full_name", r"\b(full name|your name)\b", "full_name"),
    ("degree", r"\b(degree|qualification)\b", "degree"),
    ("university", r"\b(university|college|institut)\b", "university"),
    # --- additional factual lookups ---
    ("state", r"\b(state|province)\b", "state"),
    ("country", r"\bcountry\b", "country"),
    ("pincode", r"\b(pin ?code|postal code|zip)\b", "pincode"),
    ("first_name", r"\bfirst name\b", "first_name"),
    ("last_name", r"\b(last|sur)\s?name\b", "last_name"),
    ("grad_year", r"(year of|passing|graduation) ?(year|passout)?", "grad_year"),
    ("current_designation", r"current\s+(\w+\s+){0,2}(designation|title|role|position)|(designation|job title)\\b", "current_designation"),
    ("skills", r"\b(key |primary |core )?skills\b|technolog(y|ies) you", "primary_skills"),
)

# "years of experience WITH <tech>" — answered honestly per technology rather than
# with the overall figure.
# Greedy `[^?]*` on purpose: it anchors on the LAST preposition, so
# "years of experience do you have with React" yields "React", not
# "experience do you have with React".
_TECH_YOE = re.compile(
    r"(?:years?|experience|exp)\b[^?]*\b(?:in|with|of|using)\s+(?P<tech>[\w.+#/\- ]{2,40})",
    re.I,
)
_WORKED_WITH = re.compile(
    r"(?:have you (?:ever )?(?:worked|used|built)(?:(?:\s+\w+){0,3}?\s+(?:with|using|in))?|"
    r"do you have (?:hands[- ]on )?(?:experience|exposure)(?:\s+\w+){0,2}?\s+(?:with|using|in)|"
    r"are you (?:familiar|comfortable) with)\s+(?P<techs>[^?]{2,160})",
    re.I,
)

_TOTAL_YOE = re.compile(
    r"total.*experience|years? of experience|overall experience|\byoe\b|"
    r"how many years|experience.*in years",
    re.I,
)

# Explicit prompts per qa_bank entry. Matching on the key name ("qa_about_me" ->
# "about me") never fired, because real questions say "tell us about yourself".
_QA_PATTERNS = (
    ("qa_why_leaving",   r"reason for leaving|why (are you )?leav|why looking|"
                         r"why (are you )?(looking|searching) for (a )?(new|change)"),
    ("qa_why_role",      r"why (do you want|are you interested|this (role|company|position)|"
                         r"should we hire|apply)|what (interests|attracts|excites|appeals to|"
                         r"has attracted|drew|draws) you|why us\b|interest in (this|the) (role|position)"),
    ("qa_current_role",  r"(describe|tell).*(current|present) role|what do you (currently )?do|"
                         r"current responsibilit"),
    ("qa_tech_challenge",r"technical challenge|difficult (problem|bug|technical)|hardest|"
                         r"most challenging|complex problem|toughest"),
    ("qa_leadership",    r"leadership|led a team|influence without|mentor|"
                         r"took ownership|drove a (change|decision)"),
    ("qa_product_impact",r"(product|user|business|customer) impact|impact (you|of your)|"
                         r"measurable (impact|outcome)"),
    ("qa_innovation",    r"innovat|creative solution|side project|built on your own|"
                         r"proud of|best (project|work)"),
    ("qa_about_me",      r"about (yourself|you)\b|introduce yourself|tell us about you|"
                         r"your background|walk (us|me) through your"),
)

# Numeric/scale questions must never receive a prose answer.
_RATING_STYLE = re.compile(
    r"\brate\b|\bscale of\b|out of (5|10|100)|\b1\s*-\s*(5|10)\b|"
    r"proficiency level|on a scale",
    re.I,
)
# A qa_bank essay only fits a genuinely open-ended prompt.
_OPEN_ENDED = re.compile(
    r"\b(describe|explain|tell us|tell me|why|how|what makes|share|elaborate|"
    r"walk us through|give an example|about yourself)\b",
    re.I,
)

_STOPWORDS = {"the", "a", "an", "and", "or", "your", "you", "this", "that", "any", "work",
              "working", "years", "year", "experience", "role", "job", "field", "domain"}


def _norm(q: str) -> str:
    return re.sub(r"\s+", " ", (q or "")).strip().casefold()


def answer_for_question(question: str, *, bank: dict | None = None) -> Answer:
    """Decide how to answer `question`. First matching rule wins."""
    bank = bank if bank is not None else vc.build_answer_bank()
    q = _norm(question)

    # Rule 0 — the most important line in this file. No question, no answer.
    if not q or len(q) < 3:
        return Answer(Decision.ABSTAIN, rule="empty_question")

    for name, pattern in _HARD_NO:
        if re.search(pattern, q, re.I):
            return Answer(Decision.NO, "No", rule=f"hard_no:{name}")

    for name, pattern in _FACT_NO:
        if re.search(pattern, q, re.I):
            return Answer(Decision.NO, "No", rule=f"fact_no:{name}")

    for name, pattern in _HARD_YES:
        if re.search(pattern, q, re.I):
            return Answer(Decision.YES, "Yes", rule=f"hard_yes:{name}")

    for name, pattern, key in _VALUE_RULES:
        if re.search(pattern, q, re.I):
            value = bank.get(key)
            if value in (None, ""):
                return Answer(Decision.ABSTAIN, rule=f"value_missing:{name}")
            return Answer(Decision.VALUE, vc.assert_no_private_floor(
                str(value), context=f"answer[{name}]"), rule=f"value:{name}")

    # "Have you worked with LangChain, LlamaIndex, CrewAI ...?" — answered from the
    # canonical stack. Yes if any named technology is actually in it, No if none
    # are. Both answers are verifiable; neither is a guess.
    m_used = _WORKED_WITH.search(q)
    if m_used:
        # Word-level match. Chunk-level comparison failed on real phrasing:
        # "AI frameworks such as LangChain, LlamaIndex, ..." splits into a chunk
        # that "langchain.js" is not a substring of, in either direction.
        blob = set(re.findall(r"[a-z0-9+#.]+", m_used.group("techs").casefold()))
        blob |= {w.rstrip(".") for w in blob}
        hit = None
        for known in vc.tech_stack_flat():
            head = re.split(r"[ ./(]", known.casefold(), 1)[0]
            if len(head) >= 3 and (head in blob or known.casefold() in blob):
                hit = head
                break
        if hit:
            return Answer(Decision.YES, "Yes", rule=f"worked_with:{hit[:24]}")
        return Answer(Decision.NO, "No", rule="worked_with:none_in_stack")

    # Tech-scoped YOE before total YOE — "experience with Java" is not total YOE.
    m = _TECH_YOE.search(q)
    if m:
        tech = " ".join(
            w for w in re.split(r"[\s,/]+", m.group("tech").strip())
            if w and w not in _STOPWORDS
        ).strip(" .?")
        if tech:
            return Answer(Decision.VALUE, vc.experience_for_tech(tech),
                          rule=f"tech_yoe:{tech}")

    if _TOTAL_YOE.search(q):
        return Answer(Decision.VALUE, vc.years_experience(), rule="total_yoe")

    # Long-form behavioural questions from the canonical qa_bank.
    #
    # Gated on the question actually being open-ended. Matching a bare topic word
    # meant "Rate yourself 1-10 on leadership" returned the full leadership essay.
    if not _RATING_STYLE.search(q) and len(q) >= 12:
        for key, pattern in _QA_PATTERNS:
            text = (bank or {}).get(key)
            if isinstance(text, str) and text and re.search(pattern, q, re.I):
                return Answer(Decision.VALUE, text, rule=f"qa_bank:{key}")

    # Rule 7 — unrecognised. Abstain; the caller surfaces it for human review.
    return Answer(Decision.ABSTAIN, rule="unrecognised")


def is_option_allowed(question: str, option_text: str, *, bank: dict | None = None) -> bool:
    """May we click this option for this question? Used to gate yes/no clicking."""
    token = _norm(option_text)
    ans = answer_for_question(question, bank=bank)
    if token in YES_TOKENS:
        return ans.decision is Decision.YES
    if token in NO_TOKENS:
        return ans.decision is Decision.NO
    if ans.decision is Decision.VALUE and ans.value:
        return ans.value.casefold() in token or token in ans.value.casefold()
    return False


if __name__ == "__main__":
    bank = vc.build_answer_bank()
    checks = [
        ("Do you require visa sponsorship?", Decision.NO),
        ("Have you ever been convicted of a felony?", Decision.NO),
        ("Are you willing to sign a 2 year bond?", Decision.NO),
        ("Is your notice period 90 days?", Decision.NO),
        ("Are you legally authorized to work in India?", Decision.YES),
        ("Are you willing to relocate?", Decision.YES),
        ("What is your expected CTC?", Decision.VALUE),
        ("What is your current CTC?", Decision.VALUE),
        ("What is your notice period?", Decision.VALUE),
        ("How many years of experience do you have with React?", Decision.VALUE),
        ("Years of experience in COBOL?", Decision.VALUE),
        ("What is your total experience?", Decision.VALUE),
        ("Do you have 5+ years of experience?", Decision.VALUE),
        ("", Decision.ABSTAIN),
        ("Describe a time you disagreed with your manager", Decision.ABSTAIN),
    ]
    failures = 0
    for q, want in checks:
        got = answer_for_question(q, bank=bank)
        ok = got.decision is want
        failures += not ok
        print(f"  {'✓' if ok else '✗'} {q[:52]:<54} -> {got.decision.value:<8}"
              f" {got.value[:22]:<24} [{got.rule}]")

    print("\n  blind-yes gate:")
    for q in ("Do you require visa sponsorship?", "Are you willing to relocate?"):
        allowed = is_option_allowed(q, "Yes", bank=bank)
        print(f"    click 'Yes' on {q[:44]:<46} -> {allowed}")

    raise SystemExit(1 if failures else 0)
