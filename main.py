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


def visualize_interactive_ugly(table):
    df_srcs = []
    df_dsts = []

    for ix_code in range(table.num_codes):
        curr_code = table.coeff_code_names[ix_code]

        top_inputs = sorted(
            enumerate(table.coeff_matrix[:, ix_code]), key=lambda t: t[1], reverse=True)

        print(curr_code, ["%.3f:%s" % (
            k, table.coeff_code_names[i]) for (i, k) in top_inputs if k > 0.05])

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
    G = nx.from_pandas_dataframe(
        df, 'from', 'to', create_using=nx.DiGraph())

    try:
        print("cycles:", nx.find_cycle(G))
    except nx.exception.NetworkXNoCycle:
        print("--> no cycles!")
        pass

    pos = nx.spring_layout(G, iterations=500)

    nx.draw(G, pos=pos, with_labels=True, node_size=1500,
            alpha=0.3, arrows=True, font_family='VL Gothic')
    plt.title("Techtree")
    plt.show()


def visualize_civ_style(table):
    pass


def main():
    table = parser_jp.InputCoefficientTable(
        'data-jp/2011-input_coeff_table.csv')
    visualize_interactive_ugly(table)


if __name__ == '__main__':
    main()
