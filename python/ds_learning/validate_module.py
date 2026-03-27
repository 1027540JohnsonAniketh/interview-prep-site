"""Validation helpers for ds learning modules."""

try:
    from ds_learning.learning_module import (
        array_notes,
        bfs,
        build_linked_list,
        graph_notes,
        linked_list_notes,
        linked_list_to_list,
        list_notes,
        set_notes,
        tree_notes,
    )
    from ds_learning.reading_module import glossary, practice_questions
except ModuleNotFoundError:
    # Allows direct run: python3 ds_learning/validate_module.py
    from learning_module import (  # type: ignore[no-redef]
        array_notes,
        bfs,
        build_linked_list,
        graph_notes,
        linked_list_notes,
        linked_list_to_list,
        list_notes,
        set_notes,
        tree_notes,
    )
    from reading_module import glossary, practice_questions  # type: ignore[no-redef]


def validate_learning_content() -> bool:
    checks = [
        len(array_notes()) >= 3,
        len(set_notes()) >= 3,
        len(list_notes()) >= 3,
        len(linked_list_notes()) >= 3,
        len(tree_notes()) >= 3,
        len(graph_notes()) >= 3,
    ]
    return all(checks)


def validate_linked_list_demo() -> bool:
    head = build_linked_list([1, 2, 3, 4])
    return linked_list_to_list(head) == [1, 2, 3, 4]


def validate_graph_demo() -> bool:
    graph = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": ["E"],
        "D": [],
        "E": [],
    }
    return bfs(graph, "A") == ["A", "B", "C", "D", "E"]


def validate_reading_material() -> bool:
    terms = glossary()
    questions = practice_questions()
    required = {"array", "set", "list", "linked list", "tree", "graph"}
    return required.issubset(terms.keys()) and len(questions) >= 5


def run_all_validations() -> dict[str, bool]:
    return {
        "learning_content": validate_learning_content(),
        "linked_list_demo": validate_linked_list_demo(),
        "graph_demo": validate_graph_demo(),
        "reading_material": validate_reading_material(),
    }


if __name__ == "__main__":
    results = run_all_validations()
    print("Validation results:", results)
    print("All passed:", all(results.values()))

