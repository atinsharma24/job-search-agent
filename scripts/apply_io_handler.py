#!/usr/bin/env python3

import argparse
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path


VAULT_ROOT = Path(__file__).resolve().parents[1]
CATEGORY_DIR = VAULT_ROOT / "resumes_and_docs" / "categories" / "md"
STAGED_RESUME_PATH = (
    VAULT_ROOT / "active_application_context" / "staged_application_resume.md"
)
STAGED_RESUME_PDF_PATH = (
    VAULT_ROOT / "active_application_context" / "staged_application_resume.pdf"
)
TRACKER_PATH = (
    VAULT_ROOT / "active_application_context" / "job_applications_tracker.md"
)

TRACKER_HEADER = "\n".join(
    [
        "# Job Applications Tracker",
        "",
        "Human-readable audit log for application outcomes.",
        "",
        "| Date | Company | Job Title | URL | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministic resume staging and tracker sync for job applications."
    )
    parser.add_argument(
        "--payload-file",
        type=Path,
        help="Path to a JSON payload file. If omitted, stdin is used.",
    )
    return parser.parse_args()


def load_payload(args: argparse.Namespace) -> dict:
    if args.payload_file:
        raw = args.payload_file.read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()

    if not raw.strip():
        raise ValueError("empty payload")

    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("payload must be a flat JSON object")

    required = {
        "resume_category",
        "changed_keywords",
        "company",
        "job_title",
        "application_url",
    }
    missing = sorted(required - payload.keys())
    if missing:
        raise ValueError(f"missing required keys: {', '.join(missing)}")

    return payload


def normalize_keywords(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        items = value
    elif isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        if stripped.startswith("["):
            try:
                parsed = json.loads(stripped)
                if isinstance(parsed, list):
                    items = parsed
                else:
                    items = [stripped]
            except json.JSONDecodeError:
                items = stripped.replace("\n", ",").split(",")
        else:
            items = stripped.replace("\n", ",").split(",")
    else:
        items = [value]

    normalized: list[str] = []
    seen: set[str] = set()
    for item in items:
        text = str(item).strip()
        if not text:
            continue
        lowered = text.casefold()
        if lowered in seen:
            continue
        seen.add(lowered)
        normalized.append(text)
    return normalized


def resolve_resume_path(resume_category: str) -> Path:
    category = str(resume_category).strip()
    if not category:
        raise ValueError("resume_category cannot be empty")

    candidates = []
    if category.endswith(".md"):
        candidates.append(CATEGORY_DIR / category)
    else:
        candidates.append(CATEGORY_DIR / f"{category}.md")
        candidates.append(CATEGORY_DIR / category)

    normalized = category.casefold().replace(" ", "_")
    if not normalized.endswith(".md"):
        normalized = f"{normalized}.md"
    candidates.append(CATEGORY_DIR / normalized)

    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(f"baseline resume not found for category: {resume_category}")


def keyword_missing(text: str, keyword: str) -> bool:
    return keyword.casefold() not in text.casefold()


def skill_exists(existing_skills: list[str], keyword: str) -> bool:
    lowered = keyword.casefold()
    for skill in existing_skills:
        skill_lowered = skill.casefold()
        if lowered in skill_lowered or skill_lowered in lowered:
            return True
    return False


def inject_keywords(content: str, changed_keywords: list[str]) -> str:
    lines = content.splitlines()
    profile_index = None
    tech_focus_index = None

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "**Profile:**":
            profile_index = index + 1
        elif stripped in {"**Tech Focus:**", "**Skills:**"}:
            tech_focus_index = index + 1

    if profile_index is None or profile_index >= len(lines):
        raise ValueError("profile/summary section not found in baseline resume")
    if tech_focus_index is None or tech_focus_index >= len(lines):
        raise ValueError("skills section not found in baseline resume")

    summary_line = lines[profile_index].rstrip()
    missing_for_summary = [
        keyword for keyword in changed_keywords if keyword_missing(summary_line, keyword)
    ]
    if missing_for_summary:
        summary_suffix = f" Target keywords: {', '.join(missing_for_summary)}."
        lines[profile_index] = f"{summary_line}{summary_suffix}"

    skills_line = lines[tech_focus_index].strip()
    existing_skills = [
        part.strip().rstrip(".") for part in skills_line.split(",") if part.strip()
    ]
    for keyword in changed_keywords:
        if not skill_exists(existing_skills, keyword):
            existing_skills.append(keyword)
    lines[tech_focus_index] = ", ".join(existing_skills) + "."

    return "\n".join(lines) + "\n"


def sanitize_table_cell(value: str) -> str:
    return str(value).replace("|", "/").strip()


def ensure_tracker_header() -> None:
    if not TRACKER_PATH.exists() or not TRACKER_PATH.read_text(encoding="utf-8").strip():
        TRACKER_PATH.write_text(TRACKER_HEADER, encoding="utf-8")


def append_tracker_row(payload: dict) -> None:
    ensure_tracker_header()
    existing = TRACKER_PATH.read_text(encoding="utf-8")
    row = (
        f"| {date.today().isoformat()} | "
        f"{sanitize_table_cell(payload['company'])} | "
        f"{sanitize_table_cell(payload['job_title'])} | "
        f"{sanitize_table_cell(payload['application_url'])} | "
        "Applied |\n"
    )
    with TRACKER_PATH.open("a", encoding="utf-8") as handle:
        if existing and not existing.endswith("\n"):
            handle.write("\n")
        handle.write(row)


def escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def write_minimal_pdf(markdown_text: str, output_path: Path) -> None:
    lines = markdown_text.splitlines() or [""]
    page_lines = 48
    pages = [lines[i : i + page_lines] for i in range(0, len(lines), page_lines)] or [[""]]

    objects: list[bytes] = []

    def add_object(content: bytes) -> int:
        objects.append(content)
        return len(objects)

    font_obj = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    page_object_ids: list[int] = []
    content_object_ids: list[int] = []
    pages_obj_id_placeholder = 0

    for page_lines_chunk in pages:
        text_commands = ["BT", "/F1 10 Tf", "50 780 Td", "14 TL"]
        first_line = True
        for line in page_lines_chunk:
            escaped = escape_pdf_text(line)
            if first_line:
                text_commands.append(f"({escaped}) Tj")
                first_line = False
            else:
                text_commands.append(f"T* ({escaped}) Tj")
        text_commands.append("ET")
        stream = "\n".join(text_commands).encode("utf-8")
        content_obj_id = add_object(
            b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream"
        )
        content_object_ids.append(content_obj_id)
        page_obj_id = add_object(
            b"<< /Type /Page /Parent PAGES_REF 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 "
            + str(font_obj).encode("ascii")
            + b" 0 R >> >> /Contents "
            + str(content_obj_id).encode("ascii")
            + b" 0 R >>"
        )
        page_object_ids.append(page_obj_id)

    kids_refs = " ".join(f"{obj_id} 0 R" for obj_id in page_object_ids).encode("ascii")
    pages_obj_id_placeholder = add_object(
        b"<< /Type /Pages /Kids [ " + kids_refs + b" ] /Count " + str(len(page_object_ids)).encode("ascii") + b" >>"
    )
    catalog_obj = add_object(
        b"<< /Type /Catalog /Pages " + str(pages_obj_id_placeholder).encode("ascii") + b" 0 R >>"
    )

    rewritten_objects: list[bytes] = []
    for obj in objects:
        rewritten_objects.append(
            obj.replace(b"PAGES_REF", str(pages_obj_id_placeholder).encode("ascii"))
        )
    objects = rewritten_objects

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_obj} 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    output_path.write_bytes(pdf)


def render_resume_pdf(markdown_path: Path, output_path: Path) -> str:
    pandoc_path = shutil.which("pandoc")
    if pandoc_path:
        try:
            subprocess.run(
                [
                    pandoc_path,
                    str(markdown_path),
                    "-o",
                    str(output_path),
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return "pandoc"
        except subprocess.CalledProcessError:
            pass

    write_minimal_pdf(markdown_path.read_text(encoding="utf-8"), output_path)
    return "builtin"


def main() -> int:
    try:
        args = parse_args()
        payload = load_payload(args)
        payload["changed_keywords"] = normalize_keywords(payload["changed_keywords"])

        resume_path = resolve_resume_path(payload["resume_category"])
        baseline = resume_path.read_text(encoding="utf-8")
        staged = inject_keywords(baseline, payload["changed_keywords"])
        STAGED_RESUME_PATH.write_text(staged, encoding="utf-8")
        pdf_renderer = render_resume_pdf(STAGED_RESUME_PATH, STAGED_RESUME_PDF_PATH)

        append_tracker_row(payload)

        result = {
            "status": "ok",
            "staged_resume_path": str(STAGED_RESUME_PATH),
            "staged_resume_pdf_path": str(STAGED_RESUME_PDF_PATH),
            "pdf_renderer": pdf_renderer,
            "tracker_path": str(TRACKER_PATH),
            "resume_source_path": str(resume_path),
        }
        print(json.dumps(result))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
