"""Core learning module for array, set, list, linked list, tree, and graph."""

from dataclasses import dataclass


def array_notes() -> list[str]:
    return [
        "Array-like structure in Python is list (dynamic array behavior).",
        "Index-based access is O(1).",
        "Insert/delete in middle is O(n) due to shifting.",
    ]


def set_notes() -> list[str]:
    return [
        "set stores unique elements only.",
        "Average membership check is O(1).",
        "Useful for deduplication and fast lookups.",
    ]


def list_notes() -> list[str]:
    return [
        "Python list is ordered and mutable.",
        "Supports slicing, append, pop, and iteration.",
        "Can store mixed data types, but consistent types are cleaner.",
    ]


@dataclass
class Node:
    value: int
    next: "Node | None" = None


def linked_list_notes() -> list[str]:
    return [
        "Linked list uses nodes connected by references.",
        "Efficient insert/delete at known node: O(1).",
        "Access by index is O(n), unlike array-style O(1).",
    ]


def build_linked_list(values: list[int]) -> Node | None:
    head: Node | None = None
    current: Node | None = None
    for value in values:
        node = Node(value=value)
        if head is None:
            head = node
            current = node
        else:
            current.next = node  # type: ignore[union-attr]
            current = node
    return head


def linked_list_to_list(head: Node | None) -> list[int]:
    result: list[int] = []
    curr = head
    while curr is not None:
        result.append(curr.value)
        curr = curr.next
    return result


def tree_notes() -> list[str]:
    return [
        "Tree is a hierarchical structure with parent-child relationships.",
        "Binary tree nodes have up to two children.",
        "Common traversals: preorder, inorder, postorder, level-order.",
    ]


def graph_notes() -> list[str]:
    return [
        "Graph is a collection of vertices (nodes) and edges.",
        "Can be directed/undirected and weighted/unweighted.",
        "Representations: adjacency list and adjacency matrix.",
    ]


def bfs(graph: dict[str, list[str]], start: str) -> list[str]:
    visited: set[str] = set()
    queue: list[str] = [start]
    order: list[str] = []

    while queue:
        node = queue.pop(0)
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                queue.append(neighbor)
    return order

