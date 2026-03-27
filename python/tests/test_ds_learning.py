"""Tests for ds learning package using unittest."""

import unittest

from ds_learning.agents_learning_module import agent_quiz_checks, agent_study_plan
from ds_learning.validate_module import run_all_validations


class TestDsLearning(unittest.TestCase):
    def test_all_validations_pass(self) -> None:
        results = run_all_validations()
        self.assertTrue(all(results.values()))

    def test_agent_modules_not_empty(self) -> None:
        self.assertGreaterEqual(len(agent_study_plan()), 5)
        self.assertGreaterEqual(len(agent_quiz_checks()), 3)


if __name__ == "__main__":
    unittest.main()

