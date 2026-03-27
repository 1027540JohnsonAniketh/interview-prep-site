"""Lesson 5: Object-Oriented Programming — classes, inheritance, dunder methods."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.interactive import (
    print_header, print_subheader, print_code_and_output,
    print_concept, pause, run_quiz, run_coding_challenge, lesson_menu,
)


def learn():
    print_header("Learn: Object-Oriented Programming (OOP)")

    print_concept(
        "What is OOP?",
        "OOP organizes code around 'objects' that bundle data (attributes) and "
        "behavior (methods). A class is the blueprint, an object is the instance. "
        "Think of a class as a cookie cutter and objects as cookies.",
    )

    # --- Basic class ---
    print_subheader("Defining a Class")
    print_code_and_output(
        'class Dog:\n    def __init__(self, name, breed):\n        self.name = name      # instance attribute\n        self.breed = breed\n\n    def bark(self):           # instance method\n        return f"{self.name} says Woof!"\n\nmy_dog = Dog("Rex", "Labrador")\nprint(my_dog.bark())\nprint(f"{my_dog.name} is a {my_dog.breed}")',
        "Rex says Woof!\nRex is a Labrador",
    )
    print_concept(
        "__init__ and self",
        "__init__ is the constructor — called when you create an object. "
        "'self' refers to the instance being created. Every method gets 'self' "
        "as its first parameter automatically.",
    )
    pause()

    # --- Class vs Instance attributes ---
    print_subheader("Class vs Instance Attributes")
    print_code_and_output(
        'class Counter:\n    count = 0  # Class attribute — shared by all instances\n\n    def __init__(self):\n        Counter.count += 1  # Modify via class name\n        self.id = Counter.count  # Instance attribute\n\na = Counter()\nb = Counter()\nc = Counter()\nprint(f"Total counters: {Counter.count}")  # 3\nprint(f"c.id = {c.id}")                    # 3',
        "Total counters: 3\nc.id = 3",
    )
    pause()

    # --- Inheritance ---
    print_subheader("Inheritance")
    print_concept(
        "Inheritance",
        "A child class inherits all attributes and methods from a parent class, "
        "then can add or override them. This promotes code reuse.",
    )
    print_code_and_output(
        'class Animal:\n    def __init__(self, name):\n        self.name = name\n\n    def speak(self):\n        return "..."\n\nclass Cat(Animal):  # Cat inherits from Animal\n    def speak(self):  # Override parent method\n        return f"{self.name} says Meow!"\n\nclass Dog(Animal):\n    def speak(self):\n        return f"{self.name} says Woof!"\n\nfor animal in [Cat("Whiskers"), Dog("Rex")]:\n    print(animal.speak())',
        "Whiskers says Meow!\nRex says Woof!",
    )
    pause()

    # --- Dunder methods ---
    print_subheader("Dunder (Magic) Methods")
    print_concept(
        "Dunder methods",
        "Methods with double underscores like __str__, __repr__, __len__, __eq__. "
        "They let your objects work with Python's built-in operations.",
    )
    print_code_and_output(
        'class Point:\n    def __init__(self, x, y):\n        self.x = x\n        self.y = y\n\n    def __str__(self):       # print() uses this\n        return f"Point({self.x}, {self.y})"\n\n    def __repr__(self):      # Debug representation\n        return f"Point(x={self.x}, y={self.y})"\n\n    def __eq__(self, other):  # == comparison\n        return self.x == other.x and self.y == other.y\n\n    def __add__(self, other):  # + operator\n        return Point(self.x + other.x, self.y + other.y)\n\np1 = Point(1, 2)\np2 = Point(3, 4)\nprint(p1)            # Uses __str__\nprint(p1 + p2)       # Uses __add__\nprint(p1 == Point(1, 2))  # Uses __eq__',
        "Point(1, 2)\nPoint(4, 6)\nTrue",
    )
    pause()

    # --- @property ---
    print_subheader("@property — Computed Attributes")
    print_code_and_output(
        'class Circle:\n    def __init__(self, radius):\n        self.radius = radius\n\n    @property\n    def area(self):\n        return 3.14159 * self.radius ** 2\n\n    @property\n    def diameter(self):\n        return self.radius * 2\n\nc = Circle(5)\nprint(f"Area: {c.area:.2f}")      # Accessed like attribute, not method!\nprint(f"Diameter: {c.diameter}")',
        "Area: 78.54\nDiameter: 10",
    )
    print_concept(
        "@property",
        "@property lets you define methods that look like attribute access. "
        "Use it for computed values that depend on other attributes.",
    )
    print()


def practice():
    challenges = [
        {
            "prompt": "Create a class 'Rectangle' with width and height. Add a method 'area' that returns width * height.",
            "hint": "def __init__(self, width, height): ...",
            "validator": lambda ns, code: (
                "Rectangle" in ns
                and callable(ns["Rectangle"])
                and hasattr(ns["Rectangle"](3, 4), "area")
                and ns["Rectangle"](3, 4).area() == 12
            ),
            "solution": "class Rectangle:\n    def __init__(self, width, height):\n        self.width = width\n        self.height = height\n    def area(self):\n        return self.width * self.height",
        },
        {
            "prompt": "Create a class 'BankAccount' with a balance. Add 'deposit(amount)' and 'withdraw(amount)' methods.\nwithdraw should not allow going below 0 (just don't change balance).",
            "hint": "Check if balance - amount >= 0 before withdrawing",
            "validator": lambda ns, code: (
                "BankAccount" in ns
                and (lambda: (
                    (a := ns["BankAccount"](100)) or True,
                    a.deposit(50),
                    a.withdraw(30),
                    a.withdraw(200),  # Should not go below 0
                    a.balance == 120,
                ))()[-1]
            ),
            "solution": "class BankAccount:\n    def __init__(self, balance):\n        self.balance = balance\n    def deposit(self, amount):\n        self.balance += amount\n    def withdraw(self, amount):\n        if self.balance - amount >= 0:\n            self.balance -= amount",
        },
        {
            "prompt": "Add a __str__ method to a class 'Student' with name and grade.\nprint(Student('Alice', 'A')) should output 'Student(Alice, grade=A)'",
            "hint": "def __str__(self): return f'Student(...)'",
            "validator": lambda ns, code: (
                "Student" in ns
                and str(ns["Student"]("Alice", "A")) == "Student(Alice, grade=A)"
            ),
            "solution": "class Student:\n    def __init__(self, name, grade):\n        self.name = name\n        self.grade = grade\n    def __str__(self):\n        return f'Student({self.name}, grade={self.grade})'",
        },
    ]
    run_coding_challenge(challenges)


def quiz():
    questions = [
        {
            "question": "What is 'self' in a Python class?",
            "options": ["A keyword like 'this' in Java", "Reference to the current instance", "A global variable", "The class itself"],
            "answer": 1,
        },
        {
            "question": "What method is called when you do print(my_object)?",
            "options": ["__repr__", "__str__", "__print__", "__display__"],
            "answer": 1,
            "explanation": "print() calls __str__(). If __str__ isn't defined, it falls back to __repr__.",
        },
        {
            "question": "What does @property do?",
            "options": [
                "Makes an attribute private",
                "Lets you access a method like an attribute",
                "Creates a class variable",
                "Prevents modification",
            ],
            "answer": 1,
        },
        {
            "question": "In class Cat(Animal), what is Animal?",
            "options": ["Child class", "Parent/base class", "Interface", "Module"],
            "answer": 1,
        },
        {
            "question": "What is a class attribute?",
            "options": [
                "Defined in __init__ with self",
                "Shared by all instances of the class",
                "Only accessible inside methods",
                "Automatically private",
            ],
            "answer": 1,
            "explanation": "Class attributes are defined directly in the class body, shared by all instances.",
        },
    ]
    run_quiz(questions)


def main():
    lesson_menu("Lesson 5: OOP", learn, practice, quiz)


if __name__ == "__main__":
    main()
