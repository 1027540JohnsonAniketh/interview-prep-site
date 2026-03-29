from __future__ import annotations

import os
import unittest
from dataclasses import dataclass
from unittest.mock import patch

from backend.main import python_quest_catalog, python_quest_validate
from backend.python_quest import get_python_quest_catalog


@dataclass
class FakeClient:
    host: str


@dataclass
class FakeRequest:
    host: str

    @property
    def client(self) -> FakeClient:
        return FakeClient(self.host)


class PythonQuestTests(unittest.TestCase):
    def test_catalog_has_expected_lessons(self) -> None:
        catalog = get_python_quest_catalog()
        self.assertEqual(catalog["stats"]["lesson_count"], 10)
        self.assertEqual(catalog["lessons"][0]["slug"], "basics-variables-types")
        self.assertGreater(len(catalog["lessons"][0]["practice"]), 0)
        self.assertGreater(len(catalog["lessons"][0]["quiz"]), 0)

    def test_catalog_api_returns_validation_flags(self) -> None:
        payload = python_quest_catalog(FakeRequest("127.0.0.1"))
        self.assertIn("validation_enabled", payload)
        self.assertEqual(payload["stats"]["lesson_count"], 10)

    def test_validation_accepts_correct_submission(self) -> None:
        with patch.dict(os.environ, {"ENABLE_PYTHON_CLI": "true"}, clear=False):
            payload = python_quest_validate(
                FakeRequest("10.0.0.1"),
                payload={
                    "lesson_slug": "basics-variables-types",
                    "challenge_index": 0,
                    "code": 'greeting = "Hello, Python!"',
                },
            )

        self.assertTrue(payload["ok"])

    def test_validation_rejects_wrong_submission(self) -> None:
        with patch.dict(os.environ, {"ENABLE_PYTHON_CLI": "true"}, clear=False):
            payload = python_quest_validate(
                FakeRequest("10.0.0.1"),
                payload={
                    "lesson_slug": "basics-variables-types",
                    "challenge_index": 0,
                    "code": 'greeting = "Hello there"',
                },
            )

        self.assertFalse(payload["ok"])


if __name__ == "__main__":
    unittest.main()
