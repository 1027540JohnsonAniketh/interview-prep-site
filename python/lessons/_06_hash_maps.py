"""Lesson 6: Hash Maps — hash functions, dict internals, OrderedDict, custom keys."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.interactive import (
    print_header, print_subheader, print_code_and_output,
    print_concept, pause, run_quiz, run_coding_challenge, lesson_menu,
)


def learn():
    print_header("Learn: Hash Maps & Dictionaries Deep Dive")

    print_concept(
        "What is a Hash Map?",
        "A hash map (dict in Python) stores key-value pairs using a hash function "
        "to compute an index into an internal array. This gives O(1) average lookup, "
        "insert, and delete — much faster than searching a list.",
    )

    # --- How hashing works ---
    print_subheader("How hash() Works in Python")
    print_code_and_output(
        'print(hash("hello"))      # Some integer\nprint(hash(42))           # 42 (ints hash to themselves for small values)\nprint(hash((1, 2, 3)))    # Tuples are hashable\n\n# Lists are NOT hashable (mutable = unhashable)\n# hash([1, 2, 3])  # TypeError!',
        "hash values vary by run, but you'll see integers",
    )
    print_concept(
        "Hashable = Immutable",
        "Only immutable objects can be hashed: str, int, float, tuple, frozenset. "
        "Mutable objects (list, dict, set) CANNOT be dictionary keys.",
    )
    pause()

    # --- Dict internals ---
    print_subheader("How Python Dicts Work Internally")
    print_concept(
        "Internal structure",
        "Python's dict uses an open-addressing hash table. When you do d['key'], "
        "Python: (1) computes hash('key'), (2) uses the hash to find a slot in "
        "an internal array, (3) handles collisions by probing nearby slots. "
        "Since Python 3.7, dicts preserve insertion order.",
    )
    print_code_and_output(
        '# Building a dict step by step\nd = {}\nd["name"] = "Aniketh"  # hash("name") -> slot -> store\nd["age"] = 25          # hash("age") -> slot -> store\nd["role"] = "Engineer" # hash("role") -> slot -> store\n\n# All O(1) lookups\nprint(d["name"])   # Direct hash lookup, no scanning\nprint(len(d))      # 3',
        "Aniketh\n3",
    )
    pause()

    # --- Collisions ---
    print_subheader("Hash Collisions")
    print_concept(
        "Collisions",
        "When two different keys hash to the same slot, it's a collision. "
        "Python handles this with open addressing (probing the next available slot). "
        "Good hash functions minimize collisions.",
    )
    print_code_and_output(
        '# Python handles collisions transparently\n# Even if two keys collide, both are stored correctly\nd = {}\nfor i in range(1000):\n    d[f"key_{i}"] = i\nprint(f"Stored {len(d)} items without any issues")\nprint(f"Lookup: d[\'key_500\'] = {d[\'key_500\']}")',
        "Stored 1000 items without any issues\nLookup: d['key_500'] = 500",
    )
    pause()

    # --- OrderedDict ---
    print_subheader("OrderedDict vs Regular Dict")
    print_concept(
        "OrderedDict",
        "Since Python 3.7, regular dicts preserve insertion order. So when do you "
        "need OrderedDict? Two cases: (1) when equality comparison should consider "
        "order, (2) when you need move_to_end().",
    )
    print_code_and_output(
        'from collections import OrderedDict\n\n# Regular dicts: order doesn\'t affect equality\nd1 = {"a": 1, "b": 2}\nd2 = {"b": 2, "a": 1}\nprint(f"Regular dicts equal? {d1 == d2}")  # True\n\n# OrderedDicts: order DOES affect equality\nod1 = OrderedDict([("a", 1), ("b", 2)])\nod2 = OrderedDict([("b", 2), ("a", 1)])\nprint(f"OrderedDicts equal? {od1 == od2}")  # False\n\n# move_to_end is useful for LRU caches\nod1.move_to_end("a")\nprint(list(od1.keys()))  # [\'b\', \'a\']',
        "Regular dicts equal? True\nOrderedDicts equal? False\n['b', 'a']",
    )
    pause()

    # --- Custom hashable keys ---
    print_subheader("Custom Hashable Objects as Dict Keys")
    print_code_and_output(
        'from dataclasses import dataclass\n\n@dataclass(frozen=True)  # frozen = immutable = hashable\nclass Coordinate:\n    x: float\n    y: float\n\n# Now we can use Coordinate as a dict key!\nlocations = {\n    Coordinate(0, 0): "Origin",\n    Coordinate(40.7, -74.0): "NYC",\n    Coordinate(51.5, -0.1): "London",\n}\n\nprint(locations[Coordinate(40.7, -74.0)])\nprint(hash(Coordinate(0, 0)))',
        "NYC\n(some hash integer)",
    )
    pause()

    # --- defaultdict and Counter ---
    print_subheader("Bonus: defaultdict and Counter")
    print_code_and_output(
        'from collections import defaultdict, Counter\n\n# defaultdict: auto-creates missing keys\nword_count = defaultdict(int)  # default value: 0\nfor word in "the cat sat on the mat".split():\n    word_count[word] += 1\nprint(dict(word_count))\n\n# Counter: even easier for counting\ncounts = Counter("the cat sat on the mat".split())\nprint(counts.most_common(2))',
        "{'the': 2, 'cat': 1, 'sat': 1, 'on': 1, 'mat': 1}\n[('the', 2), ('cat', 1)]",
    )
    print()


def practice():
    challenges = [
        {
            "prompt": "Create a dict 'char_count' that counts how many times each character appears in 'mississippi'.",
            "hint": "Loop through the string, use dict.get(char, 0) + 1 or defaultdict(int)",
            "validator": lambda ns, code: (
                ns.get("char_count", {}).get("s", 0) == 4
                and ns.get("char_count", {}).get("i", 0) == 4
                and ns.get("char_count", {}).get("p", 0) == 2
            ),
            "solution": "char_count = {}\nfor c in 'mississippi':\n    char_count[c] = char_count.get(c, 0) + 1",
        },
        {
            "prompt": "Create a dict 'inverted' that swaps keys and values of {'a': 1, 'b': 2, 'c': 3}.",
            "hint": "Use a dict comprehension: {v: k for k, v in ...}",
            "validator": lambda ns, code: ns.get("inverted") == {1: "a", 2: "b", 3: "c"},
            "solution": "inverted = {v: k for k, v in {'a': 1, 'b': 2, 'c': 3}.items()}",
        },
        {
            "prompt": "Using Counter from collections, find the 'most_common_word' in: 'to be or not to be that is the question to be'.",
            "hint": "Counter(words).most_common(1)[0][0]",
            "validator": lambda ns, code: ns.get("most_common_word") in ("to", "be"),
            "solution": "from collections import Counter\nwords = 'to be or not to be that is the question to be'.split()\nmost_common_word = Counter(words).most_common(1)[0][0]",
        },
    ]
    run_coding_challenge(challenges)


def quiz():
    questions = [
        {
            "question": "Why can't lists be dictionary keys?",
            "options": ["Too slow", "They're mutable (unhashable)", "They're too large", "Python doesn't support it yet"],
            "answer": 1,
        },
        {
            "question": "What is the average time complexity of dict lookup?",
            "options": ["O(n)", "O(log n)", "O(1)", "O(n^2)"],
            "answer": 2,
        },
        {
            "question": "What makes a @dataclass(frozen=True) special?",
            "options": [
                "It runs faster",
                "It's immutable and hashable",
                "It uses less memory",
                "It can't have methods",
            ],
            "answer": 1,
        },
        {
            "question": "What does defaultdict(list) do for missing keys?",
            "options": ["Raises KeyError", "Returns None", "Creates an empty list", "Returns 0"],
            "answer": 2,
        },
        {
            "question": "When is OrderedDict still useful over regular dict?",
            "options": [
                "Always — it's faster",
                "When order matters for equality comparison",
                "For large dictionaries",
                "Never — regular dict replaced it completely",
            ],
            "answer": 1,
        },
    ]
    run_quiz(questions)


def main():
    lesson_menu("Lesson 6: Hash Maps", learn, practice, quiz)


if __name__ == "__main__":
    main()
