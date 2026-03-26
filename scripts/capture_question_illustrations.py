#!/usr/bin/env python3
"""Capture one Playwright screenshot per question from internet source URLs."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True)


def capture(url: str, output_file: Path) -> tuple[bool, str]:
    cmd = [
        "npx",
        "--yes",
        "playwright",
        "screenshot",
        "--wait-for-timeout=800",
        "--device=Desktop Chrome",
        url,
        str(output_file),
    ]
    result = run_cmd(cmd)
    if result.returncode == 0:
        return True, ""
    return False, (result.stderr or result.stdout).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    bank_path = root / "backend" / "data" / "question_bank.json"
    output_dir = root / "frontend" / "illustrations" / "questions"
    output_dir.mkdir(parents=True, exist_ok=True)

    with bank_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    section_default_sources = {
        section["slug"]: section["default_illustration"]["source_url"]
        for section in payload["sections"]
    }

    total = 0
    created = 0
    skipped = 0
    failed = 0

    for section in payload["sections"]:
        section_slug = section["slug"]
        fallback_url = section_default_sources.get(section_slug, "https://en.wikipedia.org")

        for question in section["questions"]:
            total += 1
            question_id = question["id"]
            output_file = output_dir / f"{question_id}.png"

            if output_file.exists() and not args.force:
                skipped += 1
                continue

            primary_url = question["illustrations"][0]["source_url"]
            ok, err = capture(primary_url, output_file)
            if not ok:
                ok, err = capture(fallback_url, output_file)

            if ok:
                created += 1
                print(f"[{total}] captured {question_id}")
            else:
                failed += 1
                print(f"[{total}] failed {question_id}: {err[:180]}")

    print(
        f"Done. total={total} created={created} skipped={skipped} failed={failed} output={output_dir}"
    )

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
