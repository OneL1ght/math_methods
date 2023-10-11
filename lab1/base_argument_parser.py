def graph_argparser():
    import argparse

    arg_parser = argparse.ArgumentParser(add_help=True)
    arg_parser.add_argument(
        "nodes_sets",
        type=str,
        help=f"[<node>]:[<child_node>,...];\nExample: '1:2,5; 2:3,5; 5:4;' ",
    )
    return arg_parser
