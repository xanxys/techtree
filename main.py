#!/bin/python3
import pandas as pd
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import cairo
import parser_jp

# Only fixes matplotlib, not networkx labels
# cf. https://qiita.com/grachro/items/4c9b03366cae2df3a301
plt.rcParams['font.family'] = 'Droid Sans'


def visualize_print_text(table):
    for ix_code in range(table.num_codes):
        curr_code = table.coeff_code_names[ix_code]
        top_inputs = sorted(
            enumerate(table.coeff_matrix[:, ix_code]), key=lambda t: t[1], reverse=True)

        print(curr_code, ["%.3f:%s" % (
            k, table.coeff_code_names[i]) for (i, k) in top_inputs if k > 0.05])


def to_graph(table):
    """
    Returns nx.DiGraph, with vertex label being codename.
    The graph is guranteed to be a connected DAG (Directed Acyclic Graph).
    """
    df_srcs = []
    df_dsts = []

    for ix_code in range(table.num_codes):
        curr_code = table.coeff_code_names[ix_code]

        top_inputs = sorted(
            enumerate(table.coeff_matrix[:, ix_code]), key=lambda t: t[1], reverse=True)

        for (i, k) in top_inputs:
            if k < 0.05:
                continue
            if i == ix_code:
                print("Skipped self-loop for %s (k=%.4f)" %
                      (curr_code, k))
                continue
            df_srcs.append(table.coeff_code_names[i])
            df_dsts.append(curr_code)

    df = pd.DataFrame({'from': df_srcs, 'to': df_dsts})
    graph = nx.from_pandas_dataframe(
        df, 'from', 'to', create_using=nx.DiGraph())

    # DAG-ness is data-dependent, so failure can very well be a data issue rather than a bug.
    print(list(nx.simple_cycles(graph)))
    # TODO: Come up with generic cycle-breaking solution.
    # This is not just a pure algorithm question, it also touches fundamentals of what we're trying to draw here.
    graph.remove_edge('電力', '石炭・原油・天然ガス')
    assert(nx.is_directed_acyclic_graph(graph))
    return graph


def visualize_interactive_ugly(table):
    graph = to_graph(table)

    pos = nx.spring_layout(graph, iterations=500)
    nx.draw(graph, pos=pos, with_labels=True, node_size=1500,
            alpha=0.3, arrows=True, font_family='VL Gothic')
    plt.title("Techtree")
    plt.show()


# graph.num_nodes is about 100~200, don't worry about bad time complexity.
def visualize_civ_style(table):
    graph = to_graph(table)  # not necessarily a DAG

    # Get leftmost node & rightmost node, and length between them.
    srcs = [node for node in graph.nodes() if not nx.ancestors(graph, node)]
    dsts = [node for node in graph.nodes() if not nx.descendants(graph, node)]
    assert(len(set(srcs) & set(dsts)) == 0)
    print("S:", srcs)
    print("D:", dsts)

    s_d_paths = []
    for s in srcs:
        for d in dsts:
            try:
                path = nx.shortest_path(graph, s, d)
                s_d_paths.append((path, len(path)))
            except nx.exception.NetworkXNoPath:
                pass
    assert(s_d_paths)
    longest_path, dist = max(s_d_paths, key=lambda x: x[1])
    code_to_depth = {}
    for (depth, code) in enumerate(longest_path):
        code_to_depth[code] = depth

    # Super naive 0-rounded depth assignment, treating longest_path as
    # the "trunk" (i.e. each node has a depth constraint).
    current_depth = 0
    for n in nx.topological_sort(graph):
        if n in code_to_depth:
            current_depth = code_to_depth[n]
        else:
            code_to_depth[n] = current_depth
    # print(graph.number_of_nodes(), len(nx.topological_sort(graph)), len(code_to_depth), table.num_codes)
    assert(len(code_to_depth) <= table.num_codes)  # note some vertices are omitted in to_graph (TBC)
    
    depth_to_nodes = {}
    for (n, d) in code_to_depth.items():
        if d not in depth_to_nodes:
            depth_to_nodes[d] = set()
        depth_to_nodes[d].add(n)

    for (d, ns) in depth_to_nodes.items():
        print("depth=%d: %s" % (d, ns))
    


def main():
    table = parser_jp.InputCoefficientTable(
        'data-jp/2011-input_coeff_table.csv')
    visualize_print_text(table)
    visualize_civ_style(table)
    # visualize_interactive_ugly(table)


if __name__ == '__main__':
    main()
