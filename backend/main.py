from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "backend" / "data" / "question_bank.json"
FRONTEND_DIR = BASE_DIR / "frontend"


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
