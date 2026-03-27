"""Lesson 10: Decorators & Closures."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.interactive import (
    print_header, print_subheader, print_code_and_output,
    print_concept, pause, run_quiz, run_coding_challenge, lesson_menu,
)


def learn():
    print_header("Learn: Decorators & Closures")

    # --- Functions are objects ---
    print_subheader("Functions Are Objects")
    print_concept(
        "First-class functions",
        "In Python, functions are objects. You can assign them to variables, "
        "pass them as arguments, and return them from other functions. "
        "This is the foundation of decorators.",
    )
    print_code_and_output(
        'def greet(name):\n    return f"Hello, {name}!"\n\n# Assign function to a variable\nsay_hi = greet\nprint(say_hi("Aniketh"))  # Same function, different name\n\n# Pass function as argument\ndef apply(func, value):\n    return func(value)\n\nprint(apply(greet, "World"))',
        "Hello, Aniketh!\nHello, World!",
    )
    pause()

    # --- Closures ---
    print_subheader("Closures — Functions That Remember")
    print_concept(
        "Closures",
        "A closure is a function that remembers variables from its enclosing scope, "
        "even after that scope has finished executing. The inner function 'closes over' "
        "the outer variables.",
    )
    print_code_and_output(
        'def make_multiplier(factor):\n    def multiply(x):\n        return x * factor  # Remembers \'factor\' from outer scope\n    return multiply\n\ndouble = make_multiplier(2)\ntriple = make_multiplier(3)\n\nprint(double(5))   # 10\nprint(triple(5))   # 15\nprint(double(10))  # 20',
        "10\n15\n20",
    )
    pause()

    # --- Basic decorator ---
    print_subheader("Decorators — Wrapping Functions")
    print_concept(
        "What is a decorator?",
        "A decorator is a function that takes a function, adds some behavior, "
        "and returns a new function. The @decorator syntax is syntactic sugar "
        "for: func = decorator(func).",
    )
    print_code_and_output(
        'import time\n\ndef timer(func):\n    def wrapper(*args, **kwargs):\n        start = time.time()\n        result = func(*args, **kwargs)\n        elapsed = time.time() - start\n        print(f"  {func.__name__} took {elapsed:.4f}s")\n        return result\n    return wrapper\n\n@timer  # Same as: slow_add = timer(slow_add)\ndef slow_add(a, b):\n    time.sleep(0.1)\n    return a + b\n\nresult = slow_add(3, 4)\nprint(f"  Result: {result}")',
        "  slow_add took 0.10xxs\n  Result: 7",
    )
    pause()

    # --- functools.wraps ---
    print_subheader("functools.wraps — Preserving Function Identity")
    print_concept(
        "Why functools.wraps?",
        "Without @wraps, the decorated function loses its original name and docstring. "
        "@wraps copies the original function's metadata to the wrapper.",
    )
    print_code_and_output(
        'from functools import wraps\n\ndef my_decorator(func):\n    @wraps(func)  # Preserves func\'s name and docstring\n    def wrapper(*args, **kwargs):\n        print(f"  Calling {func.__name__}")\n        return func(*args, **kwargs)\n    return wrapper\n\n@my_decorator\ndef hello():\n    """Says hello."""\n    return "Hello!"\n\nprint(hello())          # Works normally\nprint(hello.__name__)   # "hello" (not "wrapper")\nprint(hello.__doc__)    # "Says hello."',
        "  Calling hello\nHello!\nhello\nSays hello.",
    )
    pause()

    # --- Decorators with arguments ---
    print_subheader("Decorators with Arguments")
    print_code_and_output(
        'from functools import wraps\n\ndef repeat(n):\n    def decorator(func):\n        @wraps(func)\n        def wrapper(*args, **kwargs):\n            for _ in range(n):\n                result = func(*args, **kwargs)\n            return result\n        return wrapper\n    return decorator\n\n@repeat(3)  # Run the function 3 times\ndef say_hello():\n    print("  Hello!")\n\nsay_hello()',
        "  Hello!\n  Hello!\n  Hello!",
    )
    print_concept(
        "Three levels",
        "Decorator with args needs THREE nested functions: "
        "outer (takes decorator args) -> decorator (takes func) -> wrapper (takes func args).",
    )
    pause()

    # --- Common use cases ---
    print_subheader("Common Decorator Use Cases")
    print("  | Use Case             | What it does                              |")
    print("  |---------------------|-------------------------------------------|")
    print("  | @timer              | Measure execution time                    |")
    print("  | @retry              | Retry on failure with backoff             |")
    print("  | @cache / @lru_cache | Cache function results                   |")
    print("  | @login_required     | Check auth before running (Flask/Django)  |")
    print("  | @property           | Make method act like attribute            |")
    print("  | @staticmethod       | Method that doesn't need self             |")
    print("  | @classmethod        | Method that gets class, not instance      |")
    print()

    # --- Built-in: lru_cache ---
    print_subheader("Built-in: @lru_cache for Memoization")
    print_code_and_output(
        'from functools import lru_cache\n\n@lru_cache(maxsize=None)  # Cache all results\ndef fibonacci(n):\n    if n < 2:\n        return n\n    return fibonacci(n - 1) + fibonacci(n - 2)\n\nprint(fibonacci(50))  # Instant! Without cache, this would take forever\nprint(fibonacci.cache_info())',
        "12586269025\nCacheInfo(hits=48, misses=51, maxsize=None, currsize=51)",
    )
    print()


def practice():
    challenges = [
        {
            "prompt": "Write a closure 'make_adder' that takes n and returns a function that adds n to its argument.\nmake_adder(10)(5) should return 15.",
            "hint": "def make_adder(n): def add(x): return x + n; return add",
            "validator": lambda ns, code: (
                callable(ns.get("make_adder"))
                and ns["make_adder"](10)(5) == 15
                and ns["make_adder"](0)(42) == 42
            ),
            "solution": "def make_adder(n):\n    def add(x):\n        return x + n\n    return add",
        },
        {
            "prompt": "Write a decorator 'shout' that makes any function's string return value UPPERCASE.\n@shout over a function returning 'hello' should make it return 'HELLO'.",
            "hint": "def shout(func): def wrapper(...): return func(...).upper(); return wrapper",
            "validator": lambda ns, code: (
                callable(ns.get("shout"))
                and ns["shout"](lambda: "hello")() == "HELLO"
            ),
            "solution": "def shout(func):\n    def wrapper(*args, **kwargs):\n        return func(*args, **kwargs).upper()\n    return wrapper",
        },
        {
            "prompt": "Write a decorator 'count_calls' that tracks how many times a function is called.\nThe decorated function should have a .calls attribute.",
            "hint": "Use wrapper.calls = 0 and increment it in the wrapper",
            "validator": lambda ns, code: (
                callable(ns.get("count_calls"))
                and (lambda: (
                    (f := ns["count_calls"](lambda: None)),
                    f(), f(), f(),
                    f.calls == 3,
                ))()[-1]
            ),
            "solution": "def count_calls(func):\n    def wrapper(*args, **kwargs):\n        wrapper.calls += 1\n        return func(*args, **kwargs)\n    wrapper.calls = 0\n    return wrapper",
        },
    ]
    run_coding_challenge(challenges)


def quiz():
    questions = [
        {
            "question": "What is a closure?",
            "options": [
                "A function that closes the program",
                "A function that remembers its enclosing scope's variables",
                "A class method",
                "A function that can't be called",
            ],
            "answer": 1,
        },
        {
            "question": "What does @decorator above a function do?",
            "options": [
                "Deletes the function",
                "Same as: func = decorator(func)",
                "Makes the function private",
                "Runs the function immediately",
            ],
            "answer": 1,
        },
        {
            "question": "Why use @functools.wraps(func)?",
            "options": [
                "Makes the function faster",
                "Preserves the original function's name and docstring",
                "Prevents the function from being called twice",
                "Adds type checking",
            ],
            "answer": 1,
        },
        {
            "question": "What does @lru_cache do?",
            "options": [
                "Limits function arguments",
                "Caches function results to avoid recomputation",
                "Makes the function thread-safe",
                "Logs function calls",
            ],
            "answer": 1,
        },
        {
            "question": "How many nested functions does a decorator WITH arguments need?",
            "options": ["1", "2", "3", "4"],
            "answer": 2,
            "explanation": "Three: outer(args) -> decorator(func) -> wrapper(*args, **kwargs)",
        },
    ]
    run_quiz(questions)


def main():
    lesson_menu("Lesson 10: Decorators & Closures", learn, practice, quiz)


if __name__ == "__main__":
    main()
