# Python Interactive Learning

An interactive CLI-based Python learning system with 10 lessons covering beginner to intermediate concepts.

## Quick Start

```bash
cd python
python3 run.py
```

## Lessons

| # | Topic | Concepts |
|---|-------|----------|
| 1 | **Basics** | Variables, types, f-strings, input/output, type conversion |
| 2 | **Control Flow** | if/elif/else, for, while, range, break/continue, enumerate |
| 3 | **Functions** | def, return, default args, *args, **kwargs, lambda, scope |
| 4 | **Data Structures** | Lists, tuples, dicts, sets, slicing, when to use what |
| 5 | **OOP** | Classes, __init__, self, inheritance, dunder methods, @property |
| 6 | **Hash Maps** | Hashing, dict internals, collisions, OrderedDict, custom keys |
| 7 | **Comprehensions** | List/dict/set comprehensions, generators, yield |
| 8 | **Error Handling** | try/except/else/finally, raise, custom exceptions |
| 9 | **File I/O** | open(), with, JSON, CSV, pathlib |
| 10 | **Decorators** | Closures, @decorator, functools.wraps, @lru_cache |

## Each Lesson Has 3 Modes

- **[L] Learn** — Concepts explained with live code examples and outputs
- **[P] Practice** — Coding challenges where you type your solution and it gets validated
- **[Q] Quiz** — Multiple choice questions with explanations

## Run Individual Lessons

```bash
python3 -m lessons._01_basics
python3 -m lessons._05_oop
```

## Project Structure

```
python/
├── run.py              # Main menu
├── lessons/            # 10 interactive lessons
│   ├── _01_basics.py
│   ├── _02_control_flow.py
│   ├── ...
│   └── _10_decorators.py
├── utils/
│   └── interactive.py  # Quiz runner, challenge runner, display helpers
├── ds_learning/        # Original data structures reference
├── hash_learning/      # Original hash maps reference
└── tests/              # Unit tests
```

## Original Reference Modules

The `ds_learning/` and `hash_learning/` directories contain the original static reference content:

```bash
python3 python/data_structures_module.py
python3 python/hash_maps_module.py
```
