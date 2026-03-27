"""Reading and practice material for core data structures."""


def glossary() -> dict[str, str]:
    return {
        "array": "Contiguous index-based structure (Python list acts like dynamic array).",
        "set": "Unordered unique collection with fast membership checks.",
        "list": "Ordered mutable sequence in Python.",
        "linked list": "Node-based linear structure connected by pointers/references.",
        "tree": "Hierarchical node-based structure with parent-child relation.",
        "graph": "General network structure of nodes and edges.",
    }


def practice_questions() -> list[str]:
    return [
        "When should you use a set instead of a list?",
        "Why is linked-list random access slower than list indexing?",
        "What is the difference between tree and graph?",
        "How does BFS traversal work on a graph?",
        "What are trade-offs of list insertion at index 0?",
    ]

