"""Lesson 8: Error Handling — try/except, custom exceptions."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.interactive import (
    print_header, print_subheader, print_code_and_output,
    print_concept, pause, run_quiz, run_coding_challenge, lesson_menu,
)


def learn():
    print_header("Learn: Error Handling")

    print_concept(
        "Why handle errors?",
        "Programs crash when they hit unexpected situations — dividing by zero, "
        "missing files, bad user input. Error handling lets you catch these problems "
        "gracefully instead of crashing.",
    )

    # --- try/except ---
    print_subheader("try / except — Catching Errors")
    print_code_and_output(
        'try:\n    result = 10 / 0\nexcept ZeroDivisionError:\n    print("Cannot divide by zero!")\n    result = 0\n\nprint(f"result = {result}")',
        "Cannot divide by zero!\nresult = 0",
    )
    pause()

    # --- Common exceptions ---
    print_subheader("Common Exception Types")
    exceptions = [
        ("ValueError", "int('abc')", "Wrong value type for conversion"),
        ("TypeError", "'hello' + 5", "Wrong type for operation"),
        ("KeyError", "{}['missing']", "Dict key doesn't exist"),
        ("IndexError", "[1,2,3][10]", "List index out of range"),
        ("FileNotFoundError", "open('nope.txt')", "File doesn't exist"),
        ("AttributeError", "'hello'.nonexistent()", "Object has no such attribute"),
        ("ZeroDivisionError", "1/0", "Division by zero"),
    ]
    for name, example, desc in exceptions:
        print(f"  {name:22s} | {example:25s} | {desc}")
    print()
    pause()

    # --- Multiple except blocks ---
    print_subheader("Multiple except Blocks")
    print_code_and_output(
        'def safe_divide(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        print("Division by zero!")\n        return None\n    except TypeError:\n        print("Invalid types!")\n        return None\n\nprint(safe_divide(10, 0))\nprint(safe_divide("10", 2))',
        "Division by zero!\nNone\n5.0",
    )
    pause()

    # --- try/except/else/finally ---
    print_subheader("Full Pattern: try / except / else / finally")
    print_code_and_output(
        'def read_number(text):\n    try:\n        num = int(text)\n    except ValueError:\n        print(f"  \'{text}\' is not a number")\n    else:\n        # Runs ONLY if try succeeded (no exception)\n        print(f"  Successfully parsed: {num}")\n    finally:\n        # ALWAYS runs, whether error or not\n        print(f"  Done processing \'{text}\'")\n\nread_number("42")\nprint()\nread_number("abc")',
        "  Successfully parsed: 42\n  Done processing '42'\n\n  'abc' is not a number\n  Done processing 'abc'",
    )
    print_concept(
        "else vs finally",
        "else: runs only if no exception occurred. "
        "finally: ALWAYS runs — good for cleanup (closing files, connections).",
    )
    pause()

    # --- raise ---
    print_subheader("Raising Exceptions")
    print_code_and_output(
        'def set_age(age):\n    if age < 0:\n        raise ValueError(f"Age cannot be negative: {age}")\n    if age > 150:\n        raise ValueError(f"Age seems unrealistic: {age}")\n    return age\n\ntry:\n    set_age(-5)\nexcept ValueError as e:\n    print(f"Error: {e}")',
        "Error: Age cannot be negative: -5",
    )
    pause()

    # --- Custom exceptions ---
    print_subheader("Custom Exceptions")
    print_code_and_output(
        'class InsufficientFundsError(Exception):\n    def __init__(self, balance, amount):\n        self.balance = balance\n        self.amount = amount\n        super().__init__(\n            f"Cannot withdraw ${amount}. Balance: ${balance}"\n        )\n\ndef withdraw(balance, amount):\n    if amount > balance:\n        raise InsufficientFundsError(balance, amount)\n    return balance - amount\n\ntry:\n    withdraw(100, 250)\nexcept InsufficientFundsError as e:\n    print(f"Error: {e}")\n    print(f"Short by: ${e.amount - e.balance}")',
        "Error: Cannot withdraw $250. Balance: $100\nShort by: $150",
    )
    print()


def practice():
    challenges = [
        {
            "prompt": "Write a function 'safe_int' that converts a string to int.\nReturn the int if valid, or None if it fails.",
            "hint": "Use try/except ValueError",
            "validator": lambda ns, code: (
                callable(ns.get("safe_int"))
                and ns["safe_int"]("42") == 42
                and ns["safe_int"]("abc") is None
            ),
            "solution": "def safe_int(s):\n    try:\n        return int(s)\n    except ValueError:\n        return None",
        },
        {
            "prompt": "Create a custom exception 'NegativeNumberError' that inherits from ValueError.\nIt should store the number and have a useful message.",
            "hint": "class NegativeNumberError(ValueError): ...",
            "validator": lambda ns, code: (
                "NegativeNumberError" in ns
                and issubclass(ns["NegativeNumberError"], ValueError)
            ),
            "solution": "class NegativeNumberError(ValueError):\n    def __init__(self, number):\n        self.number = number\n        super().__init__(f'{number} is negative')",
        },
        {
            "prompt": "Write a function 'safe_get' that takes a dict and a key.\nReturn the value if key exists, otherwise return 'Key not found' (without using .get()).",
            "hint": "Use try/except KeyError",
            "validator": lambda ns, code: (
                callable(ns.get("safe_get"))
                and ns["safe_get"]({"a": 1}, "a") == 1
                and ns["safe_get"]({"a": 1}, "b") == "Key not found"
                and "except" in code
            ),
            "solution": "def safe_get(d, key):\n    try:\n        return d[key]\n    except KeyError:\n        return 'Key not found'",
        },
    ]
    run_coding_challenge(challenges)


def quiz():
    questions = [
        {
            "question": "When does the 'finally' block run?",
            "options": ["Only when an exception occurs", "Only when no exception occurs", "Always", "Never automatically"],
            "answer": 2,
        },
        {
            "question": "What does 'raise' do?",
            "options": ["Catches an exception", "Creates a new exception and throws it", "Logs an error", "Ignores an error"],
            "answer": 1,
        },
        {
            "question": "What exception does int('abc') raise?",
            "options": ["TypeError", "ValueError", "KeyError", "RuntimeError"],
            "answer": 1,
        },
        {
            "question": "When does the 'else' block in try/except/else run?",
            "options": ["Always", "When an exception occurs", "When NO exception occurs", "Before the try block"],
            "answer": 2,
        },
        {
            "question": "What is the base class for most custom exceptions?",
            "options": ["Error", "Exception", "BaseException", "RuntimeError"],
            "answer": 1,
            "explanation": "Custom exceptions should inherit from Exception (not BaseException, which includes SystemExit).",
        },
    ]
    run_quiz(questions)


def main():
    lesson_menu("Lesson 8: Error Handling", learn, practice, quiz)


if __name__ == "__main__":
    main()
