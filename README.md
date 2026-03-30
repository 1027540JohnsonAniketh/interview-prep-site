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

## Python Interactive Lab

The app now includes a second workspace tab, **Python Interactive Lab**, which runs your existing `python/run.py` lesson CLI inside the browser.

- Start a session from the UI and send inputs exactly as you do in terminal (`1`, `L`, `P`, `Q`, `B`, `q`, etc.).
- Sessions are process-backed and auto-cleaned if idle.
- For safety, Python CLI APIs are local-only by default.

To allow remote access intentionally, set:

```bash
export ENABLE_PYTHON_CLI=true
```

## CI/CD

This repo now includes GitHub Actions in [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml).

- Pull requests run backend validation, backend tests, frontend syntax checks, and an iOS simulator build.
- Pushes to `main` run the same checks and then trigger deployment.

Render deployment is configured in two layers:

- [`render.yaml`](render.yaml) sets `autoDeployTrigger: checksPass`.
- The workflow will also call a Render deploy hook automatically if you add `RENDER_DEPLOY_HOOK_URL` as a GitHub Actions repository secret.

Recommended setup in Render:

1. Link the Render service to this GitHub repository.
2. Point it at the `main` branch.
3. Keep auto deploy enabled, ideally after CI checks pass.
4. Optionally create a Render deploy hook and store it in GitHub as `RENDER_DEPLOY_HOOK_URL`.

## One-Prompt Workflow From iPhone

The best interface for feature shipping is the ChatGPT iPhone app or browser, not Gmail.

- Use ChatGPT on iPhone as the control surface for the coding agent.
- Use Gmail only for status notifications after the Gmail connector permissions are fixed.
- Ask in one prompt for: implementation, validation, GitHub push, Render deploy, and iPhone compatibility.

Recommended prompt:

```text
Open https://github.com/1027540JohnsonAniketh/interview-prep-site, implement [feature], keep the iPhone app compatible, run the repo validation flow, push to GitHub, and deploy to Render.
```

Important behavior notes:

- Website changes should be implemented in the shared web stack so they flow into both the website and the iPhone shell.
- The iPhone app now supports an **Auto Sync** mode that uses the deployed site first and falls back to the bundled offline copy if Render is unavailable.
- Web-level changes can show up in the installed iPhone app immediately through Auto Sync.
- Native Swift changes still require a new iOS build and reinstall/TestFlight push.

For repo-local validation, use:

```bash
bash scripts/validate_feature_release.sh --skip-ios
```

On a Mac with Xcode installed, run the full suite:

```bash
bash scripts/validate_feature_release.sh
```

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
- `GET /api/python-cli/status`
- `POST /api/python-cli/sessions`
- `GET /api/python-cli/sessions/{session_id}/output?cursor=0`
- `POST /api/python-cli/sessions/{session_id}/input`
- `DELETE /api/python-cli/sessions/{session_id}`
- `GET /api/python-quest`
- `POST /api/python-quest/validate`

## iOS App

The iOS shell lives in [`ios/PythonQuestCompanion`](ios/PythonQuestCompanion).

```bash
cd /Users/johnsonanikethnagamallah/Documents/Github/interview-prep-site/ios/PythonQuestCompanion
xcodegen generate
open PythonQuestCompanion.xcodeproj
```

Notes:

- The recommended iPhone setting is **Auto Sync**.
- The simulator can use `http://localhost:8000`.
- A physical iPhone cannot use `localhost` for your Mac-hosted server. Use the deployed Render URL or your Mac's LAN IP instead.
- If the deployed site is unavailable, the app falls back to the bundled on-device copy automatically while in Auto Sync mode.
