from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import Body, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .python_quest import get_python_quest_catalog, run_validation_subprocess

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "backend" / "data" / "question_bank.json"
FRONTEND_DIR = BASE_DIR / "frontend"
PYTHON_MODULE_DIR = BASE_DIR / "python"
PYTHON_SESSION_IDLE_SECONDS = 30 * 60


@lru_cache(maxsize=1)
def load_question_bank() -> dict[str, Any]:
    with DATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def normalize(text: str | None) -> str:
    return (text or "").strip().lower()


def filter_questions(
    payload: dict[str, Any],
    section_slug: str | None,
    search: str | None,
) -> list[dict[str, Any]]:
    search_text = normalize(search)
    slug_filter = normalize(section_slug)
    results: list[dict[str, Any]] = []

    for section in payload["sections"]:
        if slug_filter and section["slug"] != slug_filter:
            continue

        for question in section["questions"]:
            blob = " ".join(
                [
                    question["question"],
                    question["core_answer"],
                    question["deep_dive"],
                    " ".join(question.get("notes", [])),
                    section["name"],
                ]
            ).lower()

            if search_text and search_text not in blob:
                continue

            results.append(
                {
                    "section": {
                        "id": section["id"],
                        "slug": section["slug"],
                        "name": section["name"],
                    },
                    **question,
                }
            )

    return results


@dataclass
class PythonCliSession:
    session_id: str
    process: subprocess.Popen[str]
    created_at: float = field(default_factory=time.time)
    last_active_at: float = field(default_factory=time.time)
    output: str = ""
    output_lock: threading.Lock = field(default_factory=threading.Lock)
    reader_thread: threading.Thread | None = None

    def start_reader(self) -> None:
        self.reader_thread = threading.Thread(target=self._read_output, daemon=True)
        self.reader_thread.start()

    def _read_output(self) -> None:
        stream = self.process.stdout
        if stream is None:
            return
        while True:
            chunk = stream.read(1)
            if chunk == "" and self.process.poll() is not None:
                break
            if not chunk:
                time.sleep(0.01)
                continue
            self.append_output(chunk)

    def append_output(self, text: str) -> None:
        with self.output_lock:
            self.output += text
            self.last_active_at = time.time()

    def output_since(self, cursor: int) -> tuple[str, int]:
        with self.output_lock:
            bounded_cursor = max(0, min(cursor, len(self.output)))
            chunk = self.output[bounded_cursor:]
            return chunk, len(self.output)

    def write_input(self, text: str) -> None:
        if self.process.poll() is not None:
            raise RuntimeError("session process has already exited")
        if self.process.stdin is None:
            raise RuntimeError("session stdin is unavailable")
        self.process.stdin.write(text)
        self.process.stdin.flush()
        self.last_active_at = time.time()

    def terminate(self) -> None:
        if self.process.poll() is not None:
            return
        self.process.terminate()
        try:
            self.process.wait(timeout=4)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=2)

    def is_alive(self) -> bool:
        return self.process.poll() is None


python_cli_sessions: dict[str, PythonCliSession] = {}
python_cli_sessions_lock = threading.Lock()


def python_cli_enabled_for_request(request: Request) -> bool:
    # Running lesson practice executes arbitrary Python code. Keep this local-only
    # by default; explicitly enable for remote requests via env var when desired.
    explicit_enable = os.getenv("ENABLE_PYTHON_CLI", "").strip().lower()
    if explicit_enable in {"1", "true", "yes", "on"}:
        return True

    client_host = (request.client.host if request.client else "").strip()
    return client_host in {"127.0.0.1", "::1", "localhost"}


def cleanup_python_cli_sessions() -> None:
    now = time.time()
    expired: list[PythonCliSession] = []

    with python_cli_sessions_lock:
        for session_id, session in list(python_cli_sessions.items()):
            idle_too_long = now - session.last_active_at > PYTHON_SESSION_IDLE_SECONDS
            dead_process = (not session.is_alive()) and (now - session.last_active_at > 120)
            if idle_too_long or dead_process:
                expired.append(session)
                del python_cli_sessions[session_id]

    for session in expired:
        session.terminate()


def get_python_cli_session(session_id: str) -> PythonCliSession:
    with python_cli_sessions_lock:
        session = python_cli_sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Python CLI session not found")
    return session


app = FastAPI(
    title="Interview Prep API",
    version="2.0.0",
    description="Vue + FastAPI interview preparation content service.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/stats")
def stats() -> dict[str, Any]:
    payload = load_question_bank()
    return {
        "generated_at": payload["generated_at"],
        "version": payload["version"],
        **payload["stats"],
    }


@app.get("/api/sections")
def sections(include_questions: bool = Query(True)) -> dict[str, Any]:
    payload = load_question_bank()

    if include_questions:
        return payload

    slim_sections = []
    for section in payload["sections"]:
        slim_sections.append(
            {
                "id": section["id"],
                "slug": section["slug"],
                "name": section["name"],
                "summary": section["summary"],
                "references": section["references"],
                "default_illustration": section["default_illustration"],
                "question_count": len(section["questions"]),
            }
        )

    return {
        "generated_at": payload["generated_at"],
        "version": payload["version"],
        "stats": payload["stats"],
        "sections": slim_sections,
    }


@app.get("/api/sections/{section_slug}")
def section_by_slug(section_slug: str) -> dict[str, Any]:
    payload = load_question_bank()
    for section in payload["sections"]:
        if section["slug"] == section_slug:
            return section
    raise HTTPException(status_code=404, detail="Section not found")


@app.get("/api/questions")
def questions(
    section: str | None = Query(None, description="Section slug"),
    search: str | None = Query(None, description="Full-text search"),
    limit: int = Query(500, ge=1, le=2000),
) -> dict[str, Any]:
    payload = load_question_bank()
    items = filter_questions(payload, section, search)

    return {
        "count": len(items[:limit]),
        "total_matched": len(items),
        "items": items[:limit],
    }


@app.get("/api/python-cli/status")
def python_cli_status(request: Request) -> dict[str, Any]:
    available = python_cli_enabled_for_request(request)
    return {
        "available": available,
        "module_exists": PYTHON_MODULE_DIR.exists(),
        "module_path": str(PYTHON_MODULE_DIR),
        "reason": (
            "ok"
            if available
            else "Python CLI is local-only by default. Set ENABLE_PYTHON_CLI=true to enable remotely."
        ),
    }


@app.get("/api/python-quest")
def python_quest_catalog(request: Request) -> dict[str, Any]:
    catalog = get_python_quest_catalog()
    validation_enabled = python_cli_enabled_for_request(request)
    return {
        **catalog,
        "validation_enabled": validation_enabled,
        "validation_reason": (
            "ok"
            if validation_enabled
            else "Python quest code validation is local-only by default. Set ENABLE_PYTHON_CLI=true to enable remotely."
        ),
    }


@app.post("/api/python-quest/validate")
def python_quest_validate(
    request: Request,
    payload: dict[str, Any] = Body(...),
) -> dict[str, Any]:
    if not python_cli_enabled_for_request(request):
        raise HTTPException(status_code=403, detail="Python quest validation is disabled for this client")

    lesson_slug = payload.get("lesson_slug")
    challenge_index = payload.get("challenge_index")
    code = payload.get("code", "")

    if not isinstance(lesson_slug, str) or not lesson_slug.strip():
        raise HTTPException(status_code=400, detail="lesson_slug must be a non-empty string")
    if not isinstance(challenge_index, int):
        raise HTTPException(status_code=400, detail="challenge_index must be an integer")
    if not isinstance(code, str):
        raise HTTPException(status_code=400, detail="code must be a string")

    return run_validation_subprocess(
        lesson_slug=lesson_slug.strip(),
        challenge_index=challenge_index,
        code=code,
    )


@app.post("/api/python-cli/sessions")
def create_python_cli_session(request: Request) -> dict[str, Any]:
    cleanup_python_cli_sessions()
    if not python_cli_enabled_for_request(request):
        raise HTTPException(status_code=403, detail="Python CLI is disabled for this client")
    if not PYTHON_MODULE_DIR.exists():
        raise HTTPException(status_code=500, detail=f"Python module not found at {PYTHON_MODULE_DIR}")

    session_id = uuid.uuid4().hex
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    process = subprocess.Popen(
        [sys.executable, "run.py"],
        cwd=PYTHON_MODULE_DIR,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=0,
        env=env,
    )
    session = PythonCliSession(session_id=session_id, process=process)
    session.start_reader()
    time.sleep(0.08)

    with python_cli_sessions_lock:
        python_cli_sessions[session_id] = session

    output, cursor = session.output_since(0)
    return {
        "session_id": session_id,
        "cursor": cursor,
        "output": output,
        "alive": session.is_alive(),
    }


@app.get("/api/python-cli/sessions/{session_id}/output")
def python_cli_output(
    session_id: str,
    request: Request,
    cursor: int = Query(0, ge=0),
) -> dict[str, Any]:
    if not python_cli_enabled_for_request(request):
        raise HTTPException(status_code=403, detail="Python CLI is disabled for this client")
    cleanup_python_cli_sessions()

    session = get_python_cli_session(session_id)
    output, next_cursor = session.output_since(cursor)
    return {
        "output": output,
        "cursor": next_cursor,
        "alive": session.is_alive(),
        "exit_code": session.process.poll(),
    }


@app.post("/api/python-cli/sessions/{session_id}/input")
def python_cli_input(
    session_id: str,
    request: Request,
    payload: dict[str, Any] = Body(...),
) -> dict[str, bool]:
    if not python_cli_enabled_for_request(request):
        raise HTTPException(status_code=403, detail="Python CLI is disabled for this client")
    session = get_python_cli_session(session_id)
    text_value = payload.get("text", "")
    if text_value is None:
        text_value = ""
    if not isinstance(text_value, str):
        raise HTTPException(status_code=400, detail="input text must be a string")
    text = text_value
    if not text.endswith("\n"):
        text = f"{text}\n"

    try:
        session.write_input(text)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"ok": True}


@app.delete("/api/python-cli/sessions/{session_id}")
def close_python_cli_session(session_id: str, request: Request) -> dict[str, bool]:
    if not python_cli_enabled_for_request(request):
        raise HTTPException(status_code=403, detail="Python CLI is disabled for this client")
    with python_cli_sessions_lock:
        session = python_cli_sessions.pop(session_id, None)
    if session is None:
        raise HTTPException(status_code=404, detail="Python CLI session not found")
    session.terminate()
    return {"closed": True}


@app.exception_handler(FileNotFoundError)
def data_missing_handler(_: Any, exc: FileNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": "question bank file missing",
            "detail": str(exc),
            "path": str(DATA_PATH),
        },
    )


if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
