import sys
from pathlib import Path

sys.path.append(str(Path(__file__).absolute().parent.parent))

import numpy as np
from functools import reduce
from lab1.utils import parse_nodes, get_unique_nodes
from lab1.base_argument_parser import graph_argparser


arg_parser = graph_argparser()


def parse_nodes_to_numpy(nodes_src: dict) -> np.ndarray:
    n = len(get_unique_nodes(nodes_src))
    mat = np.zeros(n * n).reshape(n, -1)
    parents = np.array(list(nodes_src.keys()))
    parents -= 1  # to indexes
    childrens = list(nodes_src.values())

    for i, parent in enumerate(parents):
        children = [i - 1 for i in childrens[i]]
        mat[parent, children] = 1
    return mat


def calculate_basics_recur(
    curr_mat: np.ndarray, _rank=1, _adj_mat=None, _mat_r1=None, _ranked_mats=None
) -> tuple[np.ndarray, np.ndarray, int]:
    if _mat_r1 is None:
        _mat_r1 = curr_mat
    if _ranked_mats is None:
        _ranked_mats = [curr_mat]
    next_mat = np.matmul(curr_mat, _mat_r1)
    if next_mat.sum() == 0:
        return curr_mat, _adj_mat, _rank, _ranked_mats
    _rank += 1
    _adj_mat = curr_mat + next_mat if _adj_mat is None else _adj_mat + next_mat
    curr_mat = next_mat
    _ranked_mats.append(curr_mat)
    return calculate_basics_recur(curr_mat, _rank, _adj_mat, _mat_r1, _ranked_mats)


def is_there_circuit(mat: np.ndarray) -> bool:
    """
    Return `False` if there is no circuit
    else `True`

    Args:
        mat (np.ndarray): _description_
    """
    return (mat * np.eye(mat.shape[0]) == 0).all()


def get_and_print_tacts_elems(ranked_mats: list[np.ndarray]) -> dict[int]:
    _default = list(range(ranked_mats[0].shape[0]))
    tacts_to_nodes = {}
    length = len(ranked_mats)
    for i in range(-1, length):
        num_of_tact = i + 1
        if i == -1:
            # TODO: убрать это условие, добавиви нулевым элементом нулевую матрицу
            curr_elems = _default
            next_elems = [
                i for i, val in enumerate(ranked_mats[0].sum(axis=0)) if val == 0
            ]
        else:
            assert is_there_circuit(ranked_mats[i]), "Circuit is detected" # 3.
            curr_elems = [
                i for i, val in enumerate(ranked_mats[i].sum(axis=0)) if val > 0
            ]
            if i + 1 >= length:
                next_elems = _default
            else:
                next_elems = [
                    i
                    for i, val in enumerate(ranked_mats[num_of_tact].sum(axis=0))
                    if val == 0
                ]
        tacts_to_nodes[str(num_of_tact)] = set(curr_elems) & set(next_elems)
        print(f"Элементы {num_of_tact} порядка: {[i+1 for i in tacts_to_nodes[str(num_of_tact)]]}")
    return tacts_to_nodes


def print_general_info(mat: np.ndarray, max_rank: int, tact_to_nodes: dict[int]) -> None:
    """
        Print properties 2, 4, 5 from metodichka (XD)
    Args:
        max_rank (int): _description_
        tact_to_nodes (dict[int]): _description_
    """
    inputs = [j+1 for j in range(mat.shape[1]) if mat[:,j].sum() == 0]
    outputs = [i+1 for i in range(mat.shape[0]) if mat[i,:].sum() == 0]
    print(f"Тактность системы: {max_rank}")
    print(f"Входные элементы: {inputs}")
    print(f"Выходные элементы: {outputs}")


def print_all_paths_by_length(ranked_mats: np.ndarray) -> None:
    for n, rmat in enumerate(ranked_mats):
        paths = [
            (i+1, j+1)
            for i in range(rmat.shape[0])
            for j in range(rmat.shape[0])
            if rmat[i][j] == 1.
        ]
        print(f"Пути длинной {n+1}:")
        for (st, fin) in paths:
            print(f"  {st} -> {fin}")


def print_amounts_all_possible_paths(mat_summed: np.ndarray) -> None:
    n = mat_summed.shape[0]
    print("Все возможные пути: (откуда)->(куда):(количество)")
    for i in range(n):
        for j in range(n):
            num = int(mat_summed[i][j])
            if num < 1:
                continue
            print(f"  {i+1} -> {j+1}: {num}")


def print_all_parents_for_every_node(mat_summed: np.ndarray) -> None:
    for col in range(mat_summed.shape[1]):
        parents = np.where(mat_summed[:,col] > 0)
        parents = [i+1 for i in parents[0]]
        print(f"{col+1} формируют элементы: {parents}")


def print_oriented_graph_info(mat: np.ndarray) -> None:
    _, _, max_rank, ranked_mats = calculate_basics_recur(mat)
    tact_to_nodes = get_and_print_tacts_elems(ranked_mats) # 1.
    print_general_info(mat, max_rank, tact_to_nodes) # 2. 4. 5.
    print_all_paths_by_length(ranked_mats) # 7. пути длиною x
    mat_summed = reduce(lambda x, y: x+y, ranked_mats)
    print_amounts_all_possible_paths(mat_summed) # 8. всевозможные пути
    print_all_parents_for_every_node(mat_summed) # 9. все формирующие элементы
    
    print()


if __name__ == "__main__":
    args = arg_parser.parse_args()
    nodes_source = parse_nodes(args.nodes_sets)
    graph_mat = parse_nodes_to_numpy(nodes_source)
    print_oriented_graph_info(graph_mat)
