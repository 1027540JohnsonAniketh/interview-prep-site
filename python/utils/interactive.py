"""Shared utilities for interactive Python learning."""

import textwrap
import random


def clear_screen():
    print("\n" * 2)


def print_header(title: str):
    width = 60
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width + "\n")


def print_subheader(title: str):
    print(f"\n--- {title} ---\n")


def print_code(code: str, show_output: bool = True):
    """Display code and optionally execute it, showing output."""
    print("  Code:")
    for line in code.strip().split("\n"):
        print(f"    >>> {line}")
    if show_output:
        print("  Output:")
        try:
            # Create a capture dict for exec
            capture = {}
            exec(code, {"__builtins__": __builtins__}, capture)
        except Exception as e:
            print(f"    Error: {e}")


def print_code_and_output(code: str, output: str):
    """Display code and its expected output without executing."""
    print("  Code:")
    for line in code.strip().split("\n"):
        print(f"    >>> {line}")
    print("  Output:")
    for line in output.strip().split("\n"):
        print(f"    {line}")
    print()


def print_concept(title: str, explanation: str):
    print(f"  [{title}]")
    for line in textwrap.wrap(explanation, width=70):
        print(f"    {line}")
    print()


def pause():
    input("  Press Enter to continue...")


def run_quiz(questions: list[dict]) -> int:
    """Run a multiple-choice quiz. Returns score."""
    print_subheader("Quiz Time!")
    score = 0
    shuffled = questions.copy()
    random.shuffle(shuffled)

    for i, q in enumerate(shuffled, 1):
        print(f"  Question {i}/{len(shuffled)}:")
        print(f"  {q['question']}\n")

        options = q["options"]
        for j, opt in enumerate(options):
            label = chr(65 + j)  # A, B, C, D
            print(f"    {label}) {opt}")

        answer = input("\n  Your answer (A/B/C/D): ").strip().upper()
        correct_label = chr(65 + q["answer"])

        if answer == correct_label:
            print("  Correct!\n")
            score += 1
        else:
            print(f"  Wrong! The answer is {correct_label}) {options[q['answer']]}")
            if "explanation" in q:
                print(f"  Why: {q['explanation']}")
            print()

    print(f"\n  Score: {score}/{len(shuffled)}")
    if score == len(shuffled):
        print("  Perfect score! You nailed it!")
    elif score >= len(shuffled) * 0.7:
        print("  Great job! You're getting the hang of it!")
    else:
        print("  Keep practicing! Review the learn section and try again.")
    print()
    return score


def run_coding_challenge(challenges: list[dict]) -> int:
    """Run interactive coding challenges. Returns score."""
    print_subheader("Coding Challenges")
    score = 0

    for i, ch in enumerate(challenges, 1):
        print(f"  Challenge {i}/{len(challenges)}:")
        print(f"  {ch['prompt']}\n")

        if "hint" in ch:
            show_hint = input("  Need a hint? (y/n): ").strip().lower()
            if show_hint == "y":
                print(f"  Hint: {ch['hint']}\n")

        print("  Type your code (press Enter twice to submit):")
        lines = []
        while True:
            line = input("  >>> ")
            if line == "":
                if lines:
                    break
                continue
            lines.append(line)

        user_code = "\n".join(lines)

        try:
            # Execute user code and validate
            user_ns = {}
            exec(user_code, {"__builtins__": __builtins__}, user_ns)

            # Run the validator
            result = ch["validator"](user_ns, user_code)
            if result:
                print("  Correct! Well done!\n")
                score += 1
            else:
                print("  Not quite right.")
                if "solution" in ch:
                    print(f"  Expected approach: {ch['solution']}")
                print()
        except Exception as e:
            print(f"  Error in your code: {e}")
            if "solution" in ch:
                print(f"  Example solution: {ch['solution']}")
            print()

    print(f"\n  Score: {score}/{len(challenges)}")
    print()
    return score


def lesson_menu(lesson_name: str, learn_fn, practice_fn, quiz_fn):
    """Standard menu for each lesson: Learn, Practice, Quiz."""
    while True:
        print_header(lesson_name)
        print("  [L] Learn - Read concepts with live examples")
        print("  [P] Practice - Solve coding challenges")
        print("  [Q] Quiz - Test your knowledge")
        print("  [B] Back to main menu")
        print()

        choice = input("  Choose mode: ").strip().upper()

        if choice == "L":
            learn_fn()
        elif choice == "P":
            practice_fn()
        elif choice == "Q":
            quiz_fn()
        elif choice == "B":
            break
        else:
            print("  Invalid choice. Try L, P, Q, or B.")
