# Interview Prep Site (Vue + FastAPI)

This project now runs as a Vue frontend served by a FastAPI backend.

## What changed

- Migrated UI to Vue 3 (`frontend/`)
- Added FastAPI backend (`backend/main.py`)
- Added normalized question bank (`backend/data/question_bank.json`)
- Enriched all 144 questions with:
  - core answer
  - deep-dive explanation
  - interview notes
  - references
  - internet illustration metadata
- Added Playwright-captured screenshots in `frontend/illustrations/`

## Run locally

```bash
cd /Users/johnsonanikethnagamallah/Documents/Github/interview-prep-site
python3 -m pip install -r backend/requirements.txt
python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Open: `http://localhost:8000`

## Rebuild question bank from original source

The enrichment source of truth is still your original `index.html` + `generated-draft-answers.js`.

```bash
node scripts/build_question_bank.mjs .
python3 scripts/enrich_from_vault.py --root . --vault /Users/johnsonanikethnagamallah/Documents/vault/Technical
```

## API endpoints

- `GET /api/health`
- `GET /api/stats`
- `GET /api/sections`
- `GET /api/sections/{section_slug}`
- `GET /api/questions?search=redis&section=redis&limit=20`
