import os
import pickle
import argparse
import random
import networkx as nx

import visualization


home_size_distributions = {
    'spain_2011' : { # https://www.ine.es/jaxi/Datos.htm?path=/t20/e244/hogares/p03/l0/&file=03011.px
        1 : 0.25,
        2 : 0.3,
        3 : 0.21,
        4 : 0.17,
        5 : 0.04,
        6 : 0.01
    },
    'spain_2013' : { # https://www.ine.es/ss/Satellite?L=es_ES&c=INECifrasINE_C&cid=1259944407896&p=1254735116567&pagename=ProductosYServicios%2FINECifrasINE_C%2FPYSDetalleCifrasINE
        1 : 0.24,
        2 : 0.3,
        3 : 0.21,
        4 : 0.18,
        5 : 0.06
    }
}


def create_real_life_population_network(n, home_size_dist, home_pos_dist, theta, max_edges_per_node=5):

    home_sizes, probs = zip(*home_size_distributions[home_size_dist].items())
    epsilon = 0.000001

    positions = {}
    node_to_home_id = {}
    home_id_to_nodes = {}
    fixed_nodes = []
    while n > 0:
        home_size = random.choices(home_sizes, probs, k=1)[0]

        if home_pos_dist == 'gaussian':
            pos = (random.gauss(0, 1), random.gauss(0, 1))
        else:
            pos = (random.random(), random.random())

        home_id = n
        home_id_to_nodes[home_id] = []
        for i in range(home_size):
            node = len(positions)
            positions[node] = (pos[0] + random.uniform(-0.01, 0.01), pos[1] + random.uniform(-0.01, 0.01))
            node_to_home_id[node] = home_id
            home_id_to_nodes[home_id].append(node)
            if i == 0:
                fixed_nodes.append(node)

        n -= home_size

    n = len(positions)

    # graph = nx.soft_random_geometric_graph(n, 1, pos=positions)
    graph = nx.geographical_threshold_graph(n, theta, pos=positions, p_dist=lambda r: max(r, epsilon) ** -2)

    for node in graph.nodes():
        neighbors = graph.adj[node].keys()
        if len(neighbors) > max_edges_per_node:
            neighbors_to_remove = random.sample(neighbors, len(neighbors) - max_edges_per_node)
            graph.remove_edges_from([(node, neighbor) for neighbor in neighbors_to_remove if graph.degree(neighbor) > 1])

    for home_id, node_list in home_id_to_nodes.items():
        graph.add_edges_from([(a, b) for a in node_list for b in node_list if a != b], weight=24)

    # to separate a bit the nodes in the same family
    # positions = nx.spring_layout(graph, pos=positions, fixed=fixed_nodes, k=0.1, weight='weight')

    nx.set_node_attributes(graph, positions, 'pos')
    nx.set_node_attributes(graph, node_to_home_id, 'home_id')

    return graph


network_types = {
    'complete' : (
        nx.complete_graph, 
        {
            'n' : {'help' : 'n', 'type' : int, 'required' : True}
        }
    ),
    'random_graph' : (
        nx.erdos_renyi_graph,
        {
            'n' : {'help' : 'n', 'type' : int, 'required' : True},
            'p' : {'help' : 'p', 'type' : float, 'required' : True}
        }
    ),
    'geo_graph' : (
        nx.geographical_threshold_graph,
        {
            'n' : {'help' : 'n', 'type' : int, 'required' : True},
            'theta' : {'help' : 'threshold', 'type' : float, 'required' : True}
        }
    ),
    'real_life' : (
        create_real_life_population_network,
        {
            'n' : {'help' : 'n', 'type' : int, 'required' : True},
            'home_size_dist' : {'help' : 'distribution of home sizes', 'choices' : home_size_distributions, 'default' : 'spain_2011'},
            'home_pos_dist' : {'help' : 'distribution of home positions', 'choices' : ['uniform', 'gaussian'], 'default' : 'gaussian'},
            'theta' : {'help' : 'threshold', 'type' : float, 'required' : True}
        }
    )
}


def get_network(network_type, args):
    arg_parser = argparse.ArgumentParser(description=f'{network_type} network arguments', prog='population_network.py')

    network_constructor, network_args = network_types[network_type]
    for arg, values in network_args.items():
        arg_parser.add_argument(f'-{arg}', **values)

    network_name = network_type + '_' + '_'.join(args)
    args = arg_parser.parse_args(args)
    
    file_name = 'networks/' + network_name
    if os.path.isfile(file_name):
        print('Network already created. Deserializing...')
        with open(file_name, 'rb') as file:
            network = pickle.load(file)
    else:
        print('Creating network')
        network = network_constructor(**vars(args))
        if not os.path.exists('networks'):
            os.makedirs('networks')
        with open(file_name, 'wb') as file:
            pickle.dump(network, file)

    print('Done')
    return network
