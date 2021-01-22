import sys
import os
import argparse
import random
import math
import scipy
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('MacOSX')

import population_networks
import visualization


def simulate_multiphase_epidemic(graph, beta, alpha, gamma, p_0, t_a, t_s, t_q, T, plot_animation=False, simulation_name='', **_):
    nx.set_node_attributes(graph, 'S', 'state')
    nx.set_node_attributes(graph, math.inf, 'time_to_move')

    states = {state : 0 for state in ['S', 'I_a', 'I_s', 'I_q', 'D']}
    states['S'] = len(graph.nodes())
    I = set(random.sample(graph.nodes(), int(p_0 * states['S'])))
    states_hist = {}

    def update_states_hist():
        for state, count in states.items():
            states_hist[state] = states_hist.get(state, []) + [count]

    def update_states(nodes_to_new_states):
        for node, new_state in nodes_to_new_states.items():
            prev_state = graph.nodes[node]['state']
            assert new_state != prev_state
            states[prev_state] -= 1
            states[new_state] += 1
            graph.nodes[node]['state'] = new_state
            graph.nodes[node]['time_to_move'] = {'S' : math.inf, 'I_a' : t_a, 'I_s' : t_s, 'I_q' : t_q, 'D' : math.inf}[new_state]
            if new_state in ['S', 'D']:
                I.remove(node)
            if new_state in ['I_a']:
                I.add(node)

    update_states({node : 'I_a' for node in I})    
    update_states_hist()

    if plot_animation:
        plot = visualization.AnimatedPlot(T, pagerank=False)
        plot.add_frame(graph, states_hist)

    print('Simulation epidemic')
    for t in range(T):
        print(f'{round(t / T * 100, 2)}%', end="\r")
        nodes_to_new_states = {}
        for node in I:
            state = graph.nodes[node]['state']
            infection_probability = {'I_a' : beta, 'I_s' : beta / alpha, 'I_q' : 0}[state]
            if infection_probability != 0:
                for neighbor in graph[node]:
                    if graph.nodes[neighbor]['state'] == 'S' and random.random() < infection_probability:
                        nodes_to_new_states[neighbor] = 'I_a'

            graph.nodes[node]['time_to_move'] -= 1
            if graph.nodes[node]['time_to_move'] <= 0:
                if state == 'I_a':
                    nodes_to_new_states[node] = 'I_s'
                elif state == 'I_s':
                    nodes_to_new_states[node] = random.choices(['I_q', 'D'], weights=[1 - gamma, gamma])[0]
                else:
                    nodes_to_new_states[node] = 'S'
        update_states(nodes_to_new_states)
        update_states_hist()
        if plot_animation:
            plot.add_frame(graph, states_hist)

    print('Done')

    if plot_animation:
        plot.show(simulation_name)
    return states_hist


# Usage example: 
# python simulate_multiphase_epidemic.py -model SIS -network complete
def main():
    arg_parser = argparse.ArgumentParser(description='Epidemiological simulation of covid-inspired SI/SIS model', allow_abbrev=False)
    arg_parser._get_option_tuples = lambda _: [] # To fix a bug in argparse 3.8.x that ignores allow_abbrev

    arg_parser.add_argument('-network', help='population network', choices=population_networks.network_types, required=True)
    arg_parser.add_argument('-p_0', help='initial proportion of infected population', type=float, required=True)
    arg_parser.add_argument('-beta', help='infection probability', type=float, required=True)
    arg_parser.add_argument('-alpha', help='syntomatic infection probability factor', type=float, required=True)
    arg_parser.add_argument('-gamma', help='death probability', type=float, required=True)
    arg_parser.add_argument('-t_a', help='time in infected asymptomatic state', type=int, required=True)
    arg_parser.add_argument('-t_s', help='time in infected syntomatic state (time to test)', type=int, required=True)
    arg_parser.add_argument('-t_q', help='time while in quarentine', type=int, required=True)
    arg_parser.add_argument('-T', help='total time of the simulation', type=int, default=10**5)
    arg_parser.add_argument('-seed', help='random seed', type=int, default=random.randint(0, 1000))
    arg_parser.add_argument('-plot_animation', help='plot_animation', action='store_true')
    arg_parser.add_argument('-save_plots', help='save plots', action='store_true')
    args, network_args = arg_parser.parse_known_args()
    
    random.seed(args.seed)
    np.random.seed(args.seed)

    simulation_name = ''
    if args.save_plots:
        simulation_name = '_'.join([arg for arg in sys.argv[1:] if arg not in ['-plot_animation', '-save_plots']])
        if not os.path.exists('plots/'):
            os.makedirs('plots/')
        if not os.path.exists('plots/' + simulation_name):
            os.makedirs('plots/' + simulation_name)


    graph = population_networks.get_network(args.network, network_args)

    states_hist = simulate_multiphase_epidemic(graph, simulation_name=simulation_name, **vars(args))

    visualization.plot_states_hist(states_hist, simulation_name=simulation_name)
    visualization.plot_new_cases(states_hist, simulation_name=simulation_name)

main()
