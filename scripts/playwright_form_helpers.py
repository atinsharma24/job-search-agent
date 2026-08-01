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


def fill_radio_groups_by_input(root, answer_mapper) -> int:
    """Fill yes/no and choice radios without relying on <fieldset>.

    fill_radio_groups() scopes to a fieldset container. LinkedIn's current Easy
    Apply forms render radio groups as plain divs, so the group was never found and
    required questions were left blank — the form then refused to advance and the
    application died as a generic failure, even though the answer had been
    computed correctly.

    This works from the radio inputs outward: group by `name`, derive the question
    from the nearest ancestor that carries text, then click the option whose label
    matches the answer. Returns how many groups were filled.
    """
    filled = 0
    try:
        radios = root.locator("input[type='radio']")
        count = radios.count()
    except Exception:
        return 0

    if count == 0:
        return 0
    print(f"  [radio] {count} radio input(s) in scope", flush=True)

    seen_groups: set[str] = set()
    for i in range(count):
        try:
            radio = radios.nth(i)
            # NOT gated on is_visible(): LinkedIn hides the real <input> and styles
            # the <label>, so every input reports invisible and the whole loop
            # silently did nothing — no logs, no clicks, and a required question
            # left blank while the correct answer sat unused.
            group = radio.get_attribute("name") or f"__anon{i}"
            if group in seen_groups:
                continue

            info = radio.evaluate("""el => {
                // Question text: nearest ancestor holding more than the option labels.
                let node = el.parentElement, question = '';
                for (let d = 0; d < 6 && node; d++, node = node.parentElement) {
                    const t = (node.innerText || '').trim();
                    if (t.length > 12) { question = t; break; }
                }
                const name = el.getAttribute('name');
                const opts = Array.from(
                    document.querySelectorAll(`input[type=radio][name="${name}"]`)
                ).map(r => {
                    let lab = '';
                    if (r.id) {
                        const l = document.querySelector(`label[for="${CSS.escape(r.id)}"]`);
                        if (l) lab = (l.innerText || '').trim();
                    }
                    if (!lab && r.parentElement) lab = (r.parentElement.innerText || '').trim();
                    // Some LinkedIn radios carry no label element at all; the value
                    // attribute ("Yes"/"No") is then the only usable text.
                    if (!lab) lab = (r.getAttribute('value') || '').trim();
                    return {id: r.id || '', label: lab, value: r.getAttribute('value') || ''};
                });
                return {question, options: opts};
            }""")

            question = clean_label(info.get("question", ""))
            options = info.get("options") or []
            if not question or not options:
                print(f"  [radio] group {group!r}: no question or options resolved", flush=True)
                continue

            # Strip option labels and validation chrome out of the captured block.
            # Anchoring these to the END of the string failed whenever LinkedIn
            # appended "This field is required" after the options.
            question = re.sub(r"this field is required\.?", "", question, flags=re.I)
            for opt in options:
                lab = (opt.get("label") or "").strip()
                if lab and len(lab) < 30:
                    question = re.sub(rf"\b{re.escape(lab)}\b", " ", question)
            question = clean_label(question)

            answer = answer_mapper(question)
            if not answer:
                print(f"  [radio] no answer for {question[:80]!r}", flush=True)
                continue

            wanted = answer.strip().casefold()
            for opt in options:
                lab = ((opt.get("label") or opt.get("value") or "")).strip().casefold()
                if not lab:
                    continue
                if lab == wanted or wanted in lab or lab in wanted:
                    target = (root.locator(f"#{opt['id']}") if opt.get("id")
                              else root.locator(f"input[type=radio][name='{group}']").nth(0))
                    clicked = False
                    # The visible control is the label, not the input.
                    for attempt in (
                        lambda: root.locator(f"label[for='{opt['id']}']").first.click(timeout=4000),
                        lambda: target.check(timeout=4000, force=True),
                        lambda: target.click(timeout=4000, force=True),
                        lambda: target.evaluate(
                            "el => { el.checked = true; "
                            "el.dispatchEvent(new Event('change', {bubbles: true})); }"),
                    ):
                        try:
                            attempt()
                            clicked = True
                            break
                        except Exception:
                            continue
                    if not clicked:
                        print(f"  [radio] could not click {lab!r}", flush=True)
                        break
                    filled += 1
                    seen_groups.add(group)
                    print(f"  [radio] {answer!r} <- {question[:70]!r}", flush=True)
                    break
        except Exception:
            continue
    return filled
