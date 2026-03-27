"""Lesson 1: Python Basics — Variables, Types, f-strings, Input/Output."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.interactive import (
    print_header, print_subheader, print_code_and_output,
    print_concept, pause, run_quiz, run_coding_challenge, lesson_menu,
)


def learn():
    print_header("Learn: Python Basics")

    # --- Variables ---
    print_concept(
        "Variables",
        "Variables store data. Python is dynamically typed — you don't "
        "declare the type, Python figures it out from the value you assign.",
    )
    print_code_and_output(
        'name = "Aniketh"\nage = 25\npi = 3.14\nis_learning = True',
        '# No output — variables are just stored in memory',
    )
    pause()

    # --- Types ---
    print_subheader("Built-in Types")
    types_demo = [
        ('int', '42', "Whole numbers: 1, -5, 1000"),
        ('float', '3.14', "Decimal numbers: 1.5, -0.001"),
        ('str', '"hello"', "Text in quotes: 'hi', \"hello\""),
        ('bool', 'True', "True or False — used in conditions"),
        ('NoneType', 'None', "Represents 'nothing' or 'no value'"),
    ]
    for type_name, example, desc in types_demo:
        print(f"  {type_name:12s} | {example:10s} | {desc}")
    print()
    pause()

    # --- type() function ---
    print_subheader("Checking Types with type()")
    print_code_and_output(
        'print(type(42))\nprint(type("hello"))\nprint(type(3.14))\nprint(type(True))',
        "<class 'int'>\n<class 'str'>\n<class 'float'>\n<class 'bool'>",
    )
    print_concept(
        "Key Insight",
        "Everything in Python is an object. Even 42 is an object of type int. "
        "You can call methods on it: (42).bit_length() returns 6.",
    )
    pause()

    # --- f-strings ---
    print_subheader("f-strings (Formatted String Literals)")
    print_concept(
        "f-strings",
        "Prefix a string with 'f' to embed expressions inside {curly braces}. "
        "This is the modern, preferred way to format strings in Python 3.6+.",
    )
    print_code_and_output(
        'name = "Aniketh"\nage = 25\nprint(f"Hi, I\'m {name} and I\'m {age} years old.")\nprint(f"Next year I\'ll be {age + 1}.")\nprint(f"Pi to 2 decimals: {3.14159:.2f}")',
        "Hi, I'm Aniketh and I'm 25 years old.\nNext year I'll be 26.\nPi to 2 decimals: 3.14",
    )
    pause()

    # --- input() ---
    print_subheader("Getting User Input")
    print_concept(
        "input()",
        "input() reads text from the user. It ALWAYS returns a string, "
        "so you need to convert it with int() or float() for numbers.",
    )
    print_code_and_output(
        'name = input("What is your name? ")\nprint(f"Hello, {name}!")\n\nage = int(input("How old are you? "))\nprint(f"In 10 years you will be {age + 10}.")',
        'What is your name? Aniketh\nHello, Aniketh!\nHow old are you? 25\nIn 10 years you will be 35.',
    )
    pause()

    # --- String methods ---
    print_subheader("Useful String Methods")
    print_code_and_output(
        'text = "Hello World"\nprint(text.upper())        # HELLO WORLD\nprint(text.lower())        # hello world\nprint(text.replace("World", "Python"))  # Hello Python\nprint(text.split())        # [\'Hello\', \'World\']\nprint(len(text))           # 11\nprint("World" in text)     # True',
        "HELLO WORLD\nhello world\nHello Python\n['Hello', 'World']\n11\nTrue",
    )
    pause()

    # --- Type conversion ---
    print_subheader("Type Conversion (Casting)")
    print_code_and_output(
        'x = "42"\nprint(type(x))       # <class \'str\'>\n\ny = int(x)\nprint(type(y))       # <class \'int\'>\nprint(y + 8)         # 50\n\nz = float("3.14")\nprint(z * 2)         # 6.28\n\nprint(str(100))      # "100" as a string',
        "<class 'str'>\n<class 'int'>\n50\n6.28\n100",
    )
    print()
    print("  That's the basics! Try the Practice and Quiz modes next.")
    print()


def practice():
    challenges = [
        {
            "prompt": "Create a variable called 'greeting' with value 'Hello, Python!'",
            "hint": "Just assign a string to a variable name",
            "validator": lambda ns, code: ns.get("greeting") == "Hello, Python!",
            "solution": 'greeting = "Hello, Python!"',
        },
        {
            "prompt": "Create two variables: x = 10 and y = 3. Create a third variable 'result' with their sum.",
            "hint": "Use the + operator",
            "validator": lambda ns, code: ns.get("x") == 10 and ns.get("y") == 3 and ns.get("result") == 13,
            "solution": "x = 10\ny = 3\nresult = x + y",
        },
        {
            "prompt": "Create a variable 'message' using an f-string: 'I am learning Python in 2026'.\nUse a variable year = 2026 inside the f-string.",
            "hint": "f'I am learning Python in {year}'",
            "validator": lambda ns, code: ns.get("message") == "I am learning Python in 2026" and "f'" in code or 'f"' in code,
            "solution": 'year = 2026\nmessage = f"I am learning Python in {year}"',
        },
        {
            "prompt": "Convert the string '99' to an integer and store it in a variable called 'num'.",
            "hint": "Use int() to convert",
            "validator": lambda ns, code: ns.get("num") == 99 and isinstance(ns.get("num"), int),
            "solution": 'num = int("99")',
        },
        {
            "prompt": "Create a variable 'name' with your name, and 'upper_name' with it in ALL CAPS.",
            "hint": "Use the .upper() method",
            "validator": lambda ns, code: "upper_name" in ns and ns["upper_name"] == ns.get("name", "").upper(),
            "solution": 'name = "Aniketh"\nupper_name = name.upper()',
        },
    ]
    run_coding_challenge(challenges)


def quiz():
    questions = [
        {
            "question": "What does type(42) return?",
            "options": ["<class 'str'>", "<class 'int'>", "<class 'float'>", "<class 'number'>"],
            "answer": 1,
            "explanation": "42 is a whole number, which is an int (integer) in Python.",
        },
        {
            "question": "What does input() always return?",
            "options": ["An integer", "A float", "A string", "Depends on what you type"],
            "answer": 2,
            "explanation": "input() ALWAYS returns a string. You must convert it with int() or float().",
        },
        {
            "question": "Which is the correct f-string syntax?",
            "options": ["f'Hello {name}'", "'Hello {name}'", "f(Hello {name})", "format('Hello', name)"],
            "answer": 0,
            "explanation": "f-strings use the f prefix before the quote and {} for expressions.",
        },
        {
            "question": "What is the value of bool('')?",
            "options": ["True", "False", "None", "Error"],
            "answer": 1,
            "explanation": "Empty strings are 'falsy' in Python. bool('') returns False.",
        },
        {
            "question": "How do you convert '3.14' to a float?",
            "options": ["int('3.14')", "float('3.14')", "str(3.14)", "number('3.14')"],
            "answer": 1,
            "explanation": "float() converts a string to a floating-point number.",
        },
    ]
    run_quiz(questions)


def main():
    lesson_menu("Lesson 1: Python Basics", learn, practice, quiz)


if __name__ == "__main__":
    main()
