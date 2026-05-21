#!/usr/bin/env python3

import json
import math
import re
from pathlib import Path
from typing import Callable, Optional


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def split_name(full_name: str) -> tuple[str, str]:
    parts = full_name.strip().split()
    if not parts:
        return ("", "")
    if len(parts) == 1:
        return (parts[0], "")
    return (parts[0], " ".join(parts[1:]))


def clean_label(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def build_base_answer_bank(fact_sheet_path: Path, logistics_path: Path) -> dict:
    fact_sheet = load_json(fact_sheet_path)
    logistics = load_json(logistics_path)["logistics"]
    candidate = fact_sheet["candidate"]
    first_name, last_name = split_name(candidate["full_name"])

    months = 0
    for experience in fact_sheet.get("experience", []):
        months = max(months, int(experience.get("duration_months", 0) or 0))
    years_experience = max(1, math.ceil(months / 12)) if months else 1

    expected_min = candidate["salary_expectation_inr_lpa"]["min"]
    expected_max = candidate["salary_expectation_inr_lpa"]["max"]

    bank = {
        "fact_sheet": fact_sheet,
        "logistics": logistics,
        "first_name": first_name,
        "last_name": last_name,
        "full_name": candidate["full_name"],
        "email": candidate["email"],
        "phone": candidate["phone"],
        "city": candidate["location"]["city"],
        "state": candidate["location"]["state"],
        "country": candidate["location"]["country"],
        "pincode": candidate["location"]["pincode"],
        "github": candidate["github"],
        "notice_period_days": str(candidate["notice_period_days"]),
        "availability": candidate["availability"],
        "immediate_joiner": logistics["availability"]["notice_period_label"],
        "expected_ctc_min": str(expected_min),
        "expected_ctc_max": str(expected_max),
        "expected_ctc_range": f"{expected_min}-{expected_max}",
        "expected_ctc_label": logistics["compensation"]["expected_ctc_label"],
        "expected_salary_min": str(expected_min),
        "expected_salary_max": str(expected_max),
        "expected_salary_range": f"{expected_min}-{expected_max}",
        "expected_salary_label": logistics["compensation"]["expected_ctc_label"],
        "current_ctc": "0",
        "years_experience": str(years_experience),
        "work_authorized": "Yes",
        "requires_sponsorship": "No",
        "open_to_relocate": "Yes",
        "preferred_location": logistics["work_preference"]["primary"],
        "secondary_location": logistics["work_preference"]["secondary"],
        "degree": fact_sheet["education"][0]["degree"],
        "university": fact_sheet["education"][0]["institution"],
        "linkedin_profile": "https://www.linkedin.com/in/atinsharma24/",
    }

    # Merge Q&A bank so all portal scripts can answer open-ended text fields.
    qa_bank = logistics.get("qa_bank", {})
    bank.update(qa_bank)

    return bank


def build_field_key(locator, wrapper_selector: Optional[str] = None) -> str:
    try:
        label_text = locator.evaluate(
            """(element, wrapperSelector) => {
                const labelTexts = [];
                if (element.labels) {
                    for (const label of element.labels) {
                        if (label && label.textContent) labelTexts.push(label.textContent);
                    }
                }
                const ariaLabelledBy = element.getAttribute('aria-labelledby');
                if (ariaLabelledBy) {
                    for (const id of ariaLabelledBy.split(/\\s+/)) {
                        const target = document.getElementById(id);
                        if (target && target.textContent) labelTexts.push(target.textContent);
                    }
                }
                const fieldset = element.closest('fieldset');
                if (fieldset) {
                    const legend = fieldset.querySelector('legend');
                    if (legend && legend.textContent) labelTexts.push(legend.textContent);
                }
                if (wrapperSelector) {
                    const wrapper = element.closest(wrapperSelector);
                    if (wrapper && wrapper.textContent) labelTexts.push(wrapper.textContent);
                }
                return labelTexts.join(' ');
            }""",
            wrapper_selector,
        )
        if label_text:
            return clean_label(label_text)
    except Exception:
        pass

    parts = [
        locator.get_attribute("aria-label"),
        locator.get_attribute("placeholder"),
        locator.get_attribute("name"),
        locator.get_attribute("id"),
    ]
    for part in parts:
        if part:
            return clean_label(part)
    return ""


def map_answer(label_text: str, answer_bank: dict, mapping: list[tuple[tuple[str, ...], str]]) -> Optional[str]:
    key = clean_label(label_text).casefold()
    for patterns, answer_key in mapping:
        if any(re.search(pattern, key) for pattern in patterns):
            value = answer_bank.get(answer_key)
            if value is None:
                return None
            return str(value)
    return None


def choose_select_option(select_locator, answer: str) -> bool:
    options = select_locator.locator("option")
    option_texts = [clean_label(option.inner_text()) for option in options.all()]
    for option_text in option_texts:
        if not option_text:
            continue
        lowered_option = option_text.casefold()
        lowered_answer = answer.casefold()
        if lowered_answer == lowered_option or lowered_answer in lowered_option or lowered_option in lowered_answer:
            select_locator.select_option(label=option_text)
            return True
    return False


def maybe_upload_file(root, file_path: Path, selector: str = 'input[type="file"]') -> bool:
    upload_inputs = root.locator(selector)
    if upload_inputs.count() == 0:
        return False
    upload_inputs.first.set_input_files(str(file_path))
    return True


def fill_text_inputs(
    root,
    answer_mapper: Callable[[str], Optional[str]],
    wrapper_selector: Optional[str] = None,
    selector: str = 'input:not([type="hidden"]):not([type="file"]):not([type="radio"]):not([type="checkbox"])',
) -> None:
    inputs = root.locator(selector)
    for index in range(inputs.count()):
        locator = inputs.nth(index)
        if not locator.is_visible() or locator.is_disabled():
            continue
        if locator.input_value().strip():
            continue
        answer = answer_mapper(build_field_key(locator, wrapper_selector))
        if answer is None:
            continue
        locator.fill(answer)


def fill_textareas(
    root,
    answer_mapper: Callable[[str], Optional[str]],
    wrapper_selector: Optional[str] = None,
) -> None:
    textareas = root.locator("textarea")
    for index in range(textareas.count()):
        locator = textareas.nth(index)
        if not locator.is_visible() or locator.is_disabled():
            continue
        if locator.input_value().strip():
            continue
        answer = answer_mapper(build_field_key(locator, wrapper_selector))
        if answer is None:
            continue
        locator.fill(answer)


def fill_selects(
    root,
    answer_mapper: Callable[[str], Optional[str]],
    wrapper_selector: Optional[str] = None,
) -> None:
    selects = root.locator("select")
    for index in range(selects.count()):
        locator = selects.nth(index)
        if not locator.is_visible() or locator.is_disabled():
            continue
        answer = answer_mapper(build_field_key(locator, wrapper_selector))
        if answer is None:
            continue
        choose_select_option(locator, answer)


def fill_radio_groups(
    root,
    answer_mapper: Callable[[str], Optional[str]],
    container_selector: str = "fieldset",
    option_selector: str = "label, [role='radio'], button",
) -> None:
    containers = root.locator(container_selector)
    for index in range(containers.count()):
        container = containers.nth(index)
        if not container.is_visible():
            continue
        answer = answer_mapper(clean_label(container.inner_text()))
        if answer is None:
            continue
        options = container.locator(option_selector)
        for option_index in range(options.count()):
            option = options.nth(option_index)
            option_text = clean_label(option.inner_text())
            if not option_text:
                continue
            if answer.casefold() in option_text.casefold() or option_text.casefold() in answer.casefold():
                option.click()
                break
