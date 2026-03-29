self.__pythonRuntimePromise = null;

function pyodideIndexURL() {
  return new URL("./vendor/pyodide/", self.location.href).toString();
}

async function getPyodideInstance() {
  if (!self.__pythonRuntimePromise) {
    importScripts(new URL("./vendor/pyodide/pyodide.js", self.location.href).toString());
    self.__pythonRuntimePromise = loadPyodide({
      indexURL: pyodideIndexURL(),
    });
  }

  return self.__pythonRuntimePromise;
}

async function validateChallenge(payload) {
  const pyodide = await getPyodideInstance();
  const script = `
import contextlib
import io
import json
import os
import shutil
import tempfile

lesson_slug = ${JSON.stringify(payload.lessonSlug)}
challenge = json.loads(${JSON.stringify(JSON.stringify(payload.challenge))})
code = ${JSON.stringify(payload.code)}
workspace = tempfile.mkdtemp(prefix="python_quest_")
stdout = io.StringIO()
result = {
    "ok": False,
    "message": "Validation failed before execution began.",
    "hint": challenge.get("hint", ""),
    "stdout": "",
}

try:
    namespace = {}
    os.chdir(workspace)

    try:
        with contextlib.redirect_stdout(stdout):
            exec(compile(code, f"<python-quest:{lesson_slug}>", "exec"), namespace, namespace)
    except Exception as exc:
        result = {
            "ok": False,
            "message": f"{type(exc).__name__}: {exc}",
            "hint": challenge.get("hint", ""),
            "stdout": stdout.getvalue(),
        }
    else:
        try:
            validator = eval(challenge.get("validator_source", ""))
            passed = bool(validator(namespace, code))
            result = {
                "ok": passed,
                "message": (
                    "Challenge cleared. Your spell matched the lesson goal."
                    if passed
                    else "Close, but the lesson goal is not satisfied yet."
                ),
                "hint": challenge.get("hint", ""),
                "stdout": stdout.getvalue(),
            }
        except Exception as exc:
            result = {
                "ok": False,
                "message": f"Validation error: {type(exc).__name__}: {exc}",
                "hint": challenge.get("hint", ""),
                "stdout": stdout.getvalue(),
            }
finally:
    try:
        os.chdir("/")
    except Exception:
        pass
    shutil.rmtree(workspace, ignore_errors=True)

json.dumps(result)
  `;

  const output = await pyodide.runPythonAsync(script);
  return JSON.parse(output);
}

self.onmessage = async (event) => {
  const { id, type, payload } = event.data || {};

  try {
    if (type === "validate") {
      const result = await validateChallenge(payload);
      self.postMessage({ id, ok: true, payload: result });
      return;
    }

    throw new Error(`Unsupported worker request: ${type}`);
  } catch (error) {
    self.postMessage({
      id,
      ok: false,
      error: error instanceof Error ? error.message : String(error),
    });
  }
};
