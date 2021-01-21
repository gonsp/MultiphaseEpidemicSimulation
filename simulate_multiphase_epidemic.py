import argparse
import random
import scipy
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('MacOSX')

import population_networks



def simulate_multiphase_epidemic(network, model, beta, t_a, t_s, t_q, gamma, T, video_animation=False):
    pass



# Usage example: 
# python simulate_multiphase_epidemic.py -model SIS -network complete
def main():
    arg_parser = argparse.ArgumentParser(description='Epidemiological simulation of covid-inspired SI/SIR/SIS model', allow_abbrev=False)
    arg_parser._get_option_tuples = lambda _: [] # To fix a bug in argparse 3.8.x that ignores allow_abbrev

    arg_parser.add_argument('-model', help='base epidemiological model', choices=['SI', 'SIR', 'SIS'], required=True)
    arg_parser.add_argument('-network', help='population network', choices=population_networks.network_types, required=True)
    arg_parser.add_argument('-beta', help='infection probability', type=float, required=True)
    arg_parser.add_argument('-t_a', help='time in infected asymptomatic state', type=int, required=True)
    arg_parser.add_argument('-t_s', help='time in infected syntomatic state (time to test)', type=int, required=True)
    arg_parser.add_argument('-t_q', help='time while in quarentine', type=int, required=True)
    arg_parser.add_argument('-gamma', help='death probability', type=float, required=True)
    arg_parser.add_argument('-T', help='total time of the simulation', type=int, default=10**5)
    arg_parser.add_argument('-seed', help='random seed', type=int, default=random.randint(0, 1000))
    arg_parser.add_argument('-show', help='show plot', action='store_true')
    args, network_args = arg_parser.parse_known_args()
    
    random.seed(args.seed)
    np.random.seed(args.seed)

    network = population_networks.get_network(args.network, network_args)

main()
