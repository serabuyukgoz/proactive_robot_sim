import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
from itertools import count

#','.join(strings)

# adjacency_list = {'A' : [[1, 'B'], [2, 'C']],
#                     'B' : [[1, 'A'], [3, 'C']],
#                     'C' : [[2, 'B'], [3, 'A']],
#                 }
#
# desirability = {'A' : 1.0,
#                     'B' : 0.5,
#                     'C' : 0,
#
# }
#
#
#
#
#
# groups = set(nx.get_node_attributes(g,'group').values())
# mapping = dict(zip(sorted(groups),count()))
# nodes = g.nodes()
# colors = [mapping[g.node[n]['group']] for n in nodes]
#
#
# my_G.graph
# #nx.draw(my_G)
# nx.draw(my_G, with_labels=1, node_color=desirability, cmap = cmap)
# plt.show()

def graph(adjacency_list):
    my_G = nx.DiGraph()

    for keys in adjacency_list:
        #my_G.add_node(keys)
        for each in adjacency_list[keys]:
            my_G.add_edge(keys, each[1])

    k = my_G.nodes()

    my_G.graph
    nx.draw(my_G, with_labels=1)
    plt.show()
