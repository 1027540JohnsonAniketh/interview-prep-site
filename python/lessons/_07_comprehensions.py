"""Lesson 7: Comprehensions & Generators."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.interactive import (
    print_header, print_subheader, print_code_and_output,
    print_concept, pause, run_quiz, run_coding_challenge, lesson_menu,
)


def learn():
    print_header("Learn: Comprehensions & Generators")

    print_concept(
        "Comprehensions",
        "Comprehensions are Python's elegant, concise syntax for creating "
        "collections. They replace multi-line for loops with a single readable line. "
        "Python has list, dict, set, and generator comprehensions.",
    )

    # --- List comprehension ---
    print_subheader("List Comprehensions")
    print_code_and_output(
        '# Without comprehension\nsquares = []\nfor x in range(6):\n    squares.append(x ** 2)\nprint(squares)\n\n# With comprehension — same result, one line\nsquares = [x ** 2 for x in range(6)]\nprint(squares)',
        "[0, 1, 4, 9, 16, 25]\n[0, 1, 4, 9, 16, 25]",
    )
    pause()

    # --- With filter ---
    print_subheader("Comprehensions with Conditions")
    print_code_and_output(
        '# Only even squares\neven_squares = [x**2 for x in range(10) if x % 2 == 0]\nprint(even_squares)\n\n# if-else inside the expression (not the filter)\nlabels = ["even" if x % 2 == 0 else "odd" for x in range(5)]\nprint(labels)',
        "[0, 4, 16, 36, 64]\n['even', 'odd', 'even', 'odd', 'even']",
    )
    print_concept(
        "if position matters!",
        "[expr for x in seq if cond] — filter (skip items)\n"
        "  [expr_if_true if cond else expr_if_false for x in seq] — transform all items",
    )
    pause()

    # --- Dict comprehension ---
    print_subheader("Dict Comprehensions")
    print_code_and_output(
        'words = ["hello", "world", "python"]\nword_lens = {w: len(w) for w in words}\nprint(word_lens)\n\n# Swap keys and values\noriginal = {"a": 1, "b": 2, "c": 3}\nswapped = {v: k for k, v in original.items()}\nprint(swapped)',
        "{'hello': 5, 'world': 5, 'python': 6}\n{1: 'a', 2: 'b', 3: 'c'}",
    )
    pause()

    # --- Set comprehension ---
    print_subheader("Set Comprehensions")
    print_code_and_output(
        '# Get unique first letters\nnames = ["Alice", "Bob", "Charlie", "Anna", "Brian"]\nfirst_letters = {name[0] for name in names}\nprint(first_letters)  # Duplicates removed automatically',
        "{'A', 'B', 'C'}",
    )
    pause()

    # --- Nested comprehension ---
    print_subheader("Nested Comprehensions")
    print_code_and_output(
        '# Flatten a 2D list\nmatrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]\nflat = [num for row in matrix for num in row]\nprint(flat)\n\n# Create a multiplication table\ntable = {(i, j): i * j for i in range(1, 4) for j in range(1, 4)}\nfor (i, j), product in table.items():\n    print(f"  {i} x {j} = {product}")',
        "[1, 2, 3, 4, 5, 6, 7, 8, 9]\n  1 x 1 = 1\n  1 x 2 = 2\n  ... (etc)",
    )
    pause()

    # --- Generators ---
    print_subheader("Generators — Lazy Evaluation")
    print_concept(
        "Generators",
        "Generators produce values one at a time, on demand. They DON'T store "
        "everything in memory like lists. Use () instead of [] for generator expressions, "
        "or 'yield' keyword in functions.",
    )
    print_code_and_output(
        '# Generator expression — uses () not []\ngen = (x**2 for x in range(5))\nprint(type(gen))        # <class \'generator\'>\nprint(next(gen))        # 0\nprint(next(gen))        # 1\nprint(list(gen))        # [4, 9, 16] — remaining items\n\n# Generator function with yield\ndef countdown(n):\n    while n > 0:\n        yield n\n        n -= 1\n\nfor num in countdown(3):\n    print(num, end=" ")',
        "<class 'generator'>\n0\n1\n[4, 9, 16]\n3 2 1",
    )
    print_concept(
        "When to use generators?",
        "When dealing with large datasets or infinite sequences. "
        "A list of 1 billion numbers = gigabytes of RAM. "
        "A generator of 1 billion numbers = almost zero RAM.",
    )
    print()


def practice():
    challenges = [
        {
            "prompt": "Create 'evens' — a list of even numbers from 1 to 20 using a list comprehension.",
            "hint": "[x for x in range(...) if x % 2 == 0]",
            "validator": lambda ns, code: ns.get("evens") == [2, 4, 6, 8, 10, 12, 14, 16, 18, 20] and "for" in code and "[" in code,
            "solution": "evens = [x for x in range(1, 21) if x % 2 == 0]",
        },
        {
            "prompt": "Create 'flat' — flatten [[1,2],[3,4],[5,6]] into [1,2,3,4,5,6] using a comprehension.",
            "hint": "Use a nested comprehension: [item for sublist in ... for item in sublist]",
            "validator": lambda ns, code: ns.get("flat") == [1, 2, 3, 4, 5, 6],
            "solution": "flat = [x for sub in [[1,2],[3,4],[5,6]] for x in sub]",
        },
        {
            "prompt": "Create 'squared_dict' — {1: 1, 2: 4, 3: 9, 4: 16, 5: 25} using a dict comprehension.",
            "hint": "{x: x**2 for x in range(...)}",
            "validator": lambda ns, code: ns.get("squared_dict") == {1: 1, 2: 4, 3: 9, 4: 16, 5: 25},
            "solution": "squared_dict = {x: x**2 for x in range(1, 6)}",
        },
        {
            "prompt": "Create a generator function 'fibonacci' that yields Fibonacci numbers indefinitely.\nIt should work like: gen = fibonacci(); next(gen) -> 0, next(gen) -> 1, next(gen) -> 1, next(gen) -> 2...",
            "hint": "Use a, b = 0, 1 and while True: yield a; a, b = b, a + b",
            "validator": lambda ns, code: (
                callable(ns.get("fibonacci"))
                and "yield" in code
                and (lambda g: [next(g) for _ in range(6)])(ns["fibonacci"]()) == [0, 1, 1, 2, 3, 5]
            ),
            "solution": "def fibonacci():\n    a, b = 0, 1\n    while True:\n        yield a\n        a, b = b, a + b",
        },
    ]
    run_coding_challenge(challenges)


def quiz():
    questions = [
        {
            "question": "What is the difference between [x for x in range(5)] and (x for x in range(5))?",
            "options": ["No difference", "[] creates a list, () creates a generator", "() is invalid syntax", "[] is slower"],
            "answer": 1,
        },
        {
            "question": "What does the 'yield' keyword do?",
            "options": ["Returns a value and exits", "Returns a value and pauses", "Raises an error", "Prints a value"],
            "answer": 1,
            "explanation": "yield returns a value but remembers where it left off, resuming from there on next().",
        },
        {
            "question": "What is [x for x in range(10) if x > 5]?",
            "options": ["[5, 6, 7, 8, 9]", "[6, 7, 8, 9]", "[0, 1, 2, 3, 4, 5]", "[True, True, True, True]"],
            "answer": 1,
        },
        {
            "question": "Why are generators memory-efficient?",
            "options": [
                "They compress data",
                "They compute values on-demand, not all at once",
                "They use C extensions",
                "They delete values after use",
            ],
            "answer": 1,
        },
        {
            "question": "What does {x for x in [1,1,2,2,3]} produce?",
            "options": ["[1, 1, 2, 2, 3]", "{1, 2, 3}", "{1: 1, 2: 2, 3: 3}", "Error"],
            "answer": 1,
            "explanation": "{} with single expression = set comprehension. Duplicates are removed.",
        },
    ]
    run_quiz(questions)


def main():
    lesson_menu("Lesson 7: Comprehensions & Generators", learn, practice, quiz)


if __name__ == "__main__":
    main()
