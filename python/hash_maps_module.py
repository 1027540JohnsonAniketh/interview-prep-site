"""Compatibility entrypoint that delegates to the new package modules."""

from hash_learning.agents_learning_module import agent_study_plan
from hash_learning.learning_module import (
    hash_function_notes,
    hash_map_notes,
    linked_hash_map_notes,
    map_notes,
)
from hash_learning.reading_module import practice_questions
from hash_learning.validate_module import run_all_validations


def print_section(title: str, lines: list[str]) -> None:
    print(title)
    for line in lines:
        print(f"- {line}")
    print()


if __name__ == "__main__":
    print_section("=== 1) Hash Function Basics ===", hash_function_notes())
    print_section("=== 2) Map in Python ===", map_notes())
    print_section("=== 3) Hash Map in Python ===", hash_map_notes())
    print_section("=== 4) Linked Hash Map Concept ===", linked_hash_map_notes())
    print_section("=== 5) Agent Study Plan ===", agent_study_plan())
    print_section("=== Practice Questions ===", practice_questions())
    print("Validation results:", run_all_validations())
