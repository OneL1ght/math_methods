import argparse
from datetime import datetime
from pathlib import Path
from utils import draw_graph


arg_parser = argparse.ArgumentParser(add_help=True)
arg_parser.add_argument(
    "nodes_sets",
    type=str,
    help=f"[<node>]:[<child_node>,...];\nExample: '1:2,5; 2:3,5; 5:4;' ",
)


def parse_nodes(_s: str) -> dict:
    parts = _s.split(";")
    relations = {}
    for inst in parts:
        if ":" not in inst:
            continue
        node, childs = inst.split(":")
        relations[int(node.strip())] = [int(s.strip()) for s in childs.split(",")]
    return relations


def get_unique_nodes(relations: dict):
    nodes = relations.keys() | [number for row in relations.values() for number in row]
    return sorted(list(nodes))


def find_contr_reachable_recursively(relations: dict, goal_node, result=None):
    if result is None:
        result = set()
    result.add(goal_node)
    parents = [p for p in relations.keys() if goal_node in relations[p]]
    for parent in parents:
        if parent not in result:
            find_contr_reachable_recursively(relations, parent, result)
    return result


def find_reachable_recursively(relations: dict, node, result=None):
    if result is None:
        result = set()
    childs = relations[node] if node in relations.keys() else []
    childs_with_childs = [
        child for child in childs if child in relations.keys() and child not in result
    ]

    result.add(node)  # child уже там будут, а так еще добавим корневую ноду
    result.update(childs)
    if len(childs_with_childs) > 0:
        for n in childs_with_childs:
            find_reachable_recursively(relations, n, result)
    return result


def group_strong_set(relations: dict, strong_set: set, _name: int) -> dict:
    """replace strong_set nodes by new node"""
    _name = f"V{_name}"
    relations[_name] = []
    nodes_with_children = relations.keys()
    for n in strong_set:
        if n not in nodes_with_children:
            continue
        relations[_name] += relations[n]
        relations.pop(n)
    for node, children in relations.items():
        relations[node] = [
            old_child if old_child not in strong_set else _name
            for old_child in children
        ]
    return relations


def remove_strong_set_nodes(nodes: list, strong_set: set):
    for n in strong_set:
        nodes.remove(n)


def print_nodes_and_children(relations: dict):
    print()
    for node, children in relations.items():
        if len(children) < 1:
            continue
        print(f"{node} = {set(children)}")


def optimize(relations: dict):
    session_folder = Path("./sessions").absolute() / str(
        datetime.now().strftime("%d_%b_%Y__%H_%M")
    )
    session_folder.mkdir(parents=True, exist_ok=True)
    step = 0
    draw_graph(relations, step, session_folder)

    nodes = get_unique_nodes(relations)
    while nodes:
        node = nodes[0]
        step += 1
        curr_reachable_set = set(find_reachable_recursively(relations, node))
        curr_contr_reachable_set = set(
            find_contr_reachable_recursively(relations, node)
        )
        strong_set = curr_reachable_set & curr_contr_reachable_set
        relations = group_strong_set(relations, strong_set, node)
        draw_graph(relations, step, session_folder)

        remove_strong_set_nodes(nodes, strong_set)
        print(f"V{node} contains: {strong_set}")
    print_nodes_and_children(relations)


if __name__ == "__main__":
    args = arg_parser.parse_args()
    nodes_source = args.nodes_sets
    relations = parse_nodes(nodes_source)
    optimize(relations)
