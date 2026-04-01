#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.python_quest import get_python_quest_catalog
from python import run as python_run

QUESTION_BANK_SOURCE = ROOT / "backend" / "data" / "question_bank.json"
FRONTEND_DATA_DIR = ROOT / "frontend" / "data"
QUESTION_BANK_TARGET = FRONTEND_DATA_DIR / "question_bank.json"
LESSONS_TARGET = FRONTEND_DATA_DIR / "offline_python_lessons.json"
IOS_WEBAPP_TARGET = ROOT / "ios" / "PythonQuestCompanion" / "Resources" / "WebApp"


def normalize_validator_source(source: str) -> str:
    # Keep generated validator strings stable across Python patch versions.
    return re.sub(r"lambda\s+:", "lambda:", source)


def ensure_data_dir() -> None:
    FRONTEND_DATA_DIR.mkdir(parents=True, exist_ok=True)


def extract_practice_metadata(module_path: Path) -> tuple[str, list[dict[str, str]]]:
    source = module_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    lesson_menu_title = ""
    practice_items: list[dict[str, str]] = []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            for inner in ast.walk(node):
                if (
                    isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Name)
                    and inner.func.id == "lesson_menu"
                    and inner.args
                ):
                    lesson_menu_title = ast.literal_eval(inner.args[0])
                    break

        if isinstance(node, ast.FunctionDef) and node.name == "practice":
            for stmt in node.body:
                if not isinstance(stmt, ast.Assign):
                    continue
                if not any(isinstance(target, ast.Name) and target.id == "challenges" for target in stmt.targets):
                    continue
                if not isinstance(stmt.value, ast.List):
                    continue

                for item in stmt.value.elts:
                    if not isinstance(item, ast.Dict):
                        continue
                    record: dict[str, str] = {}
                    for key_node, value_node in zip(item.keys, item.values):
                        key = ast.literal_eval(key_node)
                        if key == "validator":
                            record["validator_source"] = normalize_validator_source(ast.unparse(value_node))
                        elif key in {"prompt", "hint", "solution"}:
                            record[key] = ast.literal_eval(value_node)
                    practice_items.append(record)
                break

    return lesson_menu_title, practice_items


def build_offline_lessons() -> dict[str, object]:
    catalog = get_python_quest_catalog()
    lessons = catalog["lessons"]

    for lesson, (_title, module) in zip(lessons, python_run.LESSONS, strict=True):
        menu_title, practice_items = extract_practice_metadata(Path(module.__file__).resolve())
        lesson["menu_title"] = menu_title or lesson["title"]
        lesson["practice_full"] = []

        for challenge, metadata in zip(lesson.get("practice", []), practice_items, strict=True):
            lesson["practice_full"].append(
                {
                    **challenge,
                    "prompt": metadata.get("prompt", challenge.get("prompt", "")),
                    "hint": metadata.get("hint", challenge.get("hint", "")),
                    "solution": metadata.get("solution", ""),
                    "validator_source": metadata.get("validator_source", ""),
                }
            )

    return {
        "stats": catalog["stats"],
        "validation_enabled": True,
        "validation_reason": "On-device Python engine",
        "lessons": lessons,
    }


def main() -> None:
    ensure_data_dir()
    shutil.copyfile(QUESTION_BANK_SOURCE, QUESTION_BANK_TARGET)
    LESSONS_TARGET.write_text(
        json.dumps(build_offline_lessons(), indent=2),
        encoding="utf-8",
    )
    if IOS_WEBAPP_TARGET.exists():
        shutil.rmtree(IOS_WEBAPP_TARGET)
    shutil.copytree(ROOT / "frontend", IOS_WEBAPP_TARGET)
    print(f"Wrote {QUESTION_BANK_TARGET}")
    print(f"Wrote {LESSONS_TARGET}")
    print(f"Synced {IOS_WEBAPP_TARGET}")


if __name__ == "__main__":
    main()
