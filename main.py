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


def to_dag(table):
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

    # Assert DAG property. This is data-dependent, so failure can very well be a data issue rather than a bug.
    try:
        cycles = nx.find_cycle(graph)
        assert(False)
    except nx.exception.NetworkXNoCycle:
        return graph


def visualize_interactive_ugly(table):
    graph = to_dag(table)

    pos = nx.spring_layout(graph, iterations=500)
    nx.draw(graph, pos=pos, with_labels=True, node_size=1500,
            alpha=0.3, arrows=True, font_family='VL Gothic')
    plt.title("Techtree")
    plt.show()


def visualize_civ_style(table):
    graph = to_dag(table)

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
                s_d_paths.append(((s, d), len(nx.shortest_path(graph, s, d))))
            except nx.exception.NetworkXNoPath:
                pass
    assert(s_d_paths)
    dist, longest_path = max(s_d_paths, key=lambda x: x[1])
    print(dist, longest_path)


def main():
    table = parser_jp.InputCoefficientTable(
        'data-jp/2011-input_coeff_table.csv')
    visualize_print_text(table)
    # visualize_interactive_ugly(table)
    visualize_civ_style(table)


if __name__ == '__main__':
    main()
