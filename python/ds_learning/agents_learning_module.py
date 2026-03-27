"""Agent-style learning flow for core data structures."""


def agent_study_plan() -> list[str]:
    return [
        "Step 1: Master list and array-style operations with complexity notes.",
        "Step 2: Learn set operations for dedupe and membership checks.",
        "Step 3: Build and traverse a simple linked list.",
        "Step 4: Understand tree traversal concepts and node relationships.",
        "Step 5: Implement graph traversal (BFS/DFS) on adjacency lists.",
    ]


def agent_quiz_checks() -> list[tuple[str, str]]:
    return [
        ("Is Python list linked list?", "No, Python list is dynamic array-like."),
        ("Can set keep duplicates?", "No, duplicates are removed."),
        ("Is graph always acyclic?", "No, graphs can have cycles."),
    ]

