#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract the first valid application payload JSON object from raw LLM output."
    )
    parser.add_argument(
        "--source-file",
        type=Path,
        help="File containing raw LLM output. If omitted, stdin is used.",
    )
    parser.add_argument(
        "--payload-file",
        type=Path,
        help="File containing an already extracted JSON payload.",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        help="Optional file path to write the extracted payload JSON.",
    )
    parser.add_argument(
        "--field",
        help="Optional field name to print from the extracted payload.",
    )
    return parser.parse_args()


def read_raw_text(args: argparse.Namespace) -> str:
    if args.payload_file:
        return args.payload_file.read_text(encoding="utf-8")
    if args.source_file:
        return args.source_file.read_text(encoding="utf-8")
    return sys.stdin.read()


def is_payload(candidate: object) -> bool:
    if not isinstance(candidate, dict):
        return False
    required = {
        "job_title",
        "company",
        "application_url",
        "resume_category",
        "changed_keywords",
        "action",
    }
    return required.issubset(candidate.keys())


def extract_payload(raw_text: str) -> dict:
    stripped = raw_text.strip()
    if not stripped:
        raise ValueError("empty input")

    try:
        parsed = json.loads(stripped)
        if is_payload(parsed):
            return parsed
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    for index, char in enumerate(raw_text):
        if char != "{":
            continue
        try:
            candidate, _ = decoder.raw_decode(raw_text[index:])
        except json.JSONDecodeError:
            continue
        if is_payload(candidate):
            return candidate

    raise ValueError("no valid application payload found in input")


def main() -> int:
    try:
        args = parse_args()
        payload = extract_payload(read_raw_text(args))

        if args.output_file:
            args.output_file.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

        if args.field:
            value = payload.get(args.field, "")
            if isinstance(value, (dict, list)):
                print(json.dumps(value))
            else:
                print(value)
        else:
            print(json.dumps(payload))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
