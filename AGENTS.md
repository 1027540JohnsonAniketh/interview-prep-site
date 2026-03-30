# Agent Workflow

This repository is set up so a single feature request can move from implementation to GitHub push, Render deploy, and iPhone compatibility validation with minimal manual follow-up.

## Default shipping contract

For any feature request:

1. Implement the feature in the repo at `/Users/johnsonanikethnagamallah/Documents/Github/interview-prep-site`.
2. Keep the website as the source of truth for shared Quest and Lab behavior.
3. If `frontend/`, `backend/python_quest.py`, `python/`, or other shared lesson/runtime files change, rebuild the bundled iPhone web app:

   ```bash
   python3 scripts/build_offline_ios_assets.py
   ```

4. Run the shared validation suite:

   ```bash
   bash scripts/validate_feature_release.sh --skip-ios
   ```

5. On a Mac with Xcode tools installed, also run the iPhone validation path:

   ```bash
   bash scripts/validate_feature_release.sh --ios-only
   ```

6. Commit and push once validation passes unless the user explicitly asks for a branch or PR flow instead.
7. Let GitHub Actions validate and deploy:
   - pushes to `main` run CI/CD
   - Render deploys via GitHub-linked auto deploy and/or `RENDER_DEPLOY_HOOK_URL`

## iPhone parity rules

- `frontend/` is the product source of truth for the shared web experience.
- `scripts/build_offline_ios_assets.py` copies the current website bundle into `ios/PythonQuestCompanion/Resources/WebApp`.
- Shared Quest and Lab changes should be implemented in the web stack first whenever possible so they land in both the website and iPhone shell.
- Native Swift changes are allowed for shell behavior such as connection modes, fallback handling, or iPhone-specific UX.
- Web changes can appear in the installed iPhone app immediately through Auto Sync mode.
- Native Swift changes still require a new iOS build and reinstall/TestFlight distribution.

## One-prompt operator intent

When the user asks from iPhone for "implement X, validate, push, deploy, keep iPhone compatible", the expected workflow is:

1. Open or clone the public GitHub repo.
2. Implement the feature.
3. Rebuild offline iPhone assets if the shared web/runtime changed.
4. Run validation.
5. Push to GitHub.
6. Trigger deployment through the existing CI/CD path.
7. Report whether the change is:
   - a web-level change that will show up in Auto Sync mode immediately, or
   - a native iOS change that also needs a fresh app build.
