"""Agent-focused module: how an assistant can reason about hash maps."""


def agent_study_plan() -> list[str]:
    return [
        "Step 1: Understand hash() and hashable vs unhashable objects.",
        "Step 2: Build small dict examples for create/read/update/delete.",
        "Step 3: Observe insertion order with dict and OrderedDict.",
        "Step 4: Model a custom immutable key using dataclass(frozen=True).",
        "Step 5: Validate behavior using simple assertions/tests.",
    ]


def agent_quiz_checks() -> list[tuple[str, str]]:
    return [
        ("Is Python dict ordered?", "Yes, insertion ordered in Python 3.7+."),
        ("Are lists hashable?", "No, lists are mutable and unhashable."),
        ("Why use OrderedDict?", "For extra order operations like move_to_end."),
    ]

