"""Lesson 3: Functions — def, args, return, *args, **kwargs, lambda."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.interactive import (
    print_header, print_subheader, print_code_and_output,
    print_concept, pause, run_quiz, run_coding_challenge, lesson_menu,
)


def learn():
    print_header("Learn: Functions")

    print_concept(
        "What is a function?",
        "A reusable block of code that takes input (arguments), does something, "
        "and optionally returns output. Functions help you avoid repeating code "
        "and organize logic into named, testable pieces.",
    )

    # --- Basic function ---
    print_subheader("Defining and Calling Functions")
    print_code_and_output(
        'def greet(name):\n    return f"Hello, {name}!"\n\nmessage = greet("Aniketh")\nprint(message)',
        "Hello, Aniketh!",
    )
    pause()

    # --- Multiple params, default values ---
    print_subheader("Parameters & Default Values")
    print_code_and_output(
        'def power(base, exponent=2):\n    return base ** exponent\n\nprint(power(3))       # Uses default exponent=2\nprint(power(3, 3))    # Overrides to exponent=3\nprint(power(base=5, exponent=4))  # Keyword arguments',
        "9\n27\n625",
    )
    pause()

    # --- Return multiple values ---
    print_subheader("Returning Multiple Values")
    print_concept(
        "Tuple unpacking",
        "Python functions can return multiple values as a tuple. "
        "You can unpack them into separate variables.",
    )
    print_code_and_output(
        'def divide(a, b):\n    quotient = a // b\n    remainder = a % b\n    return quotient, remainder\n\nq, r = divide(17, 5)\nprint(f"17 / 5 = {q} remainder {r}")',
        "17 / 5 = 3 remainder 2",
    )
    pause()

    # --- *args ---
    print_subheader("*args — Variable Positional Arguments")
    print_concept(
        "*args",
        "*args collects any number of positional arguments into a tuple. "
        "Use it when you don't know how many arguments will be passed.",
    )
    print_code_and_output(
        'def add_all(*args):\n    print(f"args = {args}")  # It\'s a tuple\n    return sum(args)\n\nprint(add_all(1, 2, 3))\nprint(add_all(10, 20, 30, 40))',
        "args = (1, 2, 3)\n6\nargs = (10, 20, 30, 40)\n100",
    )
    pause()

    # --- **kwargs ---
    print_subheader("**kwargs — Variable Keyword Arguments")
    print_concept(
        "**kwargs",
        "**kwargs collects any number of keyword arguments into a dictionary. "
        "Use it when you want to accept named parameters you didn't define.",
    )
    print_code_and_output(
        'def print_info(**kwargs):\n    for key, value in kwargs.items():\n        print(f"  {key}: {value}")\n\nprint_info(name="Aniketh", role="Engineer", lang="Python")',
        "  name: Aniketh\n  role: Engineer\n  lang: Python",
    )
    pause()

    # --- Lambda ---
    print_subheader("Lambda Functions (Anonymous Functions)")
    print_concept(
        "lambda",
        "A one-line function with no name. Useful for short operations, "
        "especially as arguments to functions like sorted(), map(), filter().",
    )
    print_code_and_output(
        '# Regular function\ndef double(x):\n    return x * 2\n\n# Same thing as a lambda\ndouble_lambda = lambda x: x * 2\n\nprint(double(5))         # 10\nprint(double_lambda(5))  # 10\n\n# Lambda with sorted()\nnames = ["Charlie", "Alice", "Bob"]\nsorted_names = sorted(names, key=lambda n: len(n))\nprint(sorted_names)',
        "10\n10\n['Bob', 'Alice', 'Charlie']",
    )
    pause()

    # --- Scope ---
    print_subheader("Variable Scope")
    print_concept(
        "Scope",
        "Variables defined inside a function are LOCAL — they only exist inside "
        "that function. Variables defined outside are GLOBAL. A function can read "
        "globals but can't modify them without the 'global' keyword.",
    )
    print_code_and_output(
        'x = 10  # Global\n\ndef show():\n    y = 5  # Local\n    print(f"Inside: x={x}, y={y}")\n\nshow()\nprint(f"Outside: x={x}")\n# print(y)  # ERROR — y doesn\'t exist here',
        "Inside: x=10, y=5\nOutside: x=10",
    )
    print()
    print("  Functions are the building blocks of clean code. Practice time!")
    print()


def practice():
    challenges = [
        {
            "prompt": "Write a function 'is_even' that takes a number and returns True if even, False if odd.",
            "hint": "Use the modulo operator %",
            "validator": lambda ns, code: callable(ns.get("is_even")) and ns["is_even"](4) is True and ns["is_even"](7) is False,
            "solution": "def is_even(n):\n    return n % 2 == 0",
        },
        {
            "prompt": "Write a function 'factorial' that returns the factorial of n (e.g., factorial(5) = 120).",
            "hint": "Use recursion: n * factorial(n-1), base case: n <= 1 returns 1",
            "validator": lambda ns, code: callable(ns.get("factorial")) and ns["factorial"](5) == 120 and ns["factorial"](0) == 1,
            "solution": "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n - 1)",
        },
        {
            "prompt": "Write a function 'multiply_all' that uses *args to multiply all its arguments together.",
            "hint": "Start with result = 1 and multiply each arg",
            "validator": lambda ns, code: callable(ns.get("multiply_all")) and ns["multiply_all"](2, 3, 4) == 24,
            "solution": "def multiply_all(*args):\n    result = 1\n    for n in args:\n        result *= n\n    return result",
        },
        {
            "prompt": "Create a lambda called 'to_upper' that takes a string and returns it in uppercase.",
            "hint": "lambda s: s.upper()",
            "validator": lambda ns, code: callable(ns.get("to_upper")) and ns["to_upper"]("hello") == "HELLO" and "lambda" in code,
            "solution": "to_upper = lambda s: s.upper()",
        },
    ]
    run_coding_challenge(challenges)


def quiz():
    questions = [
        {
            "question": "What does *args collect?",
            "options": ["A list", "A tuple", "A dictionary", "A set"],
            "answer": 1,
            "explanation": "*args packs extra positional arguments into a tuple.",
        },
        {
            "question": "What does **kwargs collect?",
            "options": ["A list", "A tuple", "A dictionary", "A set"],
            "answer": 2,
            "explanation": "**kwargs packs extra keyword arguments into a dictionary.",
        },
        {
            "question": "What is the output of: (lambda x, y: x + y)(3, 4)?",
            "options": ["7", "34", "Error", "None"],
            "answer": 0,
            "explanation": "The lambda adds x + y. Called immediately with 3 and 4, returns 7.",
        },
        {
            "question": "What happens if a function has no return statement?",
            "options": ["Error", "Returns 0", "Returns None", "Returns empty string"],
            "answer": 2,
            "explanation": "Functions without return (or with bare return) return None by default.",
        },
        {
            "question": "Can a local variable be accessed outside its function?",
            "options": ["Yes", "No", "Only with global keyword", "Only if it's a string"],
            "answer": 1,
            "explanation": "Local variables only exist inside the function where they're defined.",
        },
    ]
    run_quiz(questions)


def main():
    lesson_menu("Lesson 3: Functions", learn, practice, quiz)


if __name__ == "__main__":
    main()
