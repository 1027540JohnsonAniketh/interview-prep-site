"""Lesson 2: Control Flow — if/else, loops, while, for, range."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.interactive import (
    print_header, print_subheader, print_code_and_output,
    print_concept, pause, run_quiz, run_coding_challenge, lesson_menu,
)


def learn():
    print_header("Learn: Control Flow")

    # --- if/elif/else ---
    print_concept(
        "if / elif / else",
        "Conditional statements let your code make decisions. Python uses "
        "indentation (4 spaces) to define blocks — no curly braces needed.",
    )
    print_code_and_output(
        'age = 20\n\nif age >= 21:\n    print("Can drink")\nelif age >= 18:\n    print("Can vote")\nelse:\n    print("Minor")',
        "Can vote",
    )
    pause()

    # --- Comparison & logical operators ---
    print_subheader("Comparison & Logical Operators")
    print_code_and_output(
        '# Comparison: ==  !=  >  <  >=  <=\nprint(5 == 5)    # True\nprint(5 != 3)    # True\n\n# Logical: and, or, not\nprint(True and False)   # False\nprint(True or False)    # True\nprint(not True)         # False\n\n# Chaining\nx = 5\nprint(1 < x < 10)  # True — Python supports chaining!',
        "True\nTrue\nFalse\nTrue\nFalse\nTrue",
    )
    pause()

    # --- for loop ---
    print_subheader("for Loops")
    print_concept(
        "for loop",
        "Iterates over a sequence (list, string, range, etc). "
        "Think of it as: 'for each item in this collection, do something.'",
    )
    print_code_and_output(
        '# Iterate over a list\nfruits = ["apple", "banana", "cherry"]\nfor fruit in fruits:\n    print(fruit)\n\n# Iterate over a string\nfor char in "Hi":\n    print(char)',
        "apple\nbanana\ncherry\nH\ni",
    )
    pause()

    # --- range() ---
    print_subheader("range() Function")
    print_code_and_output(
        '# range(stop) — 0 to stop-1\nfor i in range(5):\n    print(i, end=" ")\nprint()\n\n# range(start, stop)\nfor i in range(2, 6):\n    print(i, end=" ")\nprint()\n\n# range(start, stop, step)\nfor i in range(0, 10, 2):\n    print(i, end=" ")',
        "0 1 2 3 4 \n2 3 4 5 \n0 2 4 6 8",
    )
    pause()

    # --- while loop ---
    print_subheader("while Loops")
    print_concept(
        "while loop",
        "Keeps running as long as the condition is True. "
        "Be careful — if the condition never becomes False, you get an infinite loop!",
    )
    print_code_and_output(
        'count = 0\nwhile count < 3:\n    print(f"count is {count}")\n    count += 1  # Don\'t forget to update!',
        "count is 0\ncount is 1\ncount is 2",
    )
    pause()

    # --- break & continue ---
    print_subheader("break and continue")
    print_code_and_output(
        '# break — exit the loop early\nfor i in range(10):\n    if i == 5:\n        break\n    print(i, end=" ")\nprint("\\n")\n\n# continue — skip to next iteration\nfor i in range(6):\n    if i == 3:\n        continue\n    print(i, end=" ")',
        "0 1 2 3 4 \n\n0 1 2 4 5",
    )
    pause()

    # --- enumerate ---
    print_subheader("enumerate() — Get Index + Value")
    print_code_and_output(
        'colors = ["red", "green", "blue"]\nfor i, color in enumerate(colors):\n    print(f"{i}: {color}")',
        "0: red\n1: green\n2: blue",
    )
    pause()

    # --- Ternary ---
    print_subheader("Ternary Expression (One-line if)")
    print_code_and_output(
        'age = 20\nstatus = "adult" if age >= 18 else "minor"\nprint(status)',
        "adult",
    )
    print()
    print("  Great! Try Practice and Quiz to reinforce these concepts.")
    print()


def practice():
    challenges = [
        {
            "prompt": "Write code that creates a variable 'result' set to 'even' if 42 is even, else 'odd'.",
            "hint": "Use the modulo operator % and a ternary expression",
            "validator": lambda ns, code: ns.get("result") == "even",
            "solution": 'result = "even" if 42 % 2 == 0 else "odd"',
        },
        {
            "prompt": "Create a list called 'evens' containing even numbers from 0 to 10 (inclusive) using a for loop.",
            "hint": "Use range() and check with %",
            "validator": lambda ns, code: ns.get("evens") == [0, 2, 4, 6, 8, 10],
            "solution": "evens = []\nfor i in range(11):\n    if i % 2 == 0:\n        evens.append(i)",
        },
        {
            "prompt": "Use a for loop to create 'total' = sum of numbers 1 through 100.",
            "hint": "Start with total = 0 and add each number",
            "validator": lambda ns, code: ns.get("total") == 5050,
            "solution": "total = 0\nfor i in range(1, 101):\n    total += i",
        },
        {
            "prompt": "Create a variable 'first_big' — the first number in range(1, 100) divisible by 7 AND by 3. Use a loop with break.",
            "hint": "Check: if i % 7 == 0 and i % 3 == 0",
            "validator": lambda ns, code: ns.get("first_big") == 21 and "break" in code,
            "solution": "for i in range(1, 100):\n    if i % 7 == 0 and i % 3 == 0:\n        first_big = i\n        break",
        },
    ]
    run_coding_challenge(challenges)


def quiz():
    questions = [
        {
            "question": "What does range(3) produce?",
            "options": ["[1, 2, 3]", "[0, 1, 2]", "[0, 1, 2, 3]", "[3]"],
            "answer": 1,
            "explanation": "range(3) goes from 0 up to (but not including) 3.",
        },
        {
            "question": "What does 'break' do inside a loop?",
            "options": ["Skips current iteration", "Exits the loop immediately", "Restarts the loop", "Raises an error"],
            "answer": 1,
        },
        {
            "question": "What is the output of: print(10 > 5 and 3 < 1)?",
            "options": ["True", "False", "Error", "None"],
            "answer": 1,
            "explanation": "10 > 5 is True, but 3 < 1 is False. True and False = False.",
        },
        {
            "question": "How does Python define code blocks?",
            "options": ["Curly braces {}", "Indentation", "Parentheses ()", "Keywords begin/end"],
            "answer": 1,
            "explanation": "Python uses indentation (typically 4 spaces) to define blocks.",
        },
        {
            "question": "What does 'continue' do inside a loop?",
            "options": ["Exits the loop", "Skips to the next iteration", "Pauses the loop", "Repeats current iteration"],
            "answer": 1,
        },
    ]
    run_quiz(questions)


def main():
    lesson_menu("Lesson 2: Control Flow", learn, practice, quiz)


if __name__ == "__main__":
    main()
