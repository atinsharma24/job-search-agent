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


def build_base_answer_bank(fact_sheet_path: Path = None, logistics_path: Path = None) -> dict:
    """Canonical answer bank. Delegates to vault_config.

    Previously this built the bank inline and did two harmful things:

      * `years_experience = 0  # Fresher` — it computed real months from the fact
        sheet, discarded them, and submitted 0 on every application.
      * It embedded the raw `fact_sheet` and `logistics` dicts under those keys,
        which carried the PRIVATE 15 LPA negotiation floor into every bank.

    vault_config redacts the floor at load and computes experience honestly. The
    path arguments are accepted and ignored so the three existing call sites
    (cutshort:19, linkedin_discover:192, naukri_discover:290) need no change.
    """
    import vault_config as vc

    return vc.build_answer_bank()


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
        label_text = container.evaluate("""el => {
            const legend = el.querySelector('legend');
            if (legend && legend.innerText.trim()) return legend.innerText;
            
            let sibling = el.previousElementSibling;
            while (sibling) {
                if (sibling.innerText && sibling.innerText.trim()) {
                    return sibling.innerText;
                }
                sibling = sibling.previousElementSibling;
            }
            
            if (el.parentElement) {
                return el.parentElement.innerText;
            }
            return el.innerText;
        }""")
        answer = answer_mapper(clean_label(label_text))
        if answer is None:
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
