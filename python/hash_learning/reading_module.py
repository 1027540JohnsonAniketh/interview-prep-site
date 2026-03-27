"""Reading/practice prompts for self-study."""


def glossary() -> dict[str, str]:
    return {
        "map": "A data structure that stores key-value pairs.",
        "hash function": "A function that turns data into hash codes.",
        "hash map": "A map implemented using a hash table.",
        "collision": "When two different keys map to same bucket/index.",
        "linked hash map": (
            "Hash map that preserves predictable iteration order "
            "(Python dict already does insertion order)."
        ),
    }


def practice_questions() -> list[str]:
    return [
        "Why are list objects invalid as dict keys?",
        "What is the average lookup complexity in a Python dict?",
        "When would you prefer OrderedDict over dict?",
        "What is a hash collision and how is it handled conceptually?",
        "How does immutability relate to hashable keys?",
    ]

