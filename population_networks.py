import os
import pickle
import argparse
import networkx as nx

import visualization


def create_real_population_network_model(target_population):
    geographical_threshold_graph


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
            'theta' : {'help' : 'threshold', 'type' : float, 'required' : True},
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

    # visualization.draw_network(network, without_states=True)
    print('Done')
    return network
