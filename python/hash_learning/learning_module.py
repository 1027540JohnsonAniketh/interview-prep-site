"""Core learning module for hash maps and linked hash maps."""

from collections import OrderedDict
from dataclasses import dataclass


@dataclass(frozen=True)
class UserId:
    """Custom hashable key type for demo."""

    region: str
    number: int


def hash_function_notes() -> list[str]:
    return [
        "A hash function converts input into an integer hash code.",
        "Python uses hash() for hashable objects.",
        "Hash collisions happen when different keys map to same index.",
        "Good hashing spreads keys to keep lookup fast.",
    ]


def map_notes() -> list[str]:
    return [
        "A map stores key-value pairs.",
        "Python map type is dict.",
        "Average get/set/delete is O(1).",
    ]


def hash_map_notes() -> list[str]:
    return [
        "dict is a hash map (hash-table-backed).",
        "Keys must be hashable and comparable for equality.",
        "Mutable objects like list/dict/set are unhashable.",
    ]


def linked_hash_map_notes() -> list[str]:
    return [
        "Python 3.7+ dict preserves insertion order.",
        "OrderedDict adds order-specific helpers (move_to_end, popitem).",
        "This is conceptually similar to Java LinkedHashMap behavior.",
    ]


def insertion_order_demo() -> tuple[list[str], list[str]]:
    normal = {"first": 1, "second": 2, "third": 3}
    ordered = OrderedDict(normal)
    ordered.move_to_end("first")
    return list(normal.keys()), list(ordered.keys())


def custom_key_demo() -> dict[UserId, int]:
    user_a = UserId(region="IN", number=101)
    user_b = UserId(region="IN", number=102)
    return {user_a: 1500, user_b: 2300}

