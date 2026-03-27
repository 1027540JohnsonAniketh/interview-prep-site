"""Lesson 4: Data Structures — lists, dicts, sets, tuples, slicing."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.interactive import (
    print_header, print_subheader, print_code_and_output,
    print_concept, pause, run_quiz, run_coding_challenge, lesson_menu,
)


def learn():
    print_header("Learn: Data Structures")

    # --- Lists ---
    print_subheader("Lists — Ordered, Mutable Collections")
    print_concept(
        "Lists",
        "Lists are the workhorse of Python. They're ordered, mutable (you can change them), "
        "and can hold any mix of types. Created with square brackets [].",
    )
    print_code_and_output(
        'nums = [10, 20, 30, 40, 50]\n\n# Access by index (0-based)\nprint(nums[0])     # 10\nprint(nums[-1])    # 50 (last item)\n\n# Modify\nnums[1] = 99\nprint(nums)        # [10, 99, 30, 40, 50]\n\n# Common methods\nnums.append(60)    # Add to end\nnums.insert(0, 5)  # Insert at index 0\nnums.pop()         # Remove last\nprint(len(nums))   # Length',
        "10\n50\n[10, 99, 30, 40, 50]\n6",
    )
    pause()

    # --- Slicing ---
    print_subheader("Slicing — Extracting Parts of a List")
    print_concept(
        "Slicing syntax: list[start:stop:step]",
        "start is inclusive, stop is exclusive. Omit start for beginning, "
        "omit stop for end. Negative indices count from the end.",
    )
    print_code_and_output(
        'nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]\n\nprint(nums[2:5])     # [2, 3, 4]\nprint(nums[:3])      # [0, 1, 2]\nprint(nums[7:])      # [7, 8, 9]\nprint(nums[::2])     # [0, 2, 4, 6, 8] — every 2nd\nprint(nums[::-1])    # [9, 8, 7, ...] — reversed!',
        "[2, 3, 4]\n[0, 1, 2]\n[7, 8, 9]\n[0, 2, 4, 6, 8]\n[9, 8, 7, 6, 5, 4, 3, 2, 1, 0]",
    )
    pause()

    # --- Tuples ---
    print_subheader("Tuples — Ordered, Immutable Collections")
    print_concept(
        "Tuples",
        "Like lists but IMMUTABLE — once created, you can't change them. "
        "Use tuples for data that shouldn't change (coordinates, RGB colors, etc).",
    )
    print_code_and_output(
        'point = (3, 4)\nprint(point[0])      # 3\n\n# Unpacking\nx, y = point\nprint(f"x={x}, y={y}")\n\n# Tuples as dict keys (lists can\'t be!)\nlocations = {(0, 0): "origin", (1, 2): "point A"}\nprint(locations[(0, 0)])',
        "3\nx=3, y=4\norigin",
    )
    pause()

    # --- Dictionaries ---
    print_subheader("Dictionaries — Key-Value Pairs")
    print_concept(
        "Dictionaries",
        "Store data as key-value pairs. Keys must be immutable (strings, numbers, tuples). "
        "O(1) average lookup time — very fast!",
    )
    print_code_and_output(
        'person = {"name": "Aniketh", "age": 25, "role": "Engineer"}\n\nprint(person["name"])          # Aniketh\nperson["city"] = "NYC"         # Add new key\nprint(person.get("salary", 0)) # 0 (safe access with default)\n\n# Iterate\nfor key, value in person.items():\n    print(f"  {key}: {value}")',
        "Aniketh\n0\n  name: Aniketh\n  age: 25\n  role: Engineer\n  city: NYC",
    )
    pause()

    # --- Sets ---
    print_subheader("Sets — Unordered, Unique Elements")
    print_concept(
        "Sets",
        "Sets automatically remove duplicates. Great for membership testing (O(1)), "
        "and set operations like union, intersection, difference.",
    )
    print_code_and_output(
        'nums = {1, 2, 3, 2, 1}\nprint(nums)          # {1, 2, 3} — duplicates removed\n\na = {1, 2, 3, 4}\nb = {3, 4, 5, 6}\nprint(a & b)         # Intersection: {3, 4}\nprint(a | b)         # Union: {1, 2, 3, 4, 5, 6}\nprint(a - b)         # Difference: {1, 2}\nprint(3 in a)        # Membership: True',
        "{1, 2, 3}\n{3, 4}\n{1, 2, 3, 4, 5, 6}\n{1, 2}\nTrue",
    )
    pause()

    # --- When to use what ---
    print_subheader("When to Use What?")
    print("  | Structure  | Ordered? | Mutable? | Duplicates? | Best for              |")
    print("  |-----------|----------|----------|-------------|----------------------|")
    print("  | list      | Yes      | Yes      | Yes         | General collections  |")
    print("  | tuple     | Yes      | No       | Yes         | Fixed data, dict keys|")
    print("  | dict      | Yes*     | Yes      | Keys: No    | Key-value lookups    |")
    print("  | set       | No       | Yes      | No          | Uniqueness, membership|")
    print("  * Dicts preserve insertion order since Python 3.7")
    print()


def practice():
    challenges = [
        {
            "prompt": "Create a list 'squares' containing squares of 1 through 5: [1, 4, 9, 16, 25]",
            "hint": "Use a loop or list comprehension",
            "validator": lambda ns, code: ns.get("squares") == [1, 4, 9, 16, 25],
            "solution": "squares = [i**2 for i in range(1, 6)]",
        },
        {
            "prompt": "Create a dict 'word_lengths' mapping each word in ['hello', 'world', 'python'] to its length.",
            "hint": "Use a loop or dict comprehension: {word: len(word) for ...}",
            "validator": lambda ns, code: ns.get("word_lengths") == {"hello": 5, "world": 5, "python": 6},
            "solution": 'word_lengths = {w: len(w) for w in ["hello", "world", "python"]}',
        },
        {
            "prompt": "Given nums = [1, 2, 2, 3, 3, 3, 4], create 'unique_nums' as a sorted list of unique values.",
            "hint": "Convert to set, then back to sorted list",
            "validator": lambda ns, code: ns.get("unique_nums") == [1, 2, 3, 4],
            "solution": "nums = [1, 2, 2, 3, 3, 3, 4]\nunique_nums = sorted(set(nums))",
        },
        {
            "prompt": "Create a variable 'reversed_list' that is [1,2,3,4,5] reversed using slicing.",
            "hint": "Use [::-1]",
            "validator": lambda ns, code: ns.get("reversed_list") == [5, 4, 3, 2, 1] and "::" in code,
            "solution": "reversed_list = [1, 2, 3, 4, 5][::-1]",
        },
    ]
    run_coding_challenge(challenges)


def quiz():
    questions = [
        {
            "question": "What does [1,2,3][1:] return?",
            "options": ["[1]", "[2, 3]", "[1, 2]", "[1, 2, 3]"],
            "answer": 1,
        },
        {
            "question": "Which data structure does NOT allow duplicates?",
            "options": ["list", "tuple", "set", "dict values"],
            "answer": 2,
        },
        {
            "question": "What is the time complexity of 'x in my_set'?",
            "options": ["O(n)", "O(1)", "O(log n)", "O(n^2)"],
            "answer": 1,
            "explanation": "Sets use hash tables, so membership testing is O(1) on average.",
        },
        {
            "question": "Can a list be used as a dictionary key?",
            "options": ["Yes", "No", "Only if it's empty", "Only with strings inside"],
            "answer": 1,
            "explanation": "Lists are mutable, so they can't be hashed. Use tuples instead.",
        },
        {
            "question": "What does dict.get('key', 'default') do if 'key' doesn't exist?",
            "options": ["Raises KeyError", "Returns None", "Returns 'default'", "Adds the key"],
            "answer": 2,
            "explanation": ".get() returns the default value instead of raising an error.",
        },
    ]
    run_quiz(questions)


def main():
    lesson_menu("Lesson 4: Data Structures", learn, practice, quiz)


if __name__ == "__main__":
    main()
