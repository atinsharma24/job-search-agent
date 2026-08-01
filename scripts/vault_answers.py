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
    ("work_mode", r"comfortable.*(remote|wfo|work from office|hybrid|onsite)"),
    ("terms", r"agree.*(terms|conditions|privacy|policy)|read and understood"),
    ("notice_ok", r"can you join|able to join|available to join"),
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
_TOTAL_YOE = re.compile(
    r"total.*experience|years? of experience|overall experience|\byoe\b|"
    r"how many years|experience.*in years",
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
    for key, text in (bank or {}).items():
        if not key.startswith("qa_") or not isinstance(text, str):
            continue
        topic = key[3:].replace("_", " ")
        if topic and topic in q:
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
