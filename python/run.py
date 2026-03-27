#!/usr/bin/env python3
"""Interactive Python Learning — Main Menu."""

import sys
import os

# Ensure imports work from this directory
sys.path.insert(0, os.path.dirname(__file__))

from lessons import (
    _01_basics,
    _02_control_flow,
    _03_functions,
    _04_data_structures,
    _05_oop,
    _06_hash_maps,
    _07_comprehensions,
    _08_error_handling,
    _09_file_io,
    _10_decorators,
)

LESSONS = [
    ("Basics (Variables & Types)", _01_basics),
    ("Control Flow (if/else, loops)", _02_control_flow),
    ("Functions (def, *args, lambda)", _03_functions),
    ("Data Structures (list, dict, set)", _04_data_structures),
    ("OOP (classes, inheritance)", _05_oop),
    ("Hash Maps (hashing, dicts deep dive)", _06_hash_maps),
    ("Comprehensions & Generators", _07_comprehensions),
    ("Error Handling (try/except)", _08_error_handling),
    ("File I/O (files, JSON, CSV)", _09_file_io),
    ("Decorators & Closures", _10_decorators),
]


def main():
    while True:
        print("\n" + "=" * 60)
        print("  Python Interactive Learning")
        print("=" * 60)
        print()

        for i, (name, _) in enumerate(LESSONS, 1):
            progress = "  "
            print(f"  {i:2d}. {progress} {name}")

        print()
        print("   q. Quit")
        print()

        choice = input("  Pick a lesson (1-10) or 'q' to quit: ").strip().lower()

        if choice == "q":
            print("\n  Happy learning! See you next time.\n")
            break

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(LESSONS):
                LESSONS[idx][1].main()
            else:
                print("  Please enter a number between 1 and 10.")
        except ValueError:
            print("  Invalid input. Enter a number or 'q'.")


if __name__ == "__main__":
    main()
