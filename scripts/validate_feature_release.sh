#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IOS_DIR="$ROOT_DIR/ios/PythonQuestCompanion"
IOS_PROJECT="$IOS_DIR/PythonQuestCompanion.xcodeproj"
IOS_PROJECT_FILE="$IOS_PROJECT/project.pbxproj"
IOS_SPEC_FILE="$IOS_DIR/project.yml"
MODE="${1:-all}"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/validate_feature_release.sh
  bash scripts/validate_feature_release.sh --skip-ios
  bash scripts/validate_feature_release.sh --ios-only
EOF
}

ensure_ios_tools() {
  if ! command -v xcodebuild >/dev/null 2>&1; then
    echo "xcodebuild is required for iOS validation." >&2
    return 1
  fi

  if [[ ! -f "$IOS_PROJECT_FILE" || "$IOS_SPEC_FILE" -nt "$IOS_PROJECT_FILE" ]]; then
    if ! command -v xcodegen >/dev/null 2>&1; then
      echo "xcodegen is required because the generated Xcode project is missing or out of date." >&2
      return 1
    fi

    (
      cd "$IOS_DIR"
      xcodegen generate
    )
  fi
}

run_shared_checks() {
  cd "$ROOT_DIR"

  python3 scripts/build_offline_ios_assets.py
  python3 -m py_compile backend/main.py backend/python_quest.py scripts/build_offline_ios_assets.py
  python3 -m unittest backend.tests.test_python_quest
  node --check frontend/app.js
  node --check frontend/offline-runtime.js
  node --check frontend/offline-python-worker.js
}

run_ios_checks() {
  ensure_ios_tools

  xcodebuild \
    -project "$IOS_PROJECT" \
    -scheme PythonQuestCompanion \
    -destination 'platform=iOS Simulator,name=iPhone 16' \
    CODE_SIGNING_ALLOWED=NO \
    build
}

case "$MODE" in
  all)
    run_shared_checks
    if command -v xcodebuild >/dev/null 2>&1; then
      run_ios_checks
    else
      echo "Skipping iOS build because Xcode tools are unavailable on this machine."
    fi
    ;;
  --skip-ios)
    run_shared_checks
    ;;
  --ios-only)
    cd "$ROOT_DIR"
    python3 scripts/build_offline_ios_assets.py
    run_ios_checks
    ;;
  *)
    usage
    exit 1
    ;;
esac
