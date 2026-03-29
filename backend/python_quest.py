from __future__ import annotations

import contextlib
import io
import json
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
PYTHON_MODULE_DIR = BASE_DIR / "python"

if str(PYTHON_MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_MODULE_DIR))

import run as python_run  # type: ignore[import-not-found]


def slugify_lesson(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _capture_learn_cards(module: Any) -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []
    original = {
        "print_header": getattr(module, "print_header", None),
        "print_subheader": getattr(module, "print_subheader", None),
        "print_code_and_output": getattr(module, "print_code_and_output", None),
        "print_concept": getattr(module, "print_concept", None),
        "pause": getattr(module, "pause", None),
    }

    module.print_header = lambda _title: None
    module.print_subheader = lambda title: cards.append({"kind": "checkpoint", "title": title})
    module.print_concept = (
        lambda title, body: cards.append(
            {"kind": "concept", "title": title, "body": str(body).strip()}
        )
    )
    module.print_code_and_output = (
        lambda code, output: cards.append(
            {"kind": "code", "code": str(code).rstrip(), "output": str(output).rstrip()}
        )
    )
    module.pause = lambda: None

    try:
        with contextlib.redirect_stdout(io.StringIO()):
            module.learn()
    finally:
        for name, value in original.items():
            setattr(module, name, value)

    return cards


def _capture_practice_challenges(module: Any) -> list[dict[str, Any]]:
    captured: list[dict[str, Any]] = []
    original = getattr(module, "run_coding_challenge", None)
    module.run_coding_challenge = lambda challenges: captured.extend(challenges)

    try:
        with contextlib.redirect_stdout(io.StringIO()):
            module.practice()
    finally:
        module.run_coding_challenge = original

    return captured


def _capture_quiz_questions(module: Any) -> list[dict[str, Any]]:
    captured: list[dict[str, Any]] = []
    original = getattr(module, "run_quiz", None)
    module.run_quiz = lambda questions: captured.extend(questions)

    try:
        with contextlib.redirect_stdout(io.StringIO()):
            module.quiz()
    finally:
        module.run_quiz = original

    return captured


def _build_starter_code(solution: str) -> str:
    lines = [line.rstrip() for line in solution.splitlines() if line.strip()]
    if not lines:
        return "# Solve the challenge here"

    first_line = lines[0].strip()
    if first_line.startswith("def ") and first_line.endswith(":"):
        return f"{first_line}\n    "
    if " = lambda " in first_line:
        target = first_line.split("=", 1)[0].strip()
        return f"{target} = lambda "
    if "=" in first_line:
        return "# Create the requested variables here"
    return "# Solve the challenge here"


def _serialize_lesson(
    lesson_id: int,
    title: str,
    module: Any,
    learn_cards: list[dict[str, str]],
    practice_challenges: list[dict[str, Any]],
    quiz_questions: list[dict[str, Any]],
) -> dict[str, Any]:
    slug = slugify_lesson(title)
    summary = next(
        (card["body"] for card in learn_cards if card.get("kind") == "concept" and card.get("body")),
        (module.__doc__ or title).strip(),
    )
    checkpoints = [
        card["title"]
        for card in learn_cards
        if card.get("kind") == "checkpoint" and card.get("title")
    ][:5]

    return {
        "id": lesson_id,
        "slug": slug,
        "title": title,
        "summary": summary,
        "checkpoint_titles": checkpoints,
        "learn_cards": learn_cards[:12],
        "practice": [
            {
                "index": index,
                "prompt": challenge.get("prompt", ""),
                "hint": challenge.get("hint", ""),
                "starter_code": _build_starter_code(str(challenge.get("solution", ""))),
            }
            for index, challenge in enumerate(practice_challenges)
        ],
        "quiz": [
            {
                "index": index,
                "question": question.get("question", ""),
                "options": question.get("options", []),
                "answer": question.get("answer", 0),
                "explanation": question.get("explanation", ""),
            }
            for index, question in enumerate(quiz_questions)
        ],
    }


@lru_cache(maxsize=1)
def get_python_quest_runtime() -> dict[str, Any]:
    lessons: list[dict[str, Any]] = []
    practice_registry: dict[str, list[dict[str, Any]]] = {}

    for lesson_id, (title, module) in enumerate(python_run.LESSONS, start=1):
        learn_cards = _capture_learn_cards(module)
        practice_challenges = _capture_practice_challenges(module)
        quiz_questions = _capture_quiz_questions(module)
        serialized = _serialize_lesson(
            lesson_id=lesson_id,
            title=title,
            module=module,
            learn_cards=learn_cards,
            practice_challenges=practice_challenges,
            quiz_questions=quiz_questions,
        )
        lessons.append(serialized)
        practice_registry[serialized["slug"]] = practice_challenges

    return {
        "lessons": lessons,
        "practice_registry": practice_registry,
    }


def get_python_quest_catalog() -> dict[str, Any]:
    runtime = get_python_quest_runtime()
    lessons = runtime["lessons"]
    return {
        "stats": {
            "lesson_count": len(lessons),
            "challenge_count": sum(len(lesson["practice"]) for lesson in lessons),
            "quiz_question_count": sum(len(lesson["quiz"]) for lesson in lessons),
        },
        "lessons": lessons,
    }


def validate_python_quest_submission(
    lesson_slug: str,
    challenge_index: int,
    code: str,
) -> dict[str, Any]:
    runtime = get_python_quest_runtime()
    challenges = runtime["practice_registry"].get(lesson_slug)
    if challenges is None:
        return {
            "ok": False,
            "message": f"Lesson '{lesson_slug}' was not found.",
            "hint": "",
            "stdout": "",
        }

    if challenge_index < 0 or challenge_index >= len(challenges):
        return {
            "ok": False,
            "message": f"Challenge {challenge_index} is out of range for lesson '{lesson_slug}'.",
            "hint": "",
            "stdout": "",
        }

    challenge = challenges[challenge_index]
    namespace: dict[str, Any] = {}
    stdout = io.StringIO()

    try:
        compiled = compile(code, f"<python-quest:{lesson_slug}>", "exec")
        with contextlib.redirect_stdout(stdout):
            exec(compiled, namespace, namespace)
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "message": f"{type(exc).__name__}: {exc}",
            "hint": challenge.get("hint", ""),
            "stdout": stdout.getvalue(),
        }

    try:
        passed = bool(challenge["validator"](namespace, code))
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "message": f"Validation error: {type(exc).__name__}: {exc}",
            "hint": challenge.get("hint", ""),
            "stdout": stdout.getvalue(),
        }

    return {
        "ok": passed,
        "message": (
            "Challenge cleared. Your spell matched the lesson goal."
            if passed
            else "Close, but the lesson goal is not satisfied yet."
        ),
        "hint": challenge.get("hint", ""),
        "stdout": stdout.getvalue(),
    }


def run_validation_subprocess(
    lesson_slug: str,
    challenge_index: int,
    code: str,
    timeout_seconds: float = 3.0,
) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "backend.python_quest",
                "validate",
                lesson_slug,
                str(challenge_index),
            ],
            cwd=BASE_DIR,
            input=code,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "message": "Validation timed out. Shorten the code path and try again.",
            "hint": "",
            "stdout": "",
        }

    payload = (completed.stdout or "").strip()
    if not payload:
        return {
            "ok": False,
            "message": "Validation returned no output.",
            "hint": "",
            "stdout": "",
        }

    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return {
            "ok": False,
            "message": completed.stderr.strip() or "Validation produced unreadable output.",
            "hint": "",
            "stdout": payload,
        }


def _main(argv: list[str]) -> int:
    if len(argv) != 4 or argv[1] != "validate":
        print(
            json.dumps(
                {
                    "ok": False,
                    "message": "Usage: python -m backend.python_quest validate <lesson_slug> <challenge_index>",
                    "hint": "",
                    "stdout": "",
                }
            )
        )
        return 1

    lesson_slug = argv[2]
    try:
        challenge_index = int(argv[3])
    except ValueError:
        print(
            json.dumps(
                {
                    "ok": False,
                    "message": "challenge_index must be an integer.",
                    "hint": "",
                    "stdout": "",
                }
            )
        )
        return 1

    code = sys.stdin.read()
    print(json.dumps(validate_python_quest_submission(lesson_slug, challenge_index, code)))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
