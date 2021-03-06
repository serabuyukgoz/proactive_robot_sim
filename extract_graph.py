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

def setColor(key):
    if key == 1.0:
        return 'green'
    elif key == 0:
        return 'red'
    elif key == -1:
        return 'white'
    else:
        return 'pink'

def graph(adjacency_list, hashmap, current_name):
    my_G = nx.DiGraph()

    color_map = {}
    color_map[current_name] = setColor(hashmap[current_name].desirability)
    for each in adjacency_list[current_name]:
        my_G.add_edge(current_name, each.name)
        color_map[each.name] = setColor(each.desirability)


    k = my_G.nodes()

    map_color = [color_map.get(node) for node in my_G.nodes()]

    my_G.graph
    #nx.draw(my_G, with_labels=True, node_color = map_color, node_shape="s", node_size=1500)
    nx.draw(my_G, with_labels=True, node_shape="s", node_color = map_color, node_size=10000, pos=nx.drawing.nx_agraph.graphviz_layout(
        my_G,
        prog='dot',
        args='-Grankdir=LR'
    ),
    labels = {n: n.replace(";", "\n") for n in my_G.nodes})
    print(my_G.number_of_nodes())
    plt.show()
