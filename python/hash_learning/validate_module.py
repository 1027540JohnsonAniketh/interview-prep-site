"""Validation helpers for hash-learning modules."""

try:
    from hash_learning.learning_module import (
        custom_key_demo,
        hash_function_notes,
        hash_map_notes,
        insertion_order_demo,
        linked_hash_map_notes,
        map_notes,
    )
    from hash_learning.reading_module import glossary, practice_questions
except ModuleNotFoundError:
    # Allows direct script execution: python3 hash_learning/validate_module.py
    from learning_module import (  # type: ignore[no-redef]
        custom_key_demo,
        hash_function_notes,
        hash_map_notes,
        insertion_order_demo,
        linked_hash_map_notes,
        map_notes,
    )
    from reading_module import glossary, practice_questions  # type: ignore[no-redef]


def validate_learning_content() -> bool:
    if len(hash_function_notes()) < 3:
        return False
    if len(map_notes()) < 2:
        return False
    if len(hash_map_notes()) < 2:
        return False
    if len(linked_hash_map_notes()) < 2:
        return False
    return True


def validate_examples() -> bool:
    normal_order, ordered_after_move = insertion_order_demo()
    if normal_order != ["first", "second", "third"]:
        return False
    if ordered_after_move != ["second", "third", "first"]:
        return False

    balances = custom_key_demo()
    if len(balances) != 2:
        return False
    return True


def validate_reading_material() -> bool:
    g = glossary()
    q = practice_questions()
    required_terms = {"map", "hash function", "hash map", "collision"}
    if not required_terms.issubset(g.keys()):
        return False
    if len(q) < 4:
        return False
    return True


def run_all_validations() -> dict[str, bool]:
    return {
        "learning_content": validate_learning_content(),
        "examples": validate_examples(),
        "reading_material": validate_reading_material(),
    }


if __name__ == "__main__":
    results = run_all_validations()
    print("Validation results:", results)
    print("All passed:", all(results.values()))

