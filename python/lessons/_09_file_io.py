"""Lesson 9: File I/O — reading/writing files, context managers, JSON, CSV."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.interactive import (
    print_header, print_subheader, print_code_and_output,
    print_concept, pause, run_quiz, run_coding_challenge, lesson_menu,
)


def learn():
    print_header("Learn: File I/O & Context Managers")

    print_concept(
        "File I/O",
        "Python can read from and write to files on disk. The 'open()' function "
        "is the gateway. Always close files when done — or better, use 'with' "
        "to handle it automatically.",
    )

    # --- open() basics ---
    print_subheader("Opening Files — Modes")
    modes = [
        ("'r'", "Read (default)", "File must exist"),
        ("'w'", "Write", "Creates or OVERWRITES file"),
        ("'a'", "Append", "Creates or appends to file"),
        ("'x'", "Exclusive create", "Fails if file exists"),
        ("'rb'/'wb'", "Binary read/write", "For images, PDFs, etc"),
    ]
    for mode, name, desc in modes:
        print(f"  {mode:10s} | {name:20s} | {desc}")
    print()
    pause()

    # --- with statement ---
    print_subheader("The 'with' Statement (Context Manager)")
    print_concept(
        "Why 'with'?",
        "The 'with' statement automatically closes the file when the block ends, "
        "even if an error occurs. This prevents resource leaks. Always use 'with' "
        "instead of manual open()/close().",
    )
    print_code_and_output(
        '# Writing to a file\nwith open("example.txt", "w") as f:\n    f.write("Hello, File!\\n")\n    f.write("Line 2\\n")\n# File is automatically closed here\n\n# Reading the file\nwith open("example.txt", "r") as f:\n    content = f.read()\n    print(content)',
        "Hello, File!\nLine 2\n",
    )
    pause()

    # --- Reading methods ---
    print_subheader("Different Ways to Read Files")
    print_code_and_output(
        '# read() — entire file as one string\nwith open("example.txt") as f:\n    all_text = f.read()\n\n# readline() — one line at a time\nwith open("example.txt") as f:\n    first_line = f.readline()  # "Hello, File!\\n"\n\n# readlines() — list of all lines\nwith open("example.txt") as f:\n    lines = f.readlines()  # ["Hello, File!\\n", "Line 2\\n"]\n\n# Best: iterate directly (memory-efficient)\nwith open("example.txt") as f:\n    for line in f:\n        print(line.strip())  # strip() removes \\n',
        "Hello, File!\nLine 2",
    )
    pause()

    # --- JSON ---
    print_subheader("Working with JSON")
    print_concept(
        "JSON",
        "JSON (JavaScript Object Notation) is the standard format for data exchange. "
        "Python's json module converts between Python dicts/lists and JSON strings.",
    )
    print_code_and_output(
        'import json\n\n# Python dict -> JSON string\ndata = {"name": "Aniketh", "skills": ["Python", "Java"], "age": 25}\njson_str = json.dumps(data, indent=2)\nprint(json_str)\n\n# JSON string -> Python dict\nparsed = json.loads(json_str)\nprint(f"Name: {parsed[\'name\']}")\n\n# Write JSON to file\nwith open("data.json", "w") as f:\n    json.dump(data, f, indent=2)\n\n# Read JSON from file\nwith open("data.json") as f:\n    loaded = json.load(f)\n    print(f"Loaded: {loaded}")',
        '{\n  "name": "Aniketh",\n  "skills": ["Python", "Java"],\n  "age": 25\n}\nName: Aniketh\nLoaded: {\'name\': \'Aniketh\', ...}',
    )
    pause()

    # --- CSV ---
    print_subheader("Working with CSV")
    print_code_and_output(
        'import csv\n\n# Write CSV\nwith open("people.csv", "w", newline="") as f:\n    writer = csv.writer(f)\n    writer.writerow(["name", "age", "role"])\n    writer.writerow(["Aniketh", 25, "Engineer"])\n    writer.writerow(["Alice", 30, "Manager"])\n\n# Read CSV\nwith open("people.csv") as f:\n    reader = csv.DictReader(f)\n    for row in reader:\n        print(f"  {row[\'name\']} is {row[\'age\']}")',
        "  Aniketh is 25\n  Alice is 30",
    )
    pause()

    # --- pathlib ---
    print_subheader("Modern File Paths with pathlib")
    print_code_and_output(
        'from pathlib import Path\n\n# Create path objects\np = Path("example.txt")\nprint(p.exists())        # True\nprint(p.suffix)          # .txt\nprint(p.stem)            # example\nprint(p.name)            # example.txt\n\n# Read/write shortcuts\np.write_text("Quick write!\\n")\ncontent = p.read_text()\nprint(content)\n\n# List files in a directory\nfor f in Path(".").glob("*.txt"):\n    print(f"  Found: {f}")',
        "True\n.txt\nexample\nexample.txt\nQuick write!\n  Found: example.txt",
    )
    print()


def practice():
    challenges = [
        {
            "prompt": "Write a function 'count_lines' that takes a filename and returns the number of lines.\nUse a with statement.",
            "hint": "Open the file, readlines(), return len()",
            "validator": lambda ns, code: (
                callable(ns.get("count_lines"))
                and "with" in code
            ),
            "solution": "def count_lines(filename):\n    with open(filename) as f:\n        return len(f.readlines())",
        },
        {
            "prompt": "Write a function 'to_json' that takes a dict and returns a pretty-printed JSON string (indent=2).",
            "hint": "import json; json.dumps(data, indent=2)",
            "validator": lambda ns, code: (
                callable(ns.get("to_json"))
                and '"name"' in ns["to_json"]({"name": "test"})
            ),
            "solution": "import json\ndef to_json(data):\n    return json.dumps(data, indent=2)",
        },
        {
            "prompt": "Write a function 'file_extension' that takes a filename string and returns the extension.\nUse pathlib.Path. Example: file_extension('report.pdf') -> '.pdf'",
            "hint": "from pathlib import Path; Path(filename).suffix",
            "validator": lambda ns, code: (
                callable(ns.get("file_extension"))
                and ns["file_extension"]("report.pdf") == ".pdf"
                and ns["file_extension"]("data.csv") == ".csv"
            ),
            "solution": "from pathlib import Path\ndef file_extension(filename):\n    return Path(filename).suffix",
        },
    ]
    run_coding_challenge(challenges)


def quiz():
    questions = [
        {
            "question": "What does 'w' mode do if the file already exists?",
            "options": ["Appends to it", "Raises an error", "Overwrites it completely", "Does nothing"],
            "answer": 2,
            "explanation": "'w' truncates (empties) the file and writes from scratch. Use 'a' to append.",
        },
        {
            "question": "What is the main benefit of 'with open(...) as f'?",
            "options": ["Faster reading", "Auto-closes the file", "Encrypts the data", "Enables binary mode"],
            "answer": 1,
        },
        {
            "question": "What does json.dumps() do?",
            "options": ["Reads a JSON file", "Converts JSON string to dict", "Converts dict to JSON string", "Deletes JSON data"],
            "answer": 2,
            "explanation": "dumps = dump to string. loads = load from string. dump/load = file operations.",
        },
        {
            "question": "What's the difference between json.dump() and json.dumps()?",
            "options": [
                "No difference",
                "dump writes to file, dumps returns string",
                "dumps is faster",
                "dump works with lists only",
            ],
            "answer": 1,
        },
        {
            "question": "Which is the most memory-efficient way to read a large file?",
            "options": ["f.read()", "f.readlines()", "for line in f:", "f.read().split('\\n')"],
            "answer": 2,
            "explanation": "Iterating over the file object reads one line at a time — doesn't load entire file into memory.",
        },
    ]
    run_quiz(questions)


def main():
    lesson_menu("Lesson 9: File I/O", learn, practice, quiz)


if __name__ == "__main__":
    main()
