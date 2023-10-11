import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


SEED = 42


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


def draw_graph(relations: dict, step: int, save_folder: str):
    _from, _to = [], []
    for node, childs in relations.items():
        _from += [str(node)] * len(childs)
        _to += map(str, childs)
    df = pd.DataFrame({"from": _from, "to": _to})
    graph = nx.from_pandas_edgelist(df, "from", "to", create_using=nx.MultiDiGraph())

    fig = plt.figure()
    pos = nx.spring_layout(graph, k=3, scale=20, iterations=80, seed=SEED)
    nx.draw(
        graph,
        pos=pos,
        with_labels=True,
        node_size=2000,
        alpha=0.7,
        arrows=True,
        width=2,
        font_size=20,
    )
    plt.title(f"{step=}")
    plt.savefig(f"{save_folder}/{step=}")
    del graph, df, fig
