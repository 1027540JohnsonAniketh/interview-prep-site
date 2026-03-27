"""Entrypoint for array, set, list, linked list, tree, and graph learning."""

from ds_learning.agents_learning_module import agent_study_plan
from ds_learning.learning_module import (
    array_notes,
    graph_notes,
    linked_list_notes,
    list_notes,
    set_notes,
    tree_notes,
)
from ds_learning.reading_module import practice_questions
from ds_learning.validate_module import run_all_validations


def print_section(title: str, lines: list[str]) -> None:
    print(title)
    for line in lines:
        print(f"- {line}")
    print()


if __name__ == "__main__":
    print_section("=== 1) Array in Python ===", array_notes())
    print_section("=== 2) Set in Python ===", set_notes())
    print_section("=== 3) List in Python ===", list_notes())
    print_section("=== 4) Linked List Concept ===", linked_list_notes())
    print_section("=== 5) Tree Basics ===", tree_notes())
    print_section("=== 6) Graph Basics ===", graph_notes())
    print_section("=== 7) Agent Study Plan ===", agent_study_plan())
    print_section("=== Practice Questions ===", practice_questions())
    print("Validation results:", run_all_validations())

